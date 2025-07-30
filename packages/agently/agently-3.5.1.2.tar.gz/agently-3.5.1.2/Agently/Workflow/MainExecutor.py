import uuid
import asyncio
import inspect
from .Runtime import RuntimeBranchState, RuntimeState, Snapshot, Checkpoint
from ..utils import RuntimeCtx
from .utils.exec_tree import disable_chunk_dep_ticket, create_new_chunk_slot_with_val
from .utils.find import find_by_attr
from .utils.runtime_supports import get_next_chunk_from_branch_queue
from .lib.BreakingHub import BreakingHub
from .lib.Store import Store
from .lib.constants import WORKFLOW_START_DATA_HANDLE_NAME, WORKFLOW_END_DATA_HANDLE_NAME, DEFAULT_INPUT_HANDLE_VALUE, DEFAULT_OUTPUT_HANDLE_VALUE, BUILT_IN_EXECUTOR_TYPES, EXECUTOR_TYPE_CONDITION

class MainExecutor:
    def __init__(self, workflow_id, settings: RuntimeCtx, logger, checkpoint: Checkpoint = None):
        # == Step 1. 初始化设定配置 ==
        self.workflow_id = workflow_id
        self.settings = settings
        self.max_execution_limit = self.settings.get('max_execution_limit') or 10
        self.logger = logger
        self.checkpoint = checkpoint
        # == Step 2. 初始化状态配置 ==
        # 中断器
        self.breaking_hub = BreakingHub(
            breaking_handler = self._handle_breaking,
            max_execution_limit=self.max_execution_limit
        )
        # 运行时状态
        self.runtime_state = RuntimeState(
            workflow_id=self.workflow_id,
            chunks_dep_state={},
            user_store=self.settings.get('store') or Store(),  # 运行时数据存储
            sys_store=self.settings.get('sys_store') or Store() # 运行时系统存储（如存储整个 workflow 的输入输出数据）
        )
        # 是否保留执行状态
        self.persist_state = self.settings.get('persist_state') == True
        self.persist_sys_state = self.settings.get('persist_sys_state') == True
        # 已注册的执行器
        self.registed_executors = {}
        # 执行节点字典
        self.chunks_map = {}

    async def start(self, executed_schema: dict, start_data: any = None, *, storage: dict = None):
        self.reset_all_runtime_status()
        # Set Initial Storage
        if storage and not isinstance(storage, dict):
            raise Exception(f"Initial storage can only be a dictionary.\nstorage = { storage }")
        elif storage and isinstance(storage, dict):
            self.runtime_state.user_store.update_by_dict(storage)

        # 初始化运行时状态
        self.runtime_state.update(chunks_dep_state=executed_schema.get('chunks_dep_state'))
        # 尝试灌入初始数据
        self.runtime_state.sys_store.set(WORKFLOW_START_DATA_HANDLE_NAME, start_data)
        self.chunks_map = executed_schema.get('chunk_map') or {}
        # 启动
        self.runtime_state.running_status = 'start'
        await self._execute_main(executed_schema.get('entries') or [])
        self.runtime_state.running_status = 'end'
        # 尝试返回执行结果
        return self.runtime_state.sys_store.get(WORKFLOW_END_DATA_HANDLE_NAME) or None
    
    async def start_from_snapshot(self, executed_schema: dict, snapshot: 'Snapshot'):
        # Step 1. 恢复各状态数据
        self.runtime_state.restore_from_snapshot(snapshot)
        self.chunks_map = executed_schema.get('chunk_map') or {}
        # Step 2. 恢复运行
        await self._execute_main(executed_schema.get('entries') or [])
        self.runtime_state.running_status = 'end'
        return self.runtime_state.sys_store.get(WORKFLOW_END_DATA_HANDLE_NAME) or None

    def regist_executor(self, name: str, executor):
        """
        注册执行器，传入执行器的名称及executor
        """
        self.registed_executors[name] = executor

    def unregist_executor(self, name: str):
        """
        取消注册执行器，传入执行器的名称
        """
        if name in self.registed_executors:
            del self.registed_executors[name]

        return self

    def reset_all_runtime_status(self):
        """重置状态配置"""
        self.runtime_state.running_status = 'idle'
        # 中断器
        self.breaking_hub = BreakingHub(
            breaking_handler=self._handle_breaking,
            max_execution_limit=self.max_execution_limit
        )
        # 运行时数据存储
        if not self.persist_state:
            self.runtime_state.user_store.remove_all()
        if not self.persist_sys_state:
            self.runtime_state.sys_store.remove_all()
        # 执行节点字典
        self.chunks_map = {}
    
    async def _execute_main(self, entries: list):
        """执行入口"""

        # 1、声明单个执行逻辑（异步）
        async def execute_from_entry(entry):
            branch_state = None
            # 恢复模式，直接使用已存储的状态
            if self.runtime_state.restore_mode:
                branch_state = self.runtime_state.get_branch_state(entry)
                # 已执行的分支直接跳过
                if branch_state.running_status in ['success', 'error']:
                    return
            # 正常模式，创建新分支状态
            else:
                branch_state = self.runtime_state.create_branch_state(entry)

            # 执行主逻辑
            branch_state.running_status = 'running'
            await self._execute_partial(entry, branch_state)
            branch_state.running_status = 'success'

        # 2、收集执行任务
        entry_tasks = [execute_from_entry(entry_chunk) for entry_chunk in entries]

        # 3、最后再统一执行
        await asyncio.gather(*entry_tasks)

    async def _execute_partial(self, chunk, branch_state: RuntimeBranchState):
        """分组执行的核心方法，整体基于队列的逻辑，确保整个过程可暂停/可恢复"""
        # 对于非恢复模式，或者恢复模式未执行态，默认初始化队列
        if not self.runtime_state.restore_mode or branch_state.get_chunk_status(chunk['id']) == 'idle':
            branch_state.running_queue.append(chunk['id'])

        while (branch_state.running_queue or branch_state.slow_queue) and branch_state.running_status != 'pause':
            # 本次是否为慢任务
            is_slow_task = (len(branch_state.running_queue) == 0) and (len(branch_state.slow_queue) > 0)
            current_chunk_id = get_next_chunk_from_branch_queue(branch_state)
            if not current_chunk_id:
                break

            chunk = self.chunks_map.get(current_chunk_id)
            if not chunk:
                raise SystemError(f'Target chunk({current_chunk_id}) not found')

            # 1、前置处理（如果是慢任务，先清空下游已执行的节点数据）
            if is_slow_task:
                self._chunks_clean_walker(chunk)

            # 2、执行 chunk
            has_been_executed = await self._execute_single_chunk(
                chunk=chunk,
                branch_state=branch_state,
                force_exec_loop=is_slow_task
            )
            # 清理，从队列中弹出本次执行的逻辑
            if is_slow_task:
                if len(branch_state.slow_queue):
                    branch_state.slow_queue.popleft()
            else:
                if len(branch_state.running_queue):
                    branch_state.running_queue.popleft()
            # 尝试自动保存 checkpoint
            if self.checkpoint and self.settings.get('auto_save_checkpoint') != False:
                await self.checkpoint.save_async(self.runtime_state)

            # 如果根本未执行过（如无执行票据），直接返回
            if not has_been_executed:
                continue

            # 3、将子任务放入执行队列中
            for next_info in chunk['next_chunks']:
                next_chunk = self.chunks_map.get(next_info['id'])
                if not next_chunk:
                    continue

                branch_state.running_queue.append(next_info['id'])

    async def _execute_single_chunk(self, chunk, branch_state: RuntimeBranchState, force_exec_loop = False):
        """执行完一个 chunk 自身（包含所有可用的依赖数据的组合）"""
        has_been_executed = False
        # 针对循环，不在本执行组内执行，存入缓执行组中，延后执行
        if (not force_exec_loop) and (chunk.get('loop_entry') == True) and (chunk['id'] in branch_state.visited_record):
            branch_state.slow_queue.append(chunk['id'])
            self.logger.debug(
                f"Put the loop starting chunk '{self._get_chunk_title(chunk)}' into the slow tasks queue for delayed execution")
            return has_been_executed

        # 获取执行chunk的依赖数据（每个手柄可能有多份就绪的数据）
        single_dep_map = self._extract_execution_single_dep_data(chunk)
        while (single_dep_map['is_ready'] and single_dep_map['has_ticket']):
            # 标识状态（仅需设置一次）
            if not has_been_executed:
                branch_state.update_chunk_status(chunk['id'], 'running')
            has_been_executed = True
            # 基于依赖数据快照，执行分组
            await self._execute_single_chunk_core(
                chunk=chunk,
                branch_state=branch_state,
                single_dep_map=single_dep_map['data']
            )
            # 执行后，收回本次用到的执行票据（仅在自身完了后才执行）
            self._disable_dep_execution_ticket(
                single_dep_map=single_dep_map['data'],
                chunk=chunk
            )
            # 再次更新获取依赖（如没有了，则停止了）
            single_dep_map = self._extract_execution_single_dep_data(chunk)
        # 更新结果状态
        if has_been_executed:
            branch_state.update_chunk_status(chunk['id'], 'success')
        return has_been_executed

    async def _execute_single_chunk_core(
        self,
        chunk,
        branch_state: RuntimeBranchState,
        single_dep_map: dict  # 依赖项（已拆组之后的）
    ):
        """根据某一份指定的的依赖数据，执行当前 chunk 自身（不包含下游 chunk 的执行调用）"""
        # 1、执行当前 chunk
        execute_id = str(uuid.uuid4())
        branch_state.executing_ids.append(execute_id)
        # self.logger.debug("With dependent data: ", single_dep_map)
        exec_res = await self._exec_chunk_with_dep_core(chunk, single_dep_map)
        exec_value = exec_res['value']
        condition_signal = exec_res['signal']

        self.breaking_hub.recoder(chunk)  # 更新中断器信息
        if chunk['id'] not in branch_state.visited_record:
            branch_state.visited_record.append(chunk['id'])  # 更新执行记录

        # 2、执行完成后，提取当前执行的结果，尝试将当前执行结果注入到下游的运行依赖插槽上 self.runtime_state.chunks_dep_state[][]['data_slots'][] = 'xxx'
        for next_info in chunk['next_chunks']:
            next_chunk = self.chunks_map.get(next_info['id'])
            if not next_chunk:
                continue

            # 针对目标 chunk 的目标 handle 的插槽位，注入最新的值（带执行票据的）。（注意如果是条件连接线，需要在条件满足时才更新）
            for next_rel_handle in next_info['handles']:
                source_handle = next_rel_handle['source_handle']
                target_handle = next_rel_handle['handle']
                source_value = None
                # 以下情况直接将完整值注入下游对应的插槽位置（此处的 target_handle）：执行结果为非 dict 类型，或者未定义上游 chunk 的输出句柄(此处的 source_handle)，或其输出句柄为默认全量输出句柄时
                if (not isinstance(exec_value, dict)) or (not source_handle) or (source_handle == DEFAULT_OUTPUT_HANDLE_VALUE):
                    source_value = exec_value
                else:
                    source_value = exec_value.get(source_handle)

                # 有条件的情况下，仅在条件满足时，才更新下游节点的数据
                condition_call = next_rel_handle.get('condition')
                if condition_call:
                    judge_res = condition_call(condition_signal, self.runtime_state.user_store)
                    connection_status = judge_res == True
                    self.logger.debug(
                        f"The connection status of '{self._get_chunk_title(chunk)}({source_handle})' to '{self._get_chunk_title(next_chunk)}({target_handle})': {connection_status}")
                    if not connection_status:
                        continue

                # 在下一个 chunk 的依赖定义中，找到与当前 chunk 的当前 handle 定义的部分，尝试更新其插槽值依赖
                self.logger.debug(
                    f"Try update chunk '{self._get_chunk_title(next_chunk)}' dep handle '{target_handle}' with value:{source_value}")
                deps = self.runtime_state.chunks_dep_state.get(next_chunk.get('id'))
                next_chunk_target_dep = find_by_attr(deps, 'handle', target_handle)
                if next_chunk_target_dep:
                    next_chunk_dep_slots = next_chunk_target_dep['data_slots'] or []
                    # 1、首先清空掉之前由当前节点设置，但票据已失效的值
                    next_chunk_target_dep['data_slots'] = next_chunk_dep_slots = [
                        slot for slot in next_chunk_dep_slots if not ((slot['updator'] == chunk['id']) and slot['execution_ticket'] == '')
                    ]

                    # 2、再把本次新的值加入到该下游 chunk 的对应输入点的插槽位中
                    next_chunk_dep_slots.append(
                        create_new_chunk_slot_with_val(chunk['id'], source_value))

        # 任务执行完后，清理执行中的状态
        branch_state.executing_ids.remove(execute_id)
    
    async def _exec_chunk_with_dep_core(self, chunk, specified_deps = {}):
        """ 执行任务（执行到此处的都是上游数据已就绪了的） """
        # 简化参数
        deps_dict = {}
        for dep_handle in specified_deps:
            deps_dict[dep_handle] = specified_deps[dep_handle]['value']
        
        input_value = deps_dict

        # 激进模式下的特殊处理
        if self.settings.get('mode') == 'aggressive':
            # 如果只有一个数据挂载，且为 default，则直接取出来作为默认值
            all_keys = list(deps_dict.keys())
            if len(all_keys) == 1 and all_keys[0] == DEFAULT_INPUT_HANDLE_VALUE:
                input_value = deps_dict['default']

        # 交给执行器执行
        executor_type = chunk['type']
        chunk_executor = self._get_chunk_executor(executor_type) or chunk.get('executor')
        # 是否内置的执行器（会追加系统信息）
        is_built_in_type = executor_type in BUILT_IN_EXECUTOR_TYPES
        exec_res = None
        if not chunk_executor:
            err_msg = f"Node {executor_type} Error-'{self._get_chunk_title(chunk)}'({chunk['id']}): The 'executor' is required but get 'NoneType'"
            self.logger.error(err_msg)
            # 主动中断执行
            raise Exception(err_msg)
        try:
            self.logger.info(f"Executing chunk '{self._get_chunk_title(chunk)}'")
            # 如果执行器是异步的，采用 await调用
            if inspect.iscoroutinefunction(chunk_executor):
                if is_built_in_type:
                    exec_res = await chunk_executor(input_value, self.runtime_state.user_store, sys_store=self.runtime_state.sys_store, chunk=chunk)
                else:
                    exec_res = await chunk_executor(input_value, self.runtime_state.user_store)
            else:
                if is_built_in_type:
                    exec_res = chunk_executor(input_value, self.runtime_state.user_store, sys_store=self.runtime_state.sys_store, chunk=chunk)
                else:
                    exec_res = chunk_executor(input_value, self.runtime_state.user_store)
        except Exception as e:
            self.logger.error(f"Node Execution Exception-'{self._get_chunk_title(chunk)}'({chunk['id']}):\n {e}")
            # 处理 checkpoint 自动保存到默认的 checkpoint 点
            if self.checkpoint and self.settings.get('save_checkpoint_on_error') != False:
                await self.checkpoint.save_async(self.runtime_state)
                self.logger.info("Checkpoint has been automatically saved.")
            # 主动中断执行
            raise Exception(e)

        exec_value = exec_res
        condition_signal = None
        # 条件节点，拆分为条件信号和执行结果两部分
        if chunk['type'] == EXECUTOR_TYPE_CONDITION:
            exec_value = exec_res.get('values')
            condition_signal = exec_res.get('condition_signal')
        return {
            "value": exec_value,
            "signal": condition_signal
        }
    
    def _extract_execution_single_dep_data(self, chunk):
        """实时获取某个 chunk 的一组全量可执行数据（如没有，则返回 None）"""
        deps = self.runtime_state.chunks_dep_state.get(chunk.get('id'))
        if not deps or len(deps) == 0:
            return {"is_ready": True, "data": None, "has_ticket": True}
        single_dep_map = {}
        exist_exec_ticket = False

        for dep in deps:
            slots = dep['data_slots'] or []
            handle_name = dep['handle']
            # 暂存的就绪的数据（循环中会不停更新，后头的会覆盖前头的），注意，就绪的数据也有可能就是 None，所以 None 不代表没有就绪数据
            tmp_ready_slot = None
            # 是否有就绪的值
            has_ready_value = False

            for slot in slots:
                # 找到就绪的数据
                if slot['is_ready']:
                    has_ready_value = True
                    # 先暂存就绪的数据作为临时数据（后面的会覆盖前头的）
                    tmp_ready_slot = slot

                    # 如果目前全局还没遇到过有票据，且当前为有票据的情况，则作为本次执行的消耗票据
                    if slot['execution_ticket'] and not exist_exec_ticket:
                        exist_exec_ticket = True
                        single_dep_map[handle_name] = slot
                        break

            # 如果跑完所有，还是没设置值（可能没有就绪的数据，或者就绪的数据都是有票据的），需要从就绪的数据中强行取一个作为本次的值
            if (handle_name not in single_dep_map) and has_ready_value:
                single_dep_map[handle_name] = tmp_ready_slot

            # 如果本轮跑完都没有设置值，则标识该 handle 数据未就绪，直接返回
            if handle_name not in single_dep_map:
                return {"is_ready": False, "data": None, "has_ticket": exist_exec_ticket}

        return {"is_ready": True, "data": single_dep_map, "has_ticket": exist_exec_ticket}

    def _disable_dep_execution_ticket(self, single_dep_map, chunk):
        """销毁chunk对应的依赖执行票据（一般在执行结束后操作）"""
        for dep_handle in single_dep_map:
            # 找到被执行的 id
            effect_id = single_dep_map[dep_handle]['id']
            deps = self.runtime_state.chunks_dep_state.get(chunk['id'])
            for dep in deps:
                slots = dep['data_slots'] or []
                for slot in slots:
                    # 将当前 chunk 中对应手柄的数据项中的对应目标数据的执行票据收回
                    if slot['id'] == effect_id:
                        disable_chunk_dep_ticket(slot)

    def _get_chunk_executor(self, name: str):
        """ 根据类型名称获取执行器 """
        return self.registed_executors.get(name)

    def _chunks_clean_walker(self, root_chunk):
        """尝试对某个节点以下的分支做一轮清理工作"""

        visited_record = []
        def clean_core(chunk):
            for next_info in chunk['next_chunks']:
                next_chunk = self.chunks_map.get(next_info['id'])
                if not next_chunk:
                    continue

                # 同一个发起方的清理，只执行一次，避免死循环
                visited_symbol = f"{chunk['id']}-2-{next_chunk['id']}"
                if (visited_symbol in visited_record) or (next_chunk['id'] == root_chunk['id']):
                    continue

                visited_record.append(visited_symbol)
                effect_handles = [handle_desc['handle'] for handle_desc in next_info['handles']]
                deps = self.runtime_state.chunks_dep_state.get(next_chunk.get('id'))
                for dep in deps:
                    data_slots = dep['data_slots']
                    if len(data_slots):
                        for i in range(len(data_slots) - 1, -1, -1):
                            data_slot = data_slots[i]
                            # 如果当前的输入句柄是受上游影响的，则清理掉
                            if (dep['handle'] in effect_handles) and (data_slot['updator'] == '' or data_slot['updator'] == chunk['id']):
                                del data_slots[i]
                clean_core(next_chunk)

        clean_core(root_chunk)
    
    def _get_chunk_title(self, chunk):
        return chunk["title"] or f'chunk-{chunk["id"]}' or 'Unknow chunk'

    def _handle_breaking(self, chunk, type):
        """处理中断"""
        self.logger.error(
            f"Exceeded maximum execution limit: {self._get_chunk_title(chunk)}")
        # 中断之前处理相关逻辑
        # 主动中断执行
        raise Exception(
            f"Exceeded maximum execution limit: {self._get_chunk_title(chunk)}")

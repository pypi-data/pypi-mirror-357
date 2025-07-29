import json5
import asyncio
import threading
import queue
import re
from ..Request import Request
from ..utils import RuntimeCtx, RuntimeCtxNamespace, StorageDelegate, PluginManager, AliasManager, ToolManager, IdGenerator, DataGenerator, check_version, load_json

class Agent(object):
    def __init__(
        self,
        *,
        agent_id: str=None,
        auto_save: bool=False,
        parent_agent_runtime_ctx: object,
        parent_tool_manager: object,
        global_storage: object,
        parent_plugin_manager: object,
        parent_settings: object,
        is_debug: bool=None,
    ):
        # Integrate
        self.global_storage = global_storage
        self.plugin_manager = PluginManager(parent = parent_plugin_manager)
        self.tool_manager = ToolManager(parent = parent_tool_manager)
        self.settings = RuntimeCtx(parent = parent_settings)
        self.alias_manager = AliasManager(self)
        self.agent_runtime_ctx = RuntimeCtx(parent = parent_agent_runtime_ctx)
        self.request_runtime_ctx = RuntimeCtx()
        self.request = Request(
            parent_plugin_manager = self.plugin_manager,
            parent_request_runtime_ctx = self.request_runtime_ctx,
            parent_settings = self.settings,
        )
        self.worker_request = Request(
            parent_plugin_manager = self.plugin_manager,
            parent_request_runtime_ctx = None,
            parent_settings = self.settings,
        )
        # Debug
        if is_debug:
            self.settings.set("is_debug", is_debug)
        # Agent Id
        if agent_id == None or agent_id == "":
            self.agent_id = IdGenerator("agent").create()
        else:
            self.agent_id = agent_id
        # Agent Storage
        self.agent_storage = StorageDelegate(
            db_name = self.agent_id,
            plugin_manager = self.plugin_manager,
            settings = self.settings,
        )
        # Load Saved agent_runtime_ctx
        self.agent_runtime_ctx.update_by_dict(self.agent_storage.table("agent_runtime_ctx").get())
        # Set Agent Auto Save Setting
        self.agent_runtime_ctx.set("agent_auto_save", auto_save)
        # Version Check In Debug Model
        """
        if self.settings.get_trace_back("is_debug"):
            check_version_record = self.global_storage.get("agently", "check_version_record")
            today = str(datetime.date.today())
            if check_version_record != today:
                check_version(self.global_storage, today)
        """
        # Agent Request Prefix & Suffix
        self.agent_request_prefix = {}
        self.agent_request_suffix = []
        # Agent Response Generator
        self.response_generator = DataGenerator()
        # Register Default Request Alias to Agent
        self.request._register_default_alias(self.alias_manager)
        # Install Agent Components
        self.refresh_plugins()
        # Retry Count
        self.retry_count = 0

    def refresh_plugins(self):
        self.alias_manager.empty_alias()
        # Agent Components
        agent_components = self.plugin_manager.get("agent_component")
        component_toggles = self.settings.get_trace_back("component_toggles")
        for agent_component_name, AgentComponentClass in agent_components.items():
            # Skip component_toggles Those Be Toggled Off
            if agent_component_name in component_toggles and component_toggles[agent_component_name] == False:
                continue
            # Attach Component
            agent_component_instance = AgentComponentClass(agent = self)
            setattr(self, agent_component_name, agent_component_instance)
            component_export = agent_component_instance.export()
            # Register export_prefix, export_suffix
            if "prefix" in component_export:
                if callable(component_export["prefix"]):
                    component_export["prefix"] = [component_export["prefix"]]
                self.agent_request_prefix.update({ agent_component_name: component_export["prefix"] })
            if "suffix" in component_export:
                if isinstance(component_export["suffix"], list):
                    self.agent_request_suffix.extend(component_export["suffix"])
                elif callable(component_export["suffix"]):
                    self.agent_request_suffix.append(component_export["suffix"])
            # Register Alias
            if "alias" in component_export:
                for alias_name, alias_info in component_export["alias"].items():
                    self.alias_manager.register(
                        alias_name,
                        alias_info["func"],
                        return_value = alias_info["return_value"] if "return_value" in alias_info else False,
                        agent_component_name = agent_component_name,
                    )

    def toggle_auto_save(self, is_enabled: bool):
        self.agent_runtime_ctx.set("agent_auto_save", is_enabled)
        return self

    def toggle_component(self, component_name: str, is_enabled: bool):
        self.settings.set(f"component_toggles.{ component_name }", is_enabled)
        self.refresh_plugins()
        return self

    def save(self):
        self.agent_storage.table("agent_runtime_ctx").update_by_dict(self.agent_runtime_ctx.get()).save()
        return self

    def set_settings(self, settings_key: str, settings_value: any):
        self.settings.set(settings_key, settings_value)
        return self

    def set_global_variable(self, variable_name: str, variable_value: any):
        self.settings.set(f"global_variables.{ variable_name }", variable_value)
        return self

    def set_agent_prompt(self, key: str, value: any):
        self.agent_runtime_ctx.set(f"prompt.{ key }", value)
        return self

    def get_agent_prompt(self, key: str):
        return self.agent_runtime_ctx.get(f"prompt.{ key }")

    def remove_agent_prompt(self, key: str):
        self.agent_runtime_ctx.remove(f"prompt.{ key }")
        return self

    def register_agent_component(self, agent_component_name: str, agent_component_class: callable):
        self.plugin_manager.register("agent_component", agent_component_name, agent_component_class)
        self.refresh_plugins()
        return self
    
    def set_agent_component_settings(self, agent_component_name: str, key: str, value: any):
        self.plugin_manager.set_settings(f"plugin_settings.agent_component.{ agent_component_name }", key, value)
        return self
    
    def attach_workflow(self, name: str, workflow: object):
        class AttachedWorkflow:
            def __init__(self, agent: object):
                self.agent = agent
                self.get_debug_status = lambda: self.agent.settings.get_trace_back("is_debug")
                self.settings = RuntimeCtxNamespace(f"plugin_settings.agent_component.{ name }", self.agent.settings)
            
            def start_workflow(self, init_inputs: dict=None, **kwargs):
                if not kwargs:
                    kwargs = {}
                kwargs.update({ "$agent": self.agent })
                return workflow.start(init_inputs, storage=kwargs)
            
            def export(self):
                return {
                    "alias": {
                        name: { "func": self.start_workflow, "return_value": True },
                    }
                }
        return self.register_agent_component(name, AttachedWorkflow)

    async def start_async(self, request_type: str=None, *, return_generator:bool=False):
        if return_generator:
            return self.get_delta_generator()
        try:
            is_debug = self.settings.get_trace_back("is_debug")
            # Auto Save Agent runtime_ctx
            if self.agent_runtime_ctx.get("agent_auto_save") ==  True:
                self.save()
            # Load Prompt in Agent runtime_ctx to Request runtime_ctx
            self.request_runtime_ctx.set("prompt", self.agent_runtime_ctx.get("prompt", {}))
            # Call Prefix Funcs to Prepare Prefix Data(From agent_runtime_ctx To request_runtime_ctx)
            async def call_prefix_funcs(prefix_funcs):
                if prefix_funcs != None:
                    for prefix_func in prefix_funcs:
                        prefix_data = await prefix_func() if asyncio.iscoroutinefunction(prefix_func) else prefix_func()
                        if prefix_data != None:
                            if isinstance(prefix_data, tuple) and isinstance(prefix_data[0], str) and prefix_data[1] != None:
                                key = prefix_data[0] if prefix_data[0].startswith("prompt.") else f"prompt.{ prefix_data[0] }"
                                self.request.request_runtime_ctx.update(key, prefix_data[1])
                            elif isinstance(prefix_data, dict):
                                for key, value in prefix_data.items():
                                    key = key if key.startswith("prompt.") else f"prompt.{ key }"
                                    if value != None:
                                        self.request.request_runtime_ctx.delta(key, value)
                            else:
                                raise Exception("[Agent Component] Prefix return data error: only accept None or Dict({'<request slot name>': <data append to slot>, ... } or Tuple('request slot name', <data append to slot>)")

            prefix_orders = self.settings.get_trace_back("plugin_settings.agent_component.orders.prefix")
            for agent_component_name in prefix_orders["firstly"]:
                if agent_component_name in self.agent_request_prefix:
                    await call_prefix_funcs(self.agent_request_prefix[agent_component_name])
            for agent_component_name in prefix_orders["normally"]:
                if agent_component_name in self.agent_request_prefix:
                    await call_prefix_funcs(self.agent_request_prefix[agent_component_name])
            for agent_component_name in prefix_orders["finally"]:
                if agent_component_name in self.agent_request_prefix:
                    await call_prefix_funcs(self.agent_request_prefix[agent_component_name])

            # Request
            event_generator = await self.request.get_event_generator(request_type)
        
            # Call Suffix Func to Handle Response Events
            self.request_runtime_ctx.set("is_start_reasoning", False)
            self.request_runtime_ctx.set("is_start_delta", False)
            async def call_request_suffix(response):
                for suffix_func in self.agent_request_suffix:
                    if asyncio.iscoroutinefunction(suffix_func):
                        await suffix_func(response["event"], response["data"]) 
                    else:
                        suffix_func(response["event"], response["data"])

            async def handle_response(response):
                if response["event"] == "response:reasoning_delta":
                    if is_debug:
                        if not self.request_runtime_ctx.get("is_start_reasoning"):
                            print("\n[Realtime Reasoning]\n")
                            self.request_runtime_ctx.set("is_start_reasoning", True)
                        print(response["data"], end="", flush=True)
                if response["event"] == "response:delta":
                    if is_debug:
                        if not self.request_runtime_ctx.get("is_start_delta"):
                            print("\n[Realtime Response]\n")
                            self.request_runtime_ctx.set("is_start_delta", True)
                        print(response["data"], end="", flush=True)
                    self.response_generator.add(response["data"])
                if response["event"] == "response:done":
                    if self.request.response_cache["reply"] == None:
                        self.request.response_cache["reply"] = response["data"]
                    if is_debug:
                        print("\n--------------------------\n")
                        print("[Final Reply]\n", self.request.response_cache["reply"], "\n--------------------------\n")
                    self.response_generator.end()
                await call_request_suffix(response)

            await handle_response({ "event": "response:start", "data": {} })
            if "__aiter__" in dir(event_generator):
                async for response in event_generator:
                    await handle_response(response)
            else:
                for response in event_generator:
                    await handle_response(response)
            
            # Load JSON and fix if Required
            if (
                isinstance(self.request.response_cache["prompt"]["output"], (dict, list, set))
                or self.request.response_cache["type"] == "JSON"
            ):
                temp_request = (
                    Request()
                        .set_settings("current_model", self.request.settings.get_trace_back("current_model"))
                        .set_settings("model", self.request.settings.get_trace_back("model"))
                )
                reply = await load_json(
                    re.sub(r'<think(?:ing)?>.*?<\\think(?:ing)?>\s*', '', self.request.response_cache["reply"], flags=re.DOTALL),
                    self.request.response_cache["prompt"]["input"],
                    self.request.response_cache["prompt"]["output"],
                    temp_request,
                    is_debug = is_debug,
                )
                if isinstance(reply, str) and reply.startswith("$$$JSON_ERROR:"):
                    raise Exception(reply[14:])
                self.request.response_cache["reply"] = json5.loads(reply) if isinstance(reply, str) else reply

            await handle_response({ "event": "response:finally", "data": self.request.response_cache })

            self.request_runtime_ctx.empty()
            return self.request.response_cache["reply"]
        except Exception as e:
            retry_time = self.settings.get_trace_back("request.retry_times")
            if not isinstance(retry_time, int):
                retry_time = 0
            retry_count = self.request_runtime_ctx.get_trace_back("retry_count", 0)
            if retry_count >= retry_time:
                self.response_generator.end()
                self.request_runtime_ctx.empty()
                raise(e)
            else:
                self.response_generator.add({ "event": "error", "data": str(e) })
                self.request_runtime_ctx.set("retry_count", retry_count + 1)
                if is_debug:
                    print(f"[Agent Request] Error: { str(e) }\nRetrying...({ retry_count + 1 }/{ retry_time })")
                return await self.start_async(request_type, return_generator=return_generator)

    def start(self, request_type: str=None, *, return_generator:bool=False):
        if return_generator:
            return self.get_delta_generator()
        reply_queue = queue.Queue()
        is_debug = self.settings.get_trace_back("is_debug")
        def start_in_theard():
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
            if is_debug:
                reply = loop.run_until_complete(self.start_async(request_type))
                reply_queue.put_nowait(reply)
            else:
                try:
                    reply = loop.run_until_complete(self.start_async(request_type))
                    reply_queue.put_nowait(reply)
                except Exception as e:
                    reply = None
                    raise Exception(f"[Agent Request] Error: { str(e) }")                    
                finally:
                    loop.close()
        theard = threading.Thread(target=start_in_theard)
        theard.start()
        theard.join()
        try:        
            reply = reply_queue.get_nowait()
        except:
            reply = None
        return reply
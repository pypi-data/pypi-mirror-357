from ..utils import PluginManager, ToolManager, RuntimeCtx, RuntimeCtxNamespace
from .._global import global_plugin_manager, global_storage, global_settings, global_tool_manager
from .Agent import Agent

class AgentFactory(object):
    def __init__(
            self,
            *,
            parent_plugin_manager: object=global_plugin_manager,
            parent_tool_manager: object=global_tool_manager,
            parent_settings: object=global_settings,
            is_debug: bool=False
        ):
        #runtime ctx
        self.factory_agent_runtime_ctx = RuntimeCtx()
        self.settings = RuntimeCtx(parent = parent_settings)

        #use plugin manager
        self.plugin_manager = PluginManager(parent = parent_plugin_manager)

        #use tool manager
        self.tool_manager = ToolManager(parent = parent_tool_manager)

        #use global storage
        self.global_storage = global_storage

        #debug
        self.set_settings("is_debug", is_debug)

    def create_agent(self, agent_id: str=None, is_debug: bool=False):
        return Agent(
            agent_id = agent_id,
            parent_agent_runtime_ctx = self.factory_agent_runtime_ctx,
            parent_tool_manager = self.tool_manager,
            global_storage = self.global_storage,            
            parent_plugin_manager = self.plugin_manager,
            parent_settings = self.settings,
            is_debug = is_debug
        )

    def register_plugin(self, module_name: str, plugin_name: str, plugin: callable):
        self.plugin_manager.register(module_name, plugin_name, plugin)
        return self

    def attach_workflow(self, name: str, workflow: object):
        class AttachedWorkflow:
            def __init__(self, agent: object):
                self.agent = agent
                self.get_debug_status = lambda: self.agent.settings.get_trace_back("is_debug")
                self.settings = RuntimeCtxNamespace(f"plugin_settings.agent_component.{ name }", self.agent.settings)
            
            def start_workflow(self, init_inputs: dict=None, init_storage: dict={}):
                if not isinstance(init_storage, dict):
                    raise Exception("[Workflow] Initial storage must be a dict.")
                init_storage.update({ "$agent": self.agent })
                return workflow.start(init_inputs, storage=init_storage)
            
            def export(self):
                return {
                    "alias": {
                        name: { "func": self.start_workflow, "return_value": True },
                    }
                }
        return self.register_plugin("agent_component", name, AttachedWorkflow)

    def set_settings(self, settings_key: str, settings_value: any):
        self.settings.set(settings_key, settings_value)
        return self

    def set_global_variable(self, variable_name: str, variable_value: any):
        self.settings.set(f"global_variables.{ variable_name }", variable_value)
        return self

    def toggle_component(self, component_name: str, is_enabled: bool):
        self.set_settings(f"component_toggles.{ component_name }", is_enabled)
        return self

    def set_proxy(self, proxy_setting: any):
        self.set_settings("proxy", proxy_setting)
        return self
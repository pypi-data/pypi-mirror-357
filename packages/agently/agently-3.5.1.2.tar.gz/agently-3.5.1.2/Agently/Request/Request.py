import asyncio
import threading
import queue
import json
import json5
import re

from ..utils import RuntimeCtx, RuntimeCtxNamespace, PluginManager, AliasManager, load_json, DataGenerator
from .._global import global_plugin_manager, global_settings

class Request(object):
    def __init__(
            self,
            *,
            parent_plugin_manager: object = global_plugin_manager,
            parent_request_runtime_ctx: object = None,
            parent_settings: object = global_settings,
        ):
        self.request_runtime_ctx = RuntimeCtx(parent = parent_request_runtime_ctx)
        self.settings = RuntimeCtx(parent = parent_settings)
        self.response_cache = {
            "prompt": {},
            "type": None,
            "reply": None,
        }
        self.response_generator = DataGenerator()
        # Plugin Manager
        self.plugin_manager = PluginManager(parent = parent_plugin_manager)
        # Namespace
        self.model = RuntimeCtxNamespace("model", self.settings, return_to = self)
        self.prompt_general = RuntimeCtxNamespace("prompt.general", self.request_runtime_ctx, return_to = self)
        self.prompt_role = RuntimeCtxNamespace("prompt.role", self.request_runtime_ctx, return_to = self)
        self.prompt_user_info = RuntimeCtxNamespace("prompt.user_info", self.request_runtime_ctx, return_to = self)
        self.prompt_abstract = RuntimeCtxNamespace("prompt.abstract", self.request_runtime_ctx, return_to = self)
        self.prompt_chat_history = RuntimeCtxNamespace("prompt.chat_history", self.request_runtime_ctx, return_to = self)
        self.prompt_input = RuntimeCtxNamespace("prompt.input", self.request_runtime_ctx, return_to = self)
        self.prompt_info = RuntimeCtxNamespace("prompt.info", self.request_runtime_ctx, return_to = self)
        self.prompt_instruct = RuntimeCtxNamespace("prompt.instruct", self.request_runtime_ctx, return_to = self)
        self.prompt_output = RuntimeCtxNamespace("prompt.output", self.request_runtime_ctx, return_to = self)
        self.prompt_files = RuntimeCtxNamespace("prompt.files", self.request_runtime_ctx, return_to = self)
        # Alias
        self.alias_manager = AliasManager(self)
        self._register_default_alias(self.alias_manager)

    def set_settings(self, settings_key: str, settings_value: any):
        self.settings.set(settings_key, settings_value)
        return self

    def set_request_prompt(self, key: str, value: any):
        self.request_runtime_ctx.set(f"prompt.{ key }", value)
        return self

    def get_request_prompt(self, key: str):
        return self.request_runtime_ctx.get(f"prompt.{ key }")

    def remove_request_prompt(self, key: str):
        self.request_runtime_ctx.remove(f"prompt.{ key }")
        return self

    def _register_default_alias(self, alias_manager):
        def set_model_settings(key: str, value: any, *, client_name:str = None):
            client_name = client_name if client_name else self.settings.get_trace_back("current_client", self.settings.get_trace_back("current_model"))
            if client_name == None:
                raise Exception("[Model Settings] No model client was appointed. Use .use_client(<model client name>) or kwarg parameter model_name=<model_name> to set.")
            self.settings.update(f"model.{ client_name }.{ key }", value)

        alias_manager.register("use_client", lambda client_name: self.settings.set("current_client", client_name))
        alias_manager.register("use_model", lambda model_name: self.settings.set("current_model", model_name))
        alias_manager.register("set_model", set_model_settings)
        alias_manager.register("set_model_auth", lambda key, value, *, model_name=None: set_model_settings(f"auth.{ key }", value))
        alias_manager.register("set_model_url", lambda url, *, model_name=None: set_model_settings("url", url))
        alias_manager.register("set_model_option", lambda key, value, *, model_name=None: set_model_settings(f"options.{ key }", value))
        alias_manager.register("set_proxy", lambda proxy: self.settings.set("proxy", proxy))
        alias_manager.register("general", self.prompt_general.assign)
        alias_manager.register("role", self.prompt_role.assign)
        alias_manager.register("user_info", self.prompt_user_info.assign)
        alias_manager.register("abstract", self.prompt_abstract.assign)
        alias_manager.register("chat_history", self.prompt_chat_history.assign)
        alias_manager.register("input", self.prompt_input.assign)
        alias_manager.register("info", self.prompt_info.assign)
        alias_manager.register("instruct", self.prompt_instruct.assign)
        alias_manager.register("output", self.prompt_output.assign)
        alias_manager.register("file", self.prompt_files.append)
        alias_manager.register("files", self.prompt_files.extend)
        alias_manager.register("set_request_prompt", self.set_request_prompt)
        alias_manager.register("get_request_prompt", self.get_request_prompt)
        alias_manager.register("remove_request_prompt", self.remove_request_prompt) 
        
    async def get_event_generator(self, request_type: str=None):
        # Set Request Type
        self.request_runtime_ctx.set("request_type", request_type)
        # Erase response cache
        self.response_cache = {
            "prompt": {},
            "type": None,
            "reply": None,
        }
        # Confirm model name
        model_name = self.settings.get_trace_back("current_client", self.settings.get_trace_back("current_model"))
        if not model_name:
            raise Exception(f"[Request] 'current_client' must be set. Use .set_settings('current_client', <model_client_name>) to set.")
        # Load request plugin by model name
        request_plugin_instance = self.plugin_manager.get("request", model_name)(request = self)
        request_plugin_export = request_plugin_instance.export()
        # Generate request data
        if asyncio.iscoroutinefunction(request_plugin_export["generate_request_data"]):
            request_data = await request_plugin_export["generate_request_data"]()
        else:
            request_data = request_plugin_export["generate_request_data"]()
        if self.settings.get_trace_back("is_debug") == True:
            print("[Request Data]\n", json.dumps(request_data, indent=4, ensure_ascii=False))
        # Cache simple prompt
        self.response_cache["prompt"]["input"] = self.prompt_input.get()
        self.response_cache["prompt"]["output"] = self.prompt_output.get()
        if isinstance(self.response_cache["prompt"]["output"], (dict, list, set)):
            self.response_cache.update({"type": "JSON"})
        # Request and get response generator
        if asyncio.iscoroutinefunction(request_plugin_export["request_model"]):
            response_generator = await request_plugin_export["request_model"](request_data)
        else:
            response_generator = request_plugin_export["request_model"](request_data)
        # Broadcast response
        if asyncio.iscoroutinefunction(request_plugin_export["broadcast_response"]):
            broadcast_event_generator = await request_plugin_export["broadcast_response"](response_generator)
        else:
            broadcast_event_generator = request_plugin_export["broadcast_response"](response_generator)        
        self.response_cache["type"] = self.request_runtime_ctx.get("response:type")
        # Reset request runtime_ctx
        self.request_runtime_ctx.empty()
        return broadcast_event_generator

    async def get_result_async(self, request_type: str=None, *, return_generator:bool=False):
        try:
            is_debug = self.settings.get_trace_back("is_debug")
            event_generator = await self.get_event_generator(request_type)
            if is_debug:
                print("[Realtime Response]\n")
            def handle_response(response):
                if response["event"] == "response:delta":
                    self.response_generator.add(response["data"])
                    if is_debug:
                        print(response["data"], end="")
                if response["event"] == "response:done":
                    if is_debug:
                        print("\n--------------------------\n")
                        print("[Final Response]\n", response["data"], "\n--------------------------\n")
                    self.response_cache["reply"] = response["data"]
                    self.response_generator.end()

            if "__aiter__" in dir(event_generator):
                async for response in event_generator:
                    handle_response(response)
            else:
                for response in event_generator:
                    handle_response(response)
            
            if return_generator:
                self.request_runtime_ctx.empty()
                return self.response_generator.start()
            else:
                if (
                    isinstance(self.response_cache["prompt"]["output"], (dict, list, set))
                    or self.response_cache["type"] == "JSON"
                ):
                    temp_request = (
                        Request()
                            .set_settings("current_model", self.settings.get_trace_back("current_model"))
                            .set_settings("model", self.settings.get_trace_back("model"))
                    )
                    reply = await load_json(
                        re.sub(r'<think(?:ing)?>.*?<\\think(?:ing)?>\s*', '', self.response_cache["reply"], flags=re.DOTALL),
                        self.response_cache["prompt"]["input"],
                        self.response_cache["prompt"]["output"],
                        temp_request,
                        is_debug = is_debug,
                    )
                    if isinstance(reply, str) and reply.startswith("$$$JSON_ERROR:"):
                        raise Exception(reply[14:])
                    self.response_cache["reply"] = json5.loads(reply) if isinstance(reply, str) else reply
                
                self.request_runtime_ctx.empty()
                return self.response_cache["reply"]
        except Exception as e:
            self.response_generator.end()
            self.request_runtime_ctx.empty()
            raise(e)

    def get_result(self, request_type: str=None, *, return_generator:bool=False):
        reply_queue = queue.Queue()
        is_debug = self.settings.get_trace_back("is_debug")
        def start_in_theard():
            asyncio.set_event_loop(asyncio.new_event_loop())
            loop = asyncio.get_event_loop()
            if is_debug:
                reply = loop.run_until_complete(self.get_result_async(request_type))
                reply_queue.put_nowait(reply)
            else:
                try:
                    reply = loop.run_until_complete(self.get_result_async(request_type))
                    reply_queue.put_nowait(reply)
                except Exception as e:
                    reply = None
                    raise Exception(f"[Request] Error: { str(e) }")
                finally:
                    loop.close()
        theard = threading.Thread(target=start_in_theard)
        theard.start()
        if return_generator:
            return self.response_generator.start()
        else:
            theard.join()        
            reply = reply_queue.get_nowait()
            return reply

    def start(self, request_type: str=None, *, return_generator=False):
        return self.get_result(request_type, return_generator=return_generator)

    def start_async(self, request_type: str=None):
        return self.get_result_async(request_type)
from openai import AsyncOpenAI as OpenAIClient
from .utils import RequestABC, to_prompt_structure, to_instruction, to_json_desc, find_json, format_request_messages
from Agently.utils import RuntimeCtxNamespace
import httpx

class OAIClient(RequestABC):
    def __init__(self, request):
        self.request = request
        self.model_name = "OAIClient"
        self.model_settings = RuntimeCtxNamespace(f"model.{ self.model_name }", self.request.settings)
        self.request_type = self.request.request_runtime_ctx.get("request_type", "chat")
        self.default_options = {
            "stream": True
        }
        if not self.model_settings.get_trace_back("message_rules.no_multi_system_messages"):
            self.model_settings.set("message_rules.no_multi_system_messages", True)
        if not self.model_settings.get_trace_back("message_rules.strict_orders"):
            self.model_settings.set("message_rules.strict_orders", True)
        if not self.model_settings.get_trace_back("message_rules.no_multi_type_messages"):
            self.model_settings.set("message_rules.no_multi_type_messages", True)
        if not self.model_settings.get_trace_back("separate_reasoning_from_content"):
            self.model_settings.set("separate_reasoning_from_content", True)
        self.reasoning_prefixes = ["<think>", "<thinking>"]
        self.reasoning_suffixes = ["</think>", "</thinking>", "</think>\n\n", "</thinking>\n\n"]

    def construct_request_messages(self):
        #init request messages
        request_messages = []
        # - general instruction
        general_instruction_data = self.request.request_runtime_ctx.get_trace_back("prompt.general")
        if general_instruction_data:
            request_messages.append({ "role": "system", "content": [{"type": "text", "text": f"[GENERAL INSTRUCTION]\n{ to_instruction(general_instruction_data) }" }] })
        # - role
        role_data = self.request.request_runtime_ctx.get_trace_back("prompt.role")
        if role_data:
            request_messages.append({ "role": "system", "content": [{"type": "text", "text": f"[ROLE SETTINGS]\n{ to_instruction(role_data) }" }] })
        # - user info
        user_info_data = self.request.request_runtime_ctx.get_trace_back("prompt.user_info")
        if user_info_data:
            request_messages.append({ "role": "system", "content": [{"type": "text", "text": f"[ABOUT USER]\n{ to_instruction(user_info_data) }" }] })
        # - abstract
        headline_data = self.request.request_runtime_ctx.get_trace_back("prompt.abstract")
        if headline_data:
            request_messages.append({ "role": "assistant", "content": [{"type": "text", "text": f"[ABSTRACT]\n{ to_instruction(headline_data) }" }] })
        # - chat history
        chat_history_data = self.request.request_runtime_ctx.get_trace_back("prompt.chat_history")
        if chat_history_data:
            request_messages.extend(chat_history_data)
        # - request message (prompt)
        prompt_input_data = self.request.request_runtime_ctx.get_trace_back("prompt.input")
        prompt_info_data = self.request.request_runtime_ctx.get_trace_back("prompt.info")
        prompt_instruct_data = self.request.request_runtime_ctx.get_trace_back("prompt.instruct")
        prompt_output_data = self.request.request_runtime_ctx.get_trace_back("prompt.output")
        # --- only input
        if not prompt_input_data and not prompt_info_data and not prompt_instruct_data and not prompt_output_data:
            raise Exception("[Request] Missing 'prompt.input', 'prompt.info', 'prompt.instruct', 'prompt.output' in request_runtime_ctx. At least set value to one of them.")
        prompt_text = ""
        if prompt_input_data and not prompt_info_data and not prompt_instruct_data and not prompt_output_data:
            prompt_text = to_instruction(prompt_input_data)
        # --- construct prompt
        else:
            prompt_dict = {}
            if prompt_input_data:
                prompt_dict["[INPUT]"] = to_instruction(prompt_input_data)
            if prompt_info_data:
                prompt_dict["[HELPFUL INFORMATION]"] = str(prompt_info_data)
            if prompt_instruct_data:
                prompt_dict["[INSTRUCTION]"] = to_instruction(prompt_instruct_data)
            if prompt_output_data:
                if isinstance(prompt_output_data, (dict, list, set)):
                    prompt_dict["[OUTPUT REQUIREMENT]"] = {
                        "TYPE": "JSON String can be parsed",
                        "FORMAT": to_json_desc(prompt_output_data),
                    }
                    self.request.request_runtime_ctx.set("response:type", "JSON")
                else:
                    prompt_dict["[OUTPUT REQUIERMENT]"] = str(prompt_output_data)
            prompt_text = to_prompt_structure(prompt_dict, end="[OUTPUT]:\n")
        request_messages.append({ "role": "user", "content": [{"type": "text", "text": prompt_text }] })
        return request_messages

    def construct_completion_prompt(self):
        # - init prompt
        completion_prompt = ""
        # - general instruction
        general_instruction_data = self.request.request_runtime_ctx.get_trace_back("prompt.general")
        if general_instruction_data:
            completion_prompt += f"[GENERAL INSTRUCTION]\n{ to_instruction(general_instruction_data) }\n"
        # - role
        role_data = self.request.request_runtime_ctx.get_trace_back("prompt.role")
        if role_data:
            completion_prompt += f"[ROLE SETTINGS]\n{ to_instruction(role_data) }\n"
        # - user info
        user_info_data = self.request.request_runtime_ctx.get_trace_back("prompt.user_info")
        if user_info_data:
            completion_prompt += f"[ABOUT USER]\n{ to_instruction(user_info_data) }\n"
        # - abstract
        headline_data = self.request.request_runtime_ctx.get_trace_back("prompt.abstract")
        if headline_data:
            completion_prompt += f"[ABSTRACT]\n{ to_instruction(headline_data) }\n"
        # - main prompt
        chat_history_data = self.request.request_runtime_ctx.get_trace_back("prompt.chat_history")
        prompt_input_data = self.request.request_runtime_ctx.get_trace_back("prompt.input")
        prompt_info_data = self.request.request_runtime_ctx.get_trace_back("prompt.info")
        prompt_instruct_data = self.request.request_runtime_ctx.get_trace_back("prompt.instruct")
        prompt_output_data = self.request.request_runtime_ctx.get_trace_back("prompt.output")
        if not prompt_input_data and not prompt_info_data and not prompt_instruct_data and not prompt_output_data and not chat_history_data:
            raise Exception("[Request] Missing 'prompt.chat_history', 'prompt.input', 'prompt.info', 'prompt.instruct', 'prompt.output' in request_runtime_ctx. At least set value to one of them.")
        # --- only input
        if prompt_input_data and not chat_history_data and not prompt_info_data and not prompt_instruct_data and not prompt_output_data:
            if completion_prompt == "":
                completion_prompt += to_instruction(prompt_input_data)
            else:
                completion_prompt += f"[OUTPUT]\n{ to_instruction(prompt_input_data) }"
        # --- construct prompt
        else:
            # - with output format
            if isinstance(prompt_output_data, (dict, list, set)):
                prompt_dict = {}
                if chat_history_data:
                    prompt_dict["[HISTORY LOGS]"] = ""
                    for message in chat_history_data:
                        prompt_dict["[HISTORY LOGS]"] += f"{ message['role'] }: { message['content'] }\n"
                if prompt_input_data:
                    prompt_dict["[INPUT]"] = to_instruction(prompt_input_data)
                if prompt_info_data:
                    prompt_dict["[HELPFUL INFORMATION]"] = str(prompt_info_data)
                if prompt_instruct_data:
                    prompt_dict["[INSTRUCTION]"] = to_instruction(prompt_instruct_data)
                if prompt_output_data:
                    prompt_dict["[OUTPUT REQUIREMENT]"] = {
                        "TYPE": "JSON can be parsed in Python",
                        "FORMAT": to_json_desc(prompt_output_data),
                    }
                    self.request.request_runtime_ctx.set("response:type", "JSON")
                completion_prompt += to_prompt_structure(
                    prompt_dict,
                    end="[OUTPUT]:\nassistant: "
                        if chat_history_data and len(chat_history_data) > 0
                        else "[OUTPUT]:\n"
                )
            # without output format
            else:
                if prompt_info_data:
                    completion_prompt += f"[HELPFUL INFORMATION]\n{ str(prompt_info_data) }\n"
                if prompt_instruct_data:
                    completion_prompt += f"[INSTRUCTION]\n{ to_instruction(prompt_instruct_data) }\n"
                if prompt_output_data:
                    completion_prompt += f"[OUTPUT REQUIREMENT]\n{ str(prompt_output_data) }\n"
                completion_prompt += "[OUTPUT]\n"
                # chat completion
                if chat_history_data:
                    for message in chat_history_data:
                        completion_prompt += f"{ message['role'] }: { message['content'] }\n"
                    if prompt_input_data:
                        completion_prompt += f"user: { to_instruction(prompt_input_data) }\n"
                    completion_prompt += "assistant: "
                # text completion
                else:
                    if prompt_input_data:
                        completion_prompt += prompt_input_data
        return completion_prompt

    def generate_request_data(self):
        # collect options
        options = self.model_settings.get_trace_back("options", {})
        for key, value in self.default_options.items():
            if key not in options:
                options.update({ key: value })
        if self.request_type == "chat":
            return {
                "messages": format_request_messages(self.construct_request_messages(), self.model_settings),
                **options,
            }
        elif self.request_type == "completions":
            return {
                "prompt": self.construct_completion_prompt(),
                **options,
            }
        else:
            raise Exception(f"Can not support request type: { self.request_type }.")

    async def request_model(self, request_data: dict):
        # create client
        client_params = {}
        base_url = self.model_settings.get_trace_back("url")
        if base_url:
            client_params.update({ "base_url": base_url })
        httpx_client = self.model_settings.get_trace_back("httpx_client")
        if httpx_client:
            httpx_client.headers.update({ "Connection": "close" })
            client_params.update({ "http_client": httpx_client })
        else:
            proxy = self.request.settings.get_trace_back("proxy")
            verify = self.model_settings.get_trace_back("verify")
            httpx_options = self.model_settings.get_trace_back("httpx.options", {})
            httpx_params = httpx_options
            httpx_params.update({
                "headers": [("Connection", "close")],
            })
            # verify
            if verify:
                httpx_params.update({ "verify": verify })
            # proxy
            if proxy:
                httpx_params.update({ "proxy": proxy })
            client_params.update({
                "http_client": httpx.AsyncClient(**httpx_params),
            })
        api_key = self.model_settings.get_trace_back("auth.api_key")
        if api_key:
            client_params.update({ "api_key": api_key })
        else:
            client_params.update({ "api_key": "None" })
        client = OpenAIClient(**client_params)
        # request
        if self.request_type == "chat":
            stream = await client.chat.completions.create(**request_data)
        elif self.request_type == "completions":
            stream = await client.completions.create(**request_data)
        return stream

    async def broadcast_response(self, response_generator):
        if self.request_type == "chat":
            response_message = { "content": "" }
            is_reasoning = False
            is_in_content_reasoning = False
            reasoning_content = ""
            done_content = ""
            async for part in response_generator:
                if not hasattr(part, "choices") or len(part.choices) < 1:
                    continue
                delta = dict(part.choices[0].delta)
                for key, value in delta.items():
                    if key not in response_message:
                        response_message[key] = value or ""
                    elif key != "content":
                        response_message[key] += value or ""
                yield({ "event": "response:delta_origin", "data": part })
                if "reasoning_content" in delta and delta["reasoning_content"]:
                    if not self.model_settings.get_trace_back("separate_reasoning_from_content"):
                        if not is_reasoning:
                            yield({ "event": "response:delta", "data": self.reasoning_prefixes[0] })
                            yield({ "event": "response:delta", "data": "\n\n" })
                        yield({ "event": "response:delta", "data": delta["reasoning_content"] })
                        reasoning_content += delta["reasoning_content"]
                    yield({ "event": "response:reasoning_delta", "data": delta["reasoning_content"] })
                    is_reasoning = True
                    if "content" in delta and delta["content"]:
                        is_in_content_reasoning = True
                if (
                    is_reasoning
                    and ("reasoning_content" not in delta or not delta["reasoning_content"])
                ):
                    if not self.model_settings.get_trace_back("separate_reasoning_from_content"):
                        yield({ "event": "response:delta", "data": self.reasoning_suffixes[0] })
                        yield({ "event": "response:delta", "data": "\n\n" })
                    is_reasoning = False
                if is_reasoning:
                    continue
                if "content" in delta and delta["content"]:
                    if self.model_settings.get_trace_back("separate_reasoning_from_content"):
                        if delta["content"] in self.reasoning_prefixes and not is_in_content_reasoning:
                            is_in_content_reasoning = True
                            continue
                        if delta["content"] in self.reasoning_suffixes and is_in_content_reasoning:
                            is_in_content_reasoning = False
                            continue
                        if is_in_content_reasoning:
                            reasoning_content += delta["content"]
                            yield({ "event": "response:reasoning_delta", "data": delta["content"] })
                            continue
                    yield({ "event": "response:delta", "data": delta["content"] })
                    done_content += delta["content"]
            if "reasoning_content"  not in response_message and reasoning_content != "":
                response_message.update({ "reasoning_content": reasoning_content })
            if "reasoning_content" in response_message:
                yield({ "event": "response:reasoning_done", "data": response_message["reasoning_content"] })
                if not self.model_settings.get_trace_back("separate_reasoning_from_content"):
                    done_content = f"{ self.reasoning_prefixes[0] }\n\n{ response_message['reasoning_content'] }\n\n{ self.reasoning_suffixes[0] }\n\n{ done_content }"
            yield({ "event": "response:done", "data": done_content })
            response_message.update({ "content": done_content })
            yield({ "event": "response:done_origin", "data": response_message })
        elif self.request_type == "completions":
            response_message = {}
            async for part in response_generator:
                if "choices" in dir(part) and isinstance(part.choices, list) and len(part.choices) > 0:
                    delta = dict(part.choices[0])
                    for key, value in delta.items():
                        if key not in response_message and value is not None:
                            response_message[key] = value
                        elif key in response_message and value is not None:
                            response_message[key] += value
                    yield({ "event": "response:delta_origin", "data": delta })
                    yield({ "event": "response:delta", "data": delta["text"] or "" })
                else:
                    if self.request.settings.get_trace_back("is_debug"):
                        print(f"[Request] Server Response Message: { str(dict(part)) }")
                yield({ "event": "response:delta_origin", "data": part })
            yield({ "event": "response:done_origin", "data": response_message })
            if "text" in response_message:
                yield({ "event": "response:done", "data": response_message["text"] })
            else:
                yield({ "event": "response:done", "data": response_message })
                yield({ "event": "response:error", "data": response_message })
    def export(self):
        return {
            "generate_request_data": self.generate_request_data,
            "request_model": self.request_model,
            "broadcast_response": self.broadcast_response,
        }

def export():
    return("OAIClient", OAIClient)
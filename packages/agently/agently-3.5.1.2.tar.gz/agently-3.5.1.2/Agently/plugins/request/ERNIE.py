from .utils import RequestABC, to_prompt_structure, to_instruction, to_json_desc, format_request_messages
from Agently.utils import RuntimeCtxNamespace

class Ernie(RequestABC):
    def __init__(self, request):
        try:
            import erniebot
        except:
            raise ImportError("[Agently Request] Can not find package 'erniebot', please use `pip install erniebot` to install.")
        self.erniebot = erniebot
        self.request = request
        self.request_type = self.request.request_runtime_ctx.get("request_type", "chat")
        if self.request_type == None:
            self.request_type = "chat"
        self.model_name = "ERNIE"
        self.model_settings = RuntimeCtxNamespace(f"model.{self.model_name}", self.request.settings)
        if not self.model_settings.get_trace_back("message_rules.no_multi_system_messages"):
            self.model_settings.set("message_rules.no_multi_system_messages", True)
        if not self.model_settings.get_trace_back("message_rules.strict_orders"):
            self.model_settings.set("message_rules.strict_orders", True)
        if not self.model_settings.get_trace_back("message_rules.no_multi_type_messages"):
            self.model_settings.set("message_rules.no_multi_type_messages", True)    

    def _create_client(self):
        if self.request_type == "chat":
            client = self.erniebot.ChatCompletion
        elif self.request_type == "embedding":
            client = self.erniebot.Embedding
        elif self.request_type == "image":
            client = self.erniebot.Image
        return client

    def construct_request_messages(self):
        # init request messages
        request_messages = []
        # - general instruction
        general_instruction_data = self.request.request_runtime_ctx.get(
            "prompt.general")
        if general_instruction_data:
            request_messages.append({"role": "system",
                                     "content": f"[重要指导说明]\n{to_instruction(general_instruction_data)}"})
        # - role
        role_data = self.request.request_runtime_ctx.get("prompt.role")
        if role_data:
            request_messages.append(
                {"role": "system", "content": f"[角色及行为设定]\n{to_instruction(role_data)}"})
        # - user info
        user_info_data = self.request.request_runtime_ctx.get("prompt.user_info")
        if user_info_data:
            request_messages.append(
                {"role": "system", "content": f"[用户信息]\n{to_instruction(user_info_data)}"})
        # - abstract
        headline_data = self.request.request_runtime_ctx.get("prompt.abstract")
        if headline_data:
            request_messages.append(
                {"role": "user", "content": f"[主题及摘要]{to_instruction(headline_data)}"})
            request_messages.append({"role": "assistant", "content": "OK"})
        # - chat history
        chat_history_data = self.request.request_runtime_ctx.get("prompt.chat_history")
        if chat_history_data:
            request_messages.extend(chat_history_data)
        # - request message (prompt)
        prompt_input_data = self.request.request_runtime_ctx.get("prompt.input")
        prompt_info_data = self.request.request_runtime_ctx.get("prompt.info")
        prompt_instruct_data = self.request.request_runtime_ctx.get("prompt.instruct")
        prompt_output_data = self.request.request_runtime_ctx.get("prompt.output")
        # --- only input
        if not prompt_input_data and not prompt_info_data and not prompt_instruct_data and not prompt_output_data:
            raise Exception(
                "[Request] Missing 'prompt.input', 'prompt.info', 'prompt.instruct', 'prompt.output' in request_runtime_ctx. At least set value to one of them.")
        if prompt_input_data and not prompt_info_data and not prompt_instruct_data and not prompt_output_data:
            request_messages.append({"role": "user", "content": to_instruction(prompt_input_data)})
        # --- construct prompt
        else:
            prompt_dict = {}
            if prompt_input_data:
                prompt_dict["[输入]"] = to_instruction(prompt_input_data)
            if prompt_info_data:
                prompt_dict["[补充信息]"] = str(prompt_info_data)
            if prompt_instruct_data:
                prompt_dict["[处理规则]"] = to_instruction(prompt_instruct_data)
            if prompt_output_data:
                if isinstance(prompt_output_data, (dict, list, set)):
                    prompt_dict["[输出要求]"] = {
                        "TYPE": "可被解析的JSON字符串",
                        "FORMAT": to_json_desc(prompt_output_data),
                    }
                    self.request.request_runtime_ctx.set("response:type", "JSON")
                else:
                    prompt_dict["[输出要求]"] = str(prompt_output_data)
            request_messages.append(
                {"role": "user", "content": to_prompt_structure(prompt_dict, end="[输出]:\n")})
        return request_messages

    def generate_request_data(self):
        options = self.model_settings.get_trace_back("options", {})
        options = options if isinstance(options, dict) else {}
        access_token = self.model_settings.get_trace_back("auth", {})
        access_token = access_token if isinstance(access_token, dict) else {}
        request_data = {}
        # request type: chat
        if self.request_type == "chat":
            if "model" not in options:
                options["model"] = "ernie-4.0"
            if "aistudio" not in access_token and "qianfan" not in access_token:
                raise Exception(
                    f"[Request] ERNIE require 'access-token-for-aistudio or access-token-for-qianfan' when request type is '{self.request_type}'. Use .set_model_auth({{ 'aistudio': <YOUR-ACCESS-TOKEN-FOR-AISTUDIO> }} or {{ 'qianfan': <YOUR-ACCESS-TOKEN-FOR-QIANFAN> }}) to set.")
            api_type = next(iter(access_token))
            self.erniebot.api_type = api_type
            self.erniebot.access_token = access_token[api_type]
            messages = self.construct_request_messages()
            request_messages = []
            #system_prompt = ""
            for message in messages:
                if message["role"] == "system":
                    #system_prompt += f"{ message['content'] }\n"
                    message["role"] = "user"
                    request_messages.append(message)
                else:
                    request_messages.append(message)
            request_data = {
                "messages": format_request_messages(request_messages, self.model_settings),
                "stream": True,
                **options,
            }
            #if system_prompt != "" and self.request.settings.get_trace_back("retry_count", 0) > 0:
            #    request_data.update({ "system": system_prompt })
        # request type: embedding
        elif self.request_type == "embedding":
            if "model" not in options:
                options["model"] = "ernie-text-embedding"
            if "aistudio" not in access_token:
                raise Exception(
                    f"[Request] ERNIE require 'access-token-for-aistudio' when request type is '{self.request_type}'. Use .set_model_auth({{ 'aistudio': <YOUR-ACCESS-TOKEN-FOR-AISTUDIO> }}) to set.\n How to get your own access token? visit: https://github.com/PaddlePaddle/ERNIE-Bot-SDK/blob/develop/docs/authentication.md")
            self.erniebot.api_type = "aistudio"
            self.erniebot.access_token = access_token["aistudio"]
            content_input = self.request.request_runtime_ctx.get("prompt.input")
            if not isinstance(content_input, list):
                content_input = [content_input]
            request_data = {
                "input": content_input,
                **options,
            }
        # request type: image
        elif self.request_type == "image":
            if "model" not in options:
                options["model"] = "ernie-vilg-v2"
            if "yinian" not in access_token:
                raise Exception(
                    f"[Request] ERNIE require 'access-token-for-yinian' when request type is '{self.request_type}'. Use .set_model_auth({{ 'yinian': <YOUR-ACCESS-TOKEN-FOR-YINIAN> }}) to set.\n⚠️ Yinian Access Token is different from AIStudio Access Token!\n How to get your own access token? visit: https://github.com/PaddlePaddle/ERNIE-Bot-SDK/blob/develop/docs/authentication.md")
            self.erniebot.api_type = "yinian"
            self.erniebot.access_token = access_token["yinian"]
            prompt = self.request.request_runtime_ctx.get("prompt.input")
            output_requirement = self.request.request_runtime_ctx.get("prompt.output", {})
            if not isinstance(output_requirement, dict):
                output_requirement = {}
            if "width" not in output_requirement:
                output_requirement.update({"width": 512})
            if "height" not in output_requirement:
                output_requirement.update({"height": 512})
            request_data = {
                "prompt": prompt,
                **output_requirement,
                **options,
            }
        return request_data

    async def request_model(self, request_data: dict):
        client = self._create_client()
        response = await client.acreate(**request_data)
        return response

    async def broadcast_response(self, response_generator):
        if self.request_type == "chat":
            response_message = {"role": "assistant", "content": ""}
            full_response_message = {}
            async for part in response_generator:
                full_response_message = dict(part)
                delta = part["result"]
                response_message["content"] += delta
                yield ({"event": "response:delta_origin", "data": part})
                yield ({"event": "response:delta", "data": delta})
            full_response_message["result"] = response_message["content"]
            yield ({"event": "response:done_origin", "data": full_response_message})
            yield ({"event": "response:done", "data": response_message["content"]})
        elif self.request_type == "embedding":
            response = dict(response_generator)
            if response["rcode"] == 200:
                yield ({"event": "response:done_origin", "data": response})
                yield ({"event": "response:done", "data": response["rbody"]["data"]})
            else:
                raise Exception(f"[Request] ERNIE Error: {response}")
        elif self.request_type == "image":
            response = dict(response_generator)
            if response["data"]["task_status"] == "SUCCESS":
                yield ({"event": "response:done_origin", "data": response["data"]})
                yield ({"event": "response:done",
                        "data": response["data"]["sub_task_result_list"][0]["final_image_list"][0][
                            "img_url"]})
            else:
                raise Exception(f"[Request] ERNIE Error: {response['data']}")

    def export(self):
        return {
            "generate_request_data": self.generate_request_data,
            "request_model": self.request_model,
            "broadcast_response": self.broadcast_response,
        }


def export():
    return ("ERNIE", Ernie)

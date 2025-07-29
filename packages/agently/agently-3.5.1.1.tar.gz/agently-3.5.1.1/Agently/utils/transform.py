import json
import re
import yaml

def to_prompt_structure(prompt_dict: dict, layer_count: int=1, end: str=""):
    prompt = ""
    for key, content in prompt_dict.items():
        prompt += f"{ '#' * layer_count } { key }:\n"
        if isinstance(content, dict):
            prompt += to_prompt_structure(content, layer_count + 1) + '\n'
        else:
            prompt += str(content) + '\n'
        if layer_count == 1:
            prompt += "\n"
    if layer_count == 1:
        prompt += end
    return prompt

def to_instruction(origin):
    if origin == None:
        return None
    elif isinstance(origin, (list, tuple, set, dict)):
        return yaml.dump(origin, allow_unicode=True, sort_keys=False)
    else:
        return str(origin)

# def to_json_desc(origin, layer_count = 0):
#     if isinstance(origin, dict):
#         json_string = ""
#         if layer_count > 0:
#             json_string += "\n"
#         json_string += ("\t" * layer_count) + "{\n"
#         for key, value in origin.items():
#             json_string += ("\t" * (layer_count + 1)) + "\"" + key + "\": " + to_json_desc(value, layer_count + 1) + "\n"
#         if layer_count > 0:
#             json_string += ("\t" * (layer_count + 1)) + "},"
#         else:
#             json_string += "}"
#         return json_string
#     elif isinstance(origin, (list, set)):
#         json_string = ""
#         if layer_count > 0:
#             json_string += "\n"
#         json_string += ("\t" * layer_count) + "[\n"
#         for item in origin:
#             json_string += ("\t" * (layer_count + 1)) + to_json_desc(item, layer_count + 1) + ",\n"
#         json_string += ("\t" * (layer_count + 1)) + "...\n"
#         if layer_count > 0:
#             json_string += ("\t" * layer_count) + "],"
#         else:
#             json_string += "]"
#         return json_string
#     elif isinstance(origin, tuple):
#         if isinstance(origin[0], (dict, list, set)):
#             json_string = f"\n{ to_json_desc(origin[0], layer_count + 1) },"
#         else:
#             if len(origin) >= 3 and origin[2]:
#                 json_string += f"[*Required] "
#             json_string = f"<{ str(origin[0]) }>,"
#         if len(origin) >= 2:
#             json_string += f"//{ str(origin[1]) }"
#         return json_string
#     else:
#         return str(origin)

def to_json_desc(origin, layer_count=0, in_list=False):
    indent = "\t" * layer_count
    next_indent = "\t" * (layer_count + 1)

    if isinstance(origin, dict):
        lines = ["{"]
        items = list(origin.items())
        for i, (key, value) in enumerate(items):
            val_str = to_json_desc(value, layer_count + 1)
            line = f'{next_indent}"{key}": {val_str}'
            if i < len(items) - 1:
                line += ","
            lines.append(line)
        lines.append(indent + "}" + ("," if in_list else ""))
        return "\n".join(lines)

    elif isinstance(origin, (list, set)):
        lines = ["["]
        items = list(origin)
        for i, item in enumerate(items):
            line = to_json_desc(item, layer_count + 1)
            if i < len(items) - 1:
                line += ","
            lines.append(next_indent + line)
        lines.append(next_indent + "...")
        lines.append(indent + "]")
        return "\n".join(lines)

    elif isinstance(origin, tuple):
        if isinstance(origin[0], (dict, list, set)):
            result = to_json_desc(origin[0], layer_count)
        else:
            desc = ""
            if len(origin) >= 3 and origin[2]:
                desc += "[*Required] "
            desc += f"<{origin[0]}>"
            if len(origin) >= 2:
                desc += f"  // {origin[1]}"
            result = desc
        return result

    elif isinstance(origin, str):
        return f'"{ origin }"'

    else:
        return str(origin)

def find_all_jsons(origin: str):
    pattern = r'"""(.*?)"""'
    origin = re.sub(
        pattern,
        lambda match: json.dumps(match.group(1)),
        origin,
        flags=re.DOTALL
    )
    origin = origin.replace("\"\"\"", "\"").replace("[OUTPUT]", "$<<OUTPUT>>")
    stage = 1
    json_blocks = []
    block_num = 0
    layer = 0
    skip_next = False
    in_quote = False
    for index, char in enumerate(origin):
        if skip_next:
            skip_next = False
            continue
        if stage == 1:
            if char == "\\":
                skip_next = True
                continue
            if char == "[" or char == "{":
                json_blocks.append(char)
                stage = 2
                layer += 1
                continue
        elif stage == 2:
            if not in_quote:
                if char == "\\":
                    skip_next = True
                    if origin[index + 1] == "\"":
                        char = "\""
                    else:
                        continue
                if char == "\"":
                    in_quote = True
                if char == "[" or char == "{":
                    layer += 1
                elif char == "]" or char == "}":
                    layer -= 1
                #elif char in ("\t", " ", "\n"):
                    #char = ""
                json_blocks[block_num] += char
            else:
                if char == "\\":
                    char += origin[index + 1]
                    skip_next = True
                elif char == "\n":
                    char = "\\n"
                elif char == "\t":
                    char = "\\t"
                elif char == "\"":
                    in_quote = not in_quote
                json_blocks[block_num] += char
            if layer == 0:
                json_blocks[block_num] = json_blocks[block_num].replace("$<<OUTPUT>>", "[OUTPUT]")
                block_num += 1
                stage = 1
    return json_blocks

def find_json(origin: str):
    try:
        results = find_all_jsons(origin)
        if len(results) > 0:
            if len(results) == 1:
                return results[0]
            else:
                for result in results:
                    if len(result) > 2:
                        return result
                return results[0]
        else:
            return None
    except:
        return None
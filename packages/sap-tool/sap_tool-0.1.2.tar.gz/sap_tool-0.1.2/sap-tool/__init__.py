from typing import Callable
import inspect

__all__ = ["Tool"]

class Tool:
    def __init__(self, function: Callable, name: str, description: str):
        self.function = function
        self.name = name
        self.description = description
        self.python_type_to_json_schema = {
            "str": "string",
            "float": "number",
            "int": "integer",
            "bool": "boolean",
            "dict": "object",
            "list": "array",
            "None": "null"
        }

    def formulate_tool_schema(self):
        parameters = inspect.signature(self.function).parameters
        properties = {}
        for parm_name, parm in parameters.items():
            properties[parm_name] = {"type": self.python_type_to_json_schema[str(parm.annotation.__name__)]}
        print(properties)
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object", 
                    "properties": properties,
                    "required": [parm_name for parm_name, parm in parameters.items()]
                }
            }
        }
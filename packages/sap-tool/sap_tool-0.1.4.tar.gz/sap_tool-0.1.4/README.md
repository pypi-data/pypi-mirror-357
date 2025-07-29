# sap-tool

A simple Python package that helps agents create JSON schemas for methods/functions in a very simple way. This is useful for building agent tools, APIs, or any system that needs to describe callable functions in a structured format.

## Installation

```bash
pip install sap-tool
```

## Usage

```python
from sap_tool import Tool

def foo(a: int, b: str):
    pass

tool = Tool(foo, "foo", "A test function.")
schema = tool.formulate_tool_schema()
# Example print output from the package:
# {'a': {'type': 'integer'}, 'b': {'type': 'string'}}
# {'type': 'function', 'function': {'name': 'foo', 'description': 'A test function.', 'parameters': {'type': 'object', 'properties': {'a': {'type': 'integer'}, 'b': {'type': 'string'}}, 'required': ['a', 'b']}}}
print(schema)
```

## What does it do?

- Automatically generates a JSON schema for any Python function's parameters and types.
- Makes it easy to describe agent tools and methods for LLMs or other automation systems.
- Minimal, easy-to-use API.

## Example Output

```
{'a': {'type': 'integer'}, 'b': {'type': 'string'}}
{'type': 'function', 'function': {'name': 'foo', 'description': 'A test function.', 'parameters': {'type': 'object', 'properties': {'a': {'type': 'integer'}, 'b': {'type': 'string'}}, 'required': ['a', 'b']}}}
```

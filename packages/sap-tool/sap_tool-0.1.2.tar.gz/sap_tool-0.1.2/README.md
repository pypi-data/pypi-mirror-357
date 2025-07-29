# sap-tool

A simple Python tool class for schema generation from function signatures.

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
print(schema)
```

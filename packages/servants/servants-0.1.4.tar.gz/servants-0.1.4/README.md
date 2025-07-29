# servants

A simple Python library for prototyping and learning agent-based reasoning with tools.

This package helps you quickly prototype agent architectures that use tools (functions) and step-by-step reasoning. It is designed for educational and experimental purposes, not for production use.

## Installation

```bash
pip install servants
```

## Usage

```python
from servants import Tool

def foo(a: int, b: str):
    pass

tool = Tool(foo, "foo", "A test function.")
schema = tool.build_tool_schema()
print(schema)
```

## What does it do?

- Automatically generates a JSON schema for any Python function's parameters and types.
- Makes it easy to describe agent tools and methods for LLMs or other automation systems.
- Minimal, easy-to-use API.

## Note

This library is intended for prototyping and learning. For production-grade agent frameworks, see [LangChain](https://github.com/langchain-ai/langchain) or similar projects.

# servants

A simple Python library for prototyping and learning agent-based reasoning with tools.

This package helps you quickly prototype agent architectures that use tools (functions), step-by-step reasoning, and memory capabilities. It supports both single-agent workflows and multi-agent orchestration. The library is designed for educational and experimental purposes, not for production use.

## Installation

```bash
pip install servants
```

## Usage

```python
from openai import OpenAI
from servants import Servant, Tool
import csv
import os

client = OpenAI(api_key="your-api-key")

def csv_tool_function(data: str) -> str:
    """Process CSV data and save it to a file on disk."""
    try:
        lines = data.strip().split('\n')
        csv_data = []
        
        for line in lines:
            row = [field.strip() for field in line.split(',')]
            csv_data.append(row)
        
        filename = "countries_capitals.csv"
        filepath = os.path.join(os.path.expanduser("~/Desktop"), filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(csv_data)
        
        return f"CSV file saved successfully to {filepath} with {len(csv_data)} rows."
    
    except Exception as e:
        return f"Error creating CSV file: {str(e)}"

csv_tool = Tool(
    function=csv_tool_function,
    name="csv_tool",
    description="A tool that takes CSV data as string and saves it to a CSV file on the desktop.",
)

csv_servant = Servant(tools=[csv_tool], max_iterations=3)

# Create a chat completion function. The signature should be a method that takes a list of messages and returns a string.
# This makes the library flexible and not dependent on any specific LLM provider.
def chat_completion_func(messages):
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=messages,
        temperature=0.1 
    )
    content = response.choices[0].message.content
    print(f"=== AI Response ===")
    print(content)
    print(f"=== End Response ===")
    return content


# Execute the servant using the execute method.
result, messages = csv_servant.execute(
    problem="Create a CSV of 10 random countries and their capitals and save it to a file. Format the data as 'Country,Capital' with one pair per line.",
    chat_completion_func=chat_completion_func
)

```

## What does it do?

- Lets you quickly prototype agent-based architectures that use tools (functions) and step-by-step reasoning
- Provides a simple API for defining tools, agents (servants), and orchestrators (masters)
- Automatically generates JSON schemas for Python function parameters and types
- Includes built-in short-term memory capabilities for agents
- Supports multi-agent orchestration through the Master class
- Makes it easy to integrate with any LLM provider through flexible chat completion functions
- Enables pause, resume, and stop control for long-running agent processes
- Minimal, easy-to-use API designed for experimentation and learning

## Note

This library is intended for prototyping and learning. For production-grade agent frameworks, see [LangChain](https://github.com/langchain-ai/langchain) or similar projects.

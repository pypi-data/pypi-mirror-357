# servants

A simple Python library for prototyping and learning agent-based reasoning with tools.

This package helps you quickly prototype agent architectures that use tools (functions) and step-by-step reasoning. It is designed for educational and experimental purposes, not for production use.

## Installation

```bash
pip install servants
```

## Usage

```python
"""
Example usage of the SAP Tool Master.
"""

import time
import sys
import os
from openai import OpenAI

# Add the parent directory to sys.path to import from local servants
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from servants import Tool, Servant, Master

def example_usage():
    def get_weather(city: str) -> str:
        """
        Gets the current weather for a given city.
        Args:
            city (str): The city to get the weather for.
        Returns:
            str: The weather conditions (e.g., "Sunny", "Rainy", "Cloudy").
        """
        if "london" in city.lower():
            return "Rainy"
        elif "paris" in city.lower():
            return "Sunny"
        else:
            return "Cloudy"

    def suggest_activity(weather: str) -> str:
        """
        Suggests an activity based on the weather.
        Args:
            weather (str): The current weather (e.g., "Sunny", "Rainy", "Cloudy").
        Returns:
            str: A suggested activity.
        """
        if weather == "Sunny":
            return "Go for a walk in the park."
        elif weather == "Rainy":
            return "Visit a museum or watch a movie."
        else:
            return "It's a good day to read a book indoors."

    # Set up OpenAI client (replace with your API key)
    client = OpenAI(api_key="sk-...YOUR-API-KEY...")

    weather_tool = Tool(get_weather, "get_weather", "Gets the current weather for a given city.")
    activity_tool = Tool(suggest_activity, "suggest_activity", "Suggests an activity based on the weather.")

    def chat_completion_func(messages):
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content

    servant = Servant(tools=[weather_tool, activity_tool])
    manager = Master([servant])
    problem = "I'm in London today. What do you suggest I do?"
    system_message = "You are a helpful assistant. You can use tools to find information and make suggestions. Reason step-by-step to solve the user's problem."
    print("Starting the orchestrator...")
    manager.run(
        problem=problem,
        chat_completion_func=chat_completion_func,
        system_message=system_message,
        max_iterations=4,
        tools=[weather_tool, activity_tool]
    )
    for _ in range(10):
        print(f"Manager statuses: {manager.get_status()}")
        time.sleep(1)
    print("Pausing all servants...")
    manager.pause()
    time.sleep(3)
    print("Resuming all servants...")
    manager.resume()
    time.sleep(10)
    results = manager.get_results()
    print("\nResults from Manager:")
    for idx, result in results:
        print(f"Servant {idx}: {result}")
    manager.stop()
    print("All servants stopped")

if __name__ == "__main__":
    example_usage()
```

## What does it do?

- Lets you quickly prototype agent-based architectures that use tools (functions) and step-by-step reasoning.
- Provides a simple API for defining tools, agents (servants), and orchestrators (masters).
- Automatically generates a JSON schema for any Python function's parameters and types.
- Makes it easy to describe agent tools and methods for LLMs or other automation systems.
- Minimal, easy-to-use API for experimentation and learning.

## Note

This library is intended for prototyping and learning. For production-grade agent frameworks, see [LangChain](https://github.com/langchain-ai/langchain) or similar projects.

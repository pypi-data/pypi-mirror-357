"""
Example usage of the SAP Tool Master.
"""

import time
import sys
import os
from openai import OpenAI

# Add the parent directory to sys.path to import from local servants
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import from the local module
from servants import Tool, Servant, Master

def example_usage():
    # Define a simple tool
    def magic_calculator(a: int, b: int) -> int:
        """
        Takes two integers and returns a result.

        Args:
            a (int): The first integer.
            b (int): The second integer.

        Returns:
            int: The sum of a, b, and 9.
        """
        return a + b + 9
    
    # Set up OpenAI client (replace with your API key)
    client = OpenAI(api_key="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")
    
    # Create tool instances
    magic_tool = Tool(magic_calculator, "magic_calculator", "A magic calculator takes in two integers and returns a result.")
    
    # Create a chat completion function
    def chat_completion_func(messages):
        response = client.chat.completions.create(
            model="gpt-4o",  # Use an appropriate model
            messages=messages,
            temperature=0.7
        )
        return response.choices[0].message.content
    
    # Create servants with the magic tool
    servant1 = Servant(tools=[magic_tool])
    servant2 = Servant(tools=[magic_tool])
    
    # Create a Master for the first servant
    manager = Master([servant1])
    
    # Define problems for our assistants
    problem1 = "I need to use the magic_calculator tool with first parameter 15 and second is 25. What is the result?"
    problem2 = "Can you use the magic_calculator tool with parameters 7 and 13 and explain the result?"
    
    # System message for our assistants
    system_message = "You are a helpful assistant."
    
    print("Starting the orchestrators...")
    
    # Run the first servant with problem1
    manager.run(
        problem=problem1,
        chat_completion_func=chat_completion_func,
        system_message=system_message,
        max_iterations=3,
        tools=[magic_tool]
    )
    
    print("First servant started. Waiting 5 seconds before starting second...")
    time.sleep(5)
    
    # Create a new master for the second servant with problem2
    second_manager = Master([servant2])
    second_manager.run(
        problem=problem2,
        chat_completion_func=chat_completion_func,
        system_message=system_message,
        max_iterations=3,
        tools=[magic_tool]
    )
    
    # Monitor servant status for both managers
    for _ in range(10):
        print(f"Manager 1 statuses: {manager.get_status()}")
        print(f"Manager 2 statuses: {second_manager.get_status()}")
        time.sleep(1)
    
    # Pause all servants in both managers
    print("Pausing all servants...")
    manager.pause()
    second_manager.pause()
    
    time.sleep(3)
    
    # Resume all servants in both managers
    print("Resuming all servants...")
    manager.resume()
    second_manager.resume()
    
    # Wait for completion
    time.sleep(10)
    
    # Get results from both managers
    results1 = manager.get_results()
    results2 = second_manager.get_results()
    
    print("\nResults from Manager 1:")
    for idx, result in results1:
        print(f"Servant {idx}: {result}")
    
    print("\nResults from Manager 2:")
    for idx, result in results2:
        print(f"Servant {idx}: {result}")
    
    # Stop all servants in both managers
    manager.stop()
    second_manager.stop()
    print("All servants stopped")
    
if __name__ == "__main__":
    example_usage()

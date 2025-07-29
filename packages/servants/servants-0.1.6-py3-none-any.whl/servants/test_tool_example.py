# Example test for servants package
from servants import Tool, Servant
from openai import OpenAI
import os

# --- Tool Definitions ---

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

# --- LLM and Servant Setup ---

# NOTE: Replace with your own API key or set the OPENAI_API_KEY environment variable
api_key = os.environ.get("OPENAI_API_KEY", "YOUR_API_KEY_HERE")
client = OpenAI(api_key=api_key)

# Create Tool instances
weather_tool = Tool(get_weather, "get_weather", "Gets the current weather for a given city.")
activity_tool = Tool(suggest_activity, "suggest_activity", "Suggests an activity based on the weather.")

def chat_completion_func(messages):
    """A wrapper for the OpenAI chat completion API call."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        temperature=0.7
    )
    return response.choices[0].message.content

def on_thinking_complete(final_message, all_messages):
    """Callback function to handle the final result."""
    print("\n" + "="*50)
    print(f"Final Answer: {final_message}")
    print("="*50 + "\n")

# --- Main Execution ---

if __name__ == "__main__":
    problem = "I'm in London today. What do you suggest I do?"
    system_message = "You are a helpful assistant. You can use tools to find information and make suggestions. Reason step-by-step to solve the user's problem."
    
    # The servant is equipped with the necessary tools
    servant = Servant(tools=[weather_tool, activity_tool])
    
    print("Starting a logical reasoning loop...")
    print("="*50)
    
    servant.thinking_loop(
        problem=problem,
        chat_completion_func=chat_completion_func,
        system_message=system_message,
        max_iterations=4,  # Increased iterations for a multi-step task
        tools=[weather_tool, activity_tool],
        callback=on_thinking_complete
    )

    # The loop runs in a background thread, so we wait for it to complete
    servant._thinking_thread.join()

"""
Example of using action groups with the Bedrock Agents SDK.
"""
import datetime
from typing import List, Dict, Any
from bedrock_agents_sdk import BedrockAgents, Agent, ActionGroup, Message

# Define action group functions
def get_weather(location: str) -> Dict[str, Any]:
    """
    Get the current weather for a location.
    
    Args:
        location: The city or location to get weather for
        
    Returns:
        Dictionary with weather information
    """
    # In a real application, this would call a weather API
    # This is a mock implementation for demonstration
    weather_data = {
        "location": location,
        "temperature": 72,
        "condition": "Sunny",
        "humidity": 45,
        "wind_speed": 8
    }
    return weather_data

def get_forecast(location: str, days: int = 3) -> Dict[str, Any]:
    """
    Get the weather forecast for a location.
    
    Args:
        location: The city or location to get forecast for
        days: Number of days for the forecast (default: 3)
        
    Returns:
        Dictionary with forecast information
    """
    # Mock implementation
    forecast = []
    for i in range(days):
        day = {
            "day": (datetime.datetime.now() + datetime.timedelta(days=i)).strftime("%A"),
            "temperature": 70 + i * 2,
            "condition": "Partly Cloudy" if i % 2 == 0 else "Sunny"
        }
        forecast.append(day)
    
    return {
        "location": location,
        "forecast": forecast
    }

def main():
    # Create the client
    client = BedrockAgents()
    
    # Create action groups
    weather_group = ActionGroup(
        name="WeatherService",
        description="Provides weather information and forecasts",
        functions=[get_weather, get_forecast]
    )
    
    # Create the agent
    agent = Agent(
        name="WeatherAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a helpful weather assistant. Use the WeatherService action group to provide weather information when asked.",
        action_groups=[weather_group]
    )
    
    # Run the agent with a user query
    result = client.run(
        agent=agent,
        messages=[
            {
                "role": "user",
                "content": "What's the weather like in Seattle? Also, can you give me a 5-day forecast?"
            }
        ]
    )
    
    print("\nResponse from agent:")
    print("-" * 50)
    print(result["response"])
    print("-" * 50)
    
    # Interactive chat session
    print("\nChat with the Weather Agent (type 'exit' to quit):")
    messages = []
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            break
            
        messages.append({"role": "user", "content": user_input})
        
        result = client.run(agent=agent, messages=messages)
        assistant_message = result["response"]
        
        print(f"\nWeather Agent: {assistant_message}")
        
        messages.append({"role": "assistant", "content": assistant_message})

if __name__ == "__main__":
    main() 
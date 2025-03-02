"""
Example demonstrating the different ways to configure agents with action groups.

This example shows all four approaches to configuring agents:
1. Using ActionGroup objects in the constructor (recommended)
2. Adding ActionGroup objects after creation
3. Using a functions dictionary
4. Using a functions list
"""
import datetime
from typing import Dict, Any
from bedrock_agents_sdk import Client, Agent, ActionGroup, Message

# Define some example functions
def get_weather(location: str) -> Dict[str, Any]:
    """Get the current weather for a location"""
    # Mock implementation
    return {
        "location": location,
        "temperature": 72,
        "condition": "Sunny"
    }

def get_forecast(location: str, days: int = 3) -> Dict[str, Any]:
    """Get the weather forecast for a location"""
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

def get_time() -> Dict[str, Any]:
    """Get the current time"""
    now = datetime.datetime.now()
    return {"time": now.strftime("%H:%M:%S")}

def get_date() -> Dict[str, Any]:
    """Get the current date"""
    now = datetime.datetime.now()
    return {"date": now.strftime("%Y-%m-%d")}

def main():
    # Create a client
    client = Client(verbosity="verbose")
    
    # Method 1: Using ActionGroup objects in the constructor (recommended)
    print("\n=== Method 1: ActionGroup objects in constructor (recommended) ===")
    
    # Create action groups
    weather_group = ActionGroup(
        name="WeatherService",
        description="Provides weather information and forecasts",
        functions=[get_weather, get_forecast]
    )
    
    time_group = ActionGroup(
        name="TimeService",
        description="Provides time-related functions",
        functions=[get_time, get_date]
    )
    
    # Create the agent with action groups
    agent1 = Agent(
        name="Method1Agent",
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant that can provide weather and time information.",
        action_groups=[weather_group, time_group]
    )
    
    # Print information about the agent
    print(f"Agent has {len(agent1.action_groups)} action groups:")
    for ag in agent1.action_groups:
        print(f"  - {ag.name}: {len(ag.functions)} functions")
    
    # Method 2: Adding ActionGroup objects after creation
    print("\n=== Method 2: Adding ActionGroup objects after creation ===")
    
    # Create the agent
    agent2 = Agent(
        name="Method2Agent",
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant that can provide weather and time information."
    )
    
    # Create and add action groups
    weather_group = ActionGroup(
        name="WeatherService",
        description="Provides weather information and forecasts",
        functions=[get_weather, get_forecast]
    )
    
    agent2.add_action_group(weather_group)
    
    time_group = ActionGroup(
        name="TimeService",
        description="Provides time-related functions",
        functions=[get_time, get_date]
    )
    
    agent2.add_action_group(time_group)
    
    # Print information about the agent
    print(f"Agent has {len(agent2.action_groups)} action groups:")
    for ag in agent2.action_groups:
        print(f"  - {ag.name}: {len(ag.functions)} functions")
    
    # Method 3: Using a functions dictionary
    print("\n=== Method 3: Using a functions dictionary ===")
    
    # Create the agent with a functions dictionary
    agent3 = Agent(
        name="Method3Agent",
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant that can provide weather and time information.",
        functions={
            "WeatherService": [get_weather, get_forecast],
            "TimeService": [get_time, get_date]
        }
    )
    
    # Print information about the agent
    print(f"Agent has {len(agent3.action_groups)} action groups:")
    for ag in agent3.action_groups:
        print(f"  - {ag.name}: {len(ag.functions)} functions")
    
    # Method 4: Using a functions list
    print("\n=== Method 4: Using a functions list ===")
    
    # Create the agent with a functions list
    agent4 = Agent(
        name="Method4Agent",
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="You are a helpful assistant that can provide weather and time information.",
        functions=[get_weather, get_forecast, get_time, get_date]
    )
    
    # Print information about the agent
    print(f"Agent has {len(agent4.action_groups)} action groups:")
    for ag in agent4.action_groups:
        print(f"  - {ag.name}: {len(ag.functions)} functions")
    
    # Print functions
    print(f"Agent has {len(agent4.functions)} functions:")
    for func in agent4.functions:
        print(f"  - {func.name} (action group: {func.action_group or 'DefaultActions'})")
    
    # Run a simple test with the recommended approach (Method 1)
    print("\n=== Running a test with the recommended approach (Method 1) ===")
    result = client.run(
        agent=agent1,
        messages=[
            {
                "role": "user",
                "content": "What's the weather like in Seattle? Also, what time is it now?"
            }
        ]
    )
    
    print("\nResponse from agent:")
    print("-" * 50)
    print(result["response"])
    print("-" * 50)

if __name__ == "__main__":
    main() 
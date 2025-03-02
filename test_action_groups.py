"""
Test script for the action group alignment changes.
"""
import json
from typing import Dict, Any, List
from bedrock_agents_sdk import Agent, ActionGroup, Client

# Define some example functions
def get_weather(location: str) -> Dict[str, Any]:
    """Get the current weather for a location.
    
    Args:
        location: The city or location to get weather for
        
    Returns:
        Dictionary with weather information
    """
    # Mock implementation
    return {
        "location": location,
        "temperature": 72,
        "condition": "Sunny"
    }

def get_forecast(location: str, days: int = 3) -> Dict[str, Any]:
    """Get the weather forecast for a location.
    
    Args:
        location: The city or location to get forecast for
        days: Number of days for the forecast
        
    Returns:
        Dictionary with forecast information
    """
    # Mock implementation
    return {
        "location": location,
        "forecast": [{"day": i, "temp": 70 + i} for i in range(days)]
    }

def get_time(timezone: str = "UTC") -> str:
    """Get the current time in a specific timezone.
    
    Args:
        timezone: The timezone to get the time for
        
    Returns:
        Current time as a string
    """
    return f"Current time in {timezone}: 12:00 PM"

def test_action_groups_in_constructor():
    """Test creating an agent with action groups in the constructor."""
    print("\n=== Testing action groups in constructor ===")
    
    # Create action groups
    weather_group = ActionGroup(
        name="WeatherService",
        description="Provides weather information and forecasts",
        functions=[get_weather, get_forecast]
    )
    
    time_group = ActionGroup(
        name="TimeService",
        description="Provides time-related functions",
        functions=[get_time]
    )
    
    # Create the agent with action groups
    agent = Agent(
        name="WeatherAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a helpful weather assistant.",
        action_groups=[weather_group, time_group]
    )
    
    # Print action groups
    print(f"Agent has {len(agent.action_groups)} action groups:")
    for ag in agent.action_groups:
        print(f"  - {ag.name}: {len(ag.functions)} functions")
    
    # Print functions
    print(f"Agent has {len(agent.functions)} functions:")
    for func in agent.functions:
        print(f"  - {func.name} (action group: {func.action_group})")
    
    # Create client and build action groups
    client = Client(verbosity="verbose")
    action_groups = client._build_action_groups(agent)
    
    # Print action groups built by client
    print(f"Client built {len(action_groups)} action groups:")
    for ag in action_groups:
        print(f"  - {ag['actionGroupName']}: {len(ag['functionSchema']['functions']) if 'functionSchema' in ag else 0} functions")

def test_add_action_group():
    """Test adding action groups to an agent after creation."""
    print("\n=== Testing add_action_group method ===")
    
    # Create the agent
    agent = Agent(
        name="EmptyAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a helpful assistant."
    )
    
    # Print initial state
    print(f"Initial: Agent has {len(agent.action_groups)} action groups and {len(agent.functions)} functions")
    
    # Create and add action groups
    weather_group = ActionGroup(
        name="WeatherService",
        description="Provides weather information and forecasts",
        functions=[get_weather, get_forecast]
    )
    
    agent.add_action_group(weather_group)
    
    # Print after adding first action group
    print(f"After adding WeatherService: Agent has {len(agent.action_groups)} action groups and {len(agent.functions)} functions")
    
    time_group = ActionGroup(
        name="TimeService",
        description="Provides time-related functions",
        functions=[get_time]
    )
    
    agent.add_action_group(time_group)
    
    # Print after adding second action group
    print(f"After adding TimeService: Agent has {len(agent.action_groups)} action groups and {len(agent.functions)} functions")
    
    # Create client and build action groups
    client = Client(verbosity="verbose")
    action_groups = client._build_action_groups(agent)
    
    # Print action groups built by client
    print(f"Client built {len(action_groups)} action groups:")
    for ag in action_groups:
        print(f"  - {ag['actionGroupName']}: {len(ag['functionSchema']['functions']) if 'functionSchema' in ag else 0} functions")

def test_functions_dict():
    """Test creating an agent with a functions dictionary."""
    print("\n=== Testing functions dictionary ===")
    
    # Create the agent with functions dictionary
    agent = Agent(
        name="DictAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a helpful assistant.",
        functions={
            "WeatherService": [get_weather, get_forecast],
            "TimeService": [get_time]
        }
    )
    
    # Print action groups
    print(f"Agent has {len(agent.action_groups)} action groups:")
    for ag in agent.action_groups:
        print(f"  - {ag.name}: {len(ag.functions)} functions")
    
    # Print functions
    print(f"Agent has {len(agent.functions)} functions:")
    for func in agent.functions:
        print(f"  - {func.name} (action group: {func.action_group})")
    
    # Create client and build action groups
    client = Client(verbosity="verbose")
    action_groups = client._build_action_groups(agent)
    
    # Print action groups built by client
    print(f"Client built {len(action_groups)} action groups:")
    for ag in action_groups:
        print(f"  - {ag['actionGroupName']}: {len(ag['functionSchema']['functions']) if 'functionSchema' in ag else 0} functions")

def test_functions_list():
    """Test creating an agent with a functions list."""
    print("\n=== Testing functions list ===")
    
    # Create the agent with functions list
    agent = Agent(
        name="ListAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a helpful assistant.",
        functions=[get_weather, get_forecast, get_time]
    )
    
    # Print action groups
    print(f"Agent has {len(agent.action_groups)} action groups:")
    for ag in agent.action_groups:
        print(f"  - {ag.name}: {len(ag.functions)} functions")
    
    # Print functions
    print(f"Agent has {len(agent.functions)} functions:")
    for func in agent.functions:
        print(f"  - {func.name} (action group: {func.action_group or 'None'})")
    
    # Create client and build action groups
    client = Client(verbosity="verbose")
    action_groups = client._build_action_groups(agent)
    
    # Print action groups built by client
    print(f"Client built {len(action_groups)} action groups:")
    for ag in action_groups:
        print(f"  - {ag['actionGroupName']}: {len(ag['functionSchema']['functions']) if 'functionSchema' in ag else 0} functions")

if __name__ == "__main__":
    test_action_groups_in_constructor()
    test_add_action_group()
    test_functions_dict()
    test_functions_list() 
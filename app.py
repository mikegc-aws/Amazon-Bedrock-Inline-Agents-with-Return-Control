import datetime
from inline_agent import BedrockInlineAgent

def get_current_time():
    """Function to get the current time"""
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M:%S")
    timezone = datetime.datetime.now().astimezone().tzname()
    return {
        "time": current_time,
        "timezone": timezone
    }

def get_current_date():
    """Function to get the current date"""
    now = datetime.datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    timezone = datetime.datetime.now().astimezone().tzname()
    return {
        "date": current_date,
        "timezone": timezone
    }

def add_two_numbers(a, b):
    """Function to add two numbers"""
    return {"result": a + b}

def get_action_groups():
    """Define and return the action groups configuration"""
    return [
        {
            "actionGroupName": "TimeActions",
            "description": "Actions related to getting the current time",
            "actionGroupExecutor": {
                "customControl": "RETURN_CONTROL"
            },
            "functionSchema": {
                "functions": [
                    {
                        "name": "get_time",
                        "description": "Get the current time and date",
                        "parameters": {},
                        "requireConfirmation": "DISABLED"
                    },
                    {
                        "name": "get_date",
                        "description": "Get the current date",
                        "parameters": {},
                        "requireConfirmation": "DISABLED"
                    }
                ]
            }
        },
        {
            "actionGroupName": "MathActions",
            "description": "Actions related to mathematical operations",
            "actionGroupExecutor": {
                "customControl": "RETURN_CONTROL"
            },
            "functionSchema": {
                "functions": [
                    {
                        "name": "add_two_numbers",
                        "description": "Add two numbers together",  
                        "parameters": {
                            "a": {
                                "description": "The first number to add",
                                "required": True,
                                "type": "number"    
                            },
                            "b": {
                                "description": "The second number to add",
                                "required": True,
                                "type": "number"
                            }
                        }   
                    }
                ]
            }
        }
    ]

def main():
    # Define the agent configuration
    action_groups = get_action_groups()
    instruction = "You are a helpful assistant that can tell the time and perform basic math operations when asked. You can also engage in general conversation."
    
    # Create and configure the agent
    agent = BedrockInlineAgent(
        action_groups=action_groups,
        instruction=instruction,
        debug=False
    )
    
    # Register the available functions
    agent.register_function("get_time", get_current_time)
    agent.register_function("get_date", get_current_date)
    agent.register_function("add_two_numbers", add_two_numbers)
    
    # Start the chat session
    agent.chat()

if __name__ == "__main__":
    main() 
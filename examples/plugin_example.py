"""
Example of using plugins with the Bedrock Agents SDK.
"""
import datetime
from bedrock_agents_sdk import BedrockAgents, Agent, Message
from bedrock_agents_sdk import SecurityPlugin, GuardrailPlugin, KnowledgeBasePlugin
from bedrock_agents_sdk.plugins.base import BedrockAgentsPlugin

# Define a function
def get_time() -> dict:
    """Get the current time"""
    now = datetime.datetime.now()
    return {"time": now.strftime("%H:%M:%S")}

# Define a custom plugin
class LoggingPlugin(BedrockAgentsPlugin):
    """A plugin that logs all API calls"""
    
    def __init__(self, log_file="api_calls.log"):
        self.log_file = log_file
    
    def pre_invoke(self, params):
        """Log the parameters before invocation"""
        with open(self.log_file, "a") as f:
            f.write(f"API Call Parameters: {params}\n")
        return params
    
    def post_invoke(self, response):
        """Log the response after invocation"""
        with open(self.log_file, "a") as f:
            f.write(f"API Response: {response}\n")
        return response
    
    def pre_deploy(self, template):
        """Log the template before deployment"""
        with open(self.log_file, "a") as f:
            f.write(f"Deployment Template: {template}\n")
        return template

def main():
    # Create the client
    client = BedrockAgents(verbosity="verbose")
    
    # Create plugins
    kb_plugin = KnowledgeBasePlugin(
        knowledge_base_id="your-kb-id",
        description="Knowledge base containing company documentation"
    )
    
    guardrail_plugin = GuardrailPlugin(guardrail_id="your-guardrail-id")
    
    # Create a custom logging plugin
    logging_plugin = LoggingPlugin(log_file="api_calls.log")
    
    # Create a security plugin (uncomment to use)
    # security_plugin = SecurityPlugin(customer_encryption_key_arn="your-kms-key-arn")
    
    # Create the agent with plugins
    agent = Agent(
        name="PluginAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="You are a helpful assistant that can tell the time.",
        functions=[get_time],
        plugins=[
            kb_plugin,
            guardrail_plugin,
            logging_plugin,
            # security_plugin  # Uncomment to use
        ]
    )
    
    # Run the agent
    result = client.run(
        agent=agent,
        messages=[
            {
                "role": "user",
                "content": "What time is it now?"
            }
        ]
    )
    
    print("\nResponse from agent:")
    print("-" * 50)
    print(result["response"])
    print("-" * 50)
    
    # Deploy the agent to AWS
    print("\nDeploying agent to AWS...")
    
    # All plugins will be applied to the deployment
    # template_path = agent.deploy(
    #     description="Plugin example agent",
    #     # Uncomment the following lines to automatically build and deploy
    #     # auto_build=True,
    #     # auto_deploy=True
    # )

if __name__ == "__main__":
    main() 
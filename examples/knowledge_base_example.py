"""
Example of using knowledge bases with the Bedrock Agents SDK.
"""
import os
from bedrock_agents_sdk import BedrockAgents, Agent, Message, KnowledgeBasePlugin

def main():
    # Create the client
    client = BedrockAgents()
    
    # Create a knowledge base plugin
    kb_plugin = KnowledgeBasePlugin(
        knowledge_base_id="your-knowledge-base-id",  # Replace with your actual KB ID
        description="Knowledge base containing company documentation and FAQs"
    )
    
    # Register the plugin with the client
    client.register_plugin(kb_plugin)
    
    # Create the agent
    agent = Agent(
        name="SupportAgent",
        model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        instructions="""
        You are a helpful support assistant for our company.
        Use the knowledge base to answer questions about our products and services.
        If you don't know the answer, say so and don't make up information.
        """
    )
    
    # Run the agent with a user query
    result = client.run(
        agent=agent,
        messages=[
            {
                "role": "user",
                "content": "What are your refund policies?"
            }
        ]
    )
    
    print("\nResponse from agent:")
    print("-" * 50)
    print(result["response"])
    print("-" * 50)
    
    # Example of uploading a document to a knowledge base
    def upload_document_example():
        # This is a demonstration of how you might upload a document
        # In a real application, you would use the AWS SDK or console
        print("\nUploading document to knowledge base (example code):")
        print("client.upload_document(")
        print("    knowledge_base_id='your-knowledge-base-id',")
        print("    document_path='path/to/document.pdf',")
        print("    metadata={'category': 'policies', 'department': 'legal'}")
        print(")")
    
    upload_document_example()
    
    # Interactive chat session
    print("\nChat with the Support Agent (type 'exit' to quit):")
    messages = []
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            break
            
        messages.append({"role": "user", "content": user_input})
        
        result = client.run(agent=agent, messages=messages)
        assistant_message = result["response"]
        
        print(f"\nSupport Agent: {assistant_message}")
        
        messages.append({"role": "assistant", "content": assistant_message})

if __name__ == "__main__":
    main() 
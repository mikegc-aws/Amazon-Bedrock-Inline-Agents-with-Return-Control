"""
Example of deploying a Bedrock Agent with web search capabilities.

This example demonstrates how to:
1. Create functions that search the web and extract content from URLs
2. Handle different response formats from third-party libraries
3. Properly specify dependencies for Lambda deployment
4. Handle Lambda parameter format correctly (list of dictionaries)
"""
import os
from bedrock_agents_sdk import BedrockAgents, Agent, Message

# Define functions for web search and content extraction
def search_internet(query: str, num_results: int = 5) -> dict:
    """
    Search the internet using DuckDuckGo
    
    :param query: The search query
    :param num_results: Number of results to return (default: 5)
    """
    from duckduckgo_search import DDGS
    
    try:
        # Create a DuckDuckGo Search instance
        ddg = DDGS()
        
        # Perform the search
        search_results = list(ddg.text(query, max_results=num_results))
        
        # Format the results - handle different possible return formats
        results = []
        for result in search_results:
            # Check if result is a dictionary (newer versions of the library)
            if isinstance(result, dict):
                results.append({
                    "title": result.get('title', ''),
                    "url": result.get('href', ''),
                    "snippet": result.get('body', '')
                })
            # Check if result is a list or tuple (older versions or different format)
            elif isinstance(result, (list, tuple)) and len(result) >= 3:
                results.append({
                    "title": result[0] if len(result) > 0 else '',
                    "url": result[1] if len(result) > 1 else '',
                    "snippet": result[2] if len(result) > 2 else ''
                })
            # Fallback for any other format
            else:
                results.append({
                    "title": str(result),
                    "url": "",
                    "snippet": str(result)
                })
                
        return {
            "results": results,
            "query": query
        }
    except Exception as e:
        # Return error information if the search fails
        return {
            "results": [],
            "query": query,
            "error": str(e)
        }

def load_text_from_url(url: str) -> dict:
    """
    Load and extract text content from a specified URL
    
    :param url: The URL to fetch text content from
    """
    import requests
    from bs4 import BeautifulSoup
    
    try:
        # Add user agent to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise exception for 4XX/5XX responses
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script_or_style in soup(["script", "style", "header", "footer", "nav"]):
            script_or_style.extract()
            
        # Get text content
        text = soup.get_text()
        
        # Clean up text: remove extra whitespace and blank lines
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Limit text length to avoid exceeding Lambda response size limits
        max_length = 100000  # Adjust as needed
        if len(text) > max_length:
            text = text[:max_length] + "... [content truncated due to size]"
        
        return {
            "content": text,
            "url": url,
            "status_code": response.status_code
        }
    except Exception as e:
        # Handle errors gracefully
        return {
            "content": f"Error retrieving content: {str(e)}",
            "url": url,
            "status_code": 500
        }

# Helper function to extract parameters in Lambda
def extract_parameter_value(parameters, param_name, default=None):
    """
    Extract a parameter value from the parameters list
    
    Args:
        parameters: List of parameter dictionaries
        param_name: Name of the parameter to extract
        default: Default value if parameter is not found
        
    Returns:
        The parameter value or default if not found
    """
    if isinstance(parameters, list):
        # Parameters is a list of dictionaries
        for param in parameters:
            if isinstance(param, dict) and param.get('name') == param_name:
                return param.get('value', default)
    elif isinstance(parameters, dict):
        # Parameters is a dictionary
        return parameters.get(param_name, default)
    
    # If we get here, parameter was not found
    return default

def main():
    # Create the agent
    agent = Agent(
        name="WebSearchAgent",
        model="anthropic.claude-3-sonnet-20240229-v1:0",
        instructions="""You are a helpful web search assistant. 
        When asked for information, use the search_internet function to find relevant information.
        If the user wants to read content from a specific URL, use the load_text_from_url function.
        Always cite your sources by providing the URLs.""",
        functions={
            "SearchActions": [search_internet, load_text_from_url]
        }
    )
    
    # Test the agent locally before deploying
    print("Testing agent locally before deployment...")
    client = BedrockAgents(verbosity="normal")
    result = client.run(
        agent=agent,
        message="What is the current weather in Seattle?"
    )
    print("\nLocal agent response:")
    print("-" * 50)
    print(result["response"])
    print("-" * 50)
    
    # Deploy the agent to AWS
    print("\nDeploying agent to AWS...")
    
    # Add specific version constraints for dependencies
    agent.add_dependency("requests", ">=2.25.0")
    agent.add_dependency("beautifulsoup4", ">=4.9.0")
    agent.add_dependency("duckduckgo-search", ">=3.0.0")
    
    # Generate the SAM template and supporting files
    # The output directory will default to "./websearchagent_deployment"
    template_path = agent.deploy(
        description="Web search agent with DuckDuckGo and BeautifulSoup",
        # Uncomment the following lines to automatically build and deploy
        # auto_build=True,
        # auto_deploy=True
    )
    
    print("\nIMPORTANT: After deployment, you need to manually update the Lambda function code")
    print("to handle parameters correctly. In the Lambda console, add the following function:")
    print("""
def extract_parameter_value(parameters, param_name, default=None):
    \"\"\"
    Extract a parameter value from the parameters list
    \"\"\"
    if isinstance(parameters, list):
        # Parameters is a list of dictionaries
        for param in parameters:
            if isinstance(param, dict) and param.get('name') == param_name:
                return param.get('value', default)
    elif isinstance(parameters, dict):
        # Parameters is a dictionary
        return parameters.get(param_name, default)
    
    # If we get here, parameter was not found
    return default
    """)
    print("\nThen update the lambda_handler function to use this helper function:")
    print("""
# Get parameters from the event if available
parameters = event.get("parameters", [])

# For search_internet function:
query = extract_parameter_value(parameters, "query", "")
num_results_str = extract_parameter_value(parameters, "num_results", "5")
try:
    num_results = int(num_results_str)
except (ValueError, TypeError):
    num_results = 5
output_from_logic = search_internet(query=query, num_results=num_results)

# For load_text_from_url function:
url = extract_parameter_value(parameters, "url", "")
output_from_logic = load_text_from_url(url=url)
    """)

if __name__ == "__main__":
    main() 
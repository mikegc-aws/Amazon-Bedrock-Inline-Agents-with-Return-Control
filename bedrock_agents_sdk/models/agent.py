"""
Agent model for Bedrock Agents SDK.
"""
from typing import List, Dict, Any, Optional, Union, Callable, Type
from pydantic import BaseModel, ConfigDict
import os
from dataclasses import dataclass, field

from bedrock_agents_sdk.models.function import Function
from bedrock_agents_sdk.models.action_group import ActionGroup
from bedrock_agents_sdk.models.files import InputFile
from bedrock_agents_sdk.deployment.sam_template import SAMTemplateGenerator
from bedrock_agents_sdk.plugins.base import AgentPlugin, BedrockAgentsPlugin, ClientPlugin

@dataclass
class Agent:
    """Agent configuration for Amazon Bedrock Agents"""
    
    name: str
    model: str
    instructions: str
    functions: Union[List[Callable], Dict[str, List[Callable]]] = field(default_factory=list)
    action_groups: List[ActionGroup] = field(default_factory=list)
    enable_code_interpreter: bool = False
    files: List[InputFile] = field(default_factory=list)
    plugins: List[Union[AgentPlugin, BedrockAgentsPlugin, ClientPlugin]] = field(default_factory=list)
    advanced_config: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(self, **data):
        """Initialize the agent and process functions if provided"""
        # Set default values for attributes
        self.functions = []
        self.files = []
        self.plugins = []
        self.action_groups = []
        self.enable_code_interpreter = False
        self.advanced_config = None
        self._custom_dependencies = {}
        
        # Handle dictionary format for functions
        if 'functions' in data and isinstance(data['functions'], dict):
            action_groups = data.pop('functions')
            processed_functions = []
            
            for action_group, funcs in action_groups.items():
                for func in funcs:
                    processed_functions.append(self._create_function(func, action_group=action_group))
            
            data['functions'] = processed_functions
            
        # Initialize attributes from data
        for key, value in data.items():
            setattr(self, key, value)
            
        self._process_functions()
        
    def _process_functions(self):
        """Process functions provided in the constructor"""
        processed_functions = []
        
        # Process each function
        for item in self.functions:
            if isinstance(item, Function):
                # Already a Function object, keep as is
                processed_functions.append(item)
            elif callable(item):
                # Single function without action group
                processed_functions.append(self._create_function(item))
        
        # Replace the original functions list with processed functions
        self.functions = processed_functions
    
    def _create_function(self, function: Callable, description: Optional[str] = None, action_group: Optional[str] = None) -> Function:
        """Create a Function object from a callable"""
        func_name = function.__name__
        
        # Use provided description or extract first line of docstring
        if description:
            func_desc = description
        elif function.__doc__:
            # Extract only the first line of the docstring
            func_desc = function.__doc__.strip().split('\n')[0]
        else:
            func_desc = f"Execute the {func_name} function"
        
        return Function(
            name=func_name,
            description=func_desc,
            function=function,
            action_group=action_group
        )
    
    def add_function(self, function: Callable, description: Optional[str] = None, action_group: Optional[str] = None):
        """Add a function to the agent"""
        self.functions.append(self._create_function(function, description, action_group))
        return self

    def add_file(self, name: str, content: bytes, media_type: str, use_case: str = "CODE_INTERPRETER") -> InputFile:
        """Add a file to be sent to the agent"""
        file = InputFile(name=name, content=content, media_type=media_type, use_case=use_case)
        self.files.append(file)
        return file
    
    def add_file_from_path(self, file_path: str, use_case: str = "CODE_INTERPRETER") -> InputFile:
        """Add a file from a local path"""
        import mimetypes
        import os
        
        name = os.path.basename(file_path)
        media_type = mimetypes.guess_type(file_path)[0] or 'application/octet-stream'
        
        with open(file_path, 'rb') as f:
            content = f.read()
        
        return self.add_file(name, content, media_type, use_case)
    
    def add_plugin(self, plugin: Union[AgentPlugin, BedrockAgentsPlugin, ClientPlugin]):
        """
        Add a plugin to the agent
        
        Args:
            plugin: The plugin to add
        """
        self.plugins.append(plugin)
        return self

    def add_dependency(self, dependency: str, version: Optional[str] = None, action_group: Optional[str] = None):
        """
        Add a custom dependency for deployment
        
        This method allows you to specify dependencies that should be included in the
        requirements.txt file when deploying the agent to AWS Lambda.
        
        Args:
            dependency: The name of the dependency (e.g., "pandas")
            version: Optional version constraint (e.g., ">=1.0.0")
            action_group: Optional action group to add the dependency to.
                          If not provided, the dependency will be added to all action groups.
        
        Returns:
            self: For method chaining
        """
        if action_group not in self._custom_dependencies:
            self._custom_dependencies[action_group] = {}
        
        self._custom_dependencies[action_group][dependency] = version
        return self
    
    def deploy(self, 
               output_dir: Optional[str] = None, 
               foundation_model: Optional[str] = None,
               parameters: Optional[Dict[str, Dict[str, str]]] = None,
               description: Optional[str] = None,
               auto_build: bool = False,
               auto_deploy: bool = False) -> str:
        """
        Deploy the agent to AWS using SAM
        
        Args:
            output_dir: The directory to output the SAM template and code to.
                       If None, defaults to "./[agent_name]_deployment"
            foundation_model: The foundation model to use (defaults to the agent's model)
            parameters: Additional parameters to add to the template
            description: Description for the SAM template
            auto_build: Whether to automatically run 'sam build'
            auto_deploy: Whether to automatically run 'sam deploy --guided'
            
        Returns:
            str: Path to the generated template file
        """
        import os
        
        # Create the SAM template generator
        generator = SAMTemplateGenerator(
            agent=self,
            output_dir=output_dir
        )
        
        # Add custom dependencies to the generator
        for action_group, deps in self._custom_dependencies.items():
            for dep, version in deps.items():
                generator.add_custom_dependency(action_group, dep, version)
        
        # Generate the SAM template and supporting files
        template_path = generator.generate(
            foundation_model=foundation_model,
            parameters=parameters,
            description=description
        )
        
        # Create a safe name for the stack (lowercase, alphanumeric with hyphens)
        safe_stack_name = ''.join(c.lower() if c.isalnum() else '-' for c in self.name)
        safe_stack_name = safe_stack_name.strip('-')  # Remove leading/trailing hyphens
        
        # Automatically build the SAM project if requested
        if auto_build or auto_deploy:
            import subprocess
            import sys
            
            print("\n🔨 Building SAM project...")
            
            # Change to the output directory
            original_dir = os.getcwd()
            os.chdir(generator.output_dir)
            
            try:
                # Run sam build
                build_result = subprocess.run(
                    ["sam", "build"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                print(build_result.stdout)
                print("\n✅ SAM project built successfully")
                
                # Automatically deploy the SAM project if requested
                if auto_deploy:
                    print("\n🚀 Deploying SAM project...")
                    
                    # Run sam deploy with the agent name as the stack name
                    deploy_result = subprocess.run(
                        ["sam", "deploy", "--guided", "--capabilities", "CAPABILITY_NAMED_IAM", 
                         "--stack-name", f"{safe_stack_name}-agent"],
                        check=True
                    )
                    
                    print("\n✅ SAM project deployed successfully")
            
            except subprocess.CalledProcessError as e:
                print(f"\n❌ Error: {e}")
                print(e.stdout)
                print(e.stderr)
                
            except FileNotFoundError:
                print("\n❌ Error: AWS SAM CLI not found")
                print("Please install the AWS SAM CLI:")
                print("  pip install aws-sam-cli")
                
            finally:
                # Change back to the original directory
                os.chdir(original_dir)
        
        return template_path 
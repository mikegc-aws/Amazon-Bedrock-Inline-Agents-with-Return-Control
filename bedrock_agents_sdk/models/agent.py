"""
Agent model for Bedrock Agents SDK.
"""
from typing import List, Dict, Any, Optional, Union, Callable
from pydantic import BaseModel, ConfigDict
import os

from bedrock_agents_sdk.models.function import Function
from bedrock_agents_sdk.models.files import InputFile
from bedrock_agents_sdk.deployment.sam_template import SAMTemplateGenerator

class Agent(BaseModel):
    """Represents a Bedrock agent configuration"""
    name: str
    model: str
    instructions: str
    functions: List[Union[Function, Callable]] = []
    enable_code_interpreter: bool = False
    files: List[InputFile] = []
    advanced_config: Optional[Dict[str, Any]] = None
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
    def __init__(self, **data):
        """Initialize the agent and process functions if provided"""
        # Handle dictionary format for functions
        if 'functions' in data and isinstance(data['functions'], dict):
            action_groups = data.pop('functions')
            processed_functions = []
            
            for action_group, funcs in action_groups.items():
                for func in funcs:
                    processed_functions.append(self._create_function(func, action_group=action_group))
            
            data['functions'] = processed_functions
        
        # Initialize files list if not provided
        if 'files' not in data:
            data['files'] = []
            
        super().__init__(**data)
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
        
    def deploy(self, 
               output_dir: str = "./deployment", 
               foundation_model: Optional[str] = None,
               parameters: Optional[Dict[str, Dict[str, str]]] = None,
               description: Optional[str] = None,
               auto_build: bool = False,
               auto_deploy: bool = False) -> str:
        """
        Generate a SAM template and supporting files for deploying the agent to AWS
        
        This method creates a complete SAM project that can be deployed to AWS using the
        AWS SAM CLI. The project includes a Lambda function that implements all the agent's
        functions, a SAM template that defines the AWS resources, and deployment instructions.
        
        Args:
            output_dir: Directory to output the SAM template and code to
            foundation_model: The foundation model to use (defaults to the agent's model)
            parameters: Additional parameters to add to the template
            description: Description for the SAM template
            auto_build: Whether to automatically build the SAM project
            auto_deploy: Whether to automatically deploy the SAM project (implies auto_build)
            
        Returns:
            str: Path to the generated template file
            
        Example:
            ```python
            agent = Agent(
                name="MyAgent",
                model="anthropic.claude-3-sonnet-20240229-v1:0",
                instructions="You are a helpful assistant",
                functions={
                    "TimeActions": [get_time, get_date],
                    "MathActions": [add_numbers]
                }
            )
            
            # Generate the SAM template and supporting files
            template_path = agent.deploy(
                output_dir="./my_agent_deployment",
                description="My awesome agent deployment"
            )
            
            print(f"SAM template generated at: {template_path}")
            print("To deploy, run:")
            print("  cd my_agent_deployment")
            print("  sam build")
            print("  sam deploy --guided")
            ```
        """
        # Create the SAM template generator
        generator = SAMTemplateGenerator(
            agent=self,
            output_dir=output_dir
        )
        
        # Generate the SAM template and supporting files
        template_path = generator.generate(
            foundation_model=foundation_model,
            parameters=parameters,
            description=description
        )
        
        # Print success message
        print(f"\n✅ SAM template generated successfully at: {template_path}")
        print(f"📁 Deployment files created in: {os.path.abspath(output_dir)}")
        print("\n📋 To deploy manually:")
        print(f"  cd {os.path.abspath(output_dir)}")
        print("  sam build")
        print("  sam deploy --guided --capabilities CAPABILITY_NAMED_IAM")
        
        # Automatically build the SAM project if requested
        if auto_build or auto_deploy:
            import subprocess
            import sys
            
            print("\n🔨 Building SAM project...")
            
            # Change to the output directory
            original_dir = os.getcwd()
            os.chdir(output_dir)
            
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
                    
                    # Run sam deploy
                    deploy_result = subprocess.run(
                        ["sam", "deploy", "--guided", "--capabilities", "CAPABILITY_NAMED_IAM"],
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
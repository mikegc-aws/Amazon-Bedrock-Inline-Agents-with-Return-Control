# Comprehensive AWS Development Environment Setup Guide for Python Bedrock Projects

## Table of Contents
- [Introduction](#introduction)
- [Creating an AWS Account](#creating-an-aws-account)
- [Setting Up IAM Users and Permissions for Bedrock](#setting-up-iam-users-and-permissions-for-bedrock)
- [AWS CLI Installation and Configuration](#aws-cli-installation-and-configuration)
- [Python and Boto3 Setup](#python-and-boto3-setup)
- [Environment Variables and Credential Management](#environment-variables-and-credential-management)
- [AWS Profiles for Multiple Environments](#aws-profiles-for-multiple-environments)
- [AWS CloudShell for Python Development](#aws-cloudshell-for-python-development)
- [Local Development with Amazon Bedrock](#local-development-with-amazon-bedrock)
- [Best Practices for Security](#best-practices-for-security)
- [Troubleshooting Common Issues](#troubleshooting-common-issues)
- [Additional Resources](#additional-resources)

## Introduction

This guide provides comprehensive instructions for setting up an AWS development environment for Python projects using Amazon Bedrock. From creating an account to configuring your local machine, following these steps will ensure you have everything needed to start developing applications that leverage AWS's generative AI capabilities.

## Creating an AWS Account

### Step 1: Sign up for an AWS Account

1. Visit the [AWS homepage](https://aws.amazon.com/).
2. Click on "Create an AWS Account" button in the top-right corner.
3. Enter your email address and choose an AWS account name.
4. Click "Verify email address" and follow the verification process.
5. Follow the process step by step.

### Step 2: Complete Account Setup

1. After completing the above steps, you'll receive a confirmation email.
2. You can now sign in to the [AWS Management Console](https://console.aws.amazon.com/).

## Setting Up IAM Users and Permissions for Bedrock

It's a best practice to avoid using your root account for everyday tasks. Instead, create an IAM user with appropriate permissions for Amazon Bedrock.

### Step 1: Create an IAM User

1. Sign in to the [AWS Management Console](https://console.aws.amazon.com/) with your root account.
2. Search for "IAM" in the services search bar and select it.
3. In the navigation pane, choose "Users" and then "Add users".
4. Enter a username for your new IAM user (e.g., "bedrock-developer").
5. Select "Access key - Programmatic access" for AWS CLI, SDK, & API access.
6. Select "Password - AWS Management Console access" if you want this user to access the console.
7. Click "Next: Permissions".

### Step 2: Set Permissions for Bedrock

#### Option 1: Add user to a group with Bedrock permissions (Recommended)

1. Click "Create group".
2. Name your group (e.g., "BedrockDevelopers").
3. Search for and select the following policies:
   - `AmazonBedrockFullAccess` - Provides full access to Amazon Bedrock
   - `AmazonS3ReadOnlyAccess` - For accessing model artifacts and data
   - `CloudWatchLogsReadOnlyAccess` - For monitoring and debugging

   If these exact policies don't exist, search for similar ones containing "Bedrock" or create custom policies.

4. Click "Create group".
5. Select the newly created group.
6. Click "Next: Tags".

#### Option 2: Use PowerUserAccess with Bedrock permissions

1. Click "Create group".
2. Name your group (e.g., "BedrockPowerUsers").
3. Search for and select the following policies:
   - `PowerUserAccess` - Provides broad permissions but not full administrative access
   - `AmazonBedrockFullAccess` - Ensures specific access to Bedrock services
4. Click "Create group".
5. Select the newly created group.
6. Click "Next: Tags".

#### Option 3: Create a custom Bedrock policy

If you need more fine-grained control, create a custom policy:

1. In the IAM console, go to "Policies" and click "Create policy".
2. Use the JSON editor and paste the following policy:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:*"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::your-project-bucket",
                "arn:aws:s3:::your-project-bucket/*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents",
                "logs:DescribeLogStreams"
            ],
            "Resource": "arn:aws:logs:*:*:*"
        }
    ]
}
```

3. Name the policy (e.g., "BedrockDeveloperPolicy") and create it.
4. Attach this policy to your user or group.

### Step 3: Add Tags (Optional)

1. Add key-value pairs as tags to help organize and identify your IAM user.
   - For example: Key = "Project", Value = "BedrockDevelopment"
2. Click "Next: Review".

### Step 4: Review and Create

1. Review all the information.
2. Click "Create user".

### Step 5: Save Credentials

1. Download the .csv file containing the access key ID and secret access key.
   - **IMPORTANT**: This is the only time you can view or download the secret access key.
   - Store these credentials securely.
2. Click "Close".

## AWS CLI Installation and Configuration

The AWS Command Line Interface (CLI) allows you to interact with AWS services from your terminal.

### Installing AWS CLI

#### For macOS

**Option 1: Using Homebrew**
```bash
brew install awscli
```

**Option 2: Using the installer**
1. Download the macOS pkg file from the [AWS CLI download page](https://aws.amazon.com/cli/).
2. Run the downloaded installer and follow the instructions.

#### For Windows

**Option 1: Using the MSI installer**
1. Download the Windows MSI installer from the [AWS CLI download page](https://aws.amazon.com/cli/).
2. Run the downloaded MSI file and follow the installation wizard.

**Option 2: Using Chocolatey**
```bash
choco install awscli
```

#### For Linux

**Debian/Ubuntu**
```bash
sudo apt-get update
sudo apt-get install awscli
```

**Amazon Linux/RHEL/CentOS**
```bash
sudo yum install awscli
```

**Using pip (all platforms)**
```bash
pip install awscli
```

### Verifying Installation

Verify the installation by running:
```bash
aws --version
```

### Configuring AWS CLI

#### Method 1: Using `aws configure`

1. Open your terminal or command prompt.
2. Run:
   ```bash
   aws configure
   ```
3. Enter the following information when prompted:
   - AWS Access Key ID: [Your access key from IAM user creation]
   - AWS Secret Access Key: [Your secret key from IAM user creation]
   - Default region name: [Your preferred AWS region, e.g., us-east-1]
     - **Note**: Amazon Bedrock is not available in all regions. Check the [Bedrock documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html) for supported regions.
   - Default output format: [json, text, or table; json is recommended]

#### Method 2: Manually editing configuration files

1. Create or edit `~/.aws/credentials` (Linux/macOS) or `C:\Users\USERNAME\.aws\credentials` (Windows):
   ```
   [default]
   aws_access_key_id = YOUR_ACCESS_KEY
   aws_secret_access_key = YOUR_SECRET_KEY
   ```

2. Create or edit `~/.aws/config` (Linux/macOS) or `C:\Users\USERNAME\.aws\config` (Windows):
   ```
   [default]
   region = us-east-1
   output = json
   ```

### Testing the Configuration

Test your configuration by checking if you can access Bedrock:
```bash
aws bedrock list-foundation-models
```
This should return a list of available foundation models in Bedrock.

## Python and Boto3 Setup

### Setting Up Python Environment

1. Install Python (if not already installed):
   - Download from [python.org](https://www.python.org/downloads/) (Python 3.8 or newer recommended)
   - Or use a package manager:
     - macOS: `brew install python`
     - Ubuntu: `sudo apt-get install python3 python3-pip`

2. Create a virtual environment for your project:
   ```bash
   # Navigate to your project directory
   cd your-project-directory
   
   # Create a virtual environment
   python -m venv venv
   
   # Activate the virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

### Installing Boto3 and Bedrock SDK

1. With your virtual environment activated, install Boto3:
   ```bash
   pip install boto3
   ```

2. Install the AWS SDK for Bedrock:
   ```bash
   pip install boto3 botocore
   ```

3. Create a requirements.txt file for your project:
   ```bash
   echo "boto3>=1.28.0" > requirements.txt
   echo "botocore>=1.31.0" >> requirements.txt
   ```

### Example: Using Boto3 with Amazon Bedrock

Create a file named `bedrock_example.py` with the following content:

```python
import boto3
import json

# Initialize the Bedrock client
bedrock = boto3.client(
    service_name='bedrock-runtime',
    region_name='us-east-1'  # Use the region where Bedrock is available
)

# List available foundation models
def list_models():
    bedrock_client = boto3.client(service_name='bedrock')
    response = bedrock_client.list_foundation_models()
    
    print("Available Foundation Models:")
    for model in response['modelSummaries']:
        print(f"- {model['modelId']}: {model.get('modelName', 'N/A')}")

# Generate text using Claude model
def generate_text(prompt):
    model_id = "anthropic.claude-v2"  # Use the appropriate model ID
    
    body = json.dumps({
        "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
        "max_tokens_to_sample": 500,
        "temperature": 0.7,
        "top_p": 0.9,
    })
    
    response = bedrock.invoke_model(
        modelId=model_id,
        body=body
    )
    
    response_body = json.loads(response.get('body').read())
    return response_body.get('completion')

if __name__ == "__main__":
    # List available models
    list_models()
    
    # Generate text
    prompt = "Explain how to use Amazon Bedrock with Python in 3 steps"
    generated_text = generate_text(prompt)
    print("\nGenerated Text:")
    print(generated_text)
```

Run the example:
```bash
python bedrock_example.py
```

## Environment Variables and Credential Management

### Using Environment Variables

You can set AWS credentials using environment variables, which is useful for temporary sessions or CI/CD pipelines.

#### For Linux/macOS:

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1  # Use a region where Bedrock is available
```

#### For Windows (Command Prompt):

```cmd
set AWS_ACCESS_KEY_ID=your_access_key
set AWS_SECRET_ACCESS_KEY=your_secret_key
set AWS_DEFAULT_REGION=us-east-1
```

#### For Windows (PowerShell):

```powershell
$env:AWS_ACCESS_KEY_ID="your_access_key"
$env:AWS_SECRET_ACCESS_KEY="your_secret_key"
$env:AWS_DEFAULT_REGION="us-east-1"
```

### Using Credential Providers

Boto3 uses a provider chain to look for credentials in the following order:

1. Environment variables
2. Shared credentials file (~/.aws/credentials)
3. IAM roles for Amazon EC2 (if running on EC2)
4. Container credentials (if using ECS)
5. SSO credentials

### Using AWS Secrets Manager for Sensitive Data

For sensitive configuration data, consider using AWS Secrets Manager:

```python
import boto3
import json
from botocore.exceptions import ClientError

def get_secret(secret_name, region_name="us-east-1"):
    """Retrieve a secret from AWS Secrets Manager"""
    
    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        raise e
    else:
        # Depending on whether the secret is a string or binary, one of these fields will be populated
        if 'SecretString' in get_secret_value_response:
            return json.loads(get_secret_value_response['SecretString'])
        else:
            return get_secret_value_response['SecretBinary']

# Example usage
try:
    # Get API keys or other sensitive data
    secret = get_secret("bedrock/api_keys")
    print(f"Retrieved secret: {secret['api_key_name']}")
except Exception as e:
    print(f"Error retrieving secret: {e}")
```

## AWS Profiles for Multiple Environments

If you work with multiple AWS accounts or environments, you can use named profiles.

### Creating Named Profiles

#### Using AWS CLI

```bash
aws configure --profile bedrock-dev
aws configure --profile bedrock-prod
```

#### Manually editing configuration files

1. Edit `~/.aws/credentials`:
   ```
   [default]
   aws_access_key_id = DEFAULT_ACCESS_KEY
   aws_secret_access_key = DEFAULT_SECRET_KEY
   
   [bedrock-dev]
   aws_access_key_id = DEV_ACCESS_KEY
   aws_secret_access_key = DEV_SECRET_KEY
   
   [bedrock-prod]
   aws_access_key_id = PROD_ACCESS_KEY
   aws_secret_access_key = PROD_SECRET_KEY
   ```

2. Edit `~/.aws/config`:
   ```
   [default]
   region = us-east-1
   output = json
   
   [profile bedrock-dev]
   region = us-east-1
   output = json
   
   [profile bedrock-prod]
   region = us-west-2
   output = json
   ```

### Using Named Profiles with Boto3

```python
import boto3

# Create a session with the bedrock-dev profile
session = boto3.Session(profile_name='bedrock-dev')

# Use the session to get the Bedrock client
bedrock_client = session.client(service_name='bedrock')

# List available foundation models
response = bedrock_client.list_foundation_models()
print("Available Foundation Models:")
for model in response['modelSummaries']:
    print(f"- {model['modelId']}")
```

## AWS CloudShell for Python Development

AWS CloudShell provides a browser-based shell with AWS CLI and Python pre-installed and authenticated with your console credentials.

### Accessing CloudShell

1. Sign in to the [AWS Management Console](https://console.aws.amazon.com/).
2. Click the CloudShell icon in the navigation bar at the top of the console.
3. Wait for CloudShell to initialize.

### Setting Up Python Environment in CloudShell

1. Create a virtual environment:
   ```bash
   python -m venv bedrock-env
   source bedrock-env/bin/activate
   ```

2. Install Boto3 and other dependencies:
   ```bash
   pip install boto3 botocore
   ```

3. Create a Python script for Bedrock:
   ```bash
   cat > bedrock_test.py << 'EOL'
   import boto3
   
   # Create a Bedrock client
   bedrock_client = boto3.client(service_name='bedrock')
   
   # List available foundation models
   response = bedrock_client.list_foundation_models()
   
   print("Available Foundation Models:")
   for model in response['modelSummaries']:
       print(f"- {model['modelId']}: {model.get('modelName', 'N/A')}")
   EOL
   ```

4. Run the script:
   ```bash
   python bedrock_test.py
   ```

### CloudShell Advantages for Bedrock Development

- Pre-authenticated with your current console session
- No need to manage credentials locally
- Python and AWS CLI pre-installed
- 1GB persistent storage for your scripts
- Ability to upload/download files for testing

## Local Development with Amazon Bedrock

### Setting Up a Bedrock Project

1. Create a project directory:
   ```bash
   mkdir bedrock-project
   cd bedrock-project
   ```

2. Initialize a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Create a requirements.txt file:
   ```
   boto3>=1.28.0
   botocore>=1.31.0
   python-dotenv>=1.0.0
   ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Create a .env file for environment variables:
   ```
   AWS_PROFILE=bedrock-dev
   AWS_REGION=us-east-1
   ```

6. Create a Python module for Bedrock interactions:

```python
# bedrock_client.py
import os
import boto3
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class BedrockClient:
    def __init__(self, profile_name=None, region_name=None):
        """Initialize the Bedrock client"""
        # Use environment variables or parameters
        profile_name = profile_name or os.getenv('AWS_PROFILE')
        region_name = region_name or os.getenv('AWS_REGION', 'us-east-1')
        
        # Create a session
        if profile_name:
            session = boto3.Session(profile_name=profile_name)
        else:
            session = boto3.Session()
        
        # Create clients
        self.bedrock = session.client(service_name='bedrock', region_name=region_name)
        self.runtime = session.client(service_name='bedrock-runtime', region_name=region_name)
    
    def list_models(self):
        """List available foundation models"""
        response = self.bedrock.list_foundation_models()
        return response['modelSummaries']
    
    def generate_text(self, prompt, model_id="anthropic.claude-v2", max_tokens=500):
        """Generate text using a specified model"""
        body = json.dumps({
            "prompt": f"\n\nHuman: {prompt}\n\nAssistant:",
            "max_tokens_to_sample": max_tokens,
            "temperature": 0.7,
            "top_p": 0.9,
        })
        
        response = self.runtime.invoke_model(
            modelId=model_id,
            body=body
        )
        
        response_body = json.loads(response.get('body').read())
        return response_body.get('completion')

# Example usage
if __name__ == "__main__":
    client = BedrockClient()
    
    # List models
    models = client.list_models()
    print("Available models:")
    for model in models:
        print(f"- {model['modelId']}")
    
    # Generate text
    response = client.generate_text("Explain how to use Amazon Bedrock with Python")
    print("\nGenerated response:")
    print(response)
```

7. Create a main application file:

```python
# app.py
from bedrock_client import BedrockClient

def main():
    # Initialize the client
    client = BedrockClient()
    
    # Get user input
    prompt = input("Enter your prompt for Bedrock: ")
    
    # Generate response
    print("Generating response...")
    response = client.generate_text(prompt)
    
    # Display response
    print("\nBedrock response:")
    print(response)

if __name__ == "__main__":
    main()
```

8. Run the application:
   ```bash
   python app.py
   ```

## Best Practices for Security

### Secure Credential Management

1. **Never commit credentials to source control**:
   - Use `.gitignore` to exclude credential files and .env files
   - Add the following to your .gitignore:
     ```
     .env
     .aws/
     venv/
     __pycache__/
     *.pyc
     ```
   - Consider using tools like git-secrets to prevent accidental commits

2. **Rotate access keys regularly**:
   - Create new access keys before disabling old ones
   - Update all applications with new keys
   - Disable and then delete old access keys

3. **Use IAM roles instead of access keys when possible**:
   - For EC2 instances, use IAM roles
   - For Lambda functions, use execution roles
   - For ECS tasks, use task roles

### Principle of Least Privilege for Bedrock

1. Create a custom policy that grants only the permissions needed for Bedrock:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "bedrock:ListFoundationModels",
                   "bedrock:GetFoundationModel",
                   "bedrock-runtime:InvokeModel"
               ],
               "Resource": "*"
           }
       ]
   }
   ```

2. Regularly audit and remove unused permissions
3. Use permission boundaries to limit maximum permissions

### Multi-Factor Authentication (MFA)

1. Enable MFA for your root account:
   - Sign in to the AWS Management Console
   - Click on your account name and select "My Security Credentials"
   - Expand "Multi-factor authentication (MFA)"
   - Click "Assign MFA device" and follow the instructions

2. Enable MFA for IAM users:
   - In the IAM console, select the user
   - Select the "Security credentials" tab
   - Click "Manage" next to "Assigned MFA device"
   - Follow the instructions to assign an MFA device

### Using AWS Vault for Credential Management

[AWS Vault](https://github.com/99designs/aws-vault) is a tool to securely store and access AWS credentials in a development environment.

1. Install AWS Vault:
   - macOS: `brew install aws-vault`
   - Windows: Download from [releases page](https://github.com/99designs/aws-vault/releases)
   - Linux: Follow instructions on GitHub

2. Add credentials:
   ```bash
   aws-vault add bedrock-dev
   ```

3. Execute Python scripts with AWS Vault:
   ```bash
   aws-vault exec bedrock-dev -- python bedrock_example.py
   ```

## Troubleshooting Common Issues

### "Unable to locate credentials" Error

**Possible causes and solutions:**

1. **Credentials not configured**:
   - Run `aws configure` to set up credentials

2. **Incorrect profile specified**:
   - Check if you're using the correct profile in your Boto3 session
   - Verify profile exists in `~/.aws/credentials`

3. **Environment variables overriding configuration**:
   - Check if `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set
   - Unset them if needed: `unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY`

### "Access Denied" Errors with Bedrock

**Possible causes and solutions:**

1. **Insufficient permissions**:
   - Ensure your IAM user has the necessary Bedrock permissions
   - Add the `AmazonBedrockFullAccess` policy or a custom policy with required permissions

2. **Bedrock service not enabled**:
   - Go to the [Amazon Bedrock console](https://console.aws.amazon.com/bedrock/)
   - Follow prompts to enable the service if needed
   - Request access to specific models through the console

3. **Region issues**:
   - Ensure you're using a region where Bedrock is available
   - Check the [Bedrock documentation](https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html) for supported regions

### Model Access Issues

**Possible causes and solutions:**

1. **Model not accessible**:
   - In the Bedrock console, go to "Model access"
   - Request access to the models you need
   - Wait for access to be granted

2. **Incorrect model ID**:
   - Verify the model ID using `list_foundation_models()`
   - Use the exact model ID returned by the API

### Connection Issues

**Possible causes and solutions:**

1. **Network connectivity problems**:
   - Check your internet connection
   - Verify proxy settings if applicable

2. **VPC endpoint configuration**:
   - If using VPC endpoints, check their configuration

3. **Firewall blocking AWS API calls**:
   - Check firewall rules
   - Ensure outbound connections to AWS endpoints are allowed

## Additional Resources

### Official AWS Documentation

- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)

### Learning Resources

- [AWS Skill Builder - Amazon Bedrock Courses](https://explore.skillbuilder.aws/learn/course/external/view/elearning/17508/amazon-bedrock-getting-started)
- [AWS Workshops - Generative AI](https://workshops.aws/categories/Generative+AI)
- [AWS GitHub - Bedrock Examples](https://github.com/aws-samples/amazon-bedrock-samples)
- [AWS Blog - Bedrock Articles](https://aws.amazon.com/blogs/machine-learning/category/artificial-intelligence/amazon-bedrock/)

### Community Resources

- [AWS re:Post - Bedrock Topics](https://repost.aws/topics/TAGpVqJcZOUyQnvDZYTvtjMA/amazon-bedrock)
- [AWS Python SDK GitHub](https://github.com/boto/boto3)
- [AWS Community Builders](https://aws.amazon.com/developer/community/community-builders/)

### Tools and Utilities

- [AWS CloudShell](https://aws.amazon.com/cloudshell/)
- [AWS Cloud9](https://aws.amazon.com/cloud9/) - Cloud-based IDE
- [AWS Pricing Calculator](https://calculator.aws/) - Estimate AWS costs including Bedrock usage

---

This guide covers the essential steps to set up an AWS development environment for Python projects using Amazon Bedrock. As AWS services evolve, always refer to the official AWS documentation for the most up-to-date information. If you encounter issues not covered in this guide, AWS re:Post and the AWS Support Center are excellent resources for troubleshooting. 
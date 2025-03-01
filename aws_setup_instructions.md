# Setting Up AWS Credentials

Before deploying your agent to AWS, you need to configure your AWS credentials. Here are several ways to do this:

## Option 1: Using the AWS CLI

1. Install the AWS CLI if you haven't already:
   ```bash
   pip install awscli
   ```

2. Configure your credentials:
   ```bash
   aws configure
   ```

   You'll be prompted to enter:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region name (e.g., us-east-1)
   - Default output format (json is recommended)

## Option 2: Environment Variables

Set the following environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1
```

## Option 3: Shared Credentials File

Create or edit the file `~/.aws/credentials`:

```ini
[default]
aws_access_key_id = your_access_key
aws_secret_access_key = your_secret_key

[profile_name]
aws_access_key_id = your_access_key
aws_secret_access_key = your_secret_key
```

And create or edit the file `~/.aws/config`:

```ini
[default]
region = us-east-1

[profile profile_name]
region = us-east-1
```

## Getting AWS Credentials

If you don't have AWS credentials yet:

1. Sign in to the AWS Management Console
2. Go to IAM (Identity and Access Management)
3. Create a new user or use an existing one
4. Attach the following policies to the user:
   - AmazonBedrockFullAccess
   - AmazonS3FullAccess
   - AWSCloudFormationFullAccess
   - AWSLambdaFullAccess
   - IAMFullAccess (or more restricted policy that allows creating roles)
5. Create an access key for the user
6. Save the Access Key ID and Secret Access Key

## Testing Your Credentials

After setting up your credentials, you can test them with:

```bash
aws sts get-caller-identity
```

If successful, it will display your AWS account ID, user ID, and ARN. 
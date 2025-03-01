# Enabling Access to Foundation Models in Amazon Bedrock

This guide explains how to enable access to foundation models in Amazon Bedrock through the AWS Management Console.

## Prerequisites
- AWS account
- IAM permissions for Amazon Bedrock

## Setting Up IAM Permissions

1. Sign in to the AWS Management Console
2. Create an IAM role with the `AmazonBedrockFullAccess` managed policy
3. Create and attach this additional policy to manage model access:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "aws-marketplace:ViewSubscriptions",
                "aws-marketplace:Unsubscribe",
                "aws-marketplace:Subscribe"
            ],
            "Resource": "*"
        }
    ]
}
```

## Enabling Access to Foundation Models

1. Open the Amazon Bedrock console: [https://console.aws.amazon.com/bedrock/](https://console.aws.amazon.com/bedrock/)
2. Select **Model access** from the left navigation pane
3. Choose **Modify model access**
4. Select the models you want to access:
   - To enable all models, choose **Enable all models**
   - To enable specific models, select the checkboxes next to the desired models
5. Review and accept the Terms
6. Choose **Submit** to request access
7. Wait for access to be granted (status will change to **Access granted**)

## Important Notes

- Not all the models are enabled for use with Amazon Bedrock Agents
- Once access is granted to a model, it is available for all users in the AWS account
- For some models, you may need to provide use case details when requesting access
- Model access status can be verified on the **Model access** page

## Additional Resources
- [Amazon Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Amazon Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/) 
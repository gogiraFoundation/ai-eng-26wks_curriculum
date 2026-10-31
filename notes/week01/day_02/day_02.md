Day 02:  AWS account hygiene: budget alarm, Identity Center user, least privilege


What is IAM?
    IAM is a web service that allows you to securely allocate acvcess to resources, manage platform integrity and secuity. In AWS, you can manage users via the IAM Center and allocate shared recources and access by tying each users to their specific group and then creating a policy for that group..





Budget Alarm:

    You can customise and manage budget notifications using budget manager to set diffrent financial threshold and alerts. 



Security Best Practice:






Bedrock Policy:
    An Amazon Bedrock policy is a JSON config file used within AWS to define exactly who can access your Generative AI models and what they are allowed to do with them.

    Depeneding on its application - Bedrock policay can be 


        1. Identity-Based Permissions (IAM Policies)

           This is the most common usage of the policy, it is aattach to groups, roles, users to give developer permission to use bedrock.

           it divides access into three main operational tiers:
           
           Inference (Using Models): Controls who can send prompts to models and receive answers.
           
                Actions: bedrock:InvokeModel and  bedrock:InvokeModelWithResponseStream.
           
           Discovery (Reading Metadata): Allows a developer or system to see what models are available in that AWS region.
           
                Actions: bedrock:ListFoundationModels and bedrock:GetFoundationModel.
                
            Administrative & Customization (High Risk): Controls who can create custom fine-tuned models, manage knowledge bases (RAG), or set up AI Agents.
                
                Actions: bedrock:CreateModelCustomizationJob, bedrock:CreateAgent

    2. Organization-Wide Governance (AWS Organization)

        An amazon bedrock policy can also be deployed as a corporate guardrail against multiple accounts. 

        Managed via AWS Organizations, these centralized JSON policies allow companies to enforce Amazon Bedrock Guardrails automatically across entire business units or sub-accounts. For instance, a central security team can use one policy to ensure all model responses across the entire company block PII leakage or toxic content, eliminating the need to configure guardrails manually on every single application


Why Bedrock policies ?

    Cost Management: AI models charge per token. A strict policy restricts expensive model usage (like Claude 3.5 Sonnet or Ultra models) to specific applications, preventing accidental massive bills.
    
    Data Security: It keeps data boundaries clear by ensuring only authorized applications can access proprietary vector databases (Knowledge Bases) or custom-trained corporate models.
    
    Least Privilege: Following security best practices, a production app should only have permission to invoke a model, never to modify or delete model configurations.

    







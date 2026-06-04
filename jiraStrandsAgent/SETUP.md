## Create the gateway

Create a gateway to jira for local testing. Let's note that a production setup should have some type of authorizer!!!

    agentcore add gateway   --name JiraGateway   --authorizer-type AWS_IAM --runtimes JiraStrandsAgent
	
	
## Add credential-name

Note: secrets can be found in agentcore/.env. Useful if you did need to recreate resources and didn't save the variables.

agentcore add credential --name JiraAuth --type oauth --client-id "$env:CLIENT_ID" --client-secret "$env:CLIENT_SECRET" --discovery-url https://auth.atlassian.com/.well-known/openid-configuration --scopes "read:account,read:jira-user,read:jira-work,read:me"
	
## Add jira target

	agentcore add gateway-target --gateway JiraGateway --name JiraCloud --type open-api-schema --schema swagger-v3.v3.json --outbound-auth oauth --credential-name "JiraAuth" --oauth-client-id "$env:CLIENT_ID" --oauth-client-secret "$env:CLIENT_SECRET" --oauth-discovery-url https://auth.atlassian.com/.well-known/openid-configuration --oauth-scopes "read:account,read:jira-user,read:jira-work,read:me"
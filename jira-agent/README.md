# README

This folder is the exercise of workshop: https://builder.aws.com/content/38oLfyfksQOGKf9TxnJSAEIOVeB/building-agentic-demo-apps-with-strands-agents

## Prerequisite

### AWS Session

Have your AWS Env variables set

### JIRA token set

Generate your Jira API Token: 

- Go to your Atlassian Profile Settings 
→ Security 
→ API Tokens and generate a new token.

Identify Required Variables: The server will require access to:

    JIRA_BASE_URL (e.g., https://your-domain.atlassian.net)
    JIRA_USER_EMAIL (your registered login email)
    JIRA_API_TOKEN (the token you generated)
	
	
In linux you can save the variables in your bashrc

	# Append the Jira environment variables to your .bashrc
	echo 'export JIRA_BASE_URL="https://domain.atlassian.net/"' >> ~/.bashrc
	echo 'export JIRA_USER_EMAIL="email@email.com"' >> ~/.bashrc
	echo 'export JIRA_API_TOKEN="yourtoken"' >> ~/.bashrc

	# Reload your configuration immediately without restarting the terminal
	source ~/.bashrc

## Prompt using the cli

In your linux terminal

    python3 cli.py --prompt "what is the cosine of 1.4 radius"
	
Answer:

    Tool #1: cosine
    The cosine of 1.4 radians is approximately **0.17**
	
## Start cli chat

     python3 cli_chat.py
	 
Exemple:

     🤖Bot:
     Welcome! Type your message below and hit return to send.
     Type "exit", "quit", "done", "bye" or press Ctrl-C to exit.


     🙂Me:
     Hi, what's up?

     🤖Bot:
     Hello! I'm here to help with any questions or tasks you have. What’s on your mind? 😊

     🙂Me:
     exit
	
## Start Streamlit

    streamlit run ui_demo_app.py
# README

This folder is the exercise of workshop: https://builder.aws.com/content/38oLfyfksQOGKf9TxnJSAEIOVeB/building-agentic-demo-apps-with-strands-agents

## Prerequisite

Have your AWS Env variables set

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
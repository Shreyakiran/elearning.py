#import required tools
import ollama
#define your system prompt
SYSTEM_PROMPT = """
Tell me a story
instructions :
1. keep story funny
2. keep the story not more than 2 paragraphs
"""
#conversation list
chat_convo = []
#conversation loop
def chat_with_ollama():
    print("welcome to storyline")

    while True:
        try:
            user_input = input("User :").strip()
        except (keyboardInterrupt, e):
            print('User quit')

        chat_convo.append( {
            'role': 'user',
            "content": user_input
        }) 

        try:
            print('chatbot prompt started')  
            response = ollama.chat(model="phi3:mini",messages=chat_convo,options={"system":SYSTEM_PROMPT})
            chat_convo.append({
            'role': 'bot',
            "content": response    
            })    

            print(response)
        except:print("Error") 
        chat_with_ollama()    
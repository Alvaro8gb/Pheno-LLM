from models import Dialog
from openai import OpenAI
import time

class ClientLLM:
    def __init__(self, model, api_key, api_base, temperature=0.5):
        self.client = OpenAI(api_key=api_key, base_url=api_base)
        self.temperature = temperature
        self.model = model 
        self.max_tokens = 2000

    def ask_simple(self, msg_input:str):
        return self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": msg_input}],
            max_tokens=self.max_tokens,
            temperature= self.temperature
        )
    
    def ask_complete(self, prompt:Dialog, max_tokens:int=None):

        if max_tokens != None:
            maxi = max_tokens
        else:
            maxi = self.max_tokens

        return self.client.chat.completions.create(
            model=self.model,
            messages=prompt,
            max_tokens=maxi,
            temperature= self.temperature

        )

# Example usage
if __name__ == "__main__":

    api_key = "FALSE"  
    api_base = "http://localhost:8000/v1"
    model = "BioMistral/BioMistral-7B" #meta-llama/Llama-2-7b-chat-hf" #"mistralai/Mistral-7B-Instruct-v0.2"

    chat_instance = ClientLLM(model=model, api_key=api_key, api_base=api_base)

    user_input = input("You: ")

    chat_response = chat_instance.get_chat_response(user_input)
    print("Chat response:", chat_response.choices[0].message.content)
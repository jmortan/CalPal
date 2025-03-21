import json 
from openai import OpenAI

class OpenAiClient():
    def __init__(self):
        f = open('./state_data/open_ai_token.json')
        api_token = json.load(f)['goal_requestor_token']
        self.client = OpenAI(api_key=api_token)

    
    def get_client(self):
        return self.client
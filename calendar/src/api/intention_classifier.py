import json
from openai import OpenAI
from speech_to_text import SpeechToTextModule


class IntentionClassifierModule():
    def __init__(self):
        f = open('./state_data/open_ai_token.json')
        self.api_token = json.load(f)['goal_requestor_token']
        self.client = OpenAI(api_key=self.api_token) 
    
    def classify_intentions(self, user_message):
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": [
                    {
                        "type": "text",
                        "text": "You are a master at deducing a user's intentions. You will receive a message from the user and your job is to figure out whether or not the user is stating a goal they would like to achieve. "
                    }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                    {
                        "type": "text",
                        "text": user_message
                    }
                    ]
                },
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "goal_recognition",
                    "strict": True,
                    "schema": {
                    "type": "object",
                    "properties": {
                        "is_goal": {
                        "type": "boolean",
                        "description": "Indicates if the user message is recognized as a goal."
                        }
                    },
                    "required": [
                        "is_goal"
                    ],
                    "additionalProperties": False
                    }
                }
            },
            temperature=0.2,
            max_completion_tokens=1000,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            store=False
        )
        return response.choices[0].message
    
    def main(self):
        audio_filename = "./state_data/recorded_audio.wav"
        speechRecognitionModule = SpeechToTextModule()
        speechRecognitionModule.record_audio(audio_filename, 10)
        text = speechRecognitionModule.speech_to_text(audio_filename)
        print(text)
        intentions = self.classify_intentions(text)
        print(intentions)
        

if __name__ == "__main__":
    module = IntentionClassifierModule()
    module.main()
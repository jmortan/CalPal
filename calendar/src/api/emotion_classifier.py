import json
from openai import OpenAI
from open_ai_client import OpenAiClient


class IntentionClassifierModule():
    def __init__(self, client):
        self.client = client
    
    def classify_emotion(self, user_message):
        response = self.client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
            "role": "system",
            "content": [
                {
                "type": "text",
                "text": "Given the following user input, classify their current emotional state into one of three categories: (1) Low energy / discouraged, (2) Unfocused / stagnant, or (3) Nostalgic / introspective. Consider their tone, word choice, and emotional cues. Return only the category that best matches their state."
                }
            ]
            }
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
            "name": "emotional_state_classification",
            "strict": True,
            "schema": {
                "type": "object",
                "properties": {
                "user_input": {
                    "type": "string",
                    "description": "The user's input that needs to be analyzed for emotional content."
                },
                "classified_emotion": {
                    "type": "string",
                    "description": "The category that best matches the user's emotional state.",
                    "enum": [
                    "Discouraged",
                    "Unfocused",
                    "Nostalgic"
                    ]
                }
                },
                "required": [
                "user_input",
                "classified_emotion"
                ],
                "additionalProperties": False
            }
            }
        },
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        store=False
        )
        
        
        return response.choices[0].message
        

if __name__ == "__main__":
    pass
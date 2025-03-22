import requests
import json
import numpy as np
import cv2
import time
import base64
from openai import OpenAI
class GenerativeThemingModule():
    def __init__(self):
        # f = open('./state_data/api_token.json')
        # API_TOKEN = json.load(f)['token']
        # self.API_URL = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
        # print(API_TOKEN)
        # self.headers = {"Authorization": f"Bearer {API_TOKEN}"}
        f = open('./state_data/open_ai_token.json')
        self.api_token = json.load(f)['goal_requestor_token']
        self.client = OpenAI(api_key=self.api_token) 


    def query(self, prompt):
        response = self.client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            response_format="b64_json",
            n=1,
        )
        return response.data[0].b64_json

    def generate_theme(self, prompt):
        images = self.query(prompt)
        image_bytes = base64.b64decode(images)  # Decode to bytes
        nparr = np.frombuffer(image_bytes, np.uint8)
        print(len(nparr))
        if len(nparr) == 0: 
            raise Exception("Issue generating stable diffusion") 
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cv2.imwrite(f"testing_.png", img)
        resized = cv2.resize(img,(301,172))
        mirrored = cv2.hconcat([resized, cv2.flip(resized.copy(), 1)])
        imgBytes = cv2.imencode(".png", mirrored)[1]
        return imgBytes.tobytes()
    
    def main(self):
        image_bytes = self.generate_theme("Devin and Jenny coding")
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cv2.imwrite("./state_data/test.png", img)

if __name__ == "__main__":
    module = GenerativeThemingModule()
    module.main()
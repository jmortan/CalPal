import requests
import json
import numpy as np
import cv2
import time
class GenerativeThemingModule():
    def __init__(self):
        f = open('./state_data/api_token.json')
        API_TOKEN = json.load(f)['token']
        self.API_URL = "https://api-inference.huggingface.co/models/CompVis/stable-diffusion-v1-4"
        print(API_TOKEN)
        self.headers = {"Authorization": f"Bearer {API_TOKEN}"}

    def query(self, payload):
        response = requests.post(self.API_URL, headers=self.headers, json=payload)
        print(response.status_code)
        return response.content, response.status_code

    def generate_theme(self, prompt):
        image_bytes, resp = self.query({
                "inputs": prompt, 
            })
        while resp!= 200:
            time.sleep(10)
            image_bytes, resp = self.query({
                "inputs": prompt, 
            })  
        nparr = np.frombuffer(image_bytes, np.uint8)
        print(len(nparr))
        if len(nparr) == 0: 
            raise Exception("Issue generating stable diffusion") 
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        cv2.imwrite("testing.png", img)
        resized = cv2.resize(img,(172,172))
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
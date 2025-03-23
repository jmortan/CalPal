import base64
import cv2
import numpy as np
import pickle
import os.path

from cal_data import CalData
from google.cloud import vision
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

from pydub import AudioSegment

def get_data(filepath, calendar_id):
    calData = None
    if os.path.exists(filepath):
        with open(filepath, 'rb') as inp:
           calData = pickle.load(inp)

    if not calData:
        sample_string = "empty"
        sample_string_bytes = sample_string.encode("ascii") 
        
        encoded_string = base64.b64encode(sample_string_bytes) 
        calData = CalData(encoded_string, 12, calendar_id)

        with open(filepath, 'wb') as inp:
            pickle.dump(calData, inp)
    return calData

def get_creds(tokenpath, credpath):
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/calendar']

    if os.path.exists(tokenpath):
        with open(tokenpath, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credpath, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(tokenpath, 'wb') as token:
            pickle.dump(creds, token)
    return creds

def base64_to_cv2_image(base64_string):
    img_data = base64.b64decode(base64_string.split(',')[1])
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_GRAYSCALE)
    img = 255 - img
    img[img != 255] = 0
    return img

def canvas_handwriting_detection(img, visionCreds):
    client = vision.ImageAnnotatorClient(credentials=visionCreds)

    image = vision.Image(content=cv2.imencode('.jpg', img)[1].tostring())

    response = client.document_text_detection(image = image,  image_context={"language_hints": ["en"]})

    if response.error.message:
        raise Exception(
            "{}\nFor more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors".format(response.error.message)
        )
    if len(response.text_annotations) == 0: 
        return "No text detected"
    return response.text_annotations[0].description

def crop_canvas(img, coord1, coord2):
    margin = 5
    bottom, top, left, right = round(coord1[1])+margin, round(coord2[1])-margin, round(coord1[0])-margin, round(coord2[0])+margin
    print(img.shape)
    crop_img = img[top:bottom, left:right].copy()
    return crop_img

def convert_to_wav(input_file, output_file):
    audio = AudioSegment.from_file(input_file)
    audio.export(output_file, format="wav")
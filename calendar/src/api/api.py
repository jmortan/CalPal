import json

from flask import Flask, request, Response
from flask_api import status
from utils import *
from googleapiclient.discovery import build
from google.oauth2 import service_account
from enum import Enum
from speech_to_text import SpeechToTextModule
from intention_classifier import IntentionClassifierModule
from tzlocal import get_localzone
from datetime import datetime
from open_ai_client import OpenAiClient
from generative_scheduling import GenerativeSchedulingModule
from emotion_classifier import EmotionClassifierModule
import base64

app = Flask(__name__)

FILEPATH = './state_data/CalData.pkl'
TOKENPATH = './state_data/token.pickle'
CREDPATH = './state_data/credentials.json'
VISIONCREDPATH = './state_data/visionCredentials.json'
CALENDAR_ID = "ee12631861d3d53b1773f88e9b6220add9aa53925b3e4a921eca9dc6f3f17606@group.calendar.google.com"
UPLOAD_FOLDER = 'state_data'

creds = get_creds(TOKENPATH, CREDPATH)
visionCreds = service_account.Credentials.from_service_account_file(VISIONCREDPATH)
calData = get_data(FILEPATH, CALENDAR_ID)
service = build('calendar', 'v3', credentials=creds)
statuses = Enum('Statuses', ['Forward', 'Backward', 'Empty'])

flipped = statuses.Empty


@app.route('/monthEvents', methods = ['GET'])
def get_month(): 
    month = int(request.args.get('month'))
    #return bounding boxes mapping to event ids
    month_canvas =  calData.get_month_canvas(month)
    if type(month_canvas)==bytes:
        month_canvas= base64.b64encode(month_canvas).decode('utf-8')

    bb_dict = calData.get_month_events(month)

    month_info = {'month': month_canvas, 'bbox': bb_dict}
    return json.dumps(month_info)


@app.route('/monthTheme',methods = ['GET'])
def get_theme():
    month = int(request.args.get('month'))
    theme = calData.get_month_theme(month)
    if type(theme)==bytes:
        theme = base64.b64encode(theme).decode('utf-8')
    monthTheme = {'theme': theme}
    return json.dumps(monthTheme)

    
@app.route ('/modifyEvent', methods = ['POST'])
def modify_event(): 
    data = request.json
    month = data['month']
    event_id = data['event_id']
    canvas_data = data['canvasData']
    try:
        calData.delete_event(month, canvas_data, event_id)
        with open(FILEPATH, 'wb') as file:
            pickle.dump(calData, file)
        service.events().delete(calendarId=calData.get_cal_id(), eventId=event_id).execute()
        return Response("Event deleted", status = status.HTTP_200_OK)
    
    except: 
        return Response("Unable to delete event", status = status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@app.route('/addEvent', methods=['POST'])
def add_event():
    data = request.json
    canvas_data, month, dateString = data['canvasData'], data['month'], data['date']
    coord1, coord2 = data['bbox'][0], data['bbox'][1]
    img = base64_to_cv2_image(canvas_data)
    cropped = crop_canvas(img, coord1, coord2)
    #cv2.imwrite("testing.png", cropped)
    event_writing = canvas_handwriting_detection(cropped,  visionCreds) 
    if (event_writing=="No text detected"):
        return Response("Not detected", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    event_query = event_writing + " on " + dateString
    created_event = service.events().quickAdd(calendarId = calData.get_cal_id(), text=event_query).execute()

    # Set up time defaults for all day events
    local_timezone = get_localzone()
    now = datetime.now(local_timezone)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
    end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()

    event_start = created_event.get("start", {"dateTime": start_of_day}).get("dateTime")
    event_end = created_event.get("end", {"dateTime": end_of_day}).get("dateTime")

    event_name = created_event["summary"]

    calData.add_event(month, coord1, coord2, created_event['id'], event_name, event_start, event_end, False)
    calData.update_canvas(month, canvas_data)
    calData.generate_theme(month)
    with open(FILEPATH, 'wb') as file:
            pickle.dump(calData, file)
    return Response(created_event['id'], status = status.HTTP_200_OK)
    
@app.route('/addSpeech', methods=['POST'])
def add_speech():
    file = request.files.get('file')
    filename="recording.webm"
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    out_file_path = os.path.join(UPLOAD_FOLDER, "recording.wav")
    file.save(file_path)
    convert_to_wav(file_path, out_file_path)
    client = OpenAiClient().get_client()
    transcription= SpeechToTextModule(client).speech_to_text(out_file_path)
    month = request.form.get("month")
    print(f"Audio Transcribed: {transcription}")
    
    isGoalString = IntentionClassifierModule(client).classify_intentions(transcription)
    isGoal = json.loads(isGoalString)["is_goal"]
    if isGoal:
        # Get events from ChatGPT. I'm expecting something like this, I need the dateString to be in the below format.
        print("Detected Goal")
        user_events = calData.get_events()
        scheduled_events = GenerativeSchedulingModule(client).process_user_goal(transcription, user_events)
        events = json.loads(scheduled_events)["events"]
        months = set()
        for event in events: 
            event_name = event["event_description"]
            event_start = event["event_start"]
            event_end = event["event_end"]
            gcal_event = {
                'summary': event_name,
                'start': {
                    'dateTime': event_start,
                },
                'end': {
                    'dateTime': event_end,
                },
            }
            gcal_event = service.events().insert(calendarId='primary', body=gcal_event).execute()
            event["event_id"] = gcal_event["id"]
            event_month = datetime.fromisoformat(event_start).month - 1
            calData.add_event(event_month, None, None, event['id'], event_name, event_start, event_end, True)
            months.add(event_month)
        for event_month in months:
            calData.generate_theme(event_month)
        return json.dumps(events)
    else:
        print("Did not detect goal")
        # Update theming based on the classified affect of the user's statement
        emotion_string = EmotionClassifierModule(client).classify_emotion(transcription)
        emotion = json.loads(emotion_string)["classified_emotion"]
        calData.generate_theme(int(month), emotion)
        return json.dumps({'monthchange':True})


@app.route('/updateGesture/<update>', methods = ['HEAD'])
def update_gesture(update):
    global flipped
    if update == "Forward":
        flipped = statuses.Forward
    else: 
        flipped = statuses.Backward
    return Response(status = status.HTTP_200_OK)


@app.route('/lookGesture', methods=['GET'])
def look_gesture():
    global flipped
    res = "Empty"

    if flipped == statuses.Backward: 
        res = "Backward"
    if flipped == statuses.Forward:
        res = "Forward"

    flipped = statuses.Empty

    return Response(res, status = status.HTTP_200_OK)

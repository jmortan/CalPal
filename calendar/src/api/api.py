import json

from flask import Flask, request, Response
from flask_api import status
from utils import *
from googleapiclient.discovery import build
from google.oauth2 import service_account
from enum import Enum

app = Flask(__name__)

FILEPATH = './state_data/CalData.pkl'
TOKENPATH = './state_data/token.pickle'
CREDPATH = './state_data/credentials.json'
VISIONCREDPATH = './state_data/visionCredentials.json'
CALENDAR_ID = "ee12631861d3d53b1773f88e9b6220add9aa53925b3e4a921eca9dc6f3f17606@group.calendar.google.com"

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
    event_name = canvas_handwriting_detection(cropped,  visionCreds) 
    if (event_name=="No text detected"):
        return Response("Not detected", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    event_query = event_name + " on " + dateString
    created_event = service.events().quickAdd(calendarId = calData.get_cal_id(), text=event_query).execute()

    event_start = created_event["start"]["dateTime"]
    event_end = created_event["end"]["dateTime"]

    calData.add_event(month, canvas_data, coord1, coord2, created_event['id'], event_name, event_start, event_end, False)
    with open(FILEPATH, 'wb') as file:
            pickle.dump(calData, file)
    return Response(created_event['id'], status = status.HTTP_200_OK)


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

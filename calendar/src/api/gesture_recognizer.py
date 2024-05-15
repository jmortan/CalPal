import mediapipe as mp
import cv2
import argparse
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import numpy as np
import requests
from threading import Thread
from enum import Enum

MARGIN = 30  # pixels
FONT = cv2.FONT_HERSHEY_SIMPLEX 
FONT_SIZE = 1
FONT_THICKNESS = 2
TEXT_COLOR = (88, 205, 54) # vibrant green

## To allow for full motion to be completed and reset 
## Before redetection
TIME_TO_REDETECTION = 20

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

LANDMARKS_KNUCKLE_TIP = [(5, 8), (9, 12), (13, 16), (17, 20)]
WRIST = 0
MIDDLE_FINGER_KNUCKLE = 9
ORIENT = Enum('Orientation', ['Right', 'Left', 'Up', 'Down'])
ACTIONS = Enum('Actions', ['Forward', 'Backward'])

def orientation(hand_landmarks): 
    wrist_0 = hand_landmarks[WRIST]
    middle_9 = hand_landmarks[MIDDLE_FINGER_KNUCKLE]

    x_wrist, y_wrist = wrist_0.x, wrist_0.y
    x_mid, y_mid = middle_9.x, middle_9.y
    
    if abs(x_mid - x_wrist) < 0.05:
        m = np.inf
    else:
        m = abs((y_mid - y_wrist)/(x_mid - x_wrist))       
        
    if m >= 0 and m <= 1:
        if x_mid > x_wrist:
            return ORIENT.Right
        else:
            return ORIENT.Left
    if m > 1:
        if y_mid < y_wrist:
            return ORIENT.Up
        else:
            return ORIENT.Down
        
def finger_closed(knuckle, tip):
    return tip.y > knuckle.y

def finger_fully_open(wrist, tip, under_tip):
    tip_vec = np.array([tip.x, tip.y])
    wrist_vec = np.array([wrist.x, wrist.y])
    under_tip_vec = [under_tip.x, under_tip.y]
    dist_tip = np.linalg.norm(tip_vec - wrist_vec)
    dist_under_tip = np.linalg.norm(under_tip_vec - wrist_vec)
    return dist_tip > dist_under_tip

def detect_flip_forward_start(hand_landmarks):
    if orientation(hand_landmarks) != ORIENT.Up:
        return False
    for knuckle, tip in LANDMARKS_KNUCKLE_TIP:
        knuckle_landmark = hand_landmarks[knuckle]
        tip_landmark = hand_landmarks[tip]
        if not finger_closed(knuckle_landmark, tip_landmark):
            return False
    return True

def detect_flip_forward_end(hand_landmarks):
    if orientation(hand_landmarks) != ORIENT.Up:
        return False
    for knuckle, tip in LANDMARKS_KNUCKLE_TIP:
        tip_landmark = hand_landmarks[tip]
        if not finger_fully_open(hand_landmarks[WRIST], tip_landmark, hand_landmarks[tip - 1]):
            return False
    return True

def detect_flip_backward_start(hand_landmarks):
    if orientation(hand_landmarks) != ORIENT.Up:
        return False
    for idx, joint in enumerate(LANDMARKS_KNUCKLE_TIP):
        knuckle_landmark = hand_landmarks[joint[0]]
        tip_landmark = hand_landmarks[joint[1]]
        if idx == 0: 
            if not finger_fully_open(hand_landmarks[WRIST], tip_landmark, hand_landmarks[joint[1] - 1]):
                return False
        else: 
            if not finger_closed(knuckle_landmark, tip_landmark):
                return False
    return True

def detect_flip_backward_end(hand_landmarks):
    if orientation(hand_landmarks) != ORIENT.Up:
        return False
    for knuckle, tip in LANDMARKS_KNUCKLE_TIP:
        knuckle_landmark = hand_landmarks[knuckle]
        tip_landmark = hand_landmarks[tip]
        if not finger_closed(knuckle_landmark, tip_landmark):
            return False
    return True

class MediapipeHandModule():

    def __init__(self):
        self.mp_drawing = solutions.drawing_utils
        #Hand landmarker results
        self.results = None
        #Angles of starting pose 
        self.start_landmarks = None
        #Time of starting pose 
        self.start_time = None
        #Starting pose intended gesture
        self.gesture = None 

        #Last gesture completed
        self.last_gesture = None
        #Last time a gesture was completed
        self.last_flipped_time = None

    def query_server(self, port = None):
        url = "http://localhost:5000/updateGesture/" + self.last_gesture.name
        requests.head(url = url)

    def draw_landmarks(self, annotated_image, hand_landmarks):
        hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
        hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
        ])
        solutions.drawing_utils.draw_landmarks(
            annotated_image,
            hand_landmarks_proto,
            solutions.hands.HAND_CONNECTIONS,
            solutions.drawing_styles.get_default_hand_landmarks_style(),
            solutions.drawing_styles.get_default_hand_connections_style())

    def detect_gesture_end(self, hand_landmarks, curr_time): 
        if (self.gesture == None):
            return None
        
        ## Current gesture is flip forward
        if self.gesture == ACTIONS.Forward: 
           if not detect_flip_forward_end(hand_landmarks):
               return None
                
        ## Current gesture is flip backward 
        else:
            if not detect_flip_backward_end(hand_landmarks):
                return None

        self.last_gesture = self.gesture
        #Detected want to reset to detect the next gesture 
        self.start_time = None
        self.start_landmarks = None
        self.gesture = None
        self.last_flipped_time = curr_time

        return self.last_gesture

    def detect_gesture_start(self, hand_landmarks, timestamp): 
        flip_forward = detect_flip_forward_start(hand_landmarks)
        flip_backward = detect_flip_backward_start(hand_landmarks)

        if flip_forward: 
            self.gesture = ACTIONS.Forward
        elif flip_backward: 
            self.gesture = ACTIONS.Backward
        else:
            self.gesture = None

        if flip_forward or flip_backward: 
            self.start_landmarks = hand_landmarks
            self.start_time = timestamp

    def frame_analysis(self, rgb_image, detection_result, timestamp, send_to_server):
        hand_landmarks_list = detection_result.hand_landmarks
        annotated_image = np.copy(rgb_image)

        # Loop through the detected hands to visualize.
        for idx in range(len(hand_landmarks_list)):
            hand_landmarks = hand_landmarks_list[idx]
            detected = None

            #If calibrating for new gestures
            if self.gesture == None or timestamp - self.start_time > TIME_TO_REDETECTION:
                self.detect_gesture_start(hand_landmarks, timestamp)

            #If in the middle of current gesture
            elif self.gesture != None:
                detected = self.detect_gesture_end(hand_landmarks, timestamp)

            if self.last_flipped_time != None and timestamp - self.last_flipped_time <= TIME_TO_REDETECTION:
                cv2.putText(annotated_image, self.last_gesture.name, (MARGIN, MARGIN), FONT, FONT_SIZE, TEXT_COLOR, FONT_THICKNESS, cv2.LINE_AA)

            if detected != None:
                if send_to_server:
                    #Support non blocking requests
                    thread = Thread(target = self.query_server)
                    thread.start()

            # Draw the hand landmarks.
            self.draw_landmarks(annotated_image, hand_landmarks)
        return annotated_image

    def print_result(self, result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        #print('hand landmarker result: {}'.format(result))
        self.results = result
    
    def main(self, send_to_server = False):
        options = HandLandmarkerOptions(
            base_options=BaseOptions(model_asset_path='./state_data/hand_landmarker.task'),
            running_mode=VisionRunningMode.LIVE_STREAM,
            result_callback=self.print_result, 
            num_hands = 1)

        video = cv2.VideoCapture(0)

        timestamp = 0
        with HandLandmarker.create_from_options(options) as landmarker:
            while video.isOpened(): 
                # Capture frame-by-frame
                ret, frame = video.read()

                if not ret:
                    #print("Ignoring empty frame")
                    break
                frame = cv2.flip(frame, 1)
                frame.flags.writeable = False
                timestamp += 1
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
                res = landmarker.detect_async(mp_image, timestamp)
                if(self.results != None):
                    annotated_image = self.frame_analysis(mp_image.numpy_view(), self.results, timestamp, send_to_server)
                    cv2.imshow('Show',annotated_image)
                else:
                    cv2.imshow('Show', frame)
                
                if cv2.waitKey(5) & 0xFF == ord('q'):
                    print("Closing Camera Stream")
                    break

            video.release()
            cv2.destroyAllWindows()
            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '--server',
        help='Whether or not to send to server for updates',
        required=False,
        default=False)
    
    args = parser.parse_args()
    body_module = MediapipeHandModule()
    body_module.main(args.server)
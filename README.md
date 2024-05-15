# CalPal Set up Instructions
## Mouse Branch vs Touch Branch 
There are two branches of this project that run based on either mouse input or touch input. 
This is the mouse branch. To run the project with touch input please switch to the main branch.

## Frontend Files

The frontend lives in calendar/src/frontend

The files in the frontend include the following:

1. src/index.tsx - Entrypoint for the React/TypeScript compiler to compile the frontend
2. src/utils.tsx - Various utility functions used throughout React components
3. src/App.tsx - Top level React component which manages overall calendar layout and various shared states
4. src/Cal.tsx - React component for rendering a react-big-calendar Drag and Drop calendar component
5. src/canvas.tsx - React component for rendering the canvas HTML element which overlays the calendar and processes touch/mouse input
6. src/calTheme.tsx - React component for rendering the canvas HTML element which displays the generative calendar theme
7. src/css - CSS files for styling the various react components in 3-6

## Frontend Set Up

These setup instructions assume you have node and npm installed on your machine. We used node v18.17.0

1. Navigate to calendar/src/frontend and run ```npm install```

## Backend Files
The backend lives in calendar/src/api
The files in the backend include the following: 
1. .flaskenv - Tells ```flask run``` the environment and which file to run to start the Flask backend
2. api.py - Contains the backend server API and CalPal configuration options
3. cal_data.py - The backend calendar datatype for state maintenance
4. generative_theming.py - The generative theming module calling the Hugging Face API
5. gesture_recognizer_pi.py - The gesture recognizer module for the Raspberry Pi
6. gesture_recognizer.py - The gesture recognizer module for laptops and similar devices
7. utils.py - Helper functions

## Backend Set Up 
1. Set up backend virtual environment (specify site specific packages when installing on a raspberry pi (with picam3 use))
* Required packages are in the ```requirements.txt``` file in the root directory
* Python 3.10.7 was used to run this project - no guarantees are made for other versions

2. Create a folder in calendar/src/api called ```state_data```

3. Set up Google Handwriting Recognition credentials
* Create an account with Google Cloud [here](https://console.cloud.google.com/)
* Create a Google Cloud project in the Google Cloud console: [instructions](https://cloud.google.com/resource-manager/docs/creating-managing-projects)
* Enable the Vision API for your project [here](https://console.cloud.google.com/flows/enableapi?apiid=vision.googleapis.com&_ga=2.32815422.1870803964.1715798756-1489785253.1710469287&_gac=1.179971926.1715798839.CjwKCAjwupGyBhBBEiwA0UcqaP3v8u4mXms-in9QD3Uy51pnikPXwboRHJ3jHrIi9sYnSon5n5dqNhoCBTAQAvD_BwE)
* Create a [service account](https://cloud.google.com/iam/docs/service-accounts-create) for your project and create and download a [service account key](https://cloud.google.com/iam/docs/keys-create-delete) as a .json file
*Rename the downloaded json file to ```visionCredentials.json``` and move it into the ```state_data``` folder

4. Set up Google Calendar credentials and link calendar
* Create a Google Calendar in your Google account you would like CalPal to have access to
* Copy and paste the calendar id to the ```CALENDAR_ID``` field at the top of ```api.py```
* Follow the instructions for "Set up your environment" to create a Google Cloud Project for Google calendar [here](https://developers.google.com/calendar/api/quickstart/python#set_up_your_environment).
* Move the downloaded ```credentials.json``` into the ```state_data``` folder.

5. Set up Hugging Face credentials
* Follow the instructions [here](https://huggingface.co/docs/api-inference/en/quicktour#get-your-api-token) to create a Hugging Face account / generate your API token. 
* Once you have generated the token create a JSON file called ```api_token.json``` in the ```state_data``` folder with the format ```{"token": "<YOUR_API_TOKEN>"}```. 

6. Set up MediaPipe model
* Download the hand landmarker model [here](https://ai.google.dev/edge/mediapipe/solutions/vision/hand_landmarker#models) and save the model as ```hand_landmarker.task``` into the ```state_data``` folder.

## Running the System
1. Activate the virtual environment created above
2. Start up the backend Flask server on port 5000 with command ```flask run``` (make sure the terminal is in /calendar/src/api)
3. Wait until the application confirms the server is running in the terminal
* Upon the first start up or credential token expiration - the application will open a web browser asking you to log into your Google account to grant calendar access. 
4. Start up the front end in a separate terminal window by running command ```npm run start``` (make sure the terminal is in /calendar/src/frontend)
* Open [http://localhost:3000](http://localhost:3000) to view it in the browser.
5. Start up the gesture recognizer in a separate terminal window by running command ```python -m gesture_recognizer --server True``` (make sure the terminal is in /calendar/src/api)
* If using a Pi run ```python -m gesture_recognizer_pi --server True``` instead
* To run the gesture recognizer separately without making update requests to the server (ie: for testing) run the commands without the ```--server``` argument
6. Full screen the calendar (F11) 
7. Refresh the page to rerender (Ctrl-r)
7. Start scheduling!

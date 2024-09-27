import cv2
import face_recognition
import dlib
from starlette.responses import StreamingResponse
from scipy.spatial import distance
import threading
import os
import shutil
from fastapi import FastAPI, HTTPException, File, UploadFile
import requests
import numpy as np
import io
from datetime import datetime
import asyncio
import pytz

app = FastAPI()

# Initialize lists to hold known face encodings and their corresponding names
known_face_encodings = []
known_face_names = []

# Load dlib's face detector and facial landmarks predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./eye_detector/shape_predictor_68_face_landmarks.dat')

# Function to calculate the Eye Aspect Ratio (EAR) for blink detection
def eye_aspect_ratio(eye):
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])
    C = distance.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

# Thresholds for blink detection
EYE_AR_THRESH = 0.2
EYE_AR_CONSEC_FRAMES = 3

# Flag to indicate if video streaming is running
streaming_active = False
lock = threading.Lock()

# External API URL
EXTERNAL_API_URL = 'http://localhost:9000/api/notifications/'

@app.get('/welcome')
def welcome():
    return {"message": "Welcome to the FastAPI Face Recognition System"}

# Upload API
@app.post('/api/upload')
async def upload(file: UploadFile = File(...)):
    upload_directory = './uploads'
    
    # Ensure uploads directory exists
    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)

    # Save the uploaded file
    file_path = os.path.join(upload_directory, file.filename)
    with open(file_path, 'wb') as upload_file:
        shutil.copyfileobj(file.file, upload_file)

    # Reload known faces after the image is uploaded
    load_known_faces()

    return {"message": "File uploaded successfully", "filename": file.filename}

# Function to load all face encodings from the uploads directory
def load_known_faces():
    global known_face_encodings, known_face_names

    # Clear previous known faces
    known_face_encodings = []
    known_face_names = []

    # Load all images in the uploads directory
    for filename in os.listdir('./uploads'):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            # Load each image file and compute the face encoding
            image_path = os.path.join('./uploads', filename)
            image = face_recognition.load_image_file(image_path)
            face_encodings = face_recognition.face_encodings(image)
            
            if face_encodings:
                known_face_encodings.append(face_encodings[0])
                # Use the filename (without extension) as the person's name
                known_face_names.append(os.path.splitext(filename)[0])

    print(f"Loaded {len(known_face_encodings)} known faces.")

# Function to post data to the external API
async def post_to_external_api(image: np.ndarray):
    """
    Post the data to the external API including date, time, and the image.
    """
    # Convert image to bytes
    _, img_encoded = cv2.imencode('.jpg', image)
    image_bytes = img_encoded.tobytes()

    # Define Bangladesh timezone
    bd_timezone = pytz.timezone('Asia/Dhaka')

    # Prepare the data
    date = datetime.now(bd_timezone).strftime('%Y-%m-%d')
    time = datetime.now(bd_timezone).strftime('%H:%M:%S')
    files = {'image': ('image.jpg', io.BytesIO(image_bytes), 'image/jpeg')}
    data = {'date': date, 'time': time}

    try:
        response = requests.post(EXTERNAL_API_URL, data=data, files=files)
        if response.status_code == 201:
            print("Data posted successfully")
        else:
            print(f"Failed to post data: {response.status_code} {response.text}")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

# Function to handle posting data for unknown faces with delay
def handle_unknown_face_post(image: np.ndarray):
    """
    Handles the unknown face posting with a delay.
    """
    async def post_data():
        await post_to_external_api(image)
        await asyncio.sleep(30)  # Wait for 30 seconds before allowing another post

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(post_data())

# Video streaming API
@app.get('/')
def index():
    global streaming_active
    if not streaming_active:
        streaming_active = True
        threading.Thread(target=generate_stream, daemon=True).start()
    return StreamingResponse(generate_stream(), media_type="multipart/x-mixed-replace; boundary=frame")

# Function to generate the video stream
def generate_stream():
    COUNTER = 0
    BLINKS = 0

    # Initialize video stream
    video_capture = cv2.VideoCapture(0)
    if not video_capture.isOpened():
        raise HTTPException(status_code=500, detail="Could not open webcam")

    last_post_time = 0  # Timestamp of the last post

    while streaming_active:
        ret, frame = video_capture.read()
        if not ret:
            break

        # Convert the frame to grayscale for dlib face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)

        unknown_face_detected = False

        for rect in rects:
            shape = predictor(gray, rect)
            shape = face_recognition.face_landmarks(frame, [(rect.top(), rect.right(), rect.bottom(), rect.left())])

            leftEye = shape[0]["left_eye"]
            rightEye = shape[0]["right_eye"]

            leftEAR = eye_aspect_ratio(leftEye)
            rightEAR = eye_aspect_ratio(rightEye)

            ear = (leftEAR + rightEAR) / 2.0

            if ear < EYE_AR_THRESH:
                COUNTER += 1
            else:
                if COUNTER >= EYE_AR_CONSEC_FRAMES:
                    BLINKS += 1
                COUNTER = 0

            if BLINKS >= 1:
                face_locations = face_recognition.face_locations(frame)
                face_encodings = face_recognition.face_encodings(frame, face_locations)

                for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"
                    box_color = (0, 0, 255)

                    if True in matches:
                        first_match_index = matches.index(True)
                        name = known_face_names[first_match_index]
                        box_color = (0, 255, 0)

                    cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
                    cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.90, box_color, 2)

                    if name == "Unknown":
                        unknown_face_detected = True

        if unknown_face_detected:
            current_time = datetime.now().timestamp()
            if current_time - last_post_time >= 30:
                # Only post if 30 seconds have passed since the last post
                threading.Thread(target=handle_unknown_face_post, args=(frame,), daemon=True).start()
                last_post_time = current_time

        # Encode the frame as a JPEG
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        # Yield the frame for streaming
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')

    video_capture.release()
    cv2.destroyAllWindows()

@app.get('/stop')
def stop_stream():
    global streaming_active
    streaming_active = False
    return {"message": "Streaming stopped"}

# Load the known faces at server startup
load_known_faces()

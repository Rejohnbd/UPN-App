import cv2
import face_recognition
import dlib
from scipy.spatial import distance

# Load known face encodings and names
known_face_encodings = []
known_face_names = []

# Load known faces and names
known_person1_images = face_recognition.load_image_file("./uploads/rejohn.jpg")
known_person1_encoding = face_recognition.face_encodings(known_person1_images)[0]
known_face_encodings.append(known_person1_encoding)
known_face_names.append("Rejohn")

# Initialize video stream
video_capture = cv2.VideoCapture(0)
if not video_capture.isOpened():
    print("Error: Could not open webcam.")
    exit()

# Load dlib's face detector and facial landmarks predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./eye_detector/shape_predictor_68_face_landmarks.dat')

def eye_aspect_ratio(eye):
    # Compute the euclidean distances between the two sets of vertical eye landmarks (x, y)-coordinates
    A = distance.euclidean(eye[1], eye[5])
    B = distance.euclidean(eye[2], eye[4])

    # Compute the euclidean distance between the horizontal eye landmark (x, y)-coordinates
    C = distance.euclidean(eye[0], eye[3])

    # The eye aspect ratio (EAR)
    ear = (A + B) / (2.0 * C)

    return ear

# Thresholds for blink detection
EYE_AR_THRESH = 0.2
EYE_AR_CONSEC_FRAMES = 3
COUNTER = 0
BLINKS = 0

# Start video capture loop
while True:
    ret, frame = video_capture.read()

    # Convert the frame to grayscale for dlib face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    rects = detector(gray, 0)

    for rect in rects:
        shape = predictor(gray, rect)
        shape = face_recognition.face_landmarks(frame, [(rect.top(), rect.right(), rect.bottom(), rect.left())])

        # Get the eye landmarks
        leftEye = shape[0]["left_eye"]
        rightEye = shape[0]["right_eye"]

        # Compute the eye aspect ratio for both eyes
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)

        ear = (leftEAR + rightEAR) / 2.0

        # If the eye aspect ratio is below the blink threshold, increment the blink counter
        if ear < EYE_AR_THRESH:
            COUNTER += 1
        else:
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                BLINKS += 1

            COUNTER = 0

        # Only mark the person as recognized if a blink is detected
        if BLINKS >= 1:
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            # Compare each face with known encodings
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"
                box_color = (0, 0, 255)  # Red for unknown faces

                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]
                    box_color = (0, 255, 0)  # Green for known faces

                # Draw rectangle around face
                cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
                cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.90, box_color, 2)

    # Display the resulting frame
    cv2.imshow('Video', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture
video_capture.release()
cv2.destroyAllWindows()

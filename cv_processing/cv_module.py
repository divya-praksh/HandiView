import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Hands
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Global scale factor and rotation angles
scale_factor = 1.0
rotation_angle = 0.0
rotate_model = False
rotation_complete = 360

# Setup webcam
wCam, hCam = 640, 480
cam = cv2.VideoCapture(0)
cam.set(3, wCam)
cam.set(4, hCam)

def process_hand_gestures(image):
    global scale_factor, rotation_angle, rotate_model

    with mp_hands.Hands(
        model_complexity=0,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
        
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image_rgb)
        
        lmList = []
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                for id, lm in enumerate(hand_landmarks.landmark):
                    h, w, c = image.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmList.append([id, cx, cy])

                if len(lmList) != 0:
                    x1, y1 = lmList[4][1], lmList[4][2]
                    x2, y2 = lmList[8][1], lmList[8][2]

                    length = np.linalg.norm(np.array([x2 - x1, y2 - y1]))
                    new_scale_factor = np.interp(length, [50, 220], [0.5, 2.0])

                    if new_scale_factor != scale_factor:
                        scale_factor = new_scale_factor
                        rotate_model = True
                        rotation_angle = 0

                    scaleBar = np.interp(length, [50, 220], [150, 400])
                    scalePer = np.interp(length, [50, 220], [0, 100])

                    cv2.rectangle(image, (50, 150), (85, 400), (0, 0, 0), 3)
                    cv2.rectangle(image, (50, int(scaleBar)), (85, 400), (0, 0, 0), cv2.FILLED)
                    cv2.putText(image, f'{int(scalePer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 0), 3)
        
        return image

def get_hand_scale_factor():
    global scale_factor, rotation_angle, rotate_model
    
    success, image = cam.read()
    if not success:
        return scale_factor
    
    image = process_hand_gestures(image)
    
    return scale_factor

def release_resources():
    cam.release()
    cv2.destroyAllWindows()

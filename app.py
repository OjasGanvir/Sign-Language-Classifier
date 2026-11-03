from flask import Flask, render_template, Response, jsonify
import cv2
import mediapipe as mp
import pickle
import numpy as np
from collections import deque
import warnings
warnings.filterwarnings("ignore")

app = Flask(__name__)

# Trained model
model_dict = pickle.load(open("./model.p", 'rb'))
model = model_dict['model']

# Capture video
cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.5
)
mp_drawing_styles = mp.solutions.drawing_styles
mp_draw = mp.solutions.drawing_utils

# Buffers I and J
pinky_buffer = deque(maxlen=25)
index_buffer = deque(maxlen=25)
smooth_buffer = deque(maxlen=7)

current_letter = "-"
current_mode = "Waiting"

dynamic_hold_counter = 0
active_dynamic_letter = ""
DYNAMIC_HOLD_FRAMES = 45

def analyze_j(buffer):
    """
    ASL 'J' Gesture:
    Handshape: 'I' (Pinky extended).
    Movement: Pinky tip starts high, moves down, and scoops left/upward in a hook.
    """
    if len(buffer) < 14:
        return False

    pts = np.array(buffer)
    xs = pts[:, 0]
    ys = pts[:, 1]

    w_motion = np.max(xs) - np.min(xs)
    h_motion = np.max(ys) - np.min(ys)

    # Must exceed minimal movement threshold (avoids classifying minor hand tremors)
    if h_motion < 0.07 or w_motion < 0.04:
        return False

    # Check temporal ordering: starting point must be higher than lowest point
    first_y = ys[0]
    lowest_y = np.max(ys) # in image coordinates, max y is lowest on screen
    last_y = ys[-1]

    # Hand moved significantly down, then bottom point occurred before the end (curve)
    lowest_idx = np.argmax(ys)
    if lowest_idx > 4 and (lowest_idx < len(ys) - 1):
        if (lowest_y - first_y) > 0.06 and (lowest_y - last_y) > 0.02:
            return True

    return False

def analyze_z(buffer):
    """
    ASL 'Z' Gesture:
    Handshape: Index finger extended (pointing).
    Movement: Index tip traces horizontal right -> diagonal down-left -> horizontal right.
    """
    if len(buffer) < 16:
        return False

    pts = np.array(buffer)
    xs = pts[:, 0]
    ys = pts[:, 1]

    w_motion = np.max(xs) - np.min(xs)
    h_motion = np.max(ys) - np.min(ys)

    if w_motion < 0.07 or h_motion < 0.05:
        return False

    # Count horizontal direction reversals
    diffs_x = np.diff(xs)
    reversals = 0
    for i in range(len(diffs_x) - 1):
        if (diffs_x[i] > 0.003 and diffs_x[i+1] < -0.003) or (diffs_x[i] < -0.003 and diffs_x[i+1] > 0.003):
            reversals += 1

    # A zigzag motion typically has at least 2 horizontal direction reversals
    if reversals >= 2 and h_motion > 0.04:
        return True

    return False

def generate_frames():
    global current_letter, current_mode
    global dynamic_hold_counter, active_dynamic_letter
    while True:
        success, frame = cap.read()
        if not success:
            break

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame_rgb)

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )
            
            # Collect raw coordinates
            x_ = [lm.x for lm in hand_landmarks.landmark]
            y_ = [lm.y for lm in hand_landmarks.landmark]

            min_x = min(x_)
            min_y = min(y_)

            scale = max(max(x_) - min_x, max(y_) - min_y)

            if scale == 0:
                scale = 1.0

            # Must match the training format: (x - min_x) and (y - min_y) WITHOUT dividing by scale
            data_aux = []
            for lm in hand_landmarks.landmark:
                data_aux.append((lm.x - min_x) / scale)
                data_aux.append((lm.y - min_y) / scale)

            # Predict static letter
            pred = model.predict([np.asarray(data_aux)])[0]

            # Track fingertips for dynamic J and Z
            index_tip = hand_landmarks.landmark[8]
            pinky_tip = hand_landmarks.landmark[20]
            index_buffer.append((index_tip.x, index_tip.y))
            pinky_buffer.append((pinky_tip.x, pinky_tip.y))

            # Detect J
            if pred in ['I', 'J'] and analyze_j(pinky_buffer):

                current_letter = "J"
                current_mode = "Dynamic (Motion)"

                active_dynamic_letter = "J"
                dynamic_hold_counter = DYNAMIC_HOLD_FRAMES

                pinky_buffer.clear()

            # Detect Z
            elif pred in ['D', '1', 'Z'] and analyze_z(index_buffer):

                current_letter = "Z"
                current_mode = "Dynamic (Motion)"

                active_dynamic_letter = "Z"
                dynamic_hold_counter = DYNAMIC_HOLD_FRAMES

                index_buffer.clear()

            # Keep displaying the detected dynamic letter
            elif dynamic_hold_counter > 0:

                current_letter = active_dynamic_letter
                current_mode = "Dynamic (Motion)"

                dynamic_hold_counter -= 1

            # Otherwise, display static prediction
            else:

                smooth_buffer.append(pred)

                current_letter = max(
                    set(smooth_buffer),
                    key=smooth_buffer.count
                )

                current_mode = "Static Pose"
                dynamic_hold_counter = 0
                active_dynamic_letter = ""
        else:
            # When hand leaves camera, reset current letter
            current_letter = "-"
            current_mode = "Waiting for hand..."
            pinky_buffer.clear()
            index_buffer.clear()
            smooth_buffer.clear()

        # Stream video frame
        ret, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.route('/')
def index() :
    return render_template("index.html")

@app.route('/video-feed')
def video_feed() :
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_data')
def get_data():
    return jsonify({'letter': current_letter, 'mode': current_mode})

if __name__ == "__main__" :
    app.run(debug=True, use_reloader=False)
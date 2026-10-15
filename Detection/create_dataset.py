import os
import pickle
import cv2
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

DATA_DIR = './data'

data = []
labels = []

# Loop through every letter folder in your data directory
for dir_ in os.listdir(DATA_DIR):
    dir_path = os.path.join(DATA_DIR, dir_)
    
    # Check to ensure it's a directory (avoids hidden files like .DS_Store)
    if not os.path.isdir(dir_path):
        continue
        
    print(f"Processing folder: {dir_}")
    
    for img_path in os.listdir(dir_path):
        img_full_path = os.path.join(dir_path, img_path)
        
        # Load the image
        img = cv2.imread(img_full_path)
        if img is None:
            continue
            
        # Convert the image from BGR to RGB (MediaPipe requires RGB)
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Process the image and find hands
        results = hands.process(img_rgb)
        
        # If a hand is detected in the image
        if results.multi_hand_landmarks:
            data_aux = []
            x_ = []
            y_ = []
            
            # We assume one hand per image for this alphabet project
            hand_landmarks = results.multi_hand_landmarks[0]
            
            # Step 1: Collect all X and Y coordinates to find the bounding box bounds
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                x_.append(x)
                y_.append(y)
            
            # Step 2: Normalize the coordinates
            # Subtracting the minimum value ensures the data stays relative to the hand itself, 
            # no matter where your hand is positioned on the webcam screen.
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x - min(x_))
                data_aux.append(y - min(y_))
                
            # Append the 42 extracted features and the matching letter label
            data.append(data_aux)
            labels.append(dir_)

# Save the extracted data into a pickle file
with open('data.pickle', 'wb') as f:
    pickle.dump({'data': data, 'labels': labels}, f)

print("Dataset created successfully! Saved as data.pickle")
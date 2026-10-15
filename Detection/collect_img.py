import os
import cv2

# 1. Define where to save the data and the letters (excluding 'J')
DATA_DIR = './data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Alphabet from A to Z excluding 'J'
letters = [
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 
    'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 
    'T', 'U', 'V', 'W', 'X', 'Y', 'Z'
]

dataset_size = 100  # Number of images to collect per letter per session

# 2. Initialize the webcam
cap = cv2.VideoCapture(0)

for letter in letters:
    # Create a folder for the specific letter if it doesn't exist
    letter_dir = os.path.join(DATA_DIR, letter)
    if not os.path.exists(letter_dir):
        os.makedirs(letter_dir)

    print(r"Preparing to collect data for letter: {}".format(letter))

    # --- READY PHASE ---
    # Loop to let the user position their hand before recording starts
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Mirror the frame so it feels natural
        frame = cv2.flip(frame, 1)
        
        # Add instructional text to screen
        cv2.putText(frame, r"Letter: {}".format(letter), (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3, cv2.LINE_AA)
        cv2.putText(frame, "Press 'Q' when ready to capture!", (20, 100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2, cv2.LINE_AA)
        
        cv2.imshow('Data Collection Window', frame)
        
        # Press 'q' to break this loop and start saving images
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    # --- CAPTURE PHASE ---
    print(r"Collecting data for {}...".format(letter))
    counter = 0
    while counter < dataset_size:
        ret, frame = cap.read()
        if not ret:
            break
            
        frame = cv2.flip(frame, 1)
        
        # Save the frame as an image inside the letter's directory
        img_path = os.path.join(letter_dir, r"{}.jpg".format(counter))
        cv2.imwrite(img_path, frame)
        
        # Show progress on screen
        cv2.putText(frame, r"Capturing: {}/{}".format(counter + 1, dataset_size), (20, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 3, cv2.LINE_AA)
        cv2.imshow('Data Collection Window', frame)
        cv2.waitKey(25)
        
        counter += 1

print("Data collection complete for all requested letters!")
cap.release()
cv2.destroyAllWindows()
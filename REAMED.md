# Gesture Classifier

A webcam-based project that recognizes American Sign Language (ASL) fingerspelling letter gestures. The app detects hand landmarks with MediaPipe, uses a trained machine-learning model to predict static letters, and displays the prediction in a browser. J and Z are recognized using hand movement.

This is an alphabet-letter recognition demonstration, not a translator for complete sign-language conversations.

## Features

- Live webcam feed with hand landmarks drawn on the hand.
- Static hand-gesture letter classification.
- Movement-based recognition for J and Z.
- Letter output and a word/sentence area.
- Speak and Clear controls.
- An Info page with a Back to Camera button.
- A camera-unavailable message when the camera cannot be opened.

## Requirements

- Windows computer with a webcam.
- Python 3.11 recommended.
- The Python packages listed in [`requirements.txt`](requirements.txt).

The saved model was created with scikit-learn 1.3.2. Keep the scikit-learn version in `requirements.txt` unchanged when loading this model unless you retrain and verify it with another version.

## Setup on Windows

Open PowerShell in the project folder and create a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell does not allow the virtual environment to activate, open Command Prompt in the project folder and run:

```bat
python -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the app

From the project folder, with the virtual environment active, run:

```powershell
python app.py
```

Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in a browser on the same computer. Leave the terminal window running while you use the app. Press `Ctrl+C` in that window to stop it.

The webcam is opened by the Python app through OpenCV. Close other apps that may be using the camera, and make sure Windows allows desktop apps to access it.

## Using the demo

1. Place one hand clearly inside the camera frame in a well-lit area.
2. Make a supported static letter gesture and watch the Detected Letter display.
3. Hold a letter steady for about one second to add it to the word/sentence area.
4. Trace the hand movements for J and Z.
5. Select **Speak** to read the displayed text aloud, or **Clear** to erase it.
6. Select **INFO** to open the project information page and **Back to Camera** to return.

## Project files

- `app.py` — Flask server, webcam capture, MediaPipe landmark processing, model predictions, and J/Z movement logic.
- `model.p` — saved scikit-learn classifier used by the app.
- `data.pickle` — saved classifier training data/features.
- `templates/index.html` — browser page structure.
- `static/main.js` — live prediction display, text controls, and Info-page navigation.
- `static/style.css` — page styling.
- `requirements.txt` — pinned Python package versions.

The project folder does not include a model-training script. The saved model and data are used for running the demo.

## Troubleshooting

- **Camera is unavailable:** check that the webcam is connected, close video-call apps, and confirm Windows camera access for desktop apps.
- **The page does not open:** make sure `python app.py` is still running and use `http://127.0.0.1:5000` on the same computer.
- **A letter is misclassified:** improve lighting, center the hand, keep the hand visible, and try again. Predictions can vary with camera position and signer.
- **Model loading error:** install from `requirements.txt` and run `app.py` from the project folder so it can find `model.p`.

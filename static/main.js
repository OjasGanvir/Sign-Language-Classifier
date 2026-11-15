let sentence = "";
let lastLetter = "";
let holdCounter = 0;

// Poll Python every 100ms
setInterval(() => {
  fetch('/get_data')
    .then(res => res.json())
    .then(data => {
      const detectedEl = document.getElementById('detected-letter');
      const modeEl = document.getElementById('mode-badge');
      const sentenceEl = document.getElementById('sentence-text');
      const cameraStatusEl = document.getElementById('camera-status');

      cameraStatusEl.innerText = data.camera_status || "";
      cameraStatusEl.hidden = data.camera_status === "Camera connected";

      if (data.letter !== "-") {
        detectedEl.innerText = data.letter;
        modeEl.innerText = "Mode: " + data.mode;

        // Count how long the same letter is held steady
        if (data.letter === lastLetter) {
          holdCounter++;
          // When held for ~1 second (10 polls of 100ms), append it
          if (holdCounter === 10) {
            sentence += data.letter;
            sentenceEl.innerText = sentence;
          }
        } else {
          lastLetter = data.letter;
          holdCounter = 0;
        }
      } else {
        detectedEl.innerText = "-";
        modeEl.innerText = "Mode: Waiting for hand...";
        holdCounter = 0;
      }
    })
    .catch(err => {
      const cameraStatusEl = document.getElementById('camera-status');
      cameraStatusEl.innerText = "Camera is unavailable";
      cameraStatusEl.hidden = false;
      console.error("Error fetching data:", err);
    });
}, 100);

// Clear sentence button
document.getElementById('btn-clear').addEventListener('click', () => {
  sentence = "";
  lastLetter = "";
  holdCounter = 0;
  document.getElementById('sentence-text').innerText = "";
});

// Speak button
document.getElementById('btn-speak').addEventListener('click', () => {
  if (sentence.trim() && 'speechSynthesis' in window) {
    const utterance = new SpeechSynthesisUtterance(sentence);
    window.speechSynthesis.speak(utterance);
  }
});

let infobtn = document.querySelector(".info");
const cameraPage = document.getElementById("camera-page");
const infoPage = document.getElementById("info-page");
const backToCamera = document.getElementById("back-to-camera");

infobtn.addEventListener("click", () => {
  cameraPage.hidden = true;
  infoPage.hidden = false;
  infobtn.setAttribute("aria-expanded", "true");
  window.scrollTo(0, 0);
});

backToCamera.addEventListener("click", () => {
  infoPage.hidden = true;
  cameraPage.hidden = false;
  infobtn.setAttribute("aria-expanded", "false");
});

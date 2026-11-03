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
    .catch(err => console.error("Error fetching data:", err));
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
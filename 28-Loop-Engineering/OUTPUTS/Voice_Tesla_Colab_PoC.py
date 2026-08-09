# Voice_Tesla_Colab_PoC.py
# ==============================================================================
# Instructions for Google Colab:
# 1. Copy the code blocks below into separate cells in a new Google Colab notebook.
# 2. Make sure you are using a GPU runtime (Runtime -> Change runtime type -> T4 GPU or similar).
# 3. Run the cells in order.
# ==============================================================================

# --- CELL 1: Installation ---
# Run this cell to install required dependencies.
"""
!pip install faster-whisper
"""

# --- CELL 2: Audio Capture Function (JS/HTML5 -> Python) ---
# Run this cell to define the recording function.
import IPython
from google.colab import output
import base64
import numpy as np
import io

RECORD_JS = """
const sleep  = time => new Promise(resolve => setTimeout(resolve, time))
const b2text = blob => new Promise(resolve => {
  const reader = new FileReader()
  reader.onloadend = e => resolve(e.srcElement.result)
  reader.readAsDataURL(blob)
})
var record = () => new Promise(async resolve => {
  stream = await navigator.mediaDevices.getUserMedia({ audio: true })
  recorder = new MediaRecorder(stream)
  chunks = []
  recorder.ondataavailable = e => chunks.push(e.data)
  recorder.start()
  
  // Create a stop button
  var div = document.createElement('div');
  var button = document.createElement('button');
  button.textContent = 'Stop Recording';
  button.style.fontSize = '20px';
  button.style.padding = '10px 20px';
  button.style.color = 'white';
  button.style.backgroundColor = '#ff4b4b';
  button.style.border = 'none';
  button.style.borderRadius = '5px';
  button.style.cursor = 'pointer';
  div.appendChild(button);
  document.body.appendChild(div);

  // When button is clicked, stop recording
  var stopped = new Promise((resolve, reject) => {
    button.onclick = () => {
      resolve();
    }
  });

  await stopped;
  recorder.stop()
  
  // Wait for the recording to stop
  await new Promise(r => recorder.onstop = r);
  
  // Remove button
  div.remove();
  
  // Stop all audio tracks
  stream.getTracks().forEach(track => track.stop());
  
  // Convert audio blob to base64
  let blob = new Blob(chunks, {type: 'audio/webm;codecs=opus'})
  let text = await b2text(blob)
  resolve(text)
})
"""

def record_audio(filename='audio.webm'):
  display(IPython.display.Javascript(RECORD_JS))
  print("Recording... Click the 'Stop Recording' button to stop.")
  s = output.eval_js('record()')
  print("Recording stopped.")
  b = base64.b64decode(s.split(',')[1])
  with open(filename, 'wb') as f:
    f.write(b)
  return filename

# --- CELL 3: Faster-Whisper Transcription ---
# Run this cell to initialize the model.
from faster_whisper import WhisperModel

# Initialize the model on GPU with fp16
model_size = "base"
print(f"Loading Whisper model '{model_size}'...")
model = WhisperModel(model_size, device="cuda", compute_type="float16")
print("Model loaded.")

# --- CELL 4: Execute Recording and Transcription ---
# Run this cell to record audio and transcribe it.
audio_file = record_audio("user_audio.webm")

print("Transcribing...")
segments, info = model.transcribe(audio_file, beam_size=5)

print(f"Detected language '{info.language}' with probability {info.language_probability}")

print("\n--- Transcription ---")
for segment in segments:
    print("[%s -> %s] %s" % (round(segment.start, 2), round(segment.end, 2), segment.text))

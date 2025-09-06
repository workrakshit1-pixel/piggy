import sounddevice as sd
import vosk
import json
import pyttsx3
import queue

# Queue to store audio
q = queue.Queue()

# Initialize TTS
engine = pyttsx3.init()
engine.setProperty('rate', 160)  # speaking speed
engine.setProperty('volume', 1.0)

def speak(text):
    print(f"Piggy: {text}")
    engine.say(text)
    engine.runAndWait()

# Callback to feed microphone to Vosk
def callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

def listen(model_path="vosk-model-small-en-us-0.15"):
    model = vosk.Model(model_path)
    rec = vosk.KaldiRecognizer(model, 16000)

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        speak("Piggy is listening...")
        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                return text

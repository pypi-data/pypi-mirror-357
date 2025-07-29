# Open the data.json , which contains the greet message
import speech_recognition as sr
import json
import re
import time
import pygame
from .piper_helper import get_text

# read the values from data.json . if not found please obtain it from the git repo.
try:
    with open("data.json", "r") as file:
        data = json.load(file)
except FileNotFoundError:
    data = {"greet_message": "default"}

_file = "piper_output.wav"


class Assistant:
    def __init__(self):
        self.name = data.get("name", "Assistant")

    def greet(self):
        try:
            self.speak(data["greet_message"])
            
        except Exception as e:
            print(f"Error in greeting: {e}")
            self.speak("Hello, how can I assist you today?")

    def listen(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print(data["listen_text"])
            if data["pause_threshold"] == "default":
                recognizer.pause_threshold = 0.5
            else:
                recognizer.pause_threshold = float(data["pause_threshold"])
            audio = recognizer.listen(source, phrase_time_limit=4) 
        try:
            command = recognizer.recognize_google(audio, language='en-US')
            print(f"You : {command}")
            return command.lower()
        except sr.UnknownValueError:
            self.speak(data["failed_message"])
            return ""
        except sr.RequestError:
            self.speak("Speech service is unavailable.")
            return ""
    def _filter_text(self, text):
        # Remove unwanted characters
        clean_text = re.sub(r'[*_`~#>\\-]', '', text)
        # remove Emojis
        clean_text = re.sub(r'[\U00010000-\U0010ffff]', '', clean_text)
        # Break long text into 2-4 sentence chunks max
        sentences = [s.strip() for s in clean_text.replace('\n', ' ').split('.') if s.strip()]
        max_sentences = 4
        output_chunks = []
        chunk = []
        for sentence in sentences:
            chunk.append(sentence)
            if len(chunk) == max_sentences:
                output_chunks.append('. '.join(chunk) + '.')
                chunk = []
        if chunk:
            output_chunks.append('. '.join(chunk) + '.')
        return output_chunks
    
    def speak(self,text):
        clear_text = self._filter_text(text)
        for chunk_text in clear_text:
            print(f"{self.name}: {chunk_text}")
            # Send POST request to piper api. 
            try:
                response = get_text(chunk_text)
                if response.ok:
                    self._save_to_file(response)
                    self._play_audio(_file)
                else:
                    print("Piper error:", response.text)
            except Exception as e:
                print("Piper request failed:", e)
    def _save_to_file(self, response):
        with open(_file, "wb") as f:
            f.write(response.content)
            # Play the audio
    def _play_audio(self, _file):
        pygame.mixer.init()
        pygame.mixer.music.load(_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        pygame.mixer.quit()

if __name__ == "__main__":
    assistant = Assistant()
    assistant.greet()
    while True:
        speech = assistant.listen()
        if speech:
            assistant.speak(f"You : {speech}")
        else:
            assistant.speak(data["failed_message"])
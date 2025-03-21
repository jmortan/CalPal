import json
from openai import OpenAI
import wave
import pyaudio


class SpeechToTextModule():
    def __init__(self):
        f = open('./state_data/open_ai_token.json')
        self.api_token = json.load(f)['goal_requestor_token']
        self.client = OpenAI(api_key=self.api_token) 

    
    def speech_to_text(self, audio_file):
        audio_file= open(audio_file, "rb")
        transcription = self.client.audio.transcriptions.create(
            model="whisper-1", 
            temperature=.2,
            file=audio_file
        )
        return transcription.text
    
    def record_audio(self, filename, duration):
        # Parameters for audio recording
        RATE = 16000
        CHANNELS = 1
        FORMAT = pyaudio.paInt16
        FRAMES_PER_BUFFER = 1024

        p = pyaudio.PyAudio()
        
        # Start recording
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=FRAMES_PER_BUFFER)

        print("Recording...", flush=True)

        frames = []

        for _ in range(0, int(RATE / FRAMES_PER_BUFFER * duration)):
            data = stream.read(FRAMES_PER_BUFFER)
            frames.append(data)

        print("Recording finished.", flush=True)
        
        # Stop recording
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Save recorded audio to a .wav file
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

    def main(self):
        audio_filename = "./state_data/recorded_audio.wav"
        self.record_audio(audio_filename, 10)
        text = self.speech_to_text(audio_filename)
        print(text)
        

if __name__ == "__main__":
    module = SpeechToTextModule()
    module.main()
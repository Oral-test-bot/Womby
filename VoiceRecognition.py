from streamlit.runtime.uploaded_file_manager import UploadedFile
import wave
from vosk import Model, KaldiRecognizer
from constants import VOICE_MODEL_PATH
import json
from openai import OpenAI

class VoiceRecognition:
    """
    Class to transcribe audio files to text
    """
    def to_text(self, wavefile: str | UploadedFile, client: OpenAI):
        """
        Transcribe the audio file to text
        """

        return self.whisper_to_text(wavefile, client)

    def vosk_to_text(self, wavefile: str | UploadedFile):
        """
        Transcribe the audio file to text using Vosk
        """

        model = Model(VOICE_MODEL_PATH)

        with wave.open(wavefile, "rb") as wf:
            rec = KaldiRecognizer(model, wf.getframerate())
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    pass
            result = json.loads(rec.FinalResult())
            return result["text"]
        

    def whisper_to_text(self, wavefile: str | UploadedFile, client: OpenAI):
        """
        Transcribe the audio file to text using OpenAI
        """
        transcription = client.audio.transcriptions.create(
            file=wavefile,
            model="whisper-1"
        )
        return transcription.text

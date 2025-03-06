from streamlit.runtime.uploaded_file_manager import UploadedFile
import wave
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
        

    def whisper_to_text(self, wavefile: str | UploadedFile, client: OpenAI):
        """
        Transcribe the audio file to text using OpenAI
        """
        transcription = client.audio.transcriptions.create(
            file=wavefile,
            model="whisper-1",
            language="en",
        )
        return transcription.text

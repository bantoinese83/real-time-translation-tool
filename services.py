import logging
import os
import re
import signal
import sys
import uuid

import google.generativeai as genai
import speech_recognition as sr
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from google.generativeai.types import GenerationConfig
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()

# Configure Google Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

generation_config = GenerationConfig(
    temperature=1,
    top_p=0.95,
    top_k=64,
    max_output_tokens=8192,
    response_mime_type="text/plain",
)

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Configure Eleven Labs API
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable not set")

elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)


class RealTimeTranslationTool:
    def __init__(self, src_lang='en', dest_lang='es', voice_id='pNInz6obpgDQGcFmaJgB', output_format='mp3',
                 mode='formal'):
        self.recognizer = sr.Recognizer()
        self.translator = GoogleTranslator(source=src_lang, target=dest_lang)
        self.src_lang = src_lang
        self.dest_lang = dest_lang
        self.voice_id = voice_id
        self.output_format = output_format
        self.mode = mode
        signal.signal(signal.SIGINT, self.exit_gracefully)

    def recognize_speech(self):
        with sr.Microphone() as source:
            logging.info("Listening...")
            audio = self.recognizer.listen(source)
            try:
                text = self.recognizer.recognize_google(audio, language=self.src_lang)
                logging.info(f"Recognized: {text}")
                return text
            except sr.UnknownValueError:
                logging.error("Could not understand audio")
            except sr.RequestError as e:
                logging.error(f"Could not request results from Google Speech Recognition service; {e}")
            except Exception as e:
                logging.error(f"Unexpected error during speech recognition: {e}")
            return None

    def translate_text(self, text):
        try:
            # Generate a clearer and more concise version of the text using LLM
            chat_session = model.start_chat(history=[])
            if self.mode == 'slang':
                prompt = (f"Refine the following text into clear, concise street urban slang suitable for spoken "
                          f"translation: {text}")
            else:
                prompt = (f"Refine the following text into clear, concise formal professional language suitable for "
                          f"spoken translation: {text}")
            response = chat_session.send_message(prompt)
            refined_text = response.text
            logging.info(f"Refined: {refined_text}")

            # Translate the refined text using Google Translate
            translated_text = self.translator.translate(refined_text)
            logging.info(f"Translated: {translated_text}")

            # Clean up the translated text
            cleaned_text = re.sub(r'[^\w\s]', '', translated_text)
            logging.info(f"Cleaned: {cleaned_text}")
            return cleaned_text
        except Exception as e:
            logging.error(f"Translation error: {e}")
            return None

    def speak_text(self, text):
        try:
            # Calling the text_to_speech conversion API with detailed parameters
            response = elevenlabs_client.text_to_speech.convert(
                voice_id=self.voice_id,
                optimize_streaming_latency="0",
                output_format="mp3_22050_32",
                text=text,
                model_id="eleven_turbo_v2",
                voice_settings=VoiceSettings(
                    stability=0.0,
                    similarity_boost=1.0,
                    style=0.0,
                    use_speaker_boost=True,
                ),
            )

            # Create directory if it doesn't exist
            output_dir = "output_audio"
            os.makedirs(output_dir, exist_ok=True)

            # Generate a file name that includes the source and destination languages
            file_name = f"{uuid.uuid4()}_{self.src_lang}_to_{self.dest_lang}.mp3"
            save_file_path = os.path.join(output_dir, file_name)

            # Writing the audio stream to the file
            with open(save_file_path, "wb") as f:
                for chunk in tqdm(response, desc="Saving audio", unit="chunk"):
                    if chunk:
                        f.write(chunk)

            logging.info(f"A new audio file was saved successfully at {save_file_path}")
            os.system(f"mpg321 {save_file_path}")  # Install mpg321: sudo apt-get install mpg321
        except FileNotFoundError as e:
            logging.error(f"File not found error: {e}")
        except PermissionError as e:
            logging.error(f"Permission error: {e}")
        except Exception as e:
            logging.error(f"Speech synthesis error: {e}")

    def run(self):
        while True:
            text = self.recognize_speech()
            if text:
                translated_text = self.translate_text(text)
                if translated_text:
                    self.speak_text(translated_text)

    @staticmethod
    def exit_gracefully(signum, frame):
        logging.info("Exiting gracefully...")
        sys.exit(0)


if __name__ == "__main__":
    tool = RealTimeTranslationTool(src_lang='en', dest_lang='ko', mode='formal')
    tool.run()

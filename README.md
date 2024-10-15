# Real-Time Translation Tool

This project is a real-time translation tool that listens to speech, translates it into another language, and then speaks the translated text. It uses various APIs and libraries to achieve this functionality.

## Features

- **Speech Recognition**: Uses Google Speech Recognition to convert spoken words into text.
- **Text Refinement**: Uses Google Gemini API to refine the text into either formal or slang language.
- **Translation**: Uses Google Translate to translate the refined text into the target language.
- **Text-to-Speech**: Uses Eleven Labs API to convert the translated text into speech.
- **Progress Loader**: Displays a progress bar while saving the audio file.

## Requirements

- Python 3.6+
- `tqdm` library for progress bars
- `speech_recognition` library for speech recognition
- `deep_translator` library for translation
- `dotenv` library for loading environment variables
- `elevenlabs` library for text-to-speech conversion
- `google-generativeai` library for text refinement

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/real-time-translation-tool.git
   cd real-time-translation-tool
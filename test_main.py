import asyncio

import numpy as np
import speech_recognition as sr
import websockets


async def test_translation(uri, audio_data):
    async with websockets.connect(uri) as websocket:
        print("Connected to WebSocket server")

        # Convert the audio data to bytes before sending
        audio_data_bytes = audio_data.get_raw_data()
        await websocket.send(audio_data_bytes)
        print("Sent audio data")

        try:
            translated_text = await websocket.recv()
            print(f"Translated Text: {translated_text}")
        except websockets.exceptions.ConnectionClosedOK:
            print("Connection closed normally")


# Example audio data (replace with actual audio data)
audio_data_en_to_ko = np.random.bytes(32000)  # Simulated audio data for English to Korean
audio_data_ko_to_en = np.random.bytes(32000)  # Simulated audio data for Korean to English
audio_data_en_to_fr = np.random.bytes(32000)  # Simulated audio data for English to French
audio_data_fr_to_en = np.random.bytes(32000)  # Simulated audio data for French to English

# Create AudioData instances
audio_data_en_to_ko = sr.AudioData(audio_data_en_to_ko, 16000, 2)  # Assuming 16kHz sampling rate and 2 channels
audio_data_ko_to_en = sr.AudioData(audio_data_ko_to_en, 16000, 2)  # Assuming 16kHz sampling rate and 2 channels
audio_data_en_to_fr = sr.AudioData(audio_data_en_to_fr, 16000, 2)  # Assuming 16kHz sampling rate and 2 channels
audio_data_fr_to_en = sr.AudioData(audio_data_fr_to_en, 16000, 2)  # Assuming 16kHz sampling rate and 2 channels

# WebSocket server URI
uri = "ws://localhost:8000/ws"

# Run the tests
asyncio.run(test_translation(uri, audio_data_en_to_ko))
asyncio.run(test_translation(uri, audio_data_ko_to_en))
asyncio.run(test_translation(uri, audio_data_en_to_fr))
asyncio.run(test_translation(uri, audio_data_fr_to_en))

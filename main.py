import logging

import numpy as np
import speech_recognition as sr
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from services import RealTimeTranslationTool

app = FastAPI()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

translation_tool = RealTimeTranslationTool(src_lang='en', dest_lang='ko', mode='formal')


class ConnectionManager:
    def __init__(self):
        self.active_connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logging.info(f"WebSocket connection established: {websocket}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logging.info(f"WebSocket connection closed: {websocket}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
                logging.info(f"Broadcast message: {message} to {connection}")
            except WebSocketDisconnect:
                logging.info(f"Client {connection} disconnected during broadcast")
            except Exception as e:
                logging.error(f"Error during broadcast: {e}")


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_bytes()
            logging.info("Received audio data from client")
            audio_data: np.ndarray = np.frombuffer(data, dtype=np.int16)
            audio_data = sr.AudioData(audio_data.tobytes(), 16000, 2)
            text = translation_tool.recognize_speech(audio_data)
            if text:
                logging.info(f"Recognized text: {text}")
                translated_text = translation_tool.translate_text(text)
                if translated_text:
                    logging.info(f"Translated text: {translated_text}")
                    await manager.broadcast(translated_text)
    except WebSocketDisconnect:
        logging.info("Client disconnected")
        manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")


# Define a route for sending a status message
@app.get("/status")
async def status():
    return JSONResponse({"status": "OK"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

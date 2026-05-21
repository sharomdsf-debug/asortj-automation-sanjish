import os
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from google.genai import types

app = FastAPI()

# Иҷозат додани пайвастшавӣ аз телефон ва браузерҳо
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Калиди API мустақиман дар код гузошта шуд, то хатогӣ нашавад
GEMINI_API_KEY = "AIzaSyApPuYT4dG8FInQm8d8Y119tw9la5F2XzU"
client = genai.Client(api_key=GEMINI_API_KEY, http_options={"api_version": "v1beta"})

@app.websocket("/ws/voice")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    config = types.LiveConnectConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Zephyr")
            )
        ),
        system_instruction=types.Content(
            parts=[types.Part.from_text(text="Ту як ёвари варзишӣ ҳастӣ. Танҳо ба забони форсӣ ва тоҷикӣ дар бораи варзиш гап мезанӣ. Ба дигар мавзӯъҳо ҷавоб надеҳ.")],
            role="user"
        )
    )
    
    async with client.aio.live.connect(model="models/gemini-2.0-flash-exp", config=config) as session:
        async def receive_from_client():
            try:
                while True:
                    data = await websocket.receive_bytes()
                    await session.send(input={"data": data, "mime_type": "audio/pcm;rate=16000"})
            except Exception: pass

        async def send_to_client():
            try:
                while True:
                    turn = session.receive()
                    async for response in turn:
                        if response.data:
                            await websocket.send_bytes(response.data)
            except Exception: pass

        await asyncio.gather(receive_from_client(), send_to_client())
        

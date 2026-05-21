import os
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from google import genai
from google.genai import types

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

GEMINI_API_KEY = "AIzaSyApPuYT4dG8FInQm8d8Y119tw9la5F2XzU"
client = genai.Client(api_key=GEMINI_API_KEY)

@app.post("/voice-chat")
async def voice_chat(file: UploadFile = File(...)):
    # Хондани овози фиристодаи корбар
    audio_bytes = await file.read()
    
    # Танзими дастури бот
    config = types.GenerateContentConfig(
        response_modalities=["AUDIO"],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Zephyr")
            )
        ),
        system_instruction="Ту як ёвари варзишӣ ҳастӣ. Танҳо ба забони форсӣ ва тоҷикӣ кӯтоҳ ҷавоб деҳ."
    )
    
    # Фиристодани овоз ба Gemini
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[
            types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav"),
            "Ҷавобро танҳо бо овоз гардон."
        ],
        config=config
    )
    
    # Ёфтани байтҳои овози ҷавоби Gemini
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            return Response(content=part.inline_data.data, media_type="audio/mp3")
            
    return {"error": "No audio response"}
    

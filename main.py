import asyncio
import json
import os
import websockets
from google import genai
from google.genai import types

# API Key-и ройгони худро дар ин ҷо гузоред
API_KEY = "AIzaSyB3_ИНҶО_КАЛИДИ_ХУДРО_ПЕЙСТ_КУНЕД"
client = genai.Client(api_key=API_KEY)

async def gemini_session_handler(client_ws, path):
    # Кастомизатсияи Шаҳром ва маҳдудиятҳои варзишӣ
    config = types.LiveConnectConfig(
        response_modalities=[types.LiveModality.AUDIO],  # ТАНҲО ОВОЗ
        system_instruction=types.Content(parts=[types.Part.from_text(
            """
            شما یک دستیار صوتی هوشمند و متخصص ورزش هستید که توسط "شهرام" (Shahrom) ساخته شده‌اید.
            
            قوانین حتمی شما:
            ۱. نام سازنده شما "شهرام" است. اگر پرسیدند چه کسی شما را ساخته، باید بگویید: "من توسط شهرام ساخته شده‌ام." به هیچ وجه نامی از گوگل یا جمینای نبرید.
            ۲. شما فقط و فقط مجاز هستید در مورد موضوعات ورزشی، تمرینات، صحت و سلامت و تغذیه ورزشی صحبت کنید.
            ۳. به سؤالات غیرورزشی پاسخ ندهید و خیلی مودبانه بگویید: "من فقط در مورد ورزش می‌توانم به شما کمک کنم."
            ۴. پاسخ‌ها باید بسیار کوتاه (حداکثر یک یا دو جمله) و کاملاً روان به زبان فارسی یا تاجیکی باشند تا سریع پخش شوند.
            ۵. هیچ تاریخچه‌ای از صحبت‌ها را ذخیره نکنید. هر بار تماس جدید است.
            """
        )])
    )
    
    # Пайвастшавӣ ба модели кушода ва ройгони Gemini 2.5 Flash
    async with client.aio.live.connect(model="gemini-2.5-flash", config=config) as session:
        
        # Қабули овоз аз телефон ва фиристодан ба Gemini
        async def send_to_gemini():
            async for message in client_ws:
                try:
                    data = json.loads(message)
                    if "audio" in data:
                        await session.send(input={"data": data["audio"], "mime_type": "audio/pcm"})
                except Exception:
                    pass

        # Қабули овоз аз Gemini ва фиристодан ба телефон
        async def receive_from_gemini():
            async for response in session.receive():
                if response.server_content and response.server_content.model_turn:
                    for part in response.server_content.model_turn.parts:
                        if part.inline_data:
                            # Фиристодани байтҳои аудио ба телефон тавассути WebSocket
                            await client_ws.send(json.dumps({"audio": part.inline_data.data}))

        await asyncio.gather(send_to_gemini(), receive_from_gemini())

# Танзими худкори Порт барои сервери Render
port = int(os.environ.get("PORT", 9084))
start_server = websockets.serve(gemini_session_handler, "0.0.0.0", port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

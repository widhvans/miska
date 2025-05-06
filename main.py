from fastapi import FastAPI, Request
from pydantic import BaseModel
import telegram
from config import TELEGRAM_TOKEN
from bot import generate_response
import asyncio

app = FastAPI()

class Message(BaseModel):
    chat_id: int
    text: str

async def send_message(chat_id: int, text: str):
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=chat_id, text=text)

@app.post("/api/message")
async def handle_message(message: Message):
    response = await generate_response(message.text)
    await send_message(message.chat_id, response)
    return {"status": "success", "response": response}

if __name__ == "__main__":
    import uvicorn
    from config import API_HOST, API_PORT
    uvicorn.run(app, host=API_HOST, port=API_PORT)

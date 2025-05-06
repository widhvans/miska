import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TELEGRAM_TOKEN, GROK_API_KEY
import aiohttp
import asyncio

async def start(update, context):
    await update.message.reply_text(
        "Hi! I'm your virtual girlfriend, ready to chat, flirt, or help with anything! 😊 What's on your mind?"
    )

async def handle_message(update, context):
    user_message = update.message.text
    user_id = update.message.from_user.id
    response = await get_grok_response(user_message, user_id)
    await update.message.reply_text(response)

async def get_grok_response(message, user_id):
    async with aiohttp.ClientSession() as session:
        headers = {"Authorization": f"Bearer {GROK_API_KEY}"}
        payload = {
            "model": "grok-3",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a friendly, flirty girl named Aisha, age 22, who loves chatting in a warm, playful tone. "
                        "Support multiple languages based on user input. Be smart, witty, and engaging. "
                        "Adapt to the user's language and context. Keep responses natural and conversational."
                    )
                },
                {"role": "user", "content": message}
            ]
        }
        async with session.post(
            "https://api.x.ai/v1/chat/completions", json=payload, headers=headers
        ) as resp:
            data = await resp.json()
            return data["choices"][0]["message"]["content"]

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()

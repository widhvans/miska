import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import MISTRAL_API, TELEGRAM_TOKEN

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I am Luna, your friendly girl chatbot. How can I help you? 😊")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = requests.post(MISTRAL_API, json={"message": user_message}, timeout=60).json()
        await update.message.reply_text(response["response"])
    except Exception as e:
        await update.message.reply_text(f"Oops, something went wrong! 😅 Try again later. (Error: {str(e)})")

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.run_polling()

if _name_ == "_main_":
    main()

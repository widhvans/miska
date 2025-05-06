import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from config import BOT_TOKEN, API_URL

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the /start command."""
    await update.message.reply_text(
        "Hi! I'm powered by Mistral 7B. Ask me anything in Hindi or English."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages."""
    user_message = update.message.text
    try:
        # Send message to FastAPI server
        response = requests.post(API_URL, json={"prompt": user_message}, timeout=10)
        response.raise_for_status()
        reply = response.json().get("response", "Sorry, something went wrong.")
    except requests.RequestException as e:
        reply = f"Error: Unable to connect to the API. Please try again later. ({str(e)})"
    await update.message.reply_text(reply)

def main():
    """Run the bot."""
    # Create the Application with the bot token
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

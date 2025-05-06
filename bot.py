import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import MISTRAL_API, TELEGRAM_TOKEN

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),  # Log to file
        logging.StreamHandler()          # Log to console
    ]
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Received /start command from user {update.effective_user.id}")
    await update.message.reply_text("Hello! I am Luna, your friendly girl chatbot. How can I help you? 😊")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"Received message: {user_message}")
    try:
        response = requests.post(MISTRAL_API, json={"message": user_message}, timeout=10)
        response.raise_for_status()
        data = response.json()
        logger.info(f"API response: {data}")
        await update.message.reply_text(data["response"])
    except requests.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        await update.message.reply_text(f"Oops, something went wrong! 😅 Try again later. (Error: {str(e)})")

def main():
    logger.info("Starting bot...")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    logger.info("Bot polling started")
    app.run_polling()

if __name__ == "__main__":
    main()

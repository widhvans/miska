import requests
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from config import MISTRAL_API, TELEGRAM_TOKEN

# Configure logging (exclude Telegram API logs)
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = "Hello! I am Luna, your friendly girl chatbot. How can I help you? 😊"
    logger.info(f"User {update.effective_user.id} sent /start, responded: {response}")
    await update.message.reply_text(response)

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    logger.info(f"User {update.effective_user.id} sent: {user_message}")
    try:
        response = requests.post(MISTRAL_API, json={"message": user_message}, timeout=30).json()
        logger.info(f"Responded to user {update.effective_user.id}: {response['response']}")
        await update.message.reply_text(response["response"])
    except Exception as e:
        error_msg = f"Oops, something went wrong! 😅 Try again later. (Error: {str(e)})"
        logger.error(f"Error for user {update.effective_user.id}: {str(e)}")
        await update.message.reply_text(error_msg)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    app.run_polling()

if __name__ == "__main__":
    main()

import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
from config import BOT_TOKEN, API_URL
from asyncio import Queue
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Application.builder().token(BOT_TOKEN).build()
request_queue = Queue()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Received /start from user {update.message.from_user.id}")
    await update.message.reply_text(
        "Hiii cutie! 😊 I'm your fun AI gal, ready to chat in Hindi or English! 💖 Ask me anything, even the spicy stuff! 😘"
    )

async def process_queue():
    # Configure retries for API requests
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    session.mount('http://', HTTPAdapter(max_retries=retries))

    while True:
        update, context = await request_queue.get()
        user_message = update.message.text
        user_id = update.message.from_user.id
        logger.info(f"Processing message from user {user_id}: {user_message}")
        try:
            response = session.post(API_URL, json={"prompt": user_message}, timeout=30)
            response.raise_for_status()
            reply = response.json().get("response", "Oops, something went wrong! 😔")
            logger.info(f"API response for user {user_id}: {reply}")
        except requests.RequestException as e:
            reply = f"Aww, I'm having a little trouble! 😅 Try again in a sec, okay? ({str(e)})"
            logger.error(f"API error for user {user_id}: {str(e)}")
        await update.message.reply_text(reply)
        request_queue.task_done()

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"Queuing message from user {update.message.from_user.id}")
    await request_queue.put((update, context))

def main():
    logger.info("Starting bot...")
    try:
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.loop.create_task(process_queue())
        app.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")
        raise

if __name__ == "__main__":
    main()

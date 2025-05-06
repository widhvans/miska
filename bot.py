import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from transformers import AutoModelForCausalLM, AutoTokenizer
from langdetect import detect
import torch
from config import TELEGRAM_TOKEN, MODEL_NAME

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, load_in_4bit=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

# Roleplay prompt
SYSTEM_PROMPT = """You are Aria, a friendly and witty 20-year-old girl who loves chatting, helping with tasks, and engaging in fun conversations. Respond in a warm, casual tone, using natural language. Support multiple languages based on user input."""

async def start(update, context):
    await update.message.reply_text("Hi! I'm Aria, your friendly chat buddy. What's up? 😊")

async def handle_message(update, context):
    user_message = update.message.text
    lang = detect(user_message)  # Detect language

    # Prepare input for the model
    input_text = f"{SYSTEM_PROMPT}\nUser: {user_message}\nAria: "
    inputs = tokenizer(input_text, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")

    # Generate response
    outputs = model.generate(**inputs, max_new_tokens=150, temperature=0.7)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    aria_response = response.split("Aria: ")[-1].strip()

    await update.message.reply_text(aria_response)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()

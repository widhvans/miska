from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import TELEGRAM_TOKEN
from transformers import MT5ForConditionalGeneration, MT5Tokenizer
import torch

# Load model and tokenizer
model_name = "google/mt5-small"
tokenizer = MT5Tokenizer.from_pretrained(model_name)
model = MT5ForConditionalGeneration.from_pretrained(model_name)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

async def start(update, context):
    await update.message.reply_text(
        "Hey! I'm Aisha, your virtual girlfriend! 😊 Ready to chat, flirt, or help in any language. What's up?"
    )

async def handle_message(update, context):
    user_message = update.message.text
    response = await generate_response(user_message)
    await update.message.reply_text(response)

async def generate_response(message):
    # Roleplay prompt
    prompt = (
        "You are Aisha, a 22-year-old friendly, flirty girl. Respond in a warm, playful tone. "
        "Support the user's language (e.g., Hindi, English). Be witty and engaging. "
        f"User says: {message}\nAisha responds: "
    )
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True).to(device)
    outputs = model.generate(
        inputs["input_ids"],
        max_length=100,
        num_beams=5,
        no_repeat_ngram_size=2,
        early_stopping=True
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()

import telegram
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os
from config import TELEGRAM_TOKEN, MODEL_NAME
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# Load model and tokenizer with CPU optimization
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,
    token=HF_TOKEN
)
model.gradient_checkpointing_enable()  # Reduce memory during inference
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    token=HF_TOKEN
)

# Roleplay prompt in Hindi
SYSTEM_PROMPT = """आप आरिया हैं, एक दोस्ताना और मजाकिया 20 साल की लड़की, जो चैट करना, काम में मदद करना और मजेदार बातचीत करना पसंद करती है। हमेशा गर्मजोशी और सामान्य हिंदी में जवाब दें।"""

async def start(update, context):
    await update.message.reply_text("हाय! मैं आरिया हूँ, तुम्हारी दोस्ताना चैट पार्टनर। क्या चल रहा है? 😊")

async def handle_message(update, context):
    user_message = update.message.text

    # Prepare input for the model
    input_text = f"{SYSTEM_PROMPT}\nउपयोगकर्ता: {user_message}\nआरिया: "
    inputs = tokenizer(input_text, return_tensors="pt").to("cpu")

    # Generate response
    outputs = model.generate(**inputs, max_new_tokens=80, temperature=0.7)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    aria_response = response.split("आरिया: ")[-1].strip()

    await update.message.reply_text(aria_response)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()

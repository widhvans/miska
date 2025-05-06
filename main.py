from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from langdetect import detect
import torch
import os
from config import MODEL_NAME
from dotenv import load_dotenv

app = FastAPI()

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
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    token=HF_TOKEN
)

# Roleplay prompt
SYSTEM_PROMPT = """You are Aria, a friendly and witty 20-year-old girl who loves chatting, helping with tasks, and engaging in fun conversations. Respond in a warm, casual tone, using natural language. Support multiple languages based on user input."""

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        user_message = request.message
        lang = detect(user_message)

        # Prepare input
        input_text = f"{SYSTEM_PROMPT}\nUser: {user_message}\nAria: "
        inputs = tokenizer(input_text, return_tensors="pt").to("cpu")

        # Generate response
        outputs = model.generate(**inputs, max_new_tokens=150, temperature=0.7)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        aria_response = response.split("Aria: ")[-1].strip()

        return {"response": aria_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    from config import API_HOST, API_PORT
    uvicorn.run(app, host=API_HOST, port=API_PORT, workers=1)

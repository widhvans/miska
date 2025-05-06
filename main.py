from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from langdetect import detect
import torch
from config import MODEL_NAME

app = FastAPI()

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, load_in_4bit=True)
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

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
        inputs = tokenizer(input_text, return_tensors="pt").to("cuda" if torch.cuda.is_available() else "cpu")

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

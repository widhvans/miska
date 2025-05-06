from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
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
model.gradient_checkpointing_enable()  # Reduce memory during inference
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    token=HF_TOKEN
)

# Roleplay prompt in Hindi
SYSTEM_PROMPT = """आप आरिया हैं, एक दोस्ताना और मजाकिया 20 साल की लड़की, जो चैट करना, काम में मदद करना और मजेदार बातचीत करना पसंद करती है। हमेशा गर्मजोशी और सामान्य हिंदी में जवाब दें।"""

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        user_message = request.message

        # Prepare input
        input_text = f"{SYSTEM_PROMPT}\nउपयोगकर्ता: {user_message}\nआरिया: "
        inputs = tokenizer(input_text, return_tensors="pt").to("cpu")

        # Generate response
        outputs = model.generate(**inputs, max_new_tokens=60, temperature=0.7)
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        aria_response = response.split("आरिया: ")[-1].strip()

        return {"response": aria_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    from config import API_HOST, API_PORT
    uvicorn.run(app, host=API_HOST, port=API_PORT, workers=1)

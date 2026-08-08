import os
import json
import base64
import asyncio
from io import BytesIO
from typing import Optional, List
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

import torch
import requests
from PIL import Image
import numpy as np
import cv2

try:
    import ollama
except ImportError:
    ollama = None

try:
    from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
except ImportError:
    pass

try:
    from transformers import AutoProcessor, AutoModelForCausalLM
except ImportError:
    pass

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    pass

app = FastAPI(title="LocalAI Advanced", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODELS_DIR = Path.home() / "LocalAI" / "models"
MODELS_DIR.mkdir(parents=True, exist_ok=True)

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")

llm_model = "dolphin-mixtral"
sd_model = None
vision_model = None
embedding_model = None
conversation_history = []

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 2048
    system: Optional[str] = None
    keep_history: bool = True

class ImageGenRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    num_inference_steps: int = 30
    guidance_scale: float = 7.5
    height: int = 512
    width: int = 512
    seed: Optional[int] = None

class VisionRequest(BaseModel):
    image_base64: str
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 1024

class EmbeddingRequest(BaseModel):
    text: str

class CodeExecutionRequest(BaseModel):
    code: str
    language: str = "python"

class RAGRequest(BaseModel):
    query: str
    documents: List[str]
    top_k: int = 3

@app.on_event("startup")
async def startup_event():
    global sd_model, vision_model, embedding_model
    print("LocalAI Advanced starting up...")
    
    if ollama is None:
        print("WARNING: Ollama not installed. Install from https://ollama.ai")
    
    try:
        print(f"Loading Stable Diffusion model...")
        sd_model = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            safety_checker=None,
        )
        sd_model.scheduler = DPMSolverMultistepScheduler.from_config(sd_model.scheduler.config)
        sd_model = sd_model.to(DEVICE)
        print("Stable Diffusion loaded")
    except Exception as e:
        print(f"Could not load Stable Diffusion: {e}")
    
    try:
        print("Loading embedding model...")
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device=DEVICE)
        print("Embedding model loaded")
    except Exception as e:
        print(f"Could not load embedding model: {e}")

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "device": DEVICE,
        "cuda_available": torch.cuda.is_available(),
        "models": {
            "llm": llm_model,
            "sd": "stable-diffusion-v1-5" if sd_model else None,
            "embeddings": "all-MiniLM-L6-v2" if embedding_model else None,
        }
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    if ollama is None:
        raise HTTPException(status_code=503, detail="Ollama not installed")
    
    try:
        global conversation_history
        
        messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        if request.keep_history:
            conversation_history.extend(messages)
            messages = conversation_history
        
        if request.system:
            messages.insert(0, {"role": "system", "content": request.system})
        
        response = ollama.chat(
            model=llm_model,
            messages=messages,
            stream=False,
            options={
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            }
        )
        
        assistant_response = response["message"]["content"]
        
        if request.keep_history:
            conversation_history.append({"role": "assistant", "content": assistant_response})
        
        return {
            "response": assistant_response,
            "model": llm_model,
            "stop_reason": "stop"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/stream")
async def chat_stream(request: ChatRequest):
    if ollama is None:
        raise HTTPException(status_code=503, detail="Ollama not installed")
    
    async def generate():
        try:
            global conversation_history
            
            messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
            
            if request.keep_history:
                conversation_history.extend(messages)
                messages = conversation_history
            
            if request.system:
                messages.insert(0, {"role": "system", "content": request.system})
            
            response = ollama.chat(
                model=llm_model,
                messages=messages,
                stream=True,
                options={
                    "temperature": request.temperature,
                    "num_predict": request.max_tokens,
                }
            )
            
            full_response = ""
            for chunk in response:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    full_response += content
                    yield f"data: {json.dumps({'token': content})}\n\n"
            
            if request.keep_history:
                conversation_history.append({"role": "assistant", "content": full_response})
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")

@app.post("/chat/clear-history")
async def clear_history():
    global conversation_history
    conversation_history = []
    return {"status": "history cleared"}

@app.post("/generate-image")
async def generate_image(request: ImageGenRequest):
    if sd_model is None:
        raise HTTPException(status_code=503, detail="Stable Diffusion not loaded")
    
    try:
        if request.seed is not None:
            generator = torch.Generator(device=DEVICE).manual_seed(request.seed)
        else:
            generator = None
        
        with torch.no_grad():
            image = sd_model(
                prompt=request.prompt,
                negative_prompt=request.negative_prompt or "",
                height=request.height,
                width=request.width,
                num_inference_steps=request.num_inference_steps,
                guidance_scale=request.guidance_scale,
                generator=generator,
            ).images[0]
        
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "image": img_base64,
            "prompt": request.prompt,
            "model": "stable-diffusion-v1-5"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/embeddings")
async def get_embeddings(request: EmbeddingRequest):
    if embedding_model is None:
        raise HTTPException(status_code=503, detail="Embedding model not loaded")
    
    try:
        embedding = embedding_model.encode(request.text, convert_to_tensor=False)
        return {
            "embedding": embedding.tolist(),
            "model": "all-MiniLM-L6-v2",
            "dimension": len(embedding)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag")
async def rag_search(request: RAGRequest):
    if embedding_model is None:
        raise HTTPException(status_code=503, detail="Embedding model not loaded")
    
    try:
        query_embedding = embedding_model.encode(request.query, convert_to_tensor=False)
        
        doc_embeddings = [embedding_model.encode(doc, convert_to_tensor=False) for doc in request.documents]
        
        similarities = []
        for i, doc_emb in enumerate(doc_embeddings):
            similarity = np.dot(query_embedding, doc_emb) / (np.linalg.norm(query_embedding) * np.linalg.norm(doc_emb))
            similarities.append((i, similarity, request.documents[i]))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_results = similarities[:request.top_k]
        
        return {
            "query": request.query,
            "results": [{"index": idx, "score": float(score), "document": doc} for idx, score, doc in top_results]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute-code")
async def execute_code(request: CodeExecutionRequest):
    if request.language != "python":
        raise HTTPException(status_code=400, detail="Only Python supported")
    
    try:
        namespace = {"__builtins__": __builtins__}
        exec(request.code, namespace)
        
        output = namespace.get("output", "Code executed successfully")
        return {
            "output": str(output),
            "language": "python",
            "status": "success"
        }
    except Exception as e:
        return {
            "output": str(e),
            "language": "python",
            "status": "error"
        }

@app.get("/models/list")
async def list_models():
    if ollama is None:
        return {"models": []}
    
    try:
        response = ollama.list()
        return {"models": response}
    except Exception as e:
        return {"models": [], "error": str(e)}

@app.post("/models/pull")
async def pull_model(model_name: str):
    if ollama is None:
        raise HTTPException(status_code=503, detail="Ollama not installed")
    
    try:
        ollama.pull(model_name)
        return {"status": "success", "model": model_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/models/set")
async def set_model(model_name: str):
    global llm_model
    llm_model = model_name
    return {"status": "success", "model": llm_model}

@app.get("/")
async def root():
    return {
        "name": "LocalAI Advanced",
        "version": "2.0.0",
        "description": "Full-featured uncensored local AI with Mixtral, image generation, RAG, vision, embeddings, and code execution",
        "endpoints": {
            "chat": "POST /chat",
            "chat_stream": "POST /chat/stream",
            "chat_clear_history": "POST /chat/clear-history",
            "generate_image": "POST /generate-image",
            "embeddings": "POST /embeddings",
            "rag": "POST /rag",
            "execute_code": "POST /execute-code",
            "health": "GET /health",
            "models_list": "GET /models/list",
            "models_pull": "POST /models/pull",
            "models_set": "POST /models/set",
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

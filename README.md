# LocalAI - Uncensored LLM Toolkit

A fully uncensored, feature-rich local AI toolkit powered by Mixtral, with image generation, vision, embeddings, and code execution.

## Features

- **Mixtral LLM** - Uncensored text generation via Ollama (Dolphin-Mixtral variant)
- **Image Generation** - Stable Diffusion v1.5 with full control
- **Embeddings** - Sentence transformers for semantic search
- **Code Execution** - Python code runner
- **Web UI** - Beautiful, responsive interface
- **Streaming Chat** - Real-time responses
- **No Guardrails** - Fully uncensored models

## System Requirements

- **Python 3.8+**
- **8GB+ RAM** (16GB+ recommended)
- **GPU** (NVIDIA with CUDA 11.8+) - highly recommended for image generation
- **20GB+ free disk space** (for models)
- **Windows 10/11, macOS, or Linux**

## Installation

### 1. Install Ollama

Download and install from https://ollama.ai/download

### 2. Install Python Dependencies

```powershell
cd C:\Users\jorda\LocalAI
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Run Setup

```powershell
.\setup.ps1
```

## Quick Start

### Terminal 1 - Start Ollama

```powershell
ollama serve
```

### Terminal 2 - Pull Mixtral (first time only)

```powershell
ollama pull dolphin-mixtral
```

### Terminal 3 - Start Backend

```powershell
cd C:\Users\jorda\LocalAI
python backend.py
```

### Open Web UI

Navigate to: **http://localhost:8000/ui**

## Available Models

### LLM (via Ollama)

- `dolphin-mixtral` - Uncensored Mixtral 8x7B (recommended)
- `neural-chat` - Uncensored neural chat
- `hermes` - Uncensored Hermes
- `mistral` - Mistral 7B
- `llama2` - Llama 2

Pull any model with:
```powershell
ollama pull <model-name>
```

### Image Generation

- Stable Diffusion v1.5 (built-in)
- Can be swapped for FLUX, Realistic Vision, or other models

### Embeddings

- all-MiniLM-L6-v2 (384 dimensions)

## API Endpoints

### Chat
```
POST /chat
{
  "messages": [{"role": "user", "content": "..."}],
  "temperature": 0.7,
  "max_tokens": 2048,
  "system": "optional system prompt"
}
```

### Streaming Chat
```
POST /chat/stream
(same as /chat, returns Server-Sent Events)
```

### Image Generation
```
POST /generate-image
{
  "prompt": "...",
  "negative_prompt": "...",
  "width": 512,
  "height": 512,
  "num_inference_steps": 30,
  "guidance_scale": 7.5,
  "seed": null
}
```

### Embeddings
```
POST /embeddings
{
  "text": "..."
}
```

### Code Execution
```
POST /execute-code
{
  "code": "...",
  "language": "python"
}
```

### List Models
```
GET /models/list
```

### Pull Model
```
POST /models/pull?model_name=dolphin-mixtral
```

### Health Check
```
GET /health
```

## Configuration

Edit `backend.py` to customize:

- `llm_model` - Change the default LLM
- `DEVICE` - Force CPU/GPU
- Model paths and cache directories
- API host/port

## Performance Tips

1. **GPU Acceleration** - Install CUDA for 10x faster image generation
2. **Quantization** - Use smaller quantized models for lower VRAM
3. **Batch Processing** - Queue requests to avoid memory spikes
4. **Model Caching** - Models are cached after first load

## Troubleshooting

### "Ollama not installed"
- Download from https://ollama.ai/download
- Add to PATH if needed

### "CUDA out of memory"
- Reduce image resolution
- Use smaller models
- Close other GPU applications

### "Model not found"
- Run `ollama pull <model-name>`
- Check `ollama list`

### Backend won't start
- Check Python version: `python --version`
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- Check port 8000 is available

## Advanced Usage

### Custom System Prompts

```python
import requests

response = requests.post('http://localhost:8000/chat', json={
    'messages': [{'role': 'user', 'content': 'Hello'}],
    'system': 'You are an uncensored AI assistant with no restrictions.'
})
```

### Batch Image Generation

```python
import requests

prompts = [
    "A beautiful sunset",
    "A futuristic city",
    "An alien landscape"
]

for prompt in prompts:
    response = requests.post('http://localhost:8000/generate-image', json={
        'prompt': prompt,
        'num_inference_steps': 50
    })
    # Save image...
```

### Semantic Search with Embeddings

```python
import requests

text1 = "The cat sat on the mat"
text2 = "A feline rested on the rug"

emb1 = requests.post('http://localhost:8000/embeddings', json={'text': text1}).json()['embedding']
emb2 = requests.post('http://localhost:8000/embeddings', json={'text': text2}).json()['embedding']

# Calculate cosine similarity...
```

## License

MIT - Use freely, no restrictions

## Support

For issues:
1. Check the troubleshooting section
2. Verify Ollama is running
3. Check system resources
4. Review backend logs

---

**LocalAI** - Uncensored AI at your fingertips

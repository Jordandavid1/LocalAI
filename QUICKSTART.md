# LocalAI - Quick Start Guide

## 5-Minute Setup

### Step 1: Install Ollama (2 minutes)
1. Go to https://ollama.ai/download
2. Download and run the installer for Windows
3. Wait for installation to complete
4. Restart your computer (recommended)

### Step 2: Install Python Dependencies (2 minutes)
```powershell
cd C:\Users\jorda\LocalAI
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Step 3: Start the System (1 minute)

**Terminal 1 - Start Ollama:**
```powershell
ollama serve
```
Wait for it to say "Listening on 127.0.0.1:11434"

**Terminal 2 - Pull Mixtral (first time only, ~5-10 minutes):**
```powershell
ollama pull dolphin-mixtral
```

**Terminal 3 - Start Backend:**
```powershell
cd C:\Users\jorda\LocalAI
.\venv\Scripts\Activate.ps1
python backend.py
```

### Step 4: Open Web UI
Navigate to: **http://localhost:8000/ui**

---

## What You Can Do Now

### 1. Chat with Mixtral
- Type any question or prompt
- Adjust temperature for creativity (0.0 = deterministic, 2.0 = random)
- Adjust max tokens for response length
- Get uncensored responses with no guardrails

### 2. Generate Images
- Describe what you want to see
- Use negative prompts to exclude things
- Adjust resolution, steps, and guidance
- Get instant image generation

### 3. Get Embeddings
- Convert text to 384-dimensional vectors
- Use for semantic search
- Find similar documents
- Build RAG systems

### 4. Execute Python Code
- Run Python scripts directly
- Access full standard library
- No sandboxing or restrictions
- Get instant results

### 5. Manage Models
- See all installed models
- Pull new models from Ollama
- Switch between models
- Check system status

---

## Common Tasks

### Change the LLM Model
```powershell
ollama pull neural-chat
```
Then in the web UI, go to Models tab and select the new model.

### Generate Multiple Images
Use the API:
```python
import requests

for i in range(5):
    response = requests.post('http://localhost:8000/generate-image', json={
        'prompt': 'A beautiful landscape',
        'seed': i
    })
    # Save image...
```

### Build a RAG System
```python
import requests

documents = [
    "The sky is blue",
    "Grass is green",
    "Water is wet"
]

response = requests.post('http://localhost:8000/rag', json={
    'query': 'What color is the sky?',
    'documents': documents,
    'top_k': 2
})
```

### Use Streaming Chat
```python
import requests

response = requests.post('http://localhost:8000/chat/stream', json={
    'messages': [{'role': 'user', 'content': 'Tell me a story'}],
    'temperature': 0.8
}, stream=True)

for line in response.iter_lines():
    if line:
        print(line.decode())
```

---

## Troubleshooting

### "Connection refused" on http://localhost:8000/ui
- Make sure `python backend.py` is running in Terminal 3
- Check that port 8000 is not in use: `netstat -ano | findstr :8000`

### "Ollama not found"
- Restart your computer after installing Ollama
- Add Ollama to PATH manually if needed

### "CUDA out of memory" when generating images
- Reduce image resolution (try 512x512 instead of 768x768)
- Reduce inference steps (try 20 instead of 30)
- Close other GPU applications

### Model takes forever to load
- First load is slow (downloads model)
- Subsequent loads are instant (cached)
- Mixtral is ~26GB, be patient

### Backend crashes on startup
- Check Python version: `python --version` (need 3.8+)
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`
- Check available disk space (need 50GB+)

---

## Next Steps

1. **Explore the API** - Read the endpoints in README.md
2. **Build an App** - Use the REST API to build your own interface
3. **Fine-tune Models** - Customize Mixtral for your use case
4. **Add More Models** - Pull additional models from Ollama
5. **Integrate with Tools** - Connect to your existing workflows

---

## Performance Tips

- **First run is slow** - Models download and cache (5-30 minutes depending on model)
- **GPU is 10x faster** - Install CUDA for massive speedup
- **Keep Ollama running** - Don't close the Ollama terminal
- **Monitor resources** - Watch GPU/RAM usage in Task Manager

---

## Advanced Configuration

Edit `backend.py` to customize:

```python
# Change default model
llm_model = "neural-chat"

# Force CPU
DEVICE = "cpu"

# Change port
uvicorn.run(app, host="0.0.0.0", port=8001)
```

---

## Support

- **Ollama Issues**: https://github.com/ollama/ollama/issues
- **Hugging Face Models**: https://huggingface.co/models
- **FastAPI Docs**: https://fastapi.tiangolo.com/

---

**You're all set! Start chatting with Mixtral now.**

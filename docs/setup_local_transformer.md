# PakBot Local Transformer Setup (Qwen1.5-7B-Chat)

This script will install all dependencies and download the Qwen1.5-7B-Chat model for local, free, multilingual transformer-based chat.

## 1. Install Python dependencies
pip install transformers accelerate torch

## 2. Download the Qwen1.5-7B-Chat model (first run may take a while)
python -c "from transformers import AutoTokenizer, AutoModelForCausalLM; AutoTokenizer.from_pretrained('Qwen/Qwen1.5-7B-Chat'); AutoModelForCausalLM.from_pretrained('Qwen/Qwen1.5-7B-Chat')"

## 3. Update your .env file (if not already set)
USE_TRANSFORMER=true
TRANSFORMER_MODEL=Qwen/Qwen1.5-7B-Chat

## 4. Restart your Flask app

---

- This setup is 100% free and runs locally (no paid API, no internet required after download).
- Qwen1.5-7B-Chat supports English, Urdu, and code-mixed chat.
- For lower RAM, use Qwen/Qwen1.5-1.8B-Chat instead (change model name in .env).

If you need a Windows batch file or a Python script for automated setup, let me know!

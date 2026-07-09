"""
Automate setup for local HuggingFace transformer model (Qwen1.5-7B-Chat by default).
- Installs required Python packages (transformers, torch, etc.)
- Downloads the model if not present
- Verifies model loading
"""
import subprocess
import sys
import os

MODEL_NAME = os.environ.get('TRANSFORMER_MODEL', 'Qwen/Qwen1.5-7B-Chat')

REQUIRED_PACKAGES = [
    'transformers',
    'torch',
    'sentencepiece',
    'accelerate',
]

def pip_install(package):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def ensure_packages():
    for pkg in REQUIRED_PACKAGES:
        try:
            __import__(pkg.split('==')[0])
        except ImportError:
            print(f"Installing {pkg}...")
            pip_install(pkg)

def download_model():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    print(f"Downloading model: {MODEL_NAME}")
    AutoTokenizer.from_pretrained(MODEL_NAME)
    AutoModelForCausalLM.from_pretrained(MODEL_NAME)
    print("Model downloaded and ready.")

def main():
    ensure_packages()
    try:
        download_model()
        print("Setup complete! You can now use the local transformer model.")
    except Exception as e:
        print(f"Error during model download/setup: {e}")
        print("Please check your internet connection and model name.")

if __name__ == "__main__":
    main()

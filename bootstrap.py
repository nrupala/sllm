"""
SL-LLM Bootloader
Handles Ollama installation and model setup
"""

import os
import subprocess
import sys
from pathlib import Path


def check_ollama():
    """Check if Ollama is installed and running"""
    try:
        result = subprocess.run(
            ["ollama", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return True, result.stdout.strip()
    except FileNotFoundError:
        return False, "Ollama not found"
    except Exception as e:
        return False, str(e)


def check_model(model_name: str):
    """Check if model is available"""
    try:
        import requests
        resp = requests.get("http://localhost:11434/api/tags", timeout=5)
        models = resp.json().get("models", [])
        return any(m.get("name", "").startswith(model_name) for m in models)
    except:
        return False


def install_ollama():
    """Instructions for installing Ollama"""
    print("""
========================================
Ollama Installation Required
========================================

1. Download Ollama from: https://ollama.com
2. Run OllamaSetup.exe
3. Restart your terminal

Or use PowerShell:
    winget install Ollama.Ollama

After installation, run:
    ollama pull deepseek-coder:14b
    ollama serve
========================================
""")


def install_model(model: str = "deepseek-coder:14b"):
    """Install the model"""
    try:
        print(f"Pulling model: {model}")
        subprocess.run(["ollama", "pull", model], check=True)
        print(f"Model {model} installed successfully")
        return True
    except Exception as e:
        print(f"Failed to install model: {e}")
        return False


def start_ollama():
    """Start Ollama serve"""
    try:
        subprocess.Popen(["ollama", "serve"], 
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)
        print("Ollama serve started")
        return True
    except Exception as e:
        print(f"Failed to start Ollama: {e}")
        return False


def main():
    print("SL-LLM Bootloader")
    print("="*50)
    
    found, info = check_ollama()
    print(f"Ollama status: {info}")
    
    if not found:
        install_ollama()
        sys.exit(1)
    
    model = "deepseek-coder:14b"
    model_installed = check_model(model)
    
    if not model_installed:
        print(f"Model {model} not found. Installing...")
        if not install_model(model):
            print("Failed to install model automatically")
            print(f"Run manually: ollama pull {model}")
    
    print("\nStarting SL-LLM...")
    print("Run: python D:/sl/projects/sllm/run.py")


if __name__ == "__main__":
    main()
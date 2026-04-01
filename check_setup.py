"""
SL-LLM Pre-Flight Check
Run this to verify your environment is ready before running main tests.
"""

import sys
import socket


def check_lmstudio():
    """Check if LM Studio is running and accessible"""
    try:
        import requests
        r = requests.get("http://localhost:1234/v1/models", timeout=5)
        if r.status_code == 200:
            models = r.json().get("data", [])
            if models:
                print("[PASS] LM Studio is running")
                print(f"  Loaded model: {models[0].get('id', 'unknown')}")
                return True
            else:
                print("[FAIL] LM Studio running but no model loaded")
                return False
        return False
    except Exception as e:
        print(f"[FAIL] LM Studio not accessible: {e}")
        return False


def check_ollama():
    """Check if Ollama is running"""
    try:
        import requests
        r = requests.get("http://localhost:11434/api/tags", timeout=5)
        if r.status_code == 200:
            models = r.json().get("models", [])
            if models:
                print("[PASS] Ollama is running")
                print(f"  Models: {[m.get('name') for m in models]}")
                return True
            else:
                print("[FAIL] Ollama running but no models")
                return False
        return False
    except Exception as e:
        print(f"[FAIL] Ollama not accessible: {e}")
        return False


def check_gpu():
    """Check for GPU availability"""
    try:
        import subprocess
        result = subprocess.run(["nvidia-smi", "-L"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"[PASS] GPU detected: {result.stdout.strip()}")
            return True
    except:
        pass
    print("[WARN] No NVIDIA GPU detected (will use CPU)")
    return False


def check_python():
    """Check Python version"""
    v = sys.version_info
    if v.major >= 3 and v.minor >= 8:
        print(f"[PASS] Python {v.major}.{v.minor}.{v.micro}")
        return True
    print(f"[FAIL] Python {v.major}.{v.minor} (need 3.8+)")
    return False


def check_dependencies():
    """Check required packages"""
    required = ["requests", "psutil"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    
    if not missing:
        print("[PASS] Dependencies installed")
        return True
    print(f"[FAIL] Missing: {', '.join(missing)}")
    print("  Run: pip install -r requirements.txt")
    return False


def main():
    print("="*60)
    print("SL-LLM Pre-Flight Check")
    print("="*60)
    
    results = []
    
    print("\n[1/4] Checking Python...")
    results.append(check_python())
    
    print("\n[2/4] Checking Dependencies...")
    results.append(check_dependencies())
    
    print("\n[3/4] Checking GPU...")
    results.append(check_gpu())
    
    print("\n[4/4] Checking LLM Server...")
    lmstudio_ok = check_lmstudio()
    if not lmstudio_ok:
        ollama_ok = check_ollama()
        results.append(ollama_ok)
    else:
        results.append(True)
    
    print("\n" + "="*60)
    if all(results):
        print("[SUCCESS] READY TO RUN!")
        print("\nYou can now run:")
        print("  python run.py --test --verbose")
        print("  python self_learning_test.py")
        print("  python knowledge_graph.py")
    else:
        print("[WARNING] ISSUES DETECTED - Please fix before running tests")
        print("\nQuick fixes:")
        print("  - Load a model in LM Studio and start server")
        print("  - OR run: python run.py --prefer=mock --test")
    print("="*60)


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
LLM Link - Local LLM Discovery and Linking
Discovers and links with local LLM engines on the machine.

Supported Engines:
- LM Studio (port 1234)
- Ollama (port 11434)
- llama.cpp (GGUF models)
- text-gen-webui (port 5005)
- LMHD (llama.cpp binding)
- vLLM (port 8000)
- TGI (text-generation-inference, port 8080)

Usage:
    python link_llms.py           # Discover all
    python link_llms.py --status  # Check status
    python link_llms.py --test    # Test with sample prompt
    python link_llms.py --prefer ollama  # Prefer specific
"""

import argparse
import json
import os
import platform
import re
import socket
import subprocess
import sys
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class LLMEngine:
    """Represents a detected LLM engine"""
    name: str
    url: Optional[str] = None
    port: int = 0
    status: str = "unknown"  # running, stopped, error
    models: List[str] = field(default_factory=list)
    info: Dict = field(default_factory=dict)
    gpu_accelerated: bool = False
    
    @property
    def is_available(self) -> bool:
        return self.status == "running"


# Engine configurations
ENGINES = {
    "lmstudio": {"ports": [1234], "name": "LM Studio"},
    "ollama": {"ports": [11434], "name": "Ollama"},
    "llama.cpp": {"ports": [8080], "name": "llama.cpp server"},
    "text-gen-webui": {"ports": [5005], "name": "text-gen-webui"},
    "lmstudio-legacy": {"ports": [1234], "name": "LM Studio (legacy)"},
    "vllm": {"ports": [8000], "name": "vLLM"},
    "tgi": {"ports": [8080, 3000], "name": "TGI"},
}


# ============================================================================
# GPU Detection
# ============================================================================

def detect_gpu() -> Tuple[str, Optional[str]]:
    """Detect GPU availability"""
    system = platform.system()
    
    if system == "Windows":
        try:
            result = subprocess.run(
                ["nvidia-smi", "-L"], 
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return "nvidia", result.stdout.strip()
        except:
            pass
        
        try:
            result = subprocess.run(
                ["wmic", "path", "win32_VideoController", "get", "name"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and "AMD" in result.stdout:
                return "amd", result.stdout.strip()
            elif result.returncode == 0 and "Intel" in result.stdout:
                return "intel", result.stdout.strip()
        except:
            pass
    
    elif system == "Darwin":  # macOS
        try:
            result = subprocess.run(
                ["system_profiler", "SPDisplaysDataType"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                if "Apple" in result.stdout:
                    return "apple_metal", "Apple Silicon GPU"
        except:
            pass
    
    elif system == "Linux":
        try:
            result = subprocess.run(
                ["nvidia-smi", "-L"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return "nvidia", result.stdout.strip()
        except:
            pass
    
    return "cpu", None


# ============================================================================
# Engine Detection
# ============================================================================

def check_port(host: str, port: int, timeout: float = 2.0) -> bool:
    """Check if port is open"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host, port))
        return True
    except:
        return False
    finally:
        sock.close()


def detect_lmstudio() -> Optional[LLMEngine]:
    """Detect LM Studio"""
    ports = [1234]
    
    for port in ports:
        if check_port("localhost", port):
            try:
                import requests
                resp = requests.get(f"http://localhost:{port}/v1/models", timeout=3)
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("id") for m in data.get("data", [])]
                    
                    # Get server info
                    try:
                        info_resp = requests.get(f"http://localhost:{port}/v1/models", timeout=2)
                        info = info_resp.json()
                    except:
                        info = {}
                    
                    return LLMEngine(
                        name="lmstudio",
                        url=f"http://localhost:{port}/v1",
                        port=port,
                        status="running",
                        models=models,
                        info=info
                    )
            except Exception as e:
                logger.debug(f"LM Studio check failed: {e}")
    
    return None


def detect_ollama() -> Optional[LLMEngine]:
    """Detect Ollama"""
    ports = [11434]
    
    for port in ports:
        if check_port("localhost", port):
            try:
                import requests
                resp = requests.get(f"http://localhost:{port}/api/tags", timeout=3)
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("name") for m in data.get("models", [])]
                    
                    return LLMEngine(
                        name="ollama",
                        url=f"http://localhost:{port}",
                        port=port,
                        status="running",
                        models=models,
                        info=data
                    )
            except Exception as e:
                logger.debug(f"Ollama check failed: {e}")
    
    return None


def detect_llama_cpp() -> Optional[LLMEngine]:
    """Detect llama.cpp server (llama-server)"""
    ports = [8080, 8081, 8082]
    
    for port in ports:
        if check_port("localhost", port):
            try:
                import requests
                # llama.cpp doesn't have standard /v1/models, check root
                resp = requests.get(f"http://localhost:{port}/v1/models", timeout=3)
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("id") for m in data.get("data", [])]
                    
                    return LLMEngine(
                        name="llama.cpp",
                        url=f"http://localhost:{port}/v1",
                        port=port,
                        status="running",
                        models=models,
                        info=data
                    )
            except:
                # Try alternative endpoint
                try:
                    resp = requests.get(f"http://localhost:{port}/models", timeout=3)
                    if resp.status_code == 200:
                        return LLMEngine(
                            name="llama.cpp",
                            url=f"http://localhost:{port}",
                            port=port,
                            status="running"
                        )
                except:
                    pass
    
    return None


def find_local_gguf_models() -> List[Dict]:
    """Find local GGUF model files"""
    gguf_models = []
    
    # Common locations
    search_paths = [
        Path.home() / "models",
        Path.home() / "Downloads",
        Path("C:/models"),
        Path("D:/models"),
        Path("C:/llama.cpp"),
        Path("C:/LM Studio"),
    ]
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
            
        try:
            for gguf_file in search_path.rglob("*.gguf"):
                size_mb = gguf_file.stat().st_size / (1024 * 1024)
                gguf_models.append({
                    "path": str(gguf_file),
                    "name": gguf_file.stem,
                    "size_mb": round(size_mb, 1),
                    "recommended": size_mb < 5000  # < 5GB considered portable
                })
        except Exception as e:
            logger.debug(f"Error scanning {search_path}: {e}")
    
    return sorted(gguf_models, key=lambda x: x["size_mb"], reverse=True)


def detect_llama_cpp_direct() -> Optional[LLMEngine]:
    """Detect local GGUF files for direct llama.cpp binding"""
    models = find_local_gguf_models()
    
    if models:
        return LLMEngine(
            name="llama.cpp-gguf",
            url=None,
            port=0,
            status="available",
            models=[m["name"] for m in models],
            info={"models": models, "count": len(models)}
        )
    
    return None


def detect_text_gen_webui() -> Optional[LLMEngine]:
    """Detect text-gen-webui"""
    ports = [5005, 5006]
    
    for port in ports:
        if check_port("localhost", port):
            return LLMEngine(
                name="text-gen-webui",
                url=f"http://localhost:{port}",
                port=port,
                status="running"
            )
    
    return None


def detect_vllm() -> Optional[LLMEngine]:
    """Detect vLLM"""
    ports = [8000, 8001]
    
    for port in ports:
        if check_port("localhost", port):
            try:
                import requests
                resp = requests.get(f"http://localhost:{port}/v1/models", timeout=3)
                if resp.status_code == 200:
                    data = resp.json()
                    models = [m.get("id") for m in data.get("data", [])]
                    
                    return LLMEngine(
                        name="vllm",
                        url=f"http://localhost:{port}/v1",
                        port=port,
                        status="running",
                        models=models,
                        gpu_accelerated=True
                    )
            except:
                pass
    
    return None


def detect_tgi() -> Optional[LLMEngine]:
    """Detect HuggingFace TGI"""
    ports = [8080, 3000, 3001]
    
    for port in ports:
        if check_port("localhost", port):
            try:
                import requests
                resp = requests.get(f"http://localhost:{port}/info", timeout=3)
                if resp.status_code == 200:
                    data = resp.json()
                    return LLMEngine(
                        name="tgi",
                        url=f"http://localhost:{port}",
                        port=port,
                        status="running",
                        info=data,
                        gpu_accelerated=True
                    )
            except:
                pass
    
    return None


# ============================================================================
# Main Discovery
# ============================================================================

def discover_engines() -> Dict[str, LLMEngine]:
    """Discover all available LLM engines"""
    engines = {}
    
    detectors = [
        ("lmstudio", detect_lmstudio),
        ("ollama", detect_ollama),
        ("llama.cpp", detect_llama_cpp),
        ("llama.cpp-gguf", detect_llama_cpp_direct),  # Direct GGUF files
        ("text-gen-webui", detect_text_gen_webui),
        ("vllm", detect_vllm),
        ("tgi", detect_tgi),
    ]
    
    logger.info("Discovering local LLM engines...")
    
    with ThreadPoolExecutor(max_workers=7) as executor:
        futures = {executor.submit(detect): name for name, detect in detectors}
        
        for future in as_completed(futures):
            name = futures[future]
            try:
                result = future.result()
                if result:
                    engines[name] = result
            except Exception as e:
                logger.debug(f"{name} detection error: {e}")
    
    return engines


def link_to_sllm(config_path: Optional[Path] = None) -> Dict:
    """Create link configuration for SL-LLM"""
    engines = discover_engines()
    
    if not engines:
        return {
            "status": "no_engines",
            "message": "No local LLM engines detected",
            "recommendation": "Install LM Studio or Ollama"
        }
    
    # Prefer order based on GPU acceleration
    preferred = []
    for name, engine in engines.items():
        if engine.is_available:
            if engine.gpu_accelerated:
                preferred.insert(0, name)
            else:
                preferred.append(name)
    
    best = preferred[0] if preferred else None
    
    link_config = {
        "status": "linked",
        "best_engine": best,
        "engines": {
            name: {
                "url": engine.url,
                "port": engine.port,
                "status": engine.status,
                "models": engine.models,
                "gpu_accelerated": engine.gpu_accelerated
            }
            for name, engine in engines.items()
        },
        "prefer": best or "auto"
    }
    
    # Save config
    if config_path is None:
        config_path = Path("sllm_link.json")
    
    config_path.write_text(json.dumps(link_config, indent=2))
    logger.info(f"Linked to {best or 'none'} - config saved to {config_path}")
    
    return link_config


# ============================================================================
# Testing
# ============================================================================

def test_engine(engine: LLMEngine, prompt: str = "Say 'hello' in one word") -> Dict:
    """Test an engine with a simple prompt"""
    if not engine.is_available:
        return {"error": "Engine not running"}
    
    try:
        import requests
        
        # OpenAI-compatible
        if "/v1" in engine.url:
            resp = requests.post(
                f"{engine.url}/chat/completions",
                json={
                    "model": engine.models[0] if engine.models else "default",
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 50
                },
                timeout=30
            )
        else:
            # Ollama style
            resp = requests.post(
                f"{engine.url}/api/generate",
                json={"model": engine.models[0] if engine.models else "default", "prompt": prompt},
                timeout=30
            )
        
        if resp.status_code == 200:
            data = resp.json()
            return {
                "status": "ok",
                "response": data.get("message", {}).get("content") or data.get("response", ""),
                "engine": engine.name
            }
        else:
            return {"error": f"HTTP {resp.status_code}"}
            
    except Exception as e:
        return {"error": str(e)}


# ============================================================================
# CLI
# ============================================================================

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("llm-link")

import argparse
parser = argparse.ArgumentParser(description="Link with local LLM engines")
parser.add_argument("--discover", action="store_true", help="Discover engines")
parser.add_argument("--status", action="store_true", help="Show engine status")
parser.add_argument("--test", action="store_true", help="Test with sample prompt")
parser.add_argument("--prefer", help="Prefer specific engine")
parser.add_argument("--link", action="store_true", help="Link to SL-LLM")
parser.add_argument("--config", type=Path, help="Config output path")

args = parser.parse_args()

if args.discover or args.status:
    engines = discover_engines()
    gpu_type, gpu_info = detect_gpu()
    
    print(f"\nGPU: {gpu_type} - {gpu_info[:50] if gpu_info else 'CPU mode'}")
    print(f"\nDetected Engines ({len(engines)}):")
    
    if engines:
        for name, engine in engines.items():
            print(f"  {name}: {engine.url} ({engine.port})")
            if engine.models:
                print(f"    Models: {', '.join(engine.models[:3])}")
            if engine.gpu_accelerated:
                print(f"    GPU: Yes")
    else:
        print("  No engines detected")
        
    if args.test and engines:
        print("\nTesting best engine...")
        best = list(engines.values())[0]
        result = test_engine(best)
        print(f"  Result: {result}")

elif args.link:
    config = link_to_sllm(args.config)
    print(json.dumps(config, indent=2))

else:
    # Quick status
    engines = discover_engines()
    gpu_type, _ = detect_gpu()
    
    status = {
        "gpu": gpu_type,
        "engines": list(engines.keys()),
        "best": list(engines.values())[0].name if engines else None
    }
    print(json.dumps(status, indent=2))
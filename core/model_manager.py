"""
SL-LLM Model Manager & Selector
Ported from agent-project-builder (JavaScript) to Python
Handles model selection, provider management, and LLM interactions
"""

import os
import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


# ============================================================================
# Hardware Detection
# ============================================================================

@dataclass
class HardwareProfile:
    """Hardware capabilities"""
    total_ram_gb: float
    available_ram_gb: float
    cpu_cores: int
    platform: str
    arch: str
    gpu_type: str = None
    gpu_vram_gb: int = 0
    gpu_available: bool = False


def detect_hardware() -> HardwareProfile:
    """Detect hardware capabilities"""
    import platform
    import ctypes
    
    # Get RAM on Windows
    if platform.system() == "Windows":
        try:
            kernel32 = ctypes.windll.kernel32
            c_ulong = ctypes.c_ulong
            class MEMORYSTATUS(ctypes.Structure):
                _fields_ = [("dwLength", c_ulong), ("dwMemoryLoad", c_ulong),
                           ("dwTotalPhys", c_ulong), ("dwAvailPhys", c_ulong),
                           ("dwTotalPageFile", c_ulong), ("dwAvailPageFile", c_ulong),
                           ("dwTotalVirtual", c_ulong), ("dwAvailVirtual", c_ulong)]
            memstatus = MEMORYSTATUS()
            memstatus.dwLength = ctypes.sizeof(memstatus)
            kernel32.GlobalMemoryStatus(ctypes.byref(memstatus))
            total_ram = memstatus.dwTotalPhys / (1024**3)
        except:
            total_ram = 8.0  # Default
    else:
        total_ram = 8.0
    
    cpu_cores = __import__('os').cpu_count() or 4
    
    gpu_type = None
    gpu_vram = 0
    gpu_available = False
    
    # Check NVIDIA GPU
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            values = [int(v.strip()) for v in result.stdout.strip().split('\n') if v.strip()]
            gpu_vram = sum(values) // 1024
            gpu_type = "cuda"
            gpu_available = True
    except:
        pass
    
    # Check Apple Silicon
    if platform.system() == "Darwin" and platform.machine() == "arm64":
        try:
            result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                mem_bytes = int(result.stdout.strip())
                unified_ram = mem_bytes / (1024**3)
                gpu_vram = int(unified_ram * 0.7)
                gpu_type = "metal"
                gpu_available = True
        except:
            pass
    
    return HardwareProfile(
        total_ram_gb=round(total_ram, 1),
        available_ram_gb=round(total_ram * 0.7, 1),
        cpu_cores=cpu_cores,
        platform=platform.system(),
        arch=platform.machine(),
        gpu_type=gpu_type,
        gpu_vram_gb=gpu_vram,
        gpu_available=gpu_available
    )


def can_run_model(hardware: HardwareProfile, vram_required: int) -> bool:
    """Check if hardware can run model"""
    if hardware.gpu_available:
        return hardware.gpu_vram_gb >= vram_required
    return hardware.total_ram_gb >= vram_required * 1.5


# ============================================================================
# Model Registry (from modelSelector.js)
# ============================================================================

MODEL_REGISTRY: Dict[str, List[Dict]] = {
    "local": [
        {"id": "qwen2.5-coder-14b", "name": "Qwen2.5 Coder 14B", "params": "14B", "vram_required": 8, "quality": "high", "specialty": "code-generation"},
        {"id": "qwen2.5-coder-7b", "name": "Qwen2.5 Coder 7B", "params": "7B", "vram_required": 5, "quality": "high", "specialty": "code-generation"},
        {"id": "rnj-1-instruct", "name": "RNJ-1 Instruct", "params": "7B", "vram_required": 5, "quality": "medium", "specialty": "code-generation"},
    ],
    "code-generation": [
        {"id": "qwen2.5-coder-7b", "name": "Qwen2.5 Coder 7B", "params": "7B", "vram_required": 5.5, "quality": "high"},
        {"id": "qwen2.5-coder-3b", "name": "Qwen2.5 Coder 3B", "params": "3B", "vram_required": 2.5, "quality": "medium"},
        {"id": "qwen2.5-coder-1.5b", "name": "Qwen2.5 Coder 1.5B", "params": "1.5B", "vram_required": 1.2, "quality": "low"},
    ],
    "general-chat": [
        {"id": "llama-3.2-3b", "name": "Llama 3.2 3B", "params": "3B", "vram_required": 2.5, "quality": "medium"},
        {"id": "qwen2.5-7b", "name": "Qwen2.5 7B", "params": "7B", "vram_required": 5.5, "quality": "high"},
    ],
    "reasoning": [
        {"id": "deepseek-r1-distill-qwen-7b", "name": "DeepSeek R1 Distill Qwen 7B", "params": "7B", "vram_required": 5.5, "quality": "high"},
    ],
    "embedding": [
        {"id": "nomic-embed-text-v1.5", "name": "Nomic Embed Text v1.5", "params": "137M", "vram_required": 0.3, "quality": "high"},
    ],
}


class ModelSelector:
    """Selects appropriate model based on task and hardware"""
    
    def __init__(self):
        self.hardware_profile: Optional[HardwareProfile] = None
        self.local_model_paths = [
            "C:/Users/HomeUser/.lmstudio/models",
            "D:/models/lmstudio-community",
            "./models",
        ]
    
    def detect_hardware_sync(self) -> HardwareProfile:
        """Detect hardware synchronously"""
        if self.hardware_profile is None:
            self.hardware_profile = detect_hardware()
        return self.hardware_profile
    
    def find_local_model(self, name_hint: str) -> Optional[str]:
        """Find local GGUF model"""
        for search_path in self.local_model_paths:
            p = Path(search_path)
            if not p.exists():
                continue
            
            try:
                for f in p.rglob("*.gguf"):
                    if name_hint.lower() in f.name.lower():
                        return str(f)
            except:
                pass
        
        return None
    
    def select_model(self, task: str = "code-generation", quality: str = "auto") -> Dict:
        """Select best model for task"""
        hardware = self.detect_hardware_sync()
        
        # Check local models first
        local_models = MODEL_REGISTRY.get("local", [])
        for model in local_models:
            local_path = self.find_local_model(model["id"])
            if local_path:
                return {
                    **model,
                    "path": local_path,
                    "local": True,
                    "hardware_profile": hardware,
                    "will_use_gpu": hardware.gpu_available and hardware.gpu_vram_gb >= model.get("vram_required", 0),
                }
        
        # Select from registry
        models = MODEL_REGISTRY.get(task, MODEL_REGISTRY.get("code-generation", []))
        
        quality_filter = []
        if quality == "auto":
            if hardware.gpu_vram_gb >= 6:
                quality_filter = ["high", "medium"]
            elif hardware.gpu_vram_gb >= 3 or hardware.total_ram_gb >= 8:
                quality_filter = ["medium", "low"]
            else:
                quality_filter = ["low"]
        else:
            quality_filter = [quality]
        
        for q in quality_filter:
            for model in models:
                if model.get("quality") == q:
                    vram_req = model.get("vram_required", 5)
                    if can_run_model(hardware, vram_req):
                        return {
                            **model,
                            "hardware_profile": hardware,
                            "will_use_gpu": hardware.gpu_available and hardware.gpu_vram_gb >= vram_req,
                        }
        
        # Fallback to last option
        return {
            **models[-1],
            "hardware_profile": hardware,
            "will_use_gpu": False,
            "warning": "Hardware below recommended specs"
        }


# ============================================================================
# Model Manager
# ============================================================================

class ModelManager:
    """
    Manages LLM providers (LM Studio, Ollama, built-in)
    Ported from agent-project-builder modelManager.js
    """
    
    def __init__(self):
        import os as _os
        self._os = _os
        
        self.provider: str = None
        self.model_config: Dict = {}
        self.clients: Dict = {}
        self.client_type: str = None
        self.is_local_only: _os.environ.get("LOCAL_ONLY", "true").lower() == "true"
        self.max_concurrent: int = 20
        self.active_requests: int = 0
        self.request_queue: List = []
        
        self.logger = {
            "info": lambda m: print(f"[ModelManager] {m}"),
            "error": lambda m: print(f"[ModelManager] ERROR: {m}"),
            "warn": lambda m: print(f"[ModelManager] WARN: {m}"),
        }
        
        self.model_selector = ModelSelector()
        self.built_in_engine = None
    
    def get_model_config(self, provider: str) -> Dict:
        """Get model config from environment"""
        
        if provider.lower() == "lmstudio":
            return {
                "provider": "lmstudio",
                "model": os.environ.get("LMSTUDIO_MODEL", "qwen/qwen2.5-coder-14b"),
                "temperature": float(os.environ.get("TEMPERATURE", 0.7)),
                "max_tokens": int(os.environ.get("MAX_TOKENS", 4096)),
                "base_path": os.environ.get("LMSTUDIO_ENDPOINT", "http://localhost:1234/v1"),
            }
        elif provider.lower() == "ollama":
            return {
                "provider": "ollama",
                "model": os.environ.get("OLLAMA_MODEL", "qwen3.5:9b"),
                "temperature": float(os.environ.get("TEMPERATURE", 0.7)),
                "max_tokens": int(os.environ.get("MAX_TOKENS", 4096)),
                "base_path": os.environ.get("OLLAMA_ENDPOINT", "http://localhost:11434"),
            }
        else:
            return {
                "provider": "openai",
                "model": os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo"),
                "temperature": float(os.environ.get("TEMPERATURE", 0.7)),
                "max_tokens": int(os.environ.get("MAX_TOKENS", 4096)),
            }
    
    async def initialize(self, provider: str = None):
        """Initialize model manager"""
        if provider is None:
            provider = os.environ.get("MODEL_PROVIDER", "lmstudio")
        
        if self.is_local_only and provider.lower() not in ["lmstudio", "ollama"]:
            self.logger["warn"]("Provider not local-only, switching to lmstudio")
            provider = "lmstudio"
        
        model_config = self.get_model_config(provider)
        await self.set_provider(provider, model_config)
    
    async def set_provider(self, provider_name: str, model_config: Dict):
        """Set provider"""
        self.provider = provider_name
        self.model_config = model_config
        
        if self.is_local_only and provider_name not in ["lmstudio", "ollama"]:
            provider_name = "lmstudio"
        
        await self._try_local_providers()
        
        self.logger["info"](
            f"Provider: {self.provider} (type: {self.client_type})"
            + (" (local-only)" if self.is_local_only else "")
        )
    
    async def _try_local_providers(self):
        """Try local providers in order"""
        import urllib.request
        
        # Try LM Studio
        try:
            req = urllib.request.Request("http://localhost:1234/v1/models")
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    self.provider = "lmstudio"
                    self.client_type = "lmstudio"
                    self.logger["info"]("Connected to LM Studio")
                    return
        except Exception as e:
            self.logger["warn"](f"LM Studio: {e}")
        
        # Try Ollama
        try:
            import urllib.request
            req = urllib.request.Request("http://localhost:11434/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    self.provider = "ollama"
                    self.client_type = "ollama"
                    self.logger["info"]("Connected to Ollama")
                    return
        except Exception as e:
            self.logger["warn"](f"Ollama: {e}")
        
        # Fall back to mock
        self.client_type = "mock"
        self.logger["warn"]("All local providers failed, using mock")
    
    async def generate(self, prompt: str, options: Dict = None) -> str:
        """Generate completion"""
        options = options or {}
        
        if self.client_type == "lmstudio":
            return await self._generate_lmstudio(prompt, options)
        elif self.client_type == "ollama":
            return await self._generate_ollama(prompt, options)
        else:
            return self._generate_mock(prompt, options)
    
    async def _generate_lmstudio(self, prompt: str, options: Dict) -> str:
        """Generate using LM Studio"""
        import urllib.request
        import json
        
        payload = {
            "model": self.model_config.get("model", "qwen/qwen2.5-coder-14b"),
            "messages": [{"role": "user", "content": prompt}],
            "temperature": options.get("temperature", self.model_config.get("temperature", 0.7)),
            "max_tokens": options.get("max_tokens", self.model_config.get("max_tokens", 4096)),
            "stream": False,
        }
        
        base_path = self.model_config.get("base_path", "http://localhost:1234/v1")
        
        req = urllib.request.Request(
            f"{base_path}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read())
                return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        except Exception as e:
            self.logger["error"](f"LM Studio error: {e}")
            return self._generate_mock(prompt, options)
    
    async def _generate_ollama(self, prompt: str, options: Dict) -> str:
        """Generate using Ollama"""
        import urllib.request
        import json
        
        payload = {
            "model": self.model_config.get("model", "qwen3.5:9b"),
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "options": {
                "temperature": options.get("temperature", self.model_config.get("temperature", 0.7)),
                "num_predict": options.get("max_tokens", self.model_config.get("max_tokens", 4096)),
            }
        }
        
        base_path = self.model_config.get("base_path", "http://localhost:11434")
        
        req = urllib.request.Request(
            f"{base_path}/api/chat",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read())
                return result.get("message", {}).get("content", "")
        except Exception as e:
            self.logger["error"](f"Ollama error: {e}")
            return self._generate_mock(prompt, options)
    
    def _generate_mock(self, prompt: str, options: Dict) -> str:
        """Mock response"""
        responses = [
            f'Mock response to: "{prompt[:80]}..."',
            "Connect LM Studio or Ollama for real responses.",
            "Mock: Model not available. Please start a local LLM server.",
        ]
        import random
        return random.choice(responses)
    
    def get_stats(self) -> Dict:
        """Get manager stats"""
        return {
            "provider": self.provider,
            "client_type": self.client_type,
            "is_local_only": self.is_local_only,
            "active_requests": self.active_requests,
            "queued_requests": len(self.request_queue),
        }


# ============================================================================
# Convenience Functions
# ============================================================================

async def create_model_manager(provider: str = None) -> ModelManager:
    """Create and initialize model manager"""
    manager = ModelManager()
    await manager.initialize(provider)
    return manager


def get_model_selector() -> ModelSelector:
    """Get model selector instance"""
    return ModelSelector()


if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("=== SL-LLM Model Manager ===\n")
        
        # Hardware
        hw = detect_hardware()
        print(f"Hardware:")
        print(f"  RAM: {hw.total_ram_gb}GB total, {hw.available_ram_gb}GB available")
        print(f"  CPU: {hw.cpu_cores} cores")
        print(f"  GPU: {hw.gpu_type or 'none'} ({hw.gpu_vram_gb}GB)" if hw.gpu_available else "  GPU: none")
        
        # Model selector
        print("\nModel Selection:")
        selector = ModelSelector()
        
        for task in ["code-generation", "general-chat", "reasoning"]:
            model = selector.select_model(task)
            print(f"  {task}: {model['name']} ({model['params']}, will_use_gpu={model.get('will_use_gpu')})")
        
        # Model manager
        print("\nProvider Setup:")
        manager = await create_model_manager()
        print(f"  Provider: {manager.provider}")
        print(f"  Type: {manager.client_type}")
        
        # Test generation
        print("\nTest Generation:")
        result = await manager.generate("Say 'hello' in one sentence")
        print(f"  Result: {result[:200]}")
    
    asyncio.run(test())
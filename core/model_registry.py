"""
SL-LLM Model Configuration
Integrates available models from:
- Local: LM Studio, Ollama, GGUF files
- Cloud: OpenAI, Anthropic, Google, DeepSeek, Qwen, etc. (requires API keys)
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional


class ModelRegistry:
    """Central registry of all available models"""
    
    def __init__(self):
        self.local_models = self._load_local_models()
        self.cloud_providers = self._load_cloud_providers()
    
    def _load_local_models(self) -> List[Dict]:
        """Load available local models"""
        models = []
        
        # LM Studio
        try:
            import urllib.request
            req = urllib.request.Request("http://localhost:1234/v1/models")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read())
                for m in data.get("data", []):
                    models.append({
                        "id": m["id"],
                        "name": m.get("id", "Unknown"),
                        "provider": "lmstudio",
                        "type": "local"
                    })
        except:
            pass
        
        # Ollama
        try:
            import urllib.request
            req = urllib.request.Request("http://localhost:11434/api/tags")
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read())
                for m in data.get("models", []):
                    models.append({
                        "id": m["name"],
                        "name": m.get("name", m["name"]),
                        "provider": "ollama",
                        "type": "local"
                    })
        except:
            pass
        
        # GGUF files
        gguf_paths = [
            "D:/models/lmstudio-community",
            "C:/Users/nrupa/.lmstudio/hub/models"
        ]
        for base_path in gguf_paths:
            p = Path(base_path)
            if p.exists():
                for gguf in p.rglob("*.gguf"):
                    models.append({
                        "id": str(gguf),
                        "name": gguf.name,
                        "provider": "gguf",
                        "type": "local"
                    })
        
        # Fallback defaults
        if not models:
            models = [
                {"id": "mock", "name": "Mock Model (Testing)", "provider": "mock", "type": "local"},
                {"id": "qwen2.5-coder:14b", "name": "Qwen2.5 Coder 14B", "provider": "ollama", "type": "local"},
            ]
        
        return models
    
    def _load_cloud_providers(self) -> Dict:
        """Load cloud provider configurations"""
        providers = {}
        
        config_path = Path("C:/Users/nrupa/.cache/opencode/models.json")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    
                for provider_id, provider_data in data.items():
                    models = []
                    for model_id, model_info in provider_data.get("models", {}).items():
                        models.append({
                            "id": model_id,
                            "name": model_info.get("name", model_id),
                            "family": model_info.get("family", ""),
                            "reasoning": model_info.get("reasoning", False),
                            "cost": model_info.get("cost", {}),
                            "context": model_info.get("limit", {}).get("context", 0),
                            "release": model_info.get("release_date", "")
                        })
                    
                    providers[provider_id] = {
                        "name": provider_data.get("name", provider_id),
                        "api": provider_data.get("api", ""),
                        "env_var": provider_data.get("env", ""),
                        "doc": provider_data.get("doc", ""),
                        "models": models
                    }
            except Exception as e:
                print(f"Could not load cloud providers: {e}")
        
        return providers
    
    def get_all_models(self) -> List[Dict]:
        """Get all available models (local + cloud)"""
        local = [{"**m": m["id"], "name": m["name"], "provider": m["provider"], "location": "local"} 
                 for m in self.local_models]
        
        cloud = []
        for prov_id, prov in self.cloud_providers.items():
            env = prov.get("env_var", "")
            has_key = bool(os.environ.get(env.split()[0].replace("_API_KEY", "")))
            
            for m in prov["models"][:10]:  # Limit cloud models shown
                cloud.append({
                    "id": f"{prov_id}/{m['id']}",
                    "name": m["name"],
                    "provider": prov["name"],
                    "location": "cloud",
                    "configured": has_key,
                    "reasoning": m.get("reasoning", False)
                })
        
        return local + cloud
    
    def get_model_info(self, model_id: str) -> Optional[Dict]:
        """Get detailed info about a model"""
        # Check local
        for m in self.local_models:
            if m["id"] == model_id:
                return m
        
        # Check cloud
        for prov_id, prov in self.cloud_providers.items():
            for m in prov["models"]:
                full_id = f"{prov_id}/{m['id']}"
                if full_id == model_id:
                    return {
                        **m,
                        "provider": prov["name"],
                        "api": prov["api"],
                        "env": prov.get("env_var", "")
                    }
        
        return None
    
    def list_providers(self) -> List[Dict]:
        """List all cloud providers"""
        result = []
        for prov_id, prov in self.cloud_providers.items():
            env = prov.get("env_var", "")
            key_name = env.split()[0] if env else ""
            has_key = bool(os.environ.get(key_name))
            
            result.append({
                "id": prov_id,
                "name": prov["name"],
                "model_count": len(prov["models"]),
                "configured": has_key,
                "env_var": key_name
            })
        return result


# Singleton instance
_registry = None

def get_registry() -> ModelRegistry:
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry


if __name__ == "__main__":
    reg = get_registry()
    print("=== SL-LLM Model Registry ===\n")
    
    print("Local Models:")
    for m in reg.local_models[:5]:
        print(f"  - {m['name']} ({m['provider']})")
    
    print(f"\nTotal local: {len(reg.local_models)}")
    print(f"Total cloud providers: {len(reg.cloud_providers)}")
    
    print("\nCloud Providers:")
    for p in reg.list_providers()[:5]:
        status = "✓ configured" if p["configured"] else "✗ not configured"
        print(f"  - {p['name']}: {p['model_count']} models ({status})")
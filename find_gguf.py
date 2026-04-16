"""Find all local GGUF models on the system"""
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gguf-finder")

def find_gguf_models():
    """Find GGUF files in common locations"""
    models = []
    
    # Search paths
    paths = [
        Path("C:/"),
        Path("D:/"),
        Path("D:/models"),
        Path.home(),
    ]
    
    # Common model directories
    model_dirs = [
        "models",
        "Downloads",
        "llama.cpp",
        "LM Studio",
        "ollama",
    ]
    
    found_files = set()
    
    for base in [Path("D:/"), Path("C:/")]:
        for model_dir in model_dirs:
            search_path = base / model_dir
            if not search_path.exists():
                continue
            
            try:
                for gguf in search_path.rglob("*.gguf"):
                    if gguf in found_files:
                        continue
                    found_files.add(gguf)
                    
                    size_gb = gguf.stat().st_size / (1024**3)
                    models.append({
                        "path": str(gguf),
                        "name": gguf.stem,
                        "size_gb": round(size_gb, 2),
                        "size_mb": round(gguf.stat().st_size / (1024**2)),
                        "portable": size_gb < 5,
                    })
            except Exception as e:
                logger.debug(f"Error scanning {search_path}: {e}")
    
    # Sort by size (largest first)
    models.sort(key=lambda x: x["size_gb"], reverse=True)
    
    return models


if __name__ == "__main__":
    import json
    
    models = find_gguf_models()
    
    print(f"\nFound {len(models)} GGUF models:\n")
    
    for m in models:
        print(f"  {m['name']}")
        print(f"    Path: {m['path']}")
        print(f"    Size: {m['size_gb']} GB ({m['portable'] and 'portable' or 'large'})")
        print()
    
    # Save to file for reference
    output = {"models": models, "count": len(models)}
    
    with open("local_gguf_models.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"Saved to local_gguf_models.json")
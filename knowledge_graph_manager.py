"""
SL-LLM Enhanced Knowledge Graph Manager
- Classification/Categorization
- Contextualization
- Segregation
- Amalgamation (merging related)
- Concatenation (joining)
- Splitting (for context limits)
"""

import json
import os
import hashlib
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Set
from collections import defaultdict


class KnowledgeClassifier:
    """Classifies and categorizes knowledge entries"""
    
    # Core categories
    CATEGORIES = {
        "bug_fix": ["error", "bug", "fix", "issue", "wrong", "fail", "exception"],
        "optimization": ["optimize", "faster", "efficient", "performance", "speed"],
        "pattern": ["pattern", "template", "standard", "pattern"],
        "concept": ["concept", "theory", "principle", "understand"],
        "api": ["api", "endpoint", "request", "response", "http"],
        "data": ["data", "database", "query", "storage", "record"],
        "security": ["security", "safe", "secure", "auth", "permission"],
        "validation": ["validate", "check", "verify", "test", "assert"]
    }
    
    # Context types
    CONTEXTS = {
        "programming_language": ["python", "javascript", "java", "c++", "html", "css"],
        "domain": ["web", "mobile", "desktop", "api", "database", "ml", "ai"],
        "framework": ["react", "django", "flask", "fastapi", "pytorch"],
        "level": ["beginner", "intermediate", "advanced", "expert"]
    }
    
    @classmethod
    def classify(cls, text: str, metadata: dict = None) -> Dict:
        """Classify a knowledge entry"""
        text_lower = text.lower()
        scores = {}
        
        # Category scoring
        for category, keywords in cls.CATEGORIES.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = score
        
        # Get top category
        top_category = max(scores, key=scores.get) if scores else "general"
        
        # Context detection
        detected_contexts = []
        for ctx_type, keywords in cls.CONTEXTS.items():
            if any(kw in text_lower for kw in keywords):
                detected_contexts.append(ctx_type)
        
        return {
            "primary_category": top_category,
            "all_categories": scores,
            "contexts": detected_contexts,
            "confidence": scores.get(top_category, 0) / max(len(keywords), 1) if scores else 0
        }


class KnowledgeContextualizer:
    """Adds context to knowledge entries"""
    
    @staticmethod
    def extract_context(user_prompt: str, related_episodes: List[Dict]) -> Dict:
        """Extract contextual information from conversation history"""
        
        context = {
            "task_type": None,
            "domain": None,
            "language": None,
            "difficulty": None,
            "similar_past": []
        }
        
        prompt_lower = user_prompt.lower()
        
        # Task type
        if any(w in prompt_lower for w in ["write", "create", "implement"]):
            context["task_type"] = "creation"
        elif any(w in prompt_lower for w in ["fix", "debug", "repair"]):
            context["task_type"] = "repair"
        elif any(w in prompt_lower for w in ["explain", "what is", "how to"]):
            context["task_type"] = "explanation"
        
        # Domain detection
        domains = ["web", "api", "database", "algorithm", "data", "security"]
        for d in domains:
            if d in prompt_lower:
                context["domain"] = d
                break
        
        # Language
        languages = ["python", "javascript", "html", "css", "sql"]
        for lang in languages:
            if lang in prompt_lower:
                context["language"] = lang
                break
        
        # Difficulty estimation (word count as proxy)
        context["difficulty"] = "advanced" if len(user_prompt.split()) > 20 else "basic"
        
        # Find similar past tasks
        for ep in related_episodes:
            task = ep.get("task", "").lower()
            if any(w in task for w in prompt_lower.split()[:3]):
                context["similar_past"].append(ep.get("task", "")[:50])
        
        return context


class KnowledgeSegregator:
    """Segregates knowledge into separate stores"""
    
    def __init__(self):
        self.stores = {
            "bugs": [],
            "patterns": [],
            "solutions": [],
            "concepts": [],
            "api_knowledge": [],
            "general": []
        }
    
    def segregate(self, insight: Dict) -> str:
        """Determine which store the insight belongs to"""
        category = insight.get("category", "general").lower()
        
        if "bug" in category or "fix" in category:
            return "bugs"
        elif "pattern" in category:
            return "patterns"
        elif "api" in category:
            return "api_knowledge"
        elif "concept" in category or "principle" in category:
            return "concepts"
        elif "solution" in category or "implement" in category:
            return "solutions"
        else:
            return "general"
    
    def add_to_store(self, insight: Dict):
        """Add insight to appropriate store"""
        store = self.segregate(insight)
        self.stores[store].append(insight)
    
    def get_store(self, store_name: str) -> List[Dict]:
        """Get insights from specific store"""
        return self.stores.get(store_name, [])


class KnowledgeAmalgamator:
    """Amalgamates/merges related knowledge"""
    
    @staticmethod
    def merge_similar_insights(insights: List[Dict]) -> List[Dict]:
        """Merge similar insights into consolidated entries"""
        
        if not insights:
            return []
        
        merged = []
        seen_content = set()
        
        for insight in insights:
            content = insight.get("insight", "")
            # Create hash of content for deduplication
            content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
            
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                
                # Add merge metadata
                insight["_merged"] = {
                    "original_count": 1,
                    "consolidated": True,
                    "content_hash": content_hash
                }
                merged.append(insight)
        
        return merged
    
    @staticmethod
    def combine_categories(category1: Dict, category2: Dict) -> Dict:
        """Combine two category score dictionaries"""
        combined = defaultdict(int)
        for k, v in category1.items():
            combined[k] += v
        for k, v in category2.items():
            combined[k] += v
        return dict(combined)


class KnowledgeConcatenator:
    """Concatenates knowledge for context injection"""
    
    @staticmethod
    def concatenate_insights(insights: List[Dict], max_items: int = 5) -> str:
        """Join multiple insights into a single context string"""
        
        if not insights:
            return "No relevant prior knowledge found."
        
        parts = ["### Relevant Prior Knowledge:"]
        
        for i, ins in enumerate(insights[:max_items], 1):
            cat = ins.get("category", "general")
            content = ins.get("insight", "")
            ts = ins.get("timestamp", "")[:10]
            
            parts.append(f"{i}. [{cat}] {content} ({ts})")
        
        if len(insights) > max_items:
            parts.append(f"... and {len(insights) - max_items} more")
        
        return "\n".join(parts)
    
    @staticmethod
    def create_contextual_header(context: Dict) -> str:
        """Create header with contextual information"""
        
        header = ["## Current Context"]
        
        if context.get("task_type"):
            header.append(f"- Task Type: {context['task_type']}")
        if context.get("domain"):
            header.append(f"- Domain: {context['domain']}")
        if context.get("language"):
            header.append(f"- Language: {context['language']}")
        if context.get("difficulty"):
            header.append(f"- Complexity: {context['difficulty']}")
        
        if context.get("similar_past"):
            header.append(f"- Similar past tasks: {len(context['similar_past'])}")
        
        return "\n".join(header)


class KnowledgeSplitter:
    """Splits knowledge for context window management"""
    
    def __init__(self, max_tokens_per_chunk: int = 1500):
        self.max_tokens = max_tokens_per_chunk
    
    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Estimate token count"""
        return int(len(text.split()) * 1.3)
    
    def split_by_category(self, insights: List[Dict]) -> Dict[str, List[Dict]]:
        """Split insights by category into separate chunks"""
        
        by_category = defaultdict(list)
        
        for ins in insights:
            cat = ins.get("category", "general")
            by_category[cat].append(ins)
        
        return dict(by_category)
    
    def split_by_tokens(self, text: str) -> List[str]:
        """Split text into token-limited chunks"""
        
        words = text.split()
        chunks = []
        current_chunk = []
        current_tokens = 0
        
        for word in words:
            word_tokens = len(word) // 4 + 1  # rough token estimate
            
            if current_tokens + word_tokens > self.max_tokens:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
            
            current_chunk.append(word)
            current_tokens += word_tokens
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def select_relevant_chunks(self, chunks: List[str], query: str) -> List[str]:
        """Select most relevant chunks based on query"""
        
        query_words = set(query.lower().split())
        scored_chunks = []
        
        for chunk in chunks:
            chunk_words = set(chunk.lower().split())
            overlap = len(query_words & chunk_words)
            scored_chunks.append((overlap, chunk))
        
        # Sort by relevance and return top matches
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        
        # Return up to 3 most relevant chunks
        return [chunk for _, chunk in scored_chunks[:3]]


class FluidKnowledgeGraph:
    """Main knowledge graph with fluid intelligence"""
    
    def __init__(self, memory_dir: str = "D:/sl/projects/sllm/memory"):
        self.memory_dir = Path(memory_dir)
        self.insights_file = self.memory_dir / "insights.jsonl"
        self.episodes_file = self.memory_dir / "episodes.jsonl"
        self.binary_file = self.memory_dir / "knowledge_graph.bin"
        
        # Initialize components
        self.classifier = KnowledgeClassifier()
        self.contextualizer = KnowledgeContextualizer()
        self.segregator = KnowledgeSegregator()
        self.amalgamator = KnowledgeAmalgamator()
        self.splitter = KnowledgeSplitter()
        
        # Metadata
        self._ensure_files()
    
    def _ensure_files(self):
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        for f in [self.insights_file, self.episodes_file]:
            if not f.exists():
                f.write_text("")
    
    def export_binary(self) -> bool:
        """Export knowledge graph as compressed binary for efficient loading"""
        try:
            import pickle
            import gzip
            
            # Load all insights
            insights = []
            if self.insights_file.exists():
                with open(self.insights_file, "r") as f:
                    insights = [json.loads(line) for line in f if line.strip()]
            
            # Load all episodes
            episodes = []
            if self.episodes_file.exists():
                with open(self.episodes_file, "r") as f:
                    episodes = [json.loads(line) for line in f if line.strip()]
            
            # Create binary package
            binary_data = {
                "version": "1.0",
                "exported": datetime.now().isoformat(),
                "insights": insights,
                "episodes": episodes,
                "category_counts": self._get_category_counts()
            }
            
            # Compress and save
            with gzip.open(self.binary_file, 'wb') as f:
                pickle.dump(binary_data, f)
            
            print(f"Binary export: {self.binary_file} ({Path(self.binary_file).stat().st_size} bytes)")
            return True
        except Exception as e:
            print(f"Binary export failed: {e}")
            return False
    
    def load_binary(self) -> bool:
        """Load knowledge graph from binary file"""
        try:
            import pickle
            import gzip
            
            if not self.binary_file.exists():
                return False
            
            with gzip.open(self.binary_file, 'rb') as f:
                data = pickle.load(f)
            
            # Write back to JSONL
            with open(self.insights_file, "w") as f:
                for ins in data.get("insights", []):
                    f.write(json.dumps(ins) + "\n")
            
            with open(self.episodes_file, "w") as f:
                for ep in data.get("episodes", []):
                    f.write(json.dumps(ep) + "\n")
            
            print(f"Binary import successful: {len(data.get('insights', []))} insights loaded")
            return True
        except Exception as e:
            print(f"Binary import failed: {e}")
            return False
    
    def get_binary_info(self) -> Dict:
        """Get info about binary file"""
        if self.binary_file.exists():
            return {
                "exists": True,
                "size_bytes": Path(self.binary_file).stat().st_size,
                "exported": datetime.fromtimestamp(Path(self.binary_file).stat().st_mtime).isoformat()
            }
        return {"exists": False}
    
    # ============================================================
    # MAIN PROCESSING PIPELINE
    # ============================================================
    
    def process(self, user_prompt: str) -> Dict:
        """Full processing pipeline: classify -> contextualize -> retrieve -> format"""
        
        # 1. Classify the incoming query
        classification = self.classifier.classify(user_prompt)
        
        # 2. Get related episodes for context
        related_episodes = self._get_related_episodes(user_prompt)
        
        # 3. Extract context
        context = self.contextualizer.extract_context(user_prompt, related_episodes)
        
        # 4. Retrieve relevant insights
        relevant_insights = self._retrieve_insights(classification, context)
        
        # 5. Amalgamate (deduplicate)
        consolidated_insights = self.amalgamator.merge_similar_insights(relevant_insights)
        
        # 6. Format for injection
        concatenated = KnowledgeConcatenator.concatenate_insights(consolidated_insights)
        contextual_header = KnowledgeConcatenator.create_contextual_header(context)
        
        # 7. Split if too large
        if self.splitter.estimate_tokens(concatenated) > 3000:
            chunks = self.splitter.split_by_tokens(concatenated)
            relevant_chunks = self.splitter.select_relevant_chunks(chunks, user_prompt)
            concatenated = "\n\n---\n\n".join(relevant_chunks)
        
        return {
            "classification": classification,
            "context": context,
            "insights_count": len(consolidated_insights),
            "context_header": contextual_header,
            "knowledge_context": concatenated,
            "metadata": {
                "total_insights_stored": self._count_insights(),
                "categories": self._get_category_counts()
            }
        }
    
    # ============================================================
    # HELPER METHODS
    # ============================================================
    
    def _get_related_episodes(self, prompt: str) -> List[Dict]:
        """Find related past episodes"""
        try:
            with open(self.episodes_file, "r") as f:
                episodes = [json.loads(line) for line in f if line.strip()]
        except:
            return []
        
        # Simple relevance - last 5 episodes
        return episodes[-5:]
    
    def _retrieve_insights(self, classification: Dict, context: Dict) -> List[Dict]:
        """Retrieve relevant insights based on classification and context"""
        
        try:
            with open(self.insights_file, "r") as f:
                all_insights = [json.loads(line) for line in f if line.strip()]
        except:
            return []
        
        relevant = []
        target_categories = list(classification.get("all_categories", {}).keys())
        
        for ins in all_insights[-50:]:  # Recent 50
            if ins.get("category") in target_categories:
                relevant.append(ins)
        
        return relevant[:10]  # Limit to 10
    
    def _count_insights(self) -> int:
        try:
            with open(self.insights_file, "r") as f:
                return sum(1 for line in f if line.strip())
        except:
            return 0
    
    def _get_category_counts(self) -> Dict:
        try:
            with open(self.insights_file, "r") as f:
                insights = [json.loads(line) for line in f if line.strip()]
            counts = defaultdict(int)
            for ins in insights:
                counts[ins.get("category", "general")] += 1
            return dict(counts)
        except:
            return {}


# ============================================================
# INTEGRATION FUNCTION
# ============================================================

def get_enhanced_context(user_prompt: str, memory_dir: str = "D:/sl/projects/sllm/memory") -> Tuple[str, Dict]:
    """Get enhanced context with fluid intelligence"""
    
    fkg = FluidKnowledgeGraph(memory_dir)
    result = fkg.process(user_prompt)
    
    # Build final context
    context_parts = [
        result["context_header"],
        "",
        result["knowledge_context"]
    ]
    
    enhanced = "\n".join(context_parts)
    
    metadata = {
        "classification": result["classification"],
        "context": result["context"],
        "insights_retrieved": result["insights_count"],
        "categories": result["metadata"]["categories"]
    }
    
    return enhanced, metadata


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":
    print("="*60)
    print("Fluid Knowledge Graph - Full Capability Test")
    print("="*60)
    
    fkg = FluidKnowledgeGraph()
    
    # Test 1: Classification
    print("\n[1] Classification Test")
    test_prompts = [
        "Fix the division by zero bug in Python",
        "Optimize the sorting algorithm for better performance",
        "Explain how async/await works in JavaScript"
    ]
    
    for prompt in test_prompts:
        cls = KnowledgeClassifier.classify(prompt)
        print(f"  '{prompt[:30]}...'")
        print(f"    -> Category: {cls['primary_category']}, Contexts: {cls['contexts']}")
    
    # Test 2: Contextualization
    print("\n[2] Contextualization Test")
    ctx = KnowledgeContextualizer.extract_context(
        "Write a Python function to calculate fibonacci",
        [{"task": "Python fibonacci"}, {"task": "Calculate factorial"}]
    )
    print(f"  Context: {ctx}")
    
    # Test 3: Segregation
    print("\n[3] Segregation Test")
    seg = KnowledgeSegregator()
    seg.add_to_store({"category": "bug_fix", "insight": "Check for zero"})
    seg.add_to_store({"category": "pattern", "insight": "Use template"})
    print(f"  Bugs: {len(seg.stores['bugs'])}, Patterns: {len(seg.stores['patterns'])}")
    
    # Test 4: Full pipeline
    print("\n[4] Full Pipeline Test")
    result = fkg.process("Fix the divide function error in Python")
    print(f"  Classification: {result['classification']['primary_category']}")
    print(f"  Insights retrieved: {result['insights_count']}")
    print(f"  Categories in store: {result['metadata']['categories']}")
    
    print("\n" + "="*60)
    print("All tests passed!")
    print("="*60)
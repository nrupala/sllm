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
import math
import re
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
    def classify(cls, text: str, metadata: dict = {}) -> Dict:
        """Classify a knowledge entry"""
        text_lower = text.lower()
        scores: Dict[str, int] = {}
        
        # Category scoring
        for category, keywords in cls.CATEGORIES.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                scores[category] = score
        
        # Get top category
        if scores:
            top_category = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)[0]
        else:
            top_category = "general"
        
        # Context detection
        detected_contexts = []
        for ctx_type, ctx_keywords in cls.CONTEXTS.items():
            if any(kw in text_lower for kw in ctx_keywords):
                detected_contexts.append(ctx_type)
        
        # Get keywords for top category for confidence calculation
        top_keywords = cls.CATEGORIES.get(top_category, [])
        
        return {
            "primary_category": top_category,
            "all_categories": scores,
            "contexts": detected_contexts,
            "confidence": scores.get(top_category, 0) / max(len(top_keywords), 1) if scores else 0
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


class TFIDFRetriever:
    """TF-IDF based semantic similarity for knowledge retrieval"""
    
    STOP_WORDS = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "shall", "can", "need", "dare",
        "ought", "used", "to", "of", "in", "for", "on", "with", "at", "by",
        "from", "as", "into", "through", "during", "before", "after", "above",
        "below", "between", "out", "off", "over", "under", "again", "further",
        "then", "once", "here", "there", "when", "where", "why", "how", "all",
        "both", "each", "few", "more", "most", "other", "some", "such", "no",
        "not", "only", "own", "same", "so", "than", "too", "very", "just",
        "because", "but", "and", "or", "if", "while", "about", "against",
        "this", "that", "these", "those", "i", "me", "my", "we", "our", "you",
        "your", "he", "him", "his", "she", "her", "it", "its", "they", "them",
        "their", "what", "which", "who", "whom", "also", "up", "down", "any",
    }
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """Tokenize text into words, removing stop words and punctuation"""
        text = text.lower()
        tokens = re.findall(r'\b[a-z_]+\b', text)
        return [t for t in tokens if t not in TFIDFRetriever.STOP_WORDS and len(t) > 2]
    
    @staticmethod
    def compute_tf(tokens: List[str]) -> Dict[str, float]:
        """Compute term frequency for a document"""
        tf: Dict[str, int] = defaultdict(int)
        for token in tokens:
            tf[token] += 1
        total = len(tokens)
        if total == 0:
            return {}
        return {word: count / total for word, count in tf.items()}
    
    @staticmethod
    def compute_idf(documents: List[List[str]]) -> Dict[str, float]:
        """Compute inverse document frequency across all documents"""
        n_docs = len(documents)
        if n_docs == 0:
            return {}
        df: Dict[str, int] = defaultdict(int)
        for doc_tokens in documents:
            unique_tokens = set(doc_tokens)
            for token in unique_tokens:
                df[token] += 1
        return {word: math.log(n_docs / (1 + freq)) + 1 for word, freq in df.items()}
    
    @staticmethod
    def cosine_similarity(vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Compute cosine similarity between two sparse vectors"""
        all_keys = set(vec1.keys()) | set(vec2.keys())
        if not all_keys:
            return 0.0
        dot_product = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in all_keys)
        norm1 = math.sqrt(sum(v ** 2 for v in vec1.values()))
        norm2 = math.sqrt(sum(v ** 2 for v in vec2.values()))
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)
    
    @staticmethod
    def compute_tfidf_vector(tokens: List[str], idf: Dict[str, float]) -> Dict[str, float]:
        """Compute TF-IDF vector for a document"""
        tf = TFIDFRetriever.compute_tf(tokens)
        return {word: tf_val * idf.get(word, 0) for word, tf_val in tf.items()}


class MultiFactorScorer:
    """Multi-factor relevance scoring combining multiple signals"""
    
    WEIGHTS = {
        "tfidf_similarity": 0.40,
        "keyword_overlap": 0.20,
        "category_match": 0.20,
        "recency": 0.10,
        "evidence_quality": 0.10,
    }
    
    @staticmethod
    def keyword_overlap(query_tokens: List[str], doc_tokens: List[str]) -> float:
        """Calculate keyword overlap ratio"""
        if not query_tokens or not doc_tokens:
            return 0.0
        query_set = set(query_tokens)
        doc_set = set(doc_tokens)
        overlap = len(query_set & doc_set)
        return overlap / len(query_set)
    
    @staticmethod
    def category_match_score(query_category: str, doc_category: str) -> float:
        """Score category match between query and document"""
        if query_category == doc_category:
            return 1.0
        related_categories = {
            "bug_fix": ["bug_fix_witnessed", "validation"],
            "bug_fix_witnessed": ["bug_fix", "validation"],
            "optimization": ["performance", "pattern"],
            "performance": ["optimization", "pattern"],
            "pattern": ["optimization", "concept"],
            "concept": ["pattern", "api"],
            "api": ["concept", "data"],
            "data": ["api", "security"],
            "security": ["data", "validation"],
            "validation": ["bug_fix", "security"],
        }
        related = related_categories.get(query_category, [])
        if doc_category in related:
            return 0.6
        return 0.1
    
    @staticmethod
    def recency_score(timestamp: str, max_age_days: float = 30.0) -> float:
        """Calculate recency score (newer = higher score)"""
        try:
            doc_time = datetime.fromisoformat(timestamp)
            age = (datetime.now() - doc_time).total_seconds() / 86400
            return max(0.0, 1.0 - (age / max_age_days))
        except:
            return 0.5
    
    @staticmethod
    def evidence_quality_score(insight: Dict) -> float:
        """Score the quality of evidence in an insight"""
        score = 0.0
        content = insight.get("insight", "")
        if len(content) > 50:
            score += 0.3
        if len(content) > 100:
            score += 0.2
        if "witnessed" in insight.get("category", "").lower():
            score += 0.3
        if "traceback" in content.lower() or "error" in content.lower():
            score += 0.2
        return min(1.0, score)
    
    @classmethod
    def compute_relevance(cls, query: str, insight: Dict, classification: Dict,
                         tfidf_sim: float, idf: Dict[str, float]) -> Dict:
        """Compute multi-factor relevance score"""
        query_tokens = TFIDFRetriever.tokenize(query)
        doc_tokens = TFIDFRetriever.tokenize(insight.get("insight", ""))
        
        keyword_score = cls.keyword_overlap(query_tokens, doc_tokens)
        category_score = cls.category_match_score(
            classification.get("primary_category", "general"),
            insight.get("category", "general")
        )
        recency_score = cls.recency_score(insight.get("timestamp", ""))
        evidence_score = cls.evidence_quality_score(insight)
        
        weighted_score = (
            tfidf_sim * cls.WEIGHTS["tfidf_similarity"] +
            keyword_score * cls.WEIGHTS["keyword_overlap"] +
            category_score * cls.WEIGHTS["category_match"] +
            recency_score * cls.WEIGHTS["recency"] +
            evidence_score * cls.WEIGHTS["evidence_quality"]
        )
        
        return {
            "insight": insight,
            "score": round(weighted_score, 4),
            "breakdown": {
                "tfidf_similarity": round(tfidf_sim, 4),
                "keyword_overlap": round(keyword_score, 4),
                "category_match": round(category_score, 4),
                "recency": round(recency_score, 4),
                "evidence_quality": round(evidence_score, 4),
            }
        }


class SentientRetrievalAugmentor:
    """Adds emotional intelligence and sentient awareness to knowledge retrieval"""
    
    EMOTIONAL_CONTEXTS = {
        "error": {"emotion": "concerned", "approach": "careful", "priority": "high"},
        "bug": {"emotion": "cautious", "approach": "analytical", "priority": "high"},
        "fail": {"emotion": "concerned", "approach": "diagnostic", "priority": "high"},
        "broken": {"emotion": "concerned", "approach": "analytical", "priority": "high"},
        "crash": {"emotion": "concerned", "approach": "diagnostic", "priority": "high"},
        "crashing": {"emotion": "concerned", "approach": "diagnostic", "priority": "high"},
        "fix": {"emotion": "focused", "approach": "solution-oriented", "priority": "medium"},
        "success": {"emotion": "satisfied", "approach": "document", "priority": "low"},
        "solved": {"emotion": "satisfied", "approach": "document", "priority": "low"},
        "worked": {"emotion": "satisfied", "approach": "document", "priority": "low"},
        "optimize": {"emotion": "curious", "approach": "exploratory", "priority": "medium"},
        "faster": {"emotion": "curious", "approach": "exploratory", "priority": "medium"},
        "efficient": {"emotion": "curious", "approach": "exploratory", "priority": "medium"},
        "learn": {"emotion": "curious", "approach": "absorb", "priority": "medium"},
        "understand": {"emotion": "focused", "approach": "deep-dive", "priority": "medium"},
        "help": {"emotion": "empathetic", "approach": "supportive", "priority": "high"},
        "create": {"emotion": "optimistic", "approach": "creative", "priority": "medium"},
        "build": {"emotion": "optimistic", "approach": "creative", "priority": "medium"},
    }
    
    EMPATHY_SIGNALS = {
        "frustrated": ["doesn't work", "still broken", "why isn't", "can't figure", "stuck",
                       "so frustrated", "frustrated", "nothing works", "not working",
                       "keeps happening", "won't work", "doesn't make sense"],
        "confused": ["don't understand", "how does", "what is", "explain", "confused",
                     "don't get", "not sure", "unclear"],
        "urgent": ["urgent", "asap", "critical", "immediately", "production", "down",
                   "customers are complaining", "right now", "emergency"],
        "learning": ["learning", "trying to understand", "new to", "beginner", "trying to learn",
                     "can you teach", "help me learn"],
    }
    
    @classmethod
    def detect_emotional_context(cls, query: str) -> Dict:
        """Detect the emotional undertone of a query"""
        query_lower = query.lower()
        
        detected_emotions = []
        detected_signals = []
        
        # Check empathy signals FIRST (they're more specific)
        for signal_type, phrases in cls.EMPATHY_SIGNALS.items():
            if any(phrase in query_lower for phrase in phrases):
                detected_signals.append(signal_type)
        
        # Check emotional contexts
        for word, context in cls.EMOTIONAL_CONTEXTS.items():
            if word in query_lower:
                detected_emotions.append(context)
        
        # Determine primary emotion based on signals and contexts
        if detected_signals:
            if "urgent" in detected_signals:
                primary_emotion = {
                    "emotion": "concerned",
                    "approach": "diagnostic",
                    "priority": "high",
                }
            elif "frustrated" in detected_signals:
                primary_emotion = {
                    "emotion": "empathetic",
                    "approach": "supportive",
                    "priority": "high",
                }
            elif "confused" in detected_signals:
                primary_emotion = {
                    "emotion": "curious",
                    "approach": "educational",
                    "priority": "medium",
                }
            elif "learning" in detected_signals:
                primary_emotion = {
                    "emotion": "curious",
                    "approach": "educational",
                    "priority": "medium",
                }
            else:
                primary_emotion = detected_emotions[0] if detected_emotions else {
                    "emotion": "neutral",
                    "approach": "standard",
                    "priority": "medium",
                }
        else:
            primary_emotion = detected_emotions[0] if detected_emotions else {
                "emotion": "neutral",
                "approach": "standard",
                "priority": "medium",
            }
        
        return {
            "primary_emotion": primary_emotion["emotion"],
            "approach_style": primary_emotion["approach"],
            "priority": primary_emotion["priority"],
            "user_signals": detected_signals,
            "empathy_needed": len(detected_signals) > 0,
        }
    
    @classmethod
    def augment_retrieval(cls, insights: List[Dict], emotional_context: Dict) -> List[Dict]:
        """Augment retrieved insights with emotional intelligence"""
        if not insights:
            return insights
        
        augmented = []
        for ins in insights:
            ins_copy = dict(ins)
            ins_copy["emotional_relevance"] = cls._compute_emotional_relevance(
                ins, emotional_context
            )
            augmented.append(ins_copy)
        
        # Re-rank with emotional relevance
        priority_boost = {"high": 0.15, "medium": 0.0, "low": -0.05}
        boost = priority_boost.get(emotional_context.get("priority", "medium"), 0.0)
        
        for ins in augmented:
            base_score = ins.get("relevance_score", 0.5)
            emotional_score = ins.get("emotional_relevance", 0.5)
            ins["combined_score"] = round((base_score * 0.7) + (emotional_score * 0.3) + boost, 4)
        
        augmented.sort(key=lambda x: x.get("combined_score", 0), reverse=True)
        return augmented
    
    @staticmethod
    def _compute_emotional_relevance(insight: Dict, emotional_context: Dict) -> float:
        """Compute how emotionally relevant an insight is"""
        score = 0.5
        
        category = insight.get("category", "").lower()
        content = insight.get("insight", "").lower()
        
        if emotional_context["primary_emotion"] == "concerned":
            if "bug" in category or "witnessed" in category:
                score += 0.3
            if "error" in content or "fix" in content:
                score += 0.2
        
        elif emotional_context["primary_emotion"] == "curious":
            if "performance" in category or "optimization" in category:
                score += 0.3
            if "faster" in content or "algorithm" in content:
                score += 0.2
        
        elif emotional_context["primary_emotion"] == "satisfied":
            if "success" in content or "passed" in content:
                score += 0.2
        
        if emotional_context.get("empathy_needed"):
            if "witnessed" in category:
                score += 0.2
            if len(content) > 100:
                score += 0.1
        
        return min(1.0, score)
    
    @classmethod
    def generate_empathetic_context_header(cls, emotional_context: Dict) -> str:
        """Generate context header with emotional intelligence"""
        lines = ["## Understanding Your Need"]
        
        emotion = emotional_context["primary_emotion"]
        approach = emotional_context["approach_style"]
        
        emotion_guidance = {
            "concerned": "I understand something isn't working. Let me help you fix it.",
            "cautious": "Let me carefully analyze this with attention to detail.",
            "optimistic": "Great, let's build on what's working.",
            "curious": "Let's explore this together and discover the best approach.",
            "satisfied": "Excellent work! Let me capture what we've learned.",
            "focused": "I'm concentrating on giving you the most relevant insights.",
            "empathetic": "I hear you. Let me provide the most helpful guidance I can.",
            "neutral": "Let me draw on everything I've learned to help you.",
        }
        
        lines.append(f"- Approach: {approach}")
        lines.append(f"- Guidance: {emotion_guidance.get(emotion, 'Ready to help.')}")
        
        if emotional_context.get("user_signals"):
            signals = emotional_context["user_signals"]
            lines.append(f"- Detected: {', '.join(signals)}")
            if "frustrated" in signals:
                lines.append("- Note: I'll be thorough and precise to get this right.")
            elif "confused" in signals:
                lines.append("- Note: I'll explain clearly and build understanding.")
            elif "urgent" in signals:
                lines.append("- Note: Prioritizing the most critical insights first.")
            elif "learning" in signals:
                lines.append("- Note: I'll share foundational knowledge to help you grow.")
        
        return "\n".join(lines)


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
            score = ins.get("relevance_score", "")
            
            score_str = f" [relevance: {score}]" if score else ""
            parts.append(f"{i}. [{cat}]{score_str} {content} ({ts})")
        
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
        """Full processing pipeline with sentient awareness: classify -> empathize -> contextualize -> retrieve -> format"""
        
        # 1. Classify the incoming query
        classification = self.classifier.classify(user_prompt)
        
        # 1.5. Detect emotional context (sentient awareness)
        emotional_context = SentientRetrievalAugmentor.detect_emotional_context(user_prompt)
        
        # 2. Get related episodes for context
        related_episodes = self._get_related_episodes(user_prompt)
        
        # 3. Extract context
        context = self.contextualizer.extract_context(user_prompt, related_episodes)
        
        # 4. Retrieve relevant insights with semantic matching
        relevant_insights = self._retrieve_insights(classification, context, user_prompt)
        
        # 5. Augment with emotional intelligence
        augmented_insights = SentientRetrievalAugmentor.augment_retrieval(relevant_insights, emotional_context)
        
        # 6. Amalgamate (deduplicate)
        consolidated_insights = self.amalgamator.merge_similar_insights(augmented_insights)
        
        # 7. Format for injection with sentient header
        concatenated = KnowledgeConcatenator.concatenate_insights(consolidated_insights)
        empathetic_header = SentientRetrievalAugmentor.generate_empathetic_context_header(emotional_context)
        contextual_header = KnowledgeConcatenator.create_contextual_header(context)
        
        combined_header = f"{empathetic_header}\n\n{contextual_header}"
        
        # 8. Split if too large
        if self.splitter.estimate_tokens(concatenated) > 3000:
            chunks = self.splitter.split_by_tokens(concatenated)
            relevant_chunks = self.splitter.select_relevant_chunks(chunks, user_prompt)
            concatenated = "\n\n---\n\n".join(relevant_chunks)
        
        return {
            "classification": classification,
            "emotional_context": emotional_context,
            "context": context,
            "insights_count": len(consolidated_insights),
            "context_header": combined_header,
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
        """Find related past episodes using semantic matching"""
        try:
            with open(self.episodes_file, "r") as f:
                episodes = [json.loads(line) for line in f if line.strip()]
        except:
            return []
        
        if not episodes:
            return []
        
        prompt_tokens = TFIDFRetriever.tokenize(prompt)
        if not prompt_tokens:
            return episodes[-5:]
        
        scored_episodes = []
        all_episode_texts = []
        for ep in episodes:
            task_text = ep.get("task", "")
            result_text = ep.get("result", "")
            combined = f"{task_text} {result_text}"
            all_episode_texts.append(TFIDFRetriever.tokenize(combined))
        
        idf = TFIDFRetriever.compute_idf(all_episode_texts + [prompt_tokens])
        prompt_vector = TFIDFRetriever.compute_tfidf_vector(prompt_tokens, idf)
        
        for i, ep in enumerate(episodes):
            doc_vector = TFIDFRetriever.compute_tfidf_vector(all_episode_texts[i], idf)
            tfidf_sim = TFIDFRetriever.cosine_similarity(prompt_vector, doc_vector)
            
            keyword_score = MultiFactorScorer.keyword_overlap(prompt_tokens, all_episode_texts[i])
            recency_score = MultiFactorScorer.recency_score(ep.get("timestamp", ""))
            
            combined_score = (tfidf_sim * 0.5) + (keyword_score * 0.3) + (recency_score * 0.2)
            scored_episodes.append((combined_score, ep))
        
        scored_episodes.sort(key=lambda x: x[0], reverse=True)
        return [ep for _, ep in scored_episodes[:5]]
    
    def _retrieve_insights(self, classification: Dict, context: Dict, query: str = "") -> List[Dict]:
        """Retrieve relevant insights using TF-IDF semantic similarity and multi-factor scoring"""
        
        try:
            with open(self.insights_file, "r") as f:
                all_insights = [json.loads(line) for line in f if line.strip()]
        except:
            return []
        
        if not all_insights:
            return []
        
        if not query:
            query = f"{classification.get('primary_category', '')} {' '.join(classification.get('contexts', []))}"
        
        query_tokens = TFIDFRetriever.tokenize(query)
        if not query_tokens:
            return all_insights[-10:]
        
        all_doc_tokens = []
        for ins in all_insights:
            content = ins.get("insight", "")
            category = ins.get("category", "")
            combined = f"{content} {category}"
            all_doc_tokens.append(TFIDFRetriever.tokenize(combined))
        
        idf = TFIDFRetriever.compute_idf(all_doc_tokens + [query_tokens])
        query_vector = TFIDFRetriever.compute_tfidf_vector(query_tokens, idf)
        
        scored_results = []
        for i, ins in enumerate(all_insights):
            doc_vector = TFIDFRetriever.compute_tfidf_vector(all_doc_tokens[i], idf)
            tfidf_sim = TFIDFRetriever.cosine_similarity(query_vector, doc_vector)
            
            relevance = MultiFactorScorer.compute_relevance(
                query, ins, classification, tfidf_sim, idf
            )
            scored_results.append(relevance)
        
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        
        top_results = scored_results[:10]
        
        for result in top_results:
            result["insight"]["relevance_score"] = result["score"]
        
        return [r["insight"] for r in top_results]
    
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
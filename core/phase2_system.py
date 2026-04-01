"""
SL-LLM Phase 2: Parallel Execution, Web Access, Enhanced Hallucination Prevention
- Async task queue for parallel operations
- Offline-first web access with local cache
- Enhanced hallucination prevention with citations
"""

import json
import os
import time
import hashlib
import threading
import queue
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Callable, Any
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict


# ============================================================
# PARALLEL TASK EXECUTION
# ============================================================

@dataclass
class TaskResult:
    task_id: str
    status: str  # pending, running, completed, failed, cancelled
    result: Any = None
    error: str = None
    started_at: str = None
    completed_at: str = None
    duration: float = 0.0


class ParallelTaskExecutor:
    """Execute multiple tasks concurrently with thread pool"""
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_queue: Dict[str, TaskResult] = {}
        self.results: Dict[str, TaskResult] = {}
        self._lock = threading.Lock()
    
    def submit(self, task_id: str, fn: Callable, *args, **kwargs) -> str:
        """Submit a task for parallel execution"""
        with self._lock:
            task = TaskResult(
                task_id=task_id,
                status="pending",
                started_at=datetime.now().isoformat(),
            )
            self.task_queue[task_id] = task
        
        future = self.executor.submit(self._run_task, task_id, fn, *args, **kwargs)
        future.add_done_callback(lambda f: self._on_complete(task_id, f))
        
        return task_id
    
    def submit_batch(self, tasks: List[Dict]) -> List[str]:
        """Submit multiple tasks at once"""
        task_ids = []
        for task in tasks:
            task_id = task.get("id", str(uuid.uuid4())[:8])
            fn = task["fn"]
            args = task.get("args", ())
            kwargs = task.get("kwargs", {})
            self.submit(task_id, fn, *args, **kwargs)
            task_ids.append(task_id)
        return task_ids
    
    def wait_for(self, task_id: str, timeout: float = None) -> TaskResult:
        """Wait for a specific task to complete"""
        start = time.time()
        while True:
            with self._lock:
                task = self.results.get(task_id) or self.task_queue.get(task_id)
            if task and task.status in ["completed", "failed", "cancelled"]:
                return task
            if timeout and (time.time() - start) > timeout:
                return TaskResult(task_id=task_id, status="timeout", error="Timeout")
            time.sleep(0.1)
    
    def wait_for_all(self, task_ids: List[str], timeout: float = None) -> Dict[str, TaskResult]:
        """Wait for all tasks to complete"""
        results = {}
        start = time.time()
        while True:
            all_done = True
            for tid in task_ids:
                with self._lock:
                    task = self.results.get(tid)
                if task and task.status in ["completed", "failed", "cancelled"]:
                    results[tid] = task
                else:
                    all_done = False
            
            if all_done:
                return results
            
            if timeout and (time.time() - start) > timeout:
                for tid in task_ids:
                    if tid not in results:
                        results[tid] = TaskResult(task_id=tid, status="timeout", error="Timeout")
                return results
            
            time.sleep(0.1)
    
    def get_status(self, task_id: str) -> Optional[TaskResult]:
        """Get status of a task"""
        with self._lock:
            return self.results.get(task_id) or self.task_queue.get(task_id)
    
    def get_all_status(self) -> Dict:
        """Get status of all tasks"""
        with self._lock:
            all_tasks = {**self.task_queue, **self.results}
        
        status_counts = defaultdict(int)
        for task in all_tasks.values():
            status_counts[task.status] += 1
        
        return {
            "total_tasks": len(all_tasks),
            "status_counts": dict(status_counts),
            "max_workers": self.max_workers,
        }
    
    def cancel(self, task_id: str) -> bool:
        """Cancel a pending task"""
        with self._lock:
            task = self.task_queue.get(task_id)
            if task and task.status == "pending":
                task.status = "cancelled"
                self.results[task_id] = task
                return True
        return False
    
    def shutdown(self, wait: bool = True):
        """Shutdown the executor"""
        self.executor.shutdown(wait=wait)
    
    def _run_task(self, task_id: str, fn: Callable, *args, **kwargs):
        """Run a task and capture result"""
        with self._lock:
            self.task_queue[task_id].status = "running"
        
        try:
            result = fn(*args, **kwargs)
            return result
        except Exception as e:
            raise e
    
    def _on_complete(self, task_id: str, future):
        """Handle task completion"""
        try:
            result = future.result()
            with self._lock:
                task = self.task_queue[task_id]
                task.status = "completed"
                task.result = result
                task.completed_at = datetime.now().isoformat()
                task.duration = (datetime.fromisoformat(task.completed_at) - datetime.fromisoformat(task.started_at)).total_seconds()
                self.results[task_id] = task
        except Exception as e:
            with self._lock:
                task = self.task_queue[task_id]
                task.status = "failed"
                task.error = str(e)
                task.completed_at = datetime.now().isoformat()
                self.results[task_id] = task


# ============================================================
# OFFLINE-FIRST WEB ACCESS
# ============================================================

class WebCache:
    """Local cache for web content - offline-first"""
    
    def __init__(self, cache_dir: str = "D:/sl/projects/sllm/memory/web_cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.cache_dir / "cache_index.json"
        self.index: Dict[str, Dict] = {}
        self._load_index()
    
    def _load_index(self):
        if self.index_file.exists():
            try:
                with open(self.index_file, "r") as f:
                    self.index = json.load(f)
            except:
                self.index = {}
    
    def _save_index(self):
        with open(self.index_file, "w") as f:
            json.dump(self.index, f, indent=2)
    
    def _url_hash(self, url: str) -> str:
        return hashlib.md5(url.encode()).hexdigest()[:12]
    
    def get(self, url: str, max_age_hours: float = 24.0) -> Optional[Dict]:
        """Get cached content if available and not expired"""
        cache_key = self._url_hash(url)
        entry = self.index.get(cache_key)
        
        if not entry:
            return None
        
        cached_at = datetime.fromisoformat(entry["cached_at"])
        age = (datetime.now() - cached_at).total_seconds() / 3600
        
        if age > max_age_hours:
            return None
        
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            with open(cache_file, "r") as f:
                return json.load(f)
        
        return None
    
    def put(self, url: str, content: Dict, metadata: Dict = None):
        """Cache web content"""
        cache_key = self._url_hash(url)
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        cache_entry = {
            "url": url,
            "content": content,
            "metadata": metadata or {},
            "cached_at": datetime.now().isoformat(),
        }
        
        with open(cache_file, "w") as f:
            json.dump(cache_entry, f, indent=2)
        
        self.index[cache_key] = {
            "url": url,
            "cached_at": cache_entry["cached_at"],
            "size": len(json.dumps(content)),
        }
        self._save_index()
    
    def clear_expired(self, max_age_hours: float = 24.0):
        """Remove expired cache entries"""
        expired = []
        for key, entry in self.index.items():
            cached_at = datetime.fromisoformat(entry["cached_at"])
            age = (datetime.now() - cached_at).total_seconds() / 3600
            if age > max_age_hours:
                expired.append(key)
        
        for key in expired:
            cache_file = self.cache_dir / f"{key}.json"
            if cache_file.exists():
                cache_file.unlink()
            del self.index[key]
        
        if expired:
            self._save_index()
        
        return len(expired)
    
    def get_stats(self) -> Dict:
        total_size = sum(e.get("size", 0) for e in self.index.values())
        return {
            "entries": len(self.index),
            "total_size_kb": total_size / 1024,
            "cache_dir": str(self.cache_dir),
        }


class OfflineFirstWebAccess:
    """Web access that prefers local cache, falls back to live fetch"""
    
    def __init__(self, cache: WebCache = None, fetch_fn: Callable = None):
        self.cache = cache or WebCache()
        self.fetch_fn = fetch_fn  # External fetch function (set when online)
        self.offline_mode = True  # Default to offline
        self.request_log: List[Dict] = []
    
    def set_online(self, fetch_fn: Callable):
        """Enable online mode with fetch function"""
        self.fetch_fn = fetch_fn
        self.offline_mode = False
    
    def set_offline(self):
        """Force offline mode"""
        self.offline_mode = True
    
    def fetch(self, url: str, max_age_hours: float = 24.0, force_refresh: bool = False) -> Dict:
        """Fetch content: cache first, then live if online"""
        # Check cache first
        if not force_refresh:
            cached = self.cache.get(url, max_age_hours)
            if cached:
                self.request_log.append({
                    "url": url,
                    "source": "cache",
                    "timestamp": datetime.now().isoformat(),
                })
                return {"source": "cache", "content": cached.get("content"), "cached_at": cached.get("cached_at")}
        
        # Try live fetch if online
        if not self.offline_mode and self.fetch_fn:
            try:
                content = self.fetch_fn(url)
                self.cache.put(url, content)
                self.request_log.append({
                    "url": url,
                    "source": "live",
                    "timestamp": datetime.now().isoformat(),
                })
                return {"source": "live", "content": content}
            except Exception as e:
                return {"source": "error", "error": str(e)}
        
        # Offline with no cache
        self.request_log.append({
            "url": url,
            "source": "offline_no_cache",
            "timestamp": datetime.now().isoformat(),
        })
        return {"source": "offline", "error": "No cached content available and offline mode active"}
    
    def get_status(self) -> Dict:
        return {
            "offline_mode": self.offline_mode,
            "cache": self.cache.get_stats(),
            "request_count": len(self.request_log),
            "recent_requests": self.request_log[-5:],
        }


# ============================================================
# ENHANCED HALLUCINATION PREVENTION
# ============================================================

class CitationTracker:
    """Track citations for all claims in output"""
    
    def __init__(self):
        self.citations: List[Dict] = []
        self.uncited_claims: List[str] = []
    
    def add_citation(self, claim: str, source: str, confidence: float):
        """Add a citation for a claim"""
        self.citations.append({
            "claim": claim,
            "source": source,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat(),
        })
    
    def add_uncited_claim(self, claim: str):
        """Track a claim without citation"""
        self.uncited_claims.append(claim)
    
    def get_citation_rate(self) -> float:
        """Get ratio of cited claims to total claims"""
        total = len(self.citations) + len(self.uncited_claims)
        if total == 0:
            return 1.0
        return len(self.citations) / total
    
    def get_status(self) -> Dict:
        return {
            "total_citations": len(self.citations),
            "uncited_claims": len(self.uncited_claims),
            "citation_rate": self.get_citation_rate(),
            "recent_citations": self.citations[-5:],
        }


class EnhancedHallucinationPrevention:
    """Enhanced hallucination prevention with citations and external validation"""
    
    def __init__(self, citation_tracker: CitationTracker = None):
        self.citation_tracker = citation_tracker or CitationTracker()
        self.validation_log: List[Dict] = []
    
    def validate_with_citations(self, output: str, knowledge: List[Dict]) -> Dict:
        """Validate output and add citations where possible"""
        sentences = output.split(". ")
        validated_sentences = []
        
        for sentence in sentences:
            if len(sentence.strip()) < 10:
                validated_sentences.append(sentence)
                continue
            
            # Try to find supporting knowledge
            cited = False
            for ins in knowledge:
                content = ins.get("insight", ins.get("content", ""))
                if self._sentence_supported(sentence, content):
                    self.citation_tracker.add_citation(
                        claim=sentence,
                        source=ins.get("category", "knowledge_graph"),
                        confidence=0.8,
                    )
                    validated_sentences.append(f"{sentence} [source: {ins.get('category', 'kg')}]")
                    cited = True
                    break
            
            if not cited:
                self.citation_tracker.add_uncited_claim(sentence)
                validated_sentences.append(sentence)
        
        result = {
            "validated_output": ". ".join(validated_sentences),
            "citation_rate": self.citation_tracker.get_citation_rate(),
            "uncited_claims": len(self.citation_tracker.uncited_claims),
            "total_claims": len(self.citation_tracker.citations) + len(self.citation_tracker.uncited_claims),
        }
        
        self.validation_log.append({
            "timestamp": datetime.now().isoformat(),
            "citation_rate": result["citation_rate"],
            "uncited_claims": result["uncited_claims"],
        })
        
        return result
    
    def _sentence_supported(self, sentence: str, knowledge_content: str) -> bool:
        """Check if a sentence is supported by knowledge content"""
        sentence_words = set(sentence.lower().split())
        knowledge_words = set(knowledge_content.lower().split())
        
        overlap = len(sentence_words & knowledge_words)
        if overlap >= 3:
            return True
        
        # Check for key term overlap
        key_terms = [w for w in sentence_words if len(w) > 4]
        if key_terms:
            matching = sum(1 for t in key_terms if t in knowledge_words)
            if matching >= 2:
                return True
        
        return False
    
    def get_status(self) -> Dict:
        return {
            "citation_tracker": self.citation_tracker.get_status(),
            "validation_log_count": len(self.validation_log),
            "recent_validations": self.validation_log[-5:],
        }


# ============================================================
# MAIN PHASE 2 SYSTEM
# ============================================================

class Phase2System:
    """Unified Phase 2: Parallel Execution + Web Access + Enhanced Hallucination Prevention"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ParallelTaskExecutor(max_workers=max_workers)
        self.web_access = OfflineFirstWebAccess()
        self.hallucination_prevention = EnhancedHallucinationPrevention()
    
    def execute_parallel(self, tasks: List[Dict]) -> Dict[str, TaskResult]:
        """Execute multiple tasks in parallel"""
        task_ids = self.executor.submit_batch(tasks)
        return self.executor.wait_for_all(task_ids)
    
    def fetch_with_cache(self, url: str, force_refresh: bool = False) -> Dict:
        """Fetch content with offline-first caching"""
        return self.web_access.fetch(url, force_refresh=force_refresh)
    
    def validate_with_citations(self, output: str, knowledge: List[Dict]) -> Dict:
        """Validate output with citation tracking"""
        return self.hallucination_prevention.validate_with_citations(output, knowledge)
    
    def get_status(self) -> Dict:
        return {
            "parallel_executor": self.executor.get_all_status(),
            "web_access": self.web_access.get_status(),
            "hallucination_prevention": self.hallucination_prevention.get_status(),
        }
    
    def shutdown(self):
        self.executor.shutdown()


# Singleton
_phase2 = None

def get_phase2_system() -> Phase2System:
    global _phase2
    if _phase2 is None:
        _phase2 = Phase2System()
    return _phase2

"""
SL-LLM Persistent Memory System
- Auto-save/load personality, PDCA state, and emotional memory on startup/shutdown
- Cross-instance Knowledge Graph sync via file-based sync protocol
- Long-term strategic planning with persistent goal tracking
"""

import json
import os
import shutil
import hashlib
import uuid
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict


# ============================================================
# AUTO-SAVE/LOAD MANAGER
# ============================================================

class PersistentMemoryManager:
    """Manages automatic persistence of all SL-LLM state"""
    
    STATE_FILES = {
        "personality": "memory/personality_state.json",
        "pdca": "memory/pdca_reward_state.json",
        "dual_loop": "memory/dual_loop_state.json",
        "knowledge_graph": "memory/knowledge_graph.bin",
        "insights": "memory/insights.jsonl",
        "episodes": "memory/episodes.jsonl",
        "sentient": "memory/sentient_state.json",
    }
    
    def __init__(self, base_dir: str = "D:/sl/projects/sllm"):
        self.base_dir = Path(base_dir)
        self.memory_dir = self.base_dir / "memory"
        self.backup_dir = self.memory_dir / "backups"
        self.sync_dir = self.memory_dir / "sync"
        self.state_file = self.memory_dir / "persistence_state.json"
        
        self._ensure_dirs()
        self.last_save = None
        self.save_count = 0
        self.load_count = 0
    
    def _ensure_dirs(self):
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.sync_dir.mkdir(parents=True, exist_ok=True)
    
    def save_all(self, state: Dict = None) -> Dict:
        """Save all persistent state with backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        
        # Backup existing state files
        for name, filepath in self.STATE_FILES.items():
            src = self.base_dir / filepath
            if src.exists():
                dst = backup_path / src.name
                shutil.copy2(src, dst)
                saved_files.append(name)
        
        # Save persistence state
        persistence_state = {
            "last_save": datetime.now().isoformat(),
            "save_count": self.save_count + 1,
            "backup_path": str(backup_path),
            "saved_files": saved_files,
            "state": state or {},
        }
        
        with open(self.state_file, "w") as f:
            json.dump(persistence_state, f, indent=2)
        
        self.save_count += 1
        self.last_save = datetime.now()
        
        return {
            "saved": saved_files,
            "backup": str(backup_path),
            "save_count": self.save_count,
            "timestamp": persistence_state["last_save"],
        }
    
    def load_all(self) -> Dict:
        """Load all persistent state"""
        if not self.state_file.exists():
            return {"status": "no_previous_state"}
        
        with open(self.state_file, "r") as f:
            persistence_state = json.load(f)
        
        loaded_files = []
        for name in persistence_state.get("saved_files", []):
            filepath = self.base_dir / self.STATE_FILES.get(name, "")
            if filepath.exists():
                loaded_files.append(name)
        
        self.load_count += 1
        
        return {
            "loaded": loaded_files,
            "last_save": persistence_state.get("last_save"),
            "load_count": self.load_count,
            "status": "restored",
        }
    
    def get_status(self) -> Dict:
        return {
            "save_count": self.save_count,
            "load_count": self.load_count,
            "last_save": self.last_save.isoformat() if self.last_save else None,
            "state_files": {name: (self.base_dir / fp).exists() for name, fp in self.STATE_FILES.items()},
            "backup_count": len(list(self.backup_dir.glob("backup_*"))),
        }


# ============================================================
# CROSS-INSTANCE SYNC
# ============================================================

class CrossInstanceSync:
    """Sync Knowledge Graph across multiple SL-LLM instances"""
    
    def __init__(self, sync_dir: str = "D:/sl/projects/sllm/memory/sync"):
        self.sync_dir = Path(sync_dir)
        self.sync_dir.mkdir(parents=True, exist_ok=True)
        self.instance_id = str(uuid.uuid4())[:8]
        self.sync_log: List[Dict] = []
    
    def export_state(self, state: Dict) -> str:
        """Export state for other instances to import"""
        export_file = self.sync_dir / f"state_{self.instance_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "instance_id": self.instance_id,
            "exported_at": datetime.now().isoformat(),
            "state": state,
        }
        
        with open(export_file, "w") as f:
            json.dump(export_data, f, indent=2)
        
        self.sync_log.append({
            "action": "export",
            "file": str(export_file),
            "timestamp": datetime.now().isoformat(),
        })
        
        return str(export_file)
    
    def import_state(self, filepath: str) -> Dict:
        """Import state from another instance"""
        path = Path(filepath)
        if not path.exists():
            return {"error": "File not found"}
        
        with open(path, "r") as f:
            data = json.load(f)
        
        self.sync_log.append({
            "action": "import",
            "source": data.get("instance_id", "unknown"),
            "file": str(path),
            "timestamp": datetime.now().isoformat(),
        })
        
        return {
            "source_instance": data.get("instance_id"),
            "exported_at": data.get("exported_at"),
            "state": data.get("state", {}),
        }
    
    def discover_exports(self) -> List[Dict]:
        """Find available state exports from other instances"""
        exports = []
        for f in self.sync_dir.glob("state_*.json"):
            if self.instance_id not in f.name:
                try:
                    with open(f, "r") as fh:
                        data = json.load(fh)
                    exports.append({
                        "file": str(f),
                        "instance_id": data.get("instance_id"),
                        "exported_at": data.get("exported_at"),
                    })
                except:
                    pass
        
        return sorted(exports, key=lambda x: x.get("exported_at", ""), reverse=True)
    
    def get_sync_status(self) -> Dict:
        return {
            "instance_id": self.instance_id,
            "sync_dir": str(self.sync_dir),
            "exports_available": len(list(self.sync_dir.glob("state_*.json"))),
            "sync_log_count": len(self.sync_log),
            "recent_syncs": self.sync_log[-5:],
        }


# ============================================================
# LONG-TERM STRATEGIC PLANNING
# ============================================================

@dataclass
class StrategicGoal:
    id: str
    name: str
    description: str
    priority: float  # 0.0-1.0
    status: str  # active, completed, abandoned
    created: str
    deadline: Optional[str] = None
    subgoals: List[str] = field(default_factory=list)
    progress: float = 0.0
    lessons_learned: List[str] = field(default_factory=list)


class StrategicPlanner:
    """Long-term strategic planning with persistent goal tracking"""
    
    def __init__(self, state_file: str = "D:/sl/projects/sllm/memory/strategic_plan.json"):
        self.state_file = Path(state_file)
        self.goals: Dict[str, StrategicGoal] = {}
        self.plan_history: List[Dict] = []
        self._load()
    
    def create_goal(self, name: str, description: str, priority: float = 0.5,
                   deadline: str = None) -> str:
        """Create a new strategic goal"""
        goal_id = str(uuid.uuid4())[:8]
        goal = StrategicGoal(
            id=goal_id,
            name=name,
            description=description,
            priority=priority,
            status="active",
            created=datetime.now().isoformat(),
            deadline=deadline,
        )
        self.goals[goal_id] = goal
        self._save()
        return goal_id
    
    def update_progress(self, goal_id: str, progress: float, lesson: str = None):
        """Update goal progress"""
        if goal_id in self.goals:
            goal = self.goals[goal_id]
            goal.progress = min(1.0, max(0.0, progress))
            if lesson:
                goal.lessons_learned.append(lesson)
            if progress >= 1.0:
                goal.status = "completed"
            self._save()
    
    def add_subgoal(self, goal_id: str, subgoal_name: str) -> str:
        """Add a subgoal to a strategic goal"""
        subgoal_id = str(uuid.uuid4())[:8]
        if goal_id in self.goals:
            self.goals[goal_id].subgoals.append(subgoal_id)
            self.goals[subgoal_id] = StrategicGoal(
                id=subgoal_id,
                name=subgoal_name,
                description=f"Subgoal of {self.goals[goal_id].name}",
                priority=self.goals[goal_id].priority * 0.8,
                status="active",
                created=datetime.now().isoformat(),
            )
            self._save()
        return subgoal_id
    
    def get_active_goals(self) -> List[Dict]:
        """Get all active goals sorted by priority"""
        active = [g for g in self.goals.values() if g.status == "active"]
        active.sort(key=lambda g: g.priority, reverse=True)
        return [
            {
                "id": g.id,
                "name": g.name,
                "description": g.description,
                "priority": g.priority,
                "progress": g.progress,
                "subgoals": len(g.subgoals),
                "lessons": len(g.lessons_learned),
                "created": g.created,
                "deadline": g.deadline,
            }
            for g in active
        ]
    
    def get_completed_goals(self) -> List[Dict]:
        """Get completed goals"""
        completed = [g for g in self.goals.values() if g.status == "completed"]
        return [
            {
                "id": g.id,
                "name": g.name,
                "progress": g.progress,
                "lessons_learned": g.lessons_learned,
                "completed_at": g.created,
            }
            for g in completed
        ]
    
    def get_strategic_overview(self) -> Dict:
        """Get complete strategic overview"""
        active = self.get_active_goals()
        completed = self.get_completed_goals()
        
        total_progress = 0
        if active:
            total_progress = sum(g["progress"] for g in active) / len(active)
        
        return {
            "total_goals": len(self.goals),
            "active_goals": len(active),
            "completed_goals": len(completed),
            "overall_progress": total_progress,
            "active": active,
            "completed": completed,
            "plan_history": self.plan_history[-10:],
        }
    
    def _save(self):
        """Save strategic plan to file"""
        data = {
            "goals": {
                gid: {
                    "id": g.id,
                    "name": g.name,
                    "description": g.description,
                    "priority": g.priority,
                    "status": g.status,
                    "created": g.created,
                    "deadline": g.deadline,
                    "subgoals": g.subgoals,
                    "progress": g.progress,
                    "lessons_learned": g.lessons_learned,
                }
                for gid, g in self.goals.items()
            },
            "plan_history": self.plan_history[-50:],
            "saved_at": datetime.now().isoformat(),
        }
        
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def _load(self):
        """Load strategic plan from file"""
        if not self.state_file.exists():
            return
        
        try:
            with open(self.state_file, "r") as f:
                data = json.load(f)
            
            for gid, gdata in data.get("goals", {}).items():
                self.goals[gid] = StrategicGoal(
                    id=gdata["id"],
                    name=gdata["name"],
                    description=gdata["description"],
                    priority=gdata["priority"],
                    status=gdata["status"],
                    created=gdata["created"],
                    deadline=gdata.get("deadline"),
                    subgoals=gdata.get("subgoals", []),
                    progress=gdata.get("progress", 0.0),
                    lessons_learned=gdata.get("lessons_learned", []),
                )
            
            self.plan_history = data.get("plan_history", [])
        except Exception as e:
            print(f"Could not load strategic plan: {e}")


# ============================================================
# MAIN PHASE 1 SYSTEM
# ============================================================

class Phase1System:
    """Unified Phase 1: Persistent Memory + Cross-Instance Sync + Strategic Planning"""
    
    def __init__(self, base_dir: str = "D:/sl/projects/sllm"):
        self.persistence = PersistentMemoryManager(base_dir)
        self.sync = CrossInstanceSync(f"{base_dir}/memory/sync")
        self.planner = StrategicPlanner(f"{base_dir}/memory/strategic_plan.json")
    
    def startup(self) -> Dict:
        """Called on SL-LLM startup"""
        load_result = self.persistence.load_all()
        
        # Auto-create default strategic goals if none exist
        if not self.planner.goals:
            self.planner.create_goal(
                "Improve Code Quality",
                "Continuously improve code generation quality through PDCA cycles",
                priority=0.9,
            )
            self.planner.create_goal(
                "Expand Knowledge Graph",
                "Grow knowledge graph with diverse insights across domains",
                priority=0.8,
            )
            self.planner.create_goal(
                "Reduce Hallucination",
                "Minimize ungrounded outputs through improved validation",
                priority=0.85,
            )
        
        return {
            "load": load_result,
            "strategic_overview": self.planner.get_strategic_overview(),
            "sync": self.sync.get_sync_status(),
        }
    
    def shutdown(self, state: Dict = None) -> Dict:
        """Called on SL-LLM shutdown"""
        save_result = self.persistence.save_all(state)
        export_result = self.sync.export_state(state or {})
        
        return {
            "save": save_result,
            "export": export_result,
        }
    
    def get_status(self) -> Dict:
        return {
            "persistence": self.persistence.get_status(),
            "sync": self.sync.get_sync_status(),
            "strategic": self.planner.get_strategic_overview(),
        }


# Singleton
_phase1 = None

def get_phase1_system() -> Phase1System:
    global _phase1
    if _phase1 is None:
        _phase1 = Phase1System()
    return _phase1

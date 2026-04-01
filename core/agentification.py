"""
SL-LLM Agentification System
- Multi-agent collaboration and task decomposition
- Each agent has specialized role
- Communication via message passing
"""

import uuid
import json
from datetime import datetime
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


class AgentRole(Enum):
    ORCHESTRATOR = "orchestrator"      # Coordinates other agents
    PLANNER = "planner"                 # Breaks down tasks
    EXECUTOR = "executor"              # Performs actions
    ANALYZER = "analyzer"              # Analyzes results
    CRITIC = "critic"                  # Evaluates quality
    RESEARCHER = "researcher"          # Gathers information
    SYNTHESIZER = "synthesizer"        # Combines results


@dataclass
class Agent:
    id: str
    name: str
    role: AgentRole
    capabilities: List[str]
    memory: List[Dict] = field(default_factory=list)
    state: Dict = field(default_factory=dict)
    
    def can_handle(self, task_type: str) -> bool:
        return task_type in self.capabilities
    
    def remember(self, item: Dict):
        self.memory.append({
            "timestamp": datetime.now().isoformat(),
            "data": item
        })
    
    def recall(self, limit: int = 10) -> List[Dict]:
        return self.memory[-limit:]


@dataclass
class Message:
    id: str
    sender_id: str
    receiver_id: str
    content: str
    metadata: Dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class AgentMessageBus:
    """Message passing system for inter-agent communication"""
    
    def __init__(self):
        self.messages: List[Message] = []
        self.subscribers: Dict[str, List[str]] = defaultdict(list)
    
    def send(self, sender_id: str, receiver_id: str, content: str, metadata: Dict = None) -> Message:
        msg = Message(
            id=str(uuid.uuid4()),
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(msg)
        return msg
    
    def broadcast(self, sender_id: str, content: str) -> List[Message]:
        return [self.send(sender_id, "all", content)]
    
    def get_messages_for(self, agent_id: str) -> List[Message]:
        return [m for m in self.messages if m.receiver_id == agent_id or m.receiver_id == "all"]
    
    def subscribe(self, agent_id: str, channel: str):
        self.subscribers[channel].append(agent_id)


class AgentTeam:
    """Team of specialized agents working together"""
    
    def __init__(self, name: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.agents: Dict[str, Agent] = {}
        self.message_bus = AgentMessageBus()
        self.task_history: List[Dict] = []
    
    def create_agent(self, name: str, role: AgentRole, capabilities: List[str]) -> Agent:
        agent = Agent(
            id=str(uuid.uuid4()),
            name=name,
            role=role,
            capabilities=capabilities
        )
        self.agents[agent.id] = agent
        return agent
    
    def decompose_task(self, task: str) -> List[Dict]:
        """Break complex task into subtasks"""
        subtasks = []
        
        # Planning agent decomposes
        planner = self._get_agent_by_role(AgentRole.PLANNER)
        if planner:
            subtask = {
                "type": "planning",
                "description": f"Plan execution of: {task}",
                "assigned_to": planner.id
            }
            subtasks.append(subtask)
        
        # Research if needed
        if any(w in task.lower() for w in ["search", "find", "research", "look up"]):
            researcher = self._get_agent_by_role(AgentRole.RESEARCHER)
            if researcher:
                subtasks.append({
                    "type": "research",
                    "description": f"Gather information for: {task}",
                    "assigned_to": researcher.id
                })
        
        # Execution
        executor = self._get_agent_by_role(AgentRole.EXECUTOR)
        if executor:
            subtasks.append({
                "type": "execution",
                "description": f"Execute: {task}",
                "assigned_to": executor.id
            })
        
        # Analysis
        analyzer = self._get_agent_by_role(AgentRole.ANALYZER)
        if analyzer:
            subtasks.append({
                "type": "analysis",
                "description": f"Analyze results of: {task}",
                "assigned_to": analyzer.id
            })
        
        # Critique
        critic = self._get_agent_by_role(AgentRole.CRITIC)
        if critic:
            subtasks.append({
                "type": "critique",
                "description": f"Evaluate quality of: {task}",
                "assigned_to": critic.id
            })
        
        # Synthesis
        synthesizer = self._get_agent_by_role(AgentRole.SYNTHESIZER)
        if synthesizer:
            subtasks.append({
                "type": "synthesis",
                "description": f"Combine results of: {task}",
                "assigned_to": synthesizer.id
            })
        
        return subtasks
    
    def _get_agent_by_role(self, role: AgentRole) -> Optional[Agent]:
        for agent in self.agents.values():
            if agent.role == role:
                return agent
        return None
    
    def coordinate(self, task: str, execute_fn: Callable) -> Dict:
        """Coordinate multi-agent task execution"""
        subtasks = self.decompose_task(task)
        results = []
        
        for subtask in subtasks:
            agent_id = subtask.get("assigned_to")
            agent = self.agents.get(agent_id)
            
            if agent:
                # Send task to agent
                self.message_bus.send(
                    "orchestrator",
                    agent_id,
                    subtask["description"],
                    {"subtask_type": subtask["type"]}
                )
                
                # Execute (simulate)
                result = {
                    "agent": agent.name,
                    "role": agent.role.value,
                    "subtask": subtask["description"],
                    "status": "completed"
                }
                results.append(result)
                
                # Agent remembers
                agent.remember(result)
        
        # Synthesize final result
        final_result = {
            "task": task,
            "subtasks_completed": len(results),
            "agent_results": results,
            "synthesized": True
        }
        
        self.task_history.append(final_result)
        return final_result
    
    def get_team_status(self) -> Dict:
        return {
            "team_name": self.name,
            "agent_count": len(self.agents),
            "agents": [
                {
                    "name": a.name,
                    "role": a.role.value,
                    "capabilities": a.capabilities,
                    "memory_items": len(a.memory)
                }
                for a in self.agents.values()
            ],
            "messages_sent": len(self.message_bus.messages),
            "tasks_completed": len(self.task_history)
        }


# Factory for common team configurations
class AgentTeamFactory:
    
    @staticmethod
    def create_coding_team() -> AgentTeam:
        """Create a team optimized for coding tasks"""
        team = AgentTeam("Coding Team")
        
        team.create_agent("Architect", AgentRole.ORCHESTRATOR, ["plan", "coordinate", "delegate"])
        team.create_agent("Planner", AgentRole.PLANNER, ["break_down", "estimate", "sequence"])
        team.create_agent("Coder", AgentRole.EXECUTOR, ["write_code", "refactor", "test"])
        team.create_agent("Reviewer", AgentRole.CRITIC, ["review", "critique", "improve"])
        team.create_agent("Researcher", AgentRole.RESEARCHER, ["search", "lookup", "discover"])
        
        return team
    
    @staticmethod
    def create_analysis_team() -> AgentTeam:
        """Create a team optimized for analysis tasks"""
        team = AgentTeam("Analysis Team")
        
        team.create_agent("Coordinator", AgentRole.ORCHESTRATOR, ["coordinate", "synthesize"])
        team.create_agent("Analyzer", AgentRole.ANALYZER, ["analyze", "examine", "evaluate"])
        team.create_agent("Critic", AgentRole.CRITIC, ["judge", "assess", "validate"])
        team.create_agent("Researcher", AgentRole.RESEARCHER, ["gather", "collect", "discover"])
        
        return team
    
    @staticmethod
    def create_self_improvement_team() -> AgentTeam:
        """Create team focused on self-improvement"""
        team = AgentTeam("Self-Improvement Team")
        
        team.create_agent("Observer", AgentRole.ANALYZER, ["observe", "analyze", "detect"])
        team.create_agent("Reflector", AgentRole.CRITIC, ["reflect", "evaluate", "assess"])
        team.create_agent("Improver", AgentRole.EXECUTOR, ["modify", "improve", "enhance"])
        team.create_agent("Verifier", AgentRole.CRITIC, ["verify", "validate", "test"])
        
        return team


# Singleton instances
_coding_team = None
_analysis_team = None
_self_improvement_team = None


def get_coding_team() -> AgentTeam:
    global _coding_team
    if _coding_team is None:
        _coding_team = AgentTeamFactory.create_coding_team()
    return _coding_team


def get_analysis_team() -> AgentTeam:
    global _analysis_team
    if _analysis_team is None:
        _analysis_team = AgentTeamFactory.create_analysis_team()
    return _analysis_team


def get_self_improvement_team() -> AgentTeam:
    global _self_improvement_team
    if _self_improvement_team is None:
        _self_improvement_team = AgentTeamFactory.create_self_improvement_team()
    return _self_improvement_team

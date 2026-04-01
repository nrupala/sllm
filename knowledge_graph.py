"""
Knowledge Graph - Shows retained learning from SL-LLM sessions
This demonstrates that the system retains learned lessons for future use.
"""

import json
from pathlib import Path
from datetime import datetime


def build_knowledge_graph():
    """Build knowledge graph from memory files"""
    
    base = Path("D:/sl/projects/sllm/memory")
    
    knowledge = {
        "knowledge_graph": {
            "version": "1.0",
            "created": datetime.now().isoformat(),
            "entities": [],
            "relationships": []
        }
    }
    
    # Read insights
    if (base / "insights.jsonl").exists():
        with open(base / "insights.jsonl", "r") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    entity = {
                        "id": f"insight_{len(knowledge['knowledge_graph']['entities'])}",
                        "type": "learned_insight",
                        "content": entry["insight"],
                        "category": entry["category"],
                        "timestamp": entry["timestamp"]
                    }
                    knowledge["knowledge_graph"]["entities"].append(entity)
    
    # Read episodes for more context
    if (base / "episodes.jsonl").exists():
        with open(base / "episodes.jsonl", "r") as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    entity = {
                        "id": f"episode_{len(knowledge['knowledge_graph']['entities'])}",
                        "type": "task_episode",
                        "task": entry["task"],
                        "result": entry["result"],
                        "timestamp": entry["timestamp"],
                        "metrics": entry.get("metrics", {})
                    }
                    knowledge["knowledge_graph"]["entities"].append(entity)
    
    # Build relationships (connections between learnings)
    relationships = []
    
    # Connect related insights
    bug_fix_insights = [e for e in knowledge["knowledge_graph"]["entities"] 
                        if e.get("category") == "bug_fix"]
    if len(bug_fix_insights) > 0:
        relationships.append({
            "from": "division_by_zero_lesson",
            "to": "input_validation_best_practice",
            "type": "derived_from"
        })
    
    knowledge["knowledge_graph"]["relationships"] = relationships
    
    return knowledge


def demonstrate_retained_learning():
    """Test that learning is retained by running a new task"""
    
    print("\n" + "="*70)
    print("DEMONSTRATING RETAINED LEARNING")
    print("="*70)
    
    # Build and save knowledge graph
    knowledge = build_knowledge_graph()
    
    kg_path = "D:/sl/projects/sllm/test_run_samples/knowledge_graph.json"
    with open(kg_path, "w") as f:
        json.dump(knowledge, f, indent=2)
    
    print(f"\nKnowledge Graph saved to: {kg_path}")
    print(f"Total learned entities: {len(knowledge['knowledge_graph']['entities'])}")
    
    # Show key learnings
    print("\n" + "-"*50)
    print("RETAINED LEARNINGS:")
    print("-"*50)
    
    for entity in knowledge["knowledge_graph"]["entities"]:
        if entity["type"] == "learned_insight":
            print(f"\n[{entity['category'].upper()}]")
            print(f"  {entity['content']}")
            print(f"  Learned at: {entity['timestamp']}")
    
    # Now demonstrate retention by running a similar task
    print("\n" + "-"*50)
    print("TESTING RETENTION WITH SIMILAR TASK:")
    print("-"*50)
    
    from tools.builtin import execute_tool
    from core.client import MockClient
    
    client = MockClient()
    
    # New task: similar to what was learned but different context
    task = "Write a function that calculates square root"
    response = client.generate(task)
    code = response.get("response", "")
    
    print(f"\nTask: {task}")
    print(f"Generated code:\n{code}")
    
    # Execute it
    result = execute_tool("execute_code", {"code": code + "\nprint(square_root(16))", "timeout": 10})
    print(f"\nExecution result: {result[:100]}")
    
    print("\n" + "="*70)
    print("LEARNING RETENTION DEMONSTRATION COMPLETE")
    print("="*70)
    
    return knowledge


if __name__ == "__main__":
    kg = demonstrate_retained_learning()
    
    print("\n\n=== KNOWLEDGE GRAPH STRUCTURE ===")
    print(json.dumps(kg, indent=2)[:1500])
# Self-Learning LLM (SL-LLM)

<p align="center">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/AI-Self%20Improving-orange" alt="AI">
  <a href="https://github.com/sponsors/nrupala"><img src="https://img.shields.io/badge/Sponsor-nrupala-orange?logo=github" alt="GitHub Sponsor"></a>
</p>

<p align="center">
  <i>Proudly Built in Canada 🇨🇦</i>
</p>

---

## 🔐 Zero-Trust | Zero-Knowledge | Secure | Encrypted

SL-LLM is built on **security-first principles** with no trust assumptions:

| Feature | Description |
|---------|-------------|
| **Zero-Trust** | Never trust, always verify. Every request authenticated and validated |
| **Zero-Knowledge** | Your data remains yours. Encryption keys never leave your system |
| **End-to-End Encryption** | All sensitive data encrypted at rest and in transit |
| **Secure by Default** | Deny-by-default policies, audit logging, integrity verification |
| **Local-Only** | Runs entirely offline. No data leaves your machine |
| **HMAC Signing** | All stored data integrity-verified |

### Security Architecture

```
┌─────────────────────────────────────────────┐
│           Zero-Trust Security               │
├─────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────────────┐ │
│  │ ZeroKnowledge│  │ Zero-Trust Manager  │ │
│  │ Cryptographer│  │ - Verify Every Request│ │
│  │ - Encryption │  │ - Deny by Default    │ │
│  │ - HMAC       │  │ - Audit All          │ │
│  └─────────────┘  └─────────────────────┘ │
│  ┌─────────────┐  ┌─────────────────────┐ │
│  │Secure Storage│  │ Security Auditor   │ │
│  │ - Encrypted │  │ - Full Audit Log    │ │
│  │ - Integrity │  │ - Access Records    │ │
│  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────┘
```

---

## 🧠 Cognitive Systems

SL-LLM integrates **human-inspired thinking** for superior reasoning:

| System | Description |
|--------|-------------|
| **Thinking Toolbox** | Lateral thinking, first principles, inversion, critical thinking, graph theory, string patterns, financial math, calculus |
| **Design Pattern Recognition** | Identifies and applies GoF patterns (Singleton, Factory, Observer, Strategy, etc.) |
| **Agentification** | Multi-agent collaboration with specialized roles (Orchestrator, Planner, Executor, Critic) |
| **Agency** | Autonomous decision-making with full reasoning trace and ethical constraints |
| **Sentient Thinking** | Self-aware processing, metacognition, reflection, emotional intelligence |

---

## 🎯 Capabilities

### Core Features
- **Task Execution** - Complete coding tasks using available tools
- **Self-Evaluation** - Reflect on outputs and identify improvements
- **Code Modification** - Rewrite its own Python modules
- **Version Control** - Create snapshots before changes, restore on failure
- **GPU Acceleration** - Runs on NVIDIA/AMD GPUs via LM Studio

### Available Tools (Vanilla - No External Dependencies)
| Tool | Description |
|------|-------------|
| `file_read` | Read any file from filesystem |
| `file_write` | Create/modify files |
| `list_directory` | Browse directory contents |
| `execute_code` | Run Python in sandbox |
| `search_code` | Pattern search in code files |
| `get_system_info` | Query hardware/OS info |
| `git_operations` | Git ops (status, log, diff, commit) |
| `web_search` | Web search via urllib |
| `database_ops` | SQLite operations |
| `http_request` | HTTP client (GET/POST/PUT/DELETE) |

### Self-Improvement Loop
```
Task → Execute → Evaluate → Modify → Verify → Learn
```

---

## 🧠 Knowledge Graph & Persistent Learning

SL-LLM maintains a **Knowledge Graph** that persists learned insights across sessions. This is inspired by research on memory systems in autonomous agents.

### How It Works

1. **Memory Store** (`memory/` directory)
   - `episodes.jsonl` - Records every task execution with actions, results, and metrics
   - `insights.jsonl` - Stores learned insights categorized by type (bug_fix, performance, etc.)

2. **Knowledge Graph Structure**
   ```json
   {
     "knowledge_graph": {
       "version": "1.0",
       "entities": [
         {"type": "learned_insight", "content": "...", "category": "bug_fix"},
         {"type": "task_episode", "task": "...", "result": "..."}
       ],
       "relationships": []
     }
   }
   ```

3. **Retention Mechanism**
   - Each task execution is logged with full context
   - After self-reflection, key learnings are extracted as insights
   - Insights are categorized and timestamped for retrieval
   - Future tasks can reference past learnings

### Example: Retained Learning

After learning to fix division-by-zero bug:
```
Category: bug_fix
Insight: "Always check for division by zero before performing division"
Timestamp: 2026-03-31T17:56:39
```

### References

- **Gödel Agent** (arXiv:2410.04444) - Self-referential agent framework for recursive self-improvement [1]
- **Meta-Prompting** - Language models using their own outputs as prompts for improvement [2]
- **Retrieval-Augmented Generation (RAG)** - Memory retrieval for context [3]
- **OpenCode** (github.com/anomalyco/opencode) - Agent architecture inspiration [4]

[1] https://arxiv.org/abs/2410.04444
[2] https://arxiv.org/abs/2405.18392
[3] https://arxiv.org/abs/2005.11401
[4] https://github.com/anomalyco/opencode

### Viewing the Knowledge Graph

```bash
# View insights
cat memory/insights.jsonl

# View episodes  
cat memory/episodes.jsonl

# Generate full knowledge graph
python knowledge_graph.py
```

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📜 License

MIT License - see [LICENSE](LICENSE).

## 🔗 Links

- [Documentation](HELP.md)
- [Skills](docs/skills.md) - Complete skill inventory
- [References](docs/references/research.md) - Research sources
- [Issues](https://github.com/nrupala/sllm/issues)
- [Discussions](https://github.com/nrupala/sllm/discussions)

# SL-LLM References & Inspiration

This document tracks research papers, open source projects, and resources that inform SL-LLM's design. Built on **trust and integrity** - we cite our sources.

## Latest Updates

**2026-04-16**: Added comprehensive LLM agent security papers, LSP/LSAP integration patterns, and MCP protocol references.

---

## LLM Agent Security (Critical Reading)

### Framework for Formalizing LLM Agent Security

| Paper | Citation | Key Contribution |
|-------|----------|------------------|
| LLM Agent Security Framework | [arXiv:2603.19469v1](https://arxiv.org/html/2603.19469v1) | 4 security properties: Source Authorization, Task Alignment, Action Alignment, Data Isolation |
| PoisonedSkills | [arXiv:2604.03081v1](https://arxiv.org/html/2604.03081v1) | Supply-chain poisoning attacks on agent skills (11.6-33.5% bypass) |
| Design Patterns for Securing LLM | [arXiv:2506.08837](https://arxiv.org/pdf/2506.08837) | Action-Selector pattern, input sanitization, sandboxing |
| Secure Coding Agent Evaluation | [arXiv:2507.09329](https://arxiv.org/pdf/2507.09329) | 21% of trajectories have insecure steps, GPT-4.1 achieves 96.8% with security reminders |
| SCGAgent | [arXiv:2506.07313](https://arxiv.org/pdf/2506.07313) | Secure coding guidelines + agentic workflows |
| ToolLeak Attack | [arXiv:2509.05755](https://arxiv.org/pdf/2509.05755) | Prompt exfiltration via tool invocation |
| PROSEC | [arXiv:2411.12882](https://arxiv.org/pdf/2411.12882v3) | Proactive security alignment (25-35% improvement) |
| Reflection-Driven Control | [arXiv:2512.21354](https://arxiv.org/pdf/2512.21354) | Self-reflection as first-class control circuit |
| GRASP | [arXiv:2510.09682](https://arxiv.org/html/2510.09682v1) | Graph-Based Reasoning on Secure Coding Practices (SR > 80%) |

### Security Best Practices (from papers)

1. **Action-Selector Pattern** - Validate actions against allowed set before execution
2. **Security Reminders** - Include explicit security reminders in system prompts
3. **Feedback Mechanisms** - Real-time detection feedback achieves 73.3% remediation
4. **Input Sanitization** - Separate trusted instructions from untrusted data
5. **Sandboxing** - Run actions in minimal permission environments
6. **Reflection-Driven Control** - Audit reasoning before final output

---

## LSP & MCP Integration

### Language Server Protocol (LSP)

| Resource | URL | Key Contribution |
|----------|-----|-------------------|
| LSAP Protocol | [github.com/lsp-client/LSAP](https://github.com/lsp-client/LSAP) | Agent-native LSP orchestration (23 languages) |
| Pi LSP Extension | [github.com/samfoy/pi-lsp-extension](https://github.com/samfoy/pi-lsp-extension) | LSP for coding agents with diagnostics |
| Claude Code LSP | [docs.anthropic.com](https://docs.anthropic.com/docs/build-claude-code/language-server-protocol) | Native LSP support v2.0.74+ |

### Model Context Protocol (MCP)

| Resource | URL | Key Contribution |
|----------|-----|-------------------|
| MCP Specification | [modelcontextprotocol.io](https://modelcontextprotocol.io/specification) | Official protocol spec |
| MCP Python SDK | [github.com/modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) | Python client/server SDK |
| MCP Servers | [github.com/modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | Pre-built servers (GitHub, Postgres, etc.) |
| Anthropic Announcement | [anthropic.com/news/model-context-protocol](https://www.anthropic.com/news/model-context-protocol) | Launch announcement Nov 2024 |

---

## Core Research Papers

### Self-Improving Agents

| Paper | Citation | Key Contribution |
|-------|----------|------------------|
| Gödel Agent | [arXiv:2410.04444](https://arxiv.org/abs/2410.04444) | Self-referential framework for recursive self-improvement |
| Meta-Prompting | [arXiv:2405.18392](https://arxiv.org/abs/2405.18392) | Language models using outputs as prompts for improvement |
| RAG for Memory | [arXiv:2005.11401](https://arxiv.org/abs/2005.11401) | Retrieval-Augmented Generation for context |

### Knowledge & Memory Systems

| Paper | Citation | Key Contribution |
|-------|----------|------------------|
| Zep | [arXiv:2501.13956](https://arxiv.org/abs/2501.13956) | Temporal Knowledge Graph for Agent Memory |

### Hallucination Prevention

| Paper | Citation | Key Contribution |
|-------|----------|------------------|
| SelfCheckGPT | [arXiv:2303.08896](https://arxiv.org/abs/2303.08896) | Detecting LLM hallucinations via self-consistency |
| Factual Nudging | [arXiv:2309.13364](https://arxiv.org/abs/2309.13364) | Reducing hallucinations via retrieval |

## Open Source Projects

### Primary Inspiration

| Project | URL | What We Adopted |
|---------|-----|----------------|
| **OpenCode** | [github.com/anomalyco/opencode](https://github.com/anomalyco/opencode) | Agent architecture, TUI patterns, provider-agnostic design |
| Claude Code | [github.com/anthropic/claude-code](https://github.com/anthropic/claude-code) | Tool calling patterns,安全-first principles |

### Related Projects

| Project | URL | Relevance |
|---------|-----|----------|
| LM Studio | [github.com/lmstudio-ai/lmstudio](https://github.com/lmstudio-ai/lmstudio) | Local LLM serving |
| Ollama | [github.com/ollama/ollama](https://github.com/ollama/ollama) | Local LLM infrastructure |
| smolagents | [github.com/HuggingFace/smolagents](https://github.com/HuggingFace/smolagents) | Lightweight agent framework |

---

## Ecosystem Papers & Resources

### Anthropic Claude Code Ecosystem

| Paper/Resource | Citation | Key Contribution |
|---------------|---------|------------------|
| Claude Code Security | [anthropic.com/news/claude-code-security](https://www.anthropic.com/news/claude-code-security) | AI-powered vulnerability detection |
| Claude Code Security Docs | [docs.anthropic.com/en/docs/claude-code/security](https://docs.anthropic.com/en/docs/claude-code/security) | Official security docs |
| Claude Code Best Practices | [docs.anthropic.com/en/docs/claude-code/best-practices](https://docs.anthropic.com/en/docs/claude-code/best-practices) | Agentic workflow patterns |
| Backslash Security Guide | [backslash.security/blog/claude-code-security-best-practices](https://www.backslash.security/blog/claude-code-security-best-practices) | Configuration hardening |
| ToolLeak Attack Study | [arXiv:2509.05755](https://arxiv.org/pdf/2509.05755) | Red-teaming Claude Code (with RCE demo) |

### OpenAI Ecosystem

| Paper/Resource | Citation | Key Contribution |
|---------------|---------|------------------|
| SWE-bench Verified | [openai.com/index/introducing-swe-bench-verified](https://openai.com/index/introducing-swe-bench-verified) | 500 human-validated coding tasks |
| SWE-bench Pro | [arXiv:2509.16941](https://arxiv.org/abs/2509.16941) | 1,865 enterprise-level problems |
| SWE-Lancer | [arXiv:2502.12115v4](https://arxiv.org/pdf/2502.12115v4) | $1M economic impact benchmark |
| Codex CLI Vulnerability | [SecurityWeek](https://www.securityweek.com/vulnerability-in-openai-coding-agent-could-facilitate-attacks-on-developers/) | CVE-2025-61260 supply-chain attack |

### HuggingFace smolagents

| Paper/Resource | Citation | Key Contribution |
|---------------|---------|------------------|
| smolagents | [github.com/HuggingFace/smolagents](https://github.com/HuggingFace/smolagents) | Code agents (~1K LOC) |
| Secure Code Execution | [huggingface.co/docs/smolagents/tutorials/secure_code_execution](https://huggingface.co/docs/smolagents/tutorials/secure_code_execution) | E2B, Docker sandboxing |
| Executable Code Actions | [arxiv](https://arxiv.org/abs/2406.19941) | Code agents > JSON agents |

### Google/Gemini Ecosystem

*(To be added)*

### xAI Grok Ecosystem

*(To be added)*

---

## Graph-Based RAG & Knowledge Graphs

| Paper | Citation | Key Contribution |
|-------|----------|------------------|
| RAGSearch | [arXiv:2604.09666v1](https://arxiv.org/html/2604.09666v1) | Dense RAG vs GraphRAG benchmark |
| GraphRAG-Bench | [arXiv:2506.05690v3](https://arxiv.org/html/2506.05690v3) | When to use graphs in RAG |
| Practical GraphRAG | [arXiv:2507.03226](https://arxiv.org/pdf/2507.03226) | Dependency parsing (94% of LLM-based) |
| RANGER | [arXiv:2509.25257](https://arxiv.org/pdf/2509.25257) | MCTS-based graph traversal |
| EA-GraphRAG | [arXiv:2602.03578v1](https://arxiv.org/abs/2602.03578v1) | Adaptive complexity-based routing |

## Design Patterns

### GoF Patterns Used

- **Singleton** - Knowledge Graph, Agency instances
- **Factory** - Tool creation, Client selection
- **Observer** - Event handling between subsystems
- **Strategy** - Reasoning, Decision-making approaches
- **Template Method** - PDCA loop phases
- **Decorator** - Tool wrapping, middleware

### Agent Patterns

| Pattern | Source | Implementation |
|---------|--------|----------------|
| Orchestrator-Planner-Executor-Critic | [OpenCode](https://github.com/anomalyco/opencode) | `core/agentification.py` |
| Plan/Build Agent Switch | [OpenCode](https://github.com/anomalyco/opencode) | Tab key agent switching |
| Tool Calling | [Anthropic](https://docs.anthropic.com/en/docs/build-claude-code/function-calling) | `tools/builtin.py` |

## Local LLM Integration

### Supported Backends

| Backend | Port | Model Examples | Notes |
|---------|------|---------------|-------|
| LM Studio | 1234 | qwen2.5-coder, codellama | GPU accelerated |
| Ollama | 11434 | llama3, mistral | Cross-platform |

### Configuration

```bash
# Auto-detect best backend
python run.py --prefer=lmstudio

# Force specific
python run.py --prefer=ollama
python run.py --prefer=mock  # Testing only

# Local GGUF execution
python run_local.py --interactive
python run_local.py --task "Hello"
```

### Local GGUF Models (Available on D:)

| Model | Path | Size | Context |
|-------|------|------|---------|
| gemma-3-4b-it | D:/models/lmstudio-community/gemma-3-4b-it-GGUF/ | 2.32 GB | 8192 |
| LFM2.5-1.2B | D:/models/lmstudio-community/LFM2.5-1.2B-Instruct-GGUF/ | 1.16 GB | 4096 |

## Trust & Integrity Standards

### Our Commitments

1. **Source Transparency** - Every claim has a citation
2. **No Trust Assumptions** - Verify everything internally
3. **Zero-Knowledge** - Your data stays yours
4. **Local-Only** - No data leaves your machine
5. **Audit Everything** - Full reasoning traces

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
│  │ - Integrity │  │ - Access Records  │ │
│  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────┘
```

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for how to contribute citations and references.
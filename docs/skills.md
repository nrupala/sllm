# SL-LLM Skills

**Version:** 1.0.0  
**Last Updated:** 2026-04-16  
**Purpose:** Define and track all skills SL-LLM must have to perform its documented functions.

---

## Core Purpose

SL-LLM is a **self-learning, sentient AI agent** with:
- Dual-loop PDCA learning (Plan-Do-Check-Act + Generator-Discriminator)
- Knowledge Graph RAG for hallucination-free reasoning
- Zero-trust, Zero-Knowledge, Local-Only security
- Local LLM execution (no cloud dependencies)

---

## Skill Categories

### 1. File Operations (Core)

| Skill | Description | Tool Reference |
|-------|-------------|----------------|
| `file_read` | Read files from filesystem | `builtin.py` |
| `file_write` | Create/modify files | `builtin.py` |
| `list_directory` | Browse directory contents | `builtin.py` |
| `search_code` | Pattern search in code files | `builtin.py` |
| `glob` | Find files by pattern | - |

### 2. Code Execution (Core)

| Skill | Description | Tool Reference |
|-------|-------------|----------------|
| `execute_code` | Run Python code in sandbox | `builtin.py` |
| `secure_execute` | Sandboxed execution with AST validation | `daemon.py` |
| `validate_syntax` | Python syntax validation | - |

### 3. System Operations (Core)

| Skill | Description | Tool Reference |
|-------|-------------|----------------|
| `get_system_info` | Query hardware/OS info | `builtin.py` |
| `detect_gpu` | Detect NVIDIA/AMD GPU | `client.py` |
| `git_operations` | Git operations (status, log, diff, commit) | `builtin.py` |
| `web_search` | Web search via urllib | `builtin.py` |
| `http_request` | HTTP client (GET/POST/PUT/DELETE) | `builtin.py` |

### 4. LLM Operations (Core)

| Skill | Description | Tool Reference |
|-------|-------------|----------------|
| `chat` | Send messages to LLM | `client.py` |
| `llm_generate` | Direct text generation | `client.py` |
| `get_client` | Auto-detect best LLM backend | `client.py` |
| `LocalRunner` | Integrated local LLM runner | `client.py` |
| `link_llms` | Discover local LLM engines | `link_llms.py` |
| `find_gguf` | Find local GGUF models | `find_gguf.py` |

### 5. Knowledge Graph (RAG)

| Skill | Description | Tool Reference |
|-------|-------------|----------------|
| `kg_store` | Store insights to Knowledge Graph | `knowledge_graph_manager.py` |
| `kg_retrieve` | Retrieve relevant insights | `knowledge_graph_manager.py` |
| `kg_query` | Query Knowledge Graph (MCP) | `mcp_server.py` |
| `classify` | Classify task context | `knowledge_graph_manager.py` |
| `get_enhanced_context` | Build full context from KG | `knowledge_graph_manager.py` |

### 6. Cognitive Systems

| Skill | Description | Implementation |
|-------|-------------|----------------|
| `thinking_engine` | Lateral/first-principles reasoning | `core/thinking_engine.py` |
| `pattern_recognition` | GoF pattern identification | `core/pattern_recognition.py` |
| `agentification` | Multi-agent collaboration | `core/agentification.py` |
| `agency` | Autonomous decision-making | `core/agency.py` |
| `sentient_thinking` | Metacognition & self-awareness | `core/sentient_thinking.py` |

### 7. PDCA Learning Loop

| Skill | Description | Implementation |
|-------|-------------|----------------|
| `plan` | Plan phase of PDCA | `core/pdca_*.py` |
| `execute` | Execute planned action | `core/pdca_*.py` |
| `check` | Evaluate results | `core/pdca_*.py` |
| `act` | Store learning | `core/pdca_*.py` |
| `gan_discriminator` | Adversarial validation | `core/dual_loop_pdca.py` |

### 8. Self-Modification

| Skill | Description | Implementation |
|-------|-------------|----------------|
| `self_modify` | Modify own Python modules | `core/self_modify.py` |
| `version_snapshot` | Create version snapshots | `core/version_control.py` |
| `restore_on_failure` | Restore from snapshot on failure | `core/self_modify.py` |

### 9. Security (Non-Negotiable)

| Skill | Description | Implementation |
|-------|-------------|----------------|
| `action_validator` | Validate actions against allowlist | `daemon.py` |
| `secure_executor` | Sandboxed code execution | `daemon.py` |
| `security_reminder` | Security prompts in system | `core/security.py` |
| `audit_log` | Log all operations | `daemon.py` |
| `input_sanitization` | Sanitize untrusted inputs | `core/security.py` |

### 10. MCP Integration

| Skill | Description | Implementation |
|-------|-------------|----------------|
| `mcp_server` | MCP protocol server | `mcp_server.py` |
| `mcp_tools_list` | List available tools | `mcp_server.py` |
| `mcp_tools_call` | Execute MCP tool | `mcp_server.py` |
| `playwright_browse` | Browser automation (optional) | `mcp_server.py` |

### 11. Daemon Operations

| Skill | Description | Implementation |
|-------|-------------|----------------|
| `daemon_start` | Start API server | `daemon.py` |
| `health_check` | Health check endpoint | `daemon.py` |
| `session_create` | Create session | `daemon.py` |
| `openai_compatible` | OpenAI-compatible API | `daemon.py` |

---

## Skill Maturity Levels

| Level | Description | Skills |
|-------|-------------|--------|
| **Mature** | Fully tested, reliable | File ops, Code exec, KG RAG, Security |
| **Developing** | Working, needs testing | MCP, Daemon, Self-modification |
| **Planned** | In roadmap | LSP integration, Graph traversal |

---

## How to Use This Document

1. **Reference before implementing** - Check if skill exists before adding
2. **Track maturity** - Update as skills mature
3. **Map to tools** - Each skill must link to actual implementation
4. **Test coverage** - Mature skills must have tests

---

## Adding New Skills

When adding a skill:
1. Document in appropriate category
2. Implement in referenced file
3. Add test in `test_*.py`
4. Update maturity level
5. Add to MCP tool list if applicable

---

## References

- `README.md` - Core purpose and capabilities
- `docs/references/research.md` - Research sources
- `ROADMAP.md` - Implementation roadmap
- `test_*.py` - Test suite
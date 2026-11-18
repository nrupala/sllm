# Codetopo Profile — SL-LLM (Self-Learning LLM) (nrupala/sllm)

**What this is.** The agent-facing map of this repository, generated with
Codetopo 0.9.1 (local engine, `~/.cargo/bin/codetopo`) so an arriving agent
can see the machine — topology, trust boundaries, money surface — before it
submits or changes anything. Read this first; the graph snapshot beside it
(`snapshot.json`, `stats.json`) is the measured evidence.

- **Repo:** nrupala/sllm
- **Commit profiled:** `57f91f7be8b83fe023805b3d85aeaef1fcae4a91` (main)
- **Engine:** codetopo 0.9.1 · index run 2026-11-18
- **Graph:** 87 files walked · 0 failed · 2565 nodes · 8192 edges · audit chain valid (3 entries, head `a991b97c…c10fb`)
- **Nodes by kind:** class 164 · doc 27 · external 1297 · file 87 · function 171 · method 624 · module 87 · package 1 · variable 107
- **Edges by kind:** calls 3218 · contains 1267 · defines 376 · imports 311 · inherits 5 · reads 2738 · writes 277

## Coverage honesty

Codetopo extracts Rust, TypeScript/JavaScript and Python, plus Markdown
as Doc nodes. This repo is Python-only code: the graph walks 87 files
(`core/`, top-level services, `eval/`, `tools/`, tests) at full
symbol level. The 29 Markdown files are indexed as Doc nodes only.
**Not covered:** the JSON/JSONL data under `memory/`, `prompts/` and
`local_gguf_models.json` (model registry data), and the `.bin` model
artifacts, are data — not parsed into the graph; read them directly
if you need model/memory state.

## Topology

A local-only, self-learning LLM system (README): GGUF models run
on-device (LM Studio / Ollama / direct), wrapped in cognitive,
memory and self-improvement loops, with a zero-trust security layer.

- Entry points (README): `run_local.py` (CLI runner), `run.py` (full
  cognitive integration), `gui_prod.py` (production GUI on
  localhost:8080), `gui_flask.py` / `gui.py`, `daemon.py` (API
  server), `bootstrap.py` (Ollama + model setup), `check_setup.py`.
- `core/` — the engine room: `agent.py` / `sl_llm_agent.py` /
  `agency.py` (agents), `thinking_engine.py` + `sentient_thinking.py`,
  `dual_loop_pdca.py` + `pdca_reward.py` (self-improvement loops),
  `persistent_memory.py`, `pattern_recognition.py`,
  `model_manager.py` + `model_registry.py`, `client.py`,
  `self_modify.py` (guarded self-modification), `security.py`,
  `zero_check.py`, `rock_solid.py`, `phase2_system.py` /
  `phase3_system.py`, `skills_importer.py`.
- Services: `mcp_server.py` + `mcp_gateway.py` (MCP surface),
  `knowledge_graph.py` + `knowledge_graph_manager.py`,
  `integration.py`, `http_client.py`, `rate_limit.py`, `cache.py`,
  `config.py`, `log_setup.py`, `find_gguf.py`, `link_llms.py`.
- `eval/suite.py` + the root test suites (`test_suite.py`,
  `test_phase123.py`, `test_rag_retrieval.py`,
  `test_sentient_intelligence.py`, `tests/`) carry the checks.

## Trust boundaries

- **Local-only posture (README):** runs entirely offline; no data
  leaves the machine in the default design. The security model is
  implemented in `core/security.py`: `ZeroTrustManager` (L47 —
  verify every request, deny by default, audit all, trust levels and
  principal blocking), `ZeroKnowledgeCryptographer` (L140 —
  key derivation, encryption, HMAC signing/verification),
  `SecureStorage` (L202 — encrypted-at-rest storage under
  `memory/.secure`).
- **Self-modification is the sharp edge:** `core/self_modify.py` can
  change the system's own code — treat any change there, and in
  `core/security.py`, as trust-boundary changes requiring the test
  suites to pass.
- No env-var credential reads were found in the profiled sources
  (no `os.environ`/`getenv` hits in `config.py`); model access is to
  local runtimes (Ollama / LM Studio / GGUF files), not hosted APIs.

## Money surface

No money surface found. Greps for `stripe|paddle|checkout|billing`
over all Python sources return zero hits and there are no payment
imports in the graph's 311 import edges. Inference is local (GGUF /
Ollama / LM Studio), so there is no per-call API spend path in this
repo either. The README carries a GitHub Sponsors badge for the
author's profile — a link, not a payment integration.

## How an agent should approach

1. Read `README.md` and `HELP.md`, then this profile, then the
   snapshot.
2. Use codetopo blast-radius queries before touching `core/agent.py`,
   `core/security.py` or `core/self_modify.py` — call edges (3,218)
   concentrate through the agent and thinking engine.
3. Run the root test suites after changes; regenerate this profile
   (below) at every material change. Keep the local-only posture:
   do not add hosted-API calls without an explicit decision.

## Regeneration

`docs/codetopo-profile/refresh.sh` (in this pack) re-downloads the repo
at a named ref, re-runs the index, and rewrites `snapshot.json`,
`stats.json` and the header block inputs of this profile. Regenerate at
every release / material change.

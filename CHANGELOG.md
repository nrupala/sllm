# Changelog

All notable changes to SL-LLM will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Docs honesty pass (2026-11-18): README security section now states only what the code does (local keys, encryption at rest, localhost daemon); removed "Zero-Knowledge", "in transit" and "Sentient Thinking" claims; reflective reasoning described as a technique.
- Ollama is documented as an optional backend; GGUF via LM Studio / llama.cpp listed first.
- Minimum Python raised to 3.10 (3.8 is end-of-life): README, docs/getting-started.md and check_setup.py updated together.

### Added
- Portfolio certification: PR-flow discipline documented in CONTRIBUTING.md
  (draft PR -> tests green -> owner merges; no direct pushes to main; each PR
  adds a CHANGELOG entry under Unreleased and bumps SemVer).
- Portfolio certification: ATTRIBUTION.md (owned by Nrupal Akolkar).
- Portfolio certification: MIT license headers on all Python source files.

All notable changes to SL-LLM will be documented in this file.

## [1.0.0] - 2025-03-31

### Added
- Initial release
- Self-learning agent with recursive improvement capability
- Multi-backend support (LM Studio, Ollama, Mock)
- Tool execution (file read/write, code execution, search)
- Self-modification with checkpoint/rollback
- GPU detection and acceleration
- Web GUI control panel
- Comprehensive documentation (README, HELP, CONTRIBUTING)

### Features
- `run.py` - Main CLI entry point
- `gui.py` - Web-based control panel
- `core/client.py` - Auto-detecting LLM client
- `core/self_modify.py` - Self-modification engine
- `tools/builtin.py` - 6 built-in tools
- `eval/suite.py` - Benchmark suite

### Architecture
- Gödel Agent-inspired self-referential framework
- Tool calling with function execution
- Reflection-based self-evaluation
- Safe sandbox code execution

---

## Future Plans
- [ ] Add more benchmarks
- [ ] Improve self-modification safety
- [ ] Add more tool integrations
- [ ] Support for more LLM backends
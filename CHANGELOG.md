# Changelog

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
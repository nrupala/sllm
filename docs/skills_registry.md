# SL-LLM Skills & Model Registry

## Available Models (23 local, 111 cloud providers)

### Local Models (No API key required)
- LM Studio: qwen2.5-coder-14b, gemma-3-4b-it, etc.
- Ollama: qwen3.5:9b, llama3.1:8b, codellama:34b-code
- GGUF files: gemma-3-4b-it-Q4_K_M.gguf, LFM2.5-1.2B-Instruct-Q8_0.gguf

### Cloud Providers (Require API key)
Source: `C:\Users\nrupa\.cache\opencode\models.json`

| Provider | API Variable | Models |
|----------|--------------|--------|
| OpenAI | OPENAI_API_KEY | GPT-5, GPT-4o, o1, o3 |
| Anthropic | ANTHROPIC_API_KEY | Claude Opus 4, Sonnet 4 |
| Google | GEMINI_API_KEY | Gemini 2.5 Pro/Flash |
| DeepSeek | DEEPSEEK_API_KEY | DeepSeek R1, V3 |
| Qwen (Alibaba) | DASHSCOPE_API_KEY | Qwen3 series |
| OpenRouter | OPENROUTER_API_KEY | 1000+ models |
| HuggingFace | HF_TOKEN | Open models |
| Fireworks | FIREWORKS_API_KEY | GLM, DeepSeek |

## Imported Skills

### From Claude/MstyStudio (`C:\Users\nrupa\.claude\skills`)
- **Architecture:** agent-designer
- **Development:** code-reviewer, figma-use, fullstackdevelopment, skill-creator
- **Security:** security-best-practices, secrets-vault-manager
- **Advisory:** c-level-advisor, ceo-advisor, cto-advisor
- **Strategy:** change-management, copywriting, launch-strategy, pricing-strategy
- **Growth:** x-twitter-growth, finance, free-tool-strategy
- **Research:** autoresearch-agent, wiki-researcher

### From Cursor Skills (`C:\Users\nrupa\.cursor\skills-cursor`)
- babysit (PR management), create-hook, create-rule, create-skill, create-subagent
- migrate-to-skills, shell, statusline, update-cli-config, update-cursor-settings

### From `.llmskillvault` (`C:\Users\nrupa\.llmskillvault`)
- Core Coding, Architecture, Debugging, Refactoring
- Testing, Documentation, Agentic Behavior, Safety

## MCP Gateway Tools (13 tools)
- **SL-LLM:** slll_generate, slll_chat, slll_code
- **Design:** design_agent_architecture, design_tool_schema
- **Analysis:** analyze_pr, check_code_quality
- **Development:** create_feature, security_review
- **Research:** deep_research, plan_launch
- **Cursor:** babysit_pr, create_skill

## SL-LLM Native Skills

### Zero-Check Safety (`core/zero_check.py`)
- Division by zero prevention, Array bounds validation
- File path sanitization, Type checking

### Context Awareness
- Session-based conversation history
- Context window management
- Truncation handling with follow-up prompts

### Agentic Autonomy
- Plan before execution, Ask clarifying questions only when needed
- Maintain state across interactions, Deterministic output

### Self-Learning & Adaptation
- Track successful/failed strategies
- Update knowledge from feedback
- Pattern recognition in user behavior
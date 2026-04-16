# SL-LLM Skills Reference

## Imported Skills from External Sources

### Claude/MstyStudio Skills (`C:\Users\nrupa\.claude\skills` → `C:\Users\nrupa\AppData\Roaming\MstyStudio\skills`)

| Skill | Description | Category |
|-------|-------------|----------|
| agent-designer | Multi-agent system architecture design | Development |
| code-reviewer | PR analysis, code quality checking | Development |
| figma-use | Figma design tool integration | Design |
| fullstackdevelopment | TDD, branch management, PR lifecycle | Development |
| skill-creator | Create new skills | Development |
| security-best-practices | Language-specific security reviews | Security |
| secrets-vault-manager | Secret management infrastructure | Security |
| c-level-advisor | CEO, CTO, COO guidance | Advisory |
| ceo-advisor | Executive leadership strategy | Advisory |
| cto-advisor | Technical leadership & architecture | Advisory |
| change-management | Organizational change framework | Strategy |
| copywriting | Marketing copy writing | Strategy |
| launch-strategy | Product launch planning | Strategy |
| pricing-strategy | SaaS pricing design | Strategy |
| x-twitter-growth | X/Twitter growth engine | Growth |
| finance | Financial analysis (DCF, ratio analysis) | Growth |
| free-tool-strategy | Marketing tool building | Growth |
| autoresearch-agent | Autonomous experiment optimization | Research |
| wiki-researcher | In-depth code research | Research |

### Cursor Skills (`C:\Users\nrupa\.cursor\skills-cursor`)

| Skill | Description |
|-------|-------------|
| babysit | Keep PR merge-ready |
| create-hook | Create git hooks |
| create-rule | Create linting/rules |
| create-skill | Create new skill |
| create-subagent | Create subagent |
| migrate-to-skills | Migration tools |
| shell | Shell command integration |
| statusline | Status line tools |
| update-cli-config | Update CLI config |
| update-cursor-settings | Update Cursor settings |

### Skills from .llmskillvault (`C:\Users\nrupa\.llmskillvault`)

**From `skills.txt`:**
- Core Coding - Write correct, minimal, idiomatic code
- Architecture - Modules, boundaries, tradeoffs
- Debugging - Diagnose with discipline
- Refactoring - Improve structure without behavior change
- Testing - Meaningful, deterministic tests
- Documentation - Communicate intent concisely
- Agentic Behavior - Act autonomously with discipline
- Safety & Grounding - Prevent hallucination, express uncertainty

**From `skills_agentic.txt`:**
- Core Coding Competence
- Architecture & Systems Thinking
- Advanced Debugging & Troubleshooting
- Refactoring & Code Quality
- Testing Mastery
- Documentation & Explanation
- Agentic Autonomy & Task Execution
- Safety, Determinism & Constraint Adherence

### Skills from .agents/skills (`C:\Users\nrupa\.agents\skills`)

| Skill | Description |
|-------|-------------|
| agent-designer | Multi-agent systems architecture |
| appinsights-instrumentation | Azure App Insights telemetry |
| autoresearch-agent | Karpathy-style optimization loop |
| azure-ai | Azure AI Search, Speech, OpenAI |
| azure-aigateway | Azure API Management as AI Gateway |
| azure-cloud-migrate | Cross-cloud migration to Azure |
| azure-compliance | Azure security audits (azqr) |
| azure-compute | Azure VM/VMSS recommendations |
| azure-cost | Azure cost management |
| azure-deploy | Azure deployment (azd, terraform) |
| azure-diagnostics | Azure production debugging |
| azure-enterprise-infra-planner | Enterprise Azure infrastructure |
| azure-hosted-copilot-sdk | GitHub Copilot SDK on Azure |
| azure-kubernetes | AKS cluster planning |
| azure-kusto | KQL/ADX queries |
| azure-messaging | Event Hubs/Service Bus troubleshooting |
| azure-prepare | Azure app preparation |
| azure-quotas | Azure quota management |
| azure-rbac | Azure RBAC role assignment |
| azure-resource-lookup | Azure resource discovery |
| azure-resource-visualizer | Azure architecture diagrams |
| azure-storage | Blob, File, Queue, Table storage |
| azure-upgrade | Azure SKU upgrades |
| azure-validate | Azure pre-deployment validation |
| c-level-advisor | 10 C-level advisory agents |
| ceo-advisor | Executive leadership guidance |
| change-management | ADKAR change model |
| code-reviewer | PR analysis, quality checking |
| copywriting | Marketing copy writing |
| cto-advisor | Technical leadership |
| entra-app-registration | Microsoft Entra ID setup |
| figma-use | Figma design tool |
| finance | Financial analysis |
| free-tool-strategy | Engineering as marketing |
| fullstackdevelopment | TDD & PR lifecycle |
| launch-strategy | Product launch |
| microsoft-foundry | Azure Foundry agents |
| pricing-strategy | SaaS pricing |
| secrets-vault-manager | Secret management |
| security-best-practices | Language-specific security |
| skill-creator | Create/modify skills |
| wiki-researcher | Deep codebase research |
| x-twitter-growth | X/Twitter growth |

## SL-LLM Native Skills

### Zero-Check Safety (`core/zero_check.py`)
- Division by zero prevention
- Array bounds validation  
- File path sanitization
- Type checking

### Context Awareness
- Session-based conversation history
- Context window management (20 messages)
- Truncation handling with follow-up prompts

### Agentic Autonomy
- Plan before execution
- Ask clarifying questions only when needed
- Maintain state across interactions

### Self-Learning
- Track successful/failed strategies
- Update knowledge from feedback
- Pattern recognition in user behavior

## MCP Gateway Tools

| Tool | Purpose |
|------|---------|
| slll_generate | Generate text |
| slll_chat | Chat with history |
| slll_code | Code generation |
| design_agent_architecture | Agent design |
| design_tool_schema | Tool schema design |
| analyze_pr | PR analysis |
| check_code_quality | Code quality |
| create_feature | Feature creation |
| security_review | Security review |
| deep_research | Deep research |
| plan_launch | Launch planning |
| babysit_pr | PR babysitting |
| create_skill | Skill creation |
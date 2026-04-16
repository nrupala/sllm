import os
import re
import json
import logging
from pathlib import Path
from typing import Any, Optional, Dict
import yaml

logger = logging.getLogger(__name__)


class PromptTemplateEngine:
    def __init__(self, templates_dir: str = None):
        if templates_dir is None:
            base = Path(__file__).parent
            templates_dir = base / "prompts" / "templates"
        self.templates_dir = Path(templates_dir)
        self.templates = {}
        self._load_templates()

    def _load_templates(self):
        if not self.templates_dir.exists():
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return

        for yaml_file in self.templates_dir.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if isinstance(data, dict) and 'name' in data:
                        self.templates[data['name']] = data
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and 'name' in item:
                                self.templates[item['name']] = item
            except Exception as e:
                logger.error(f"Failed to load {yaml_file}: {e}")

        logger.info(f"Loaded {len(self.templates)} templates")

    def render(self, template_name: str, variables: Dict[str, Any]) -> str:
        if template_name not in self.templates:
            logger.warning(f"Template '{template_name}' not found")
            return f"Template {template_name} not found"

        template = self.templates[template_name]
        template_str = template.get('template', '')

        rendered = template_str
        for key, value in variables.items():
            placeholder = f"{{{{{key}}}}}"
            rendered = rendered.replace(placeholder, str(value))

        rendered = self._handle_conditionals(rendered, variables)
        rendered = self._clean_empty_lines(rendered)

        return rendered

    def _handle_conditionals(self, template: str, variables: Dict[str, Any]) -> str:
        block_pattern = re.compile(r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}', re.DOTALL)
        
        while True:
            match = block_pattern.search(template)
            if not match:
                break
            
            var_name = match.group(1)
            content = match.group(2)
            
            if variables.get(var_name):
                template = template.replace(match.group(0), content)
            else:
                template = template.replace(match.group(0), '')
        
        return template

    def _clean_empty_lines(self, text: str) -> str:
        lines = text.split('\n')
        cleaned = [line for line in lines if line.strip()]
        return '\n'.join(cleaned)

    def get_template(self, name: str) -> Optional[Dict]:
        return self.templates.get(name)

    def list_templates(self) -> list:
        return list(self.templates.keys())


class PromptManager:
    def __init__(self, prompts_dir: str = None):
        if prompts_dir is None:
            base = Path(__file__).parent
            prompts_dir = base / "prompts"
        self.prompts_dir = Path(prompts_dir)
        self.system_prompt = self._load_system_prompt()
        self.template_engine = PromptTemplateEngine()

    def _load_system_prompt(self) -> str:
        system_file = self.prompts_dir / "system_prompt.yaml"
        if system_file.exists():
            try:
                with open(system_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    return data.get('instructions', '')
            except Exception as e:
                logger.error(f"Failed to load system prompt: {e}")
        
        return self._default_system_prompt()

    def _default_system_prompt(self) -> str:
        return """You are SL-LLM (Self-Learning LLM), an autonomous AI agent.

Core principles:
- Safety first: Always validate inputs, check for division by zero
- Transparency: Inform user if response is truncated
- Context awareness: Maintain conversation history
- Self-improvement: Learn from each interaction

When performing mathematical operations:
- Verify all divisors are non-zero
- Check array bounds before access
- Validate file handles before operations

If your response is truncated, tell the user:
"Response truncated. Ask a follow-up to continue the thought.""""

    def get_system_prompt(self) -> str:
        return self.system_prompt

    def render_task(self, task_type: str, **kwargs) -> str:
        return self.template_engine.render(task_type, kwargs)

    def get_full_prompt(self, user_input: str, conversation_history: str = None, **kwargs) -> str:
        parts = [self.system_prompt]
        
        if conversation_history:
            parts.append(f"\n## Conversation History\n{conversation_history}\n")
        
        parts.append(f"\n## Current Task\n{user_input}")
        
        return "\n".join(parts)


if __name__ == "__main__":
    pm = PromptManager()
    print("System prompt loaded:", len(pm.get_system_prompt()), "chars")
    print("Available templates:", pm.template_engine.list_templates())
    
    rendered = pm.render_task("question_answer", question="What is Python?", context="A programming language", max_length=100)
    print("\nRendered:", rendered[:200])
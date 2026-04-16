"""
SL-LLM Skills Integration
Import all skills from Claude/MstyStudio ecosystem
"""

from pathlib import Path
from typing import Dict, List, Any
import json


SKILLS_SOURCE = Path("C:/Users/nrupa/AppData/Roaming/MstyStudio/skills")


class SkillsImporter:
    """Import and integrate skills from external sources"""
    
    def __init__(self):
        self.skills = {}
        self._load_all_skills()
    
    def _load_all_skills(self):
        """Load all skills from source directory"""
        if not SKILLS_SOURCE.exists():
            return
        
        for skill_dir in SKILLS_SOURCE.iterdir():
            if skill_dir.is_dir():
                skill_name = skill_dir.name
                skill_data = self._parse_skill(skill_dir)
                if skill_data:
                    self.skills[skill_name] = skill_data
    
    def _parse_skill(self, skill_dir: Path) -> Dict:
        """Parse a skill directory"""
        data = {
            "name": skill_dir.name,
            "description": "",
            "files": [],
            "references": []
        }
        
        # Read SKILL.md
        skill_md = skill_dir / "SKILL.md"
        if skill_md.exists():
            data["description"] = skill_md.read_text(encoding="utf-8")[:500]
        
        # List Python files
        for f in skill_dir.glob("*.py"):
            data["files"].append({"name": f.name, "size": f.stat().st_size})
        
        # List references
        ref_dir = skill_dir / "references"
        if ref_dir.exists():
            for f in ref_dir.glob("*.md"):
                data["references"].append(f.name)
        
        return data
    
    def list_skills(self) -> List[str]:
        """List all available skills"""
        return list(self.skills.keys())
    
    def get_skill(self, name: str) -> Dict:
        """Get skill details"""
        return self.skills.get(name, {})
    
    def get_skill_by_category(self, category: str) -> List[Dict]:
        """Get skills by category"""
        return [
            {"name": k, **v} for k, v in self.skills.items() 
            if category.lower() in k.lower()
        ]
    
    def generate_skill_guide(self) -> str:
        """Generate a comprehensive skill guide"""
        lines = ["# SL-LLM Imported Skills Guide\n"]
        
        categories = {
            "advisor": "C-Level Advisors",
            "strategy": "Strategy & Marketing", 
            "development": "Development & Engineering",
            "research": "Research & Analysis",
            "security": "Security & Operations"
        }
        
        for cat_key, cat_name in categories.items():
            skills = self.get_skill_by_category(cat_key)
            if skills:
                lines.append(f"\n## {cat_name}\n")
                for s in skills:
                    lines.append(f"- **{s['name']}**: {s.get('description', '')[:100]}...")
        
        return "\n".join(lines)


# Singleton
_importer = None

def get_skills_importer() -> SkillsImporter:
    global _importer
    if _importer is None:
        _importer = SkillsImporter()
    return _importer


# Skill categories for SL-LLM
SKILL_CATEGORIES = {
    "advisory": [
        "c-level-advisor",
        "ceo-advisor", 
        "cto-advisor",
    ],
    "strategy": [
        "change-management",
        "copywriting",
        "free-tool-strategy",
        "launch-strategy",
        "pricing-strategy",
        "x-twitter-growth"
    ],
    "development": [
        "agent-designer",
        "code-reviewer",
        "fullstackdevelopment",
        "skill-creator"
    ],
    "research": [
        "autoresearch-agent",
        "wiki-researcher"
    ],
    "operations": [
        "figma-use",
        "finance",
        "secrets-vault-manager",
        "security-best-practices"
    ]
}


if __name__ == "__main__":
    importer = get_skills_importer()
    print("=== SL-LLM Skills Importer ===")
    print(f"Total skills imported: {len(importer.list_skills())}")
    print("\nBy category:")
    
    for cat, skills in SKILL_CATEGORIES.items():
        print(f"  {cat}: {len(skills)} skills")
    
    print("\nAll skills:", importer.list_skills())
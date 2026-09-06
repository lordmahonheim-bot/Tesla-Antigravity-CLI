import json

with open('$TESLA_ROOT/MVP-GITHUB/11-Tesla-Arcanis-360-Skill/SKILL.md', 'r') as f:
    content = f.read()

print(json.dumps(content[:200])) # just testing

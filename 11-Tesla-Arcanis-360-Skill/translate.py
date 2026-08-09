import json

with open('/home/lord-mahonheim/bifrost/tesla/MVP-GITHUB/11-Tesla-Arcanis-360-Skill/SKILL.md', 'r') as f:
    content = f.read()

print(json.dumps(content[:200])) # just testing

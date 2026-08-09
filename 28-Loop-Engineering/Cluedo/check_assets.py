import re

path = '/home/lord-mahonheim/bifrost/tesla/OUTPUTS/Synergy/N1/arcanis_base64_assets.md'
with open(path, 'r') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith('## Asset:'):
        print(line.strip())
        # Print a few lines before and after
        start = max(0, i-2)
        end = min(len(lines), i+3)
        print("".join(lines[start:end]))
        print("---")

import re
import os

path = '/home/lord-mahonheim/bifrost/tesla/OUTPUTS/Synergy/N1/arcanis_base64_assets.md'
with open(path, 'r') as f:
    content = f.read()

assets = re.findall(r'## Asset: `(.*?)`', content)
print("Found assets:", assets)

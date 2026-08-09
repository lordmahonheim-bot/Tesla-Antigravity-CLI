import json

graph_path = "/home/lord-mahonheim/bifrost/tesla/Avalon/.obsidian/graph.json"

def hex_to_dec(hex_str):
    return int(hex_str.lstrip('#'), 16)

with open(graph_path, 'r') as f:
    data = json.load(f)

data["colorGroups"] = [
    {"query": "path:00-Inbox", "color": {"a": 1, "rgb": hex_to_dec("ff3333")}},
    {"query": "path:01-Projects", "color": {"a": 1, "rgb": hex_to_dec("ff9933")}},
    {"query": "path:02-Areas", "color": {"a": 1, "rgb": hex_to_dec("ffcc00")}},
    {"query": "path:10-Alexandria", "color": {"a": 1, "rgb": hex_to_dec("00cc66")}},
    {"query": "path:20-MOCs", "color": {"a": 1, "rgb": hex_to_dec("9933ff")}},
    {"query": "file:Avalon-Sanctuary", "color": {"a": 1, "rgb": hex_to_dec("00ffff")}}
]

with open(graph_path, 'w') as f:
    json.dump(data, f, indent=2)

print("Updated graph.json")

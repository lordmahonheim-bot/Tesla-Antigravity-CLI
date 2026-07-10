import json
import os

class UnderstandGraphLSPWrapper:
    """
    Mock LSP Wrapper that intersects standard LSP queries with the Understand-Anything semantic graph.
    Instead of searching file text linearly, it queries the SQLite DB / JSON graph for context.
    """
    def __init__(self, graph_path='code_graph.json'):
        self.graph_path = graph_path
        self.nodes = {}
        self.edges = []
        self._load_graph()

    def _load_graph(self):
        if not os.path.exists(self.graph_path):
            return
        with open(self.graph_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for node in data.get('nodes', []):
                self.nodes[node['name']] = node
            self.edges = data.get('edges', [])

    def textDocument_definition(self, symbol_name):
        # Query the graph for definition
        if symbol_name in self.nodes:
            return {"status": "success", "data": self.nodes[symbol_name]}
        return {"status": "not_found", "message": "Symbol not in semantic graph."}

    def textDocument_references(self, symbol_name):
        # Query the graph for references
        refs = [edge for edge in self.edges if edge.get('target') == symbol_name]
        return {"status": "success", "references_count": len(refs), "data": refs}

# Future integration with `karellen-lsp-mcp` or `Loop Engineering` will instantiate this wrapper 
# and use it to intercept AST queries before falling back to linear text reading.

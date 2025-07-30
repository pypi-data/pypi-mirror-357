import ast
from .patterns import all_patterns
from .suggestor import format_suggestions

def analyze_code(source: str, filename: str = '<string>'):
    tree = ast.parse(source, filename=filename)
    suggestions = []
    for node in ast.walk(tree):
        for pattern in all_patterns():
            try:
                if pattern.match(node):
                    suggestions.append((filename, node.lineno, pattern.name, pattern.suggest(node)))
            except Exception:
                continue
    return suggestions

def analyze_file(path: str):
    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()
    return analyze_code(source, filename=path)

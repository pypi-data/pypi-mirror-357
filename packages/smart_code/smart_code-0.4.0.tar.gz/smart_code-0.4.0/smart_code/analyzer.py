import ast
import os
import json
import sys

class CodeAnalyzer(ast.NodeVisitor):
    """
    Static code analyzer that detects inefficient code patterns using AST.
    Distinguishes DataFrame operations, detects list.append in loops, and provides robust error handling.
    """
    def __init__(self, lang='zh'):
        self.lang = lang
        self.reset_state()

    def reset_state(self):
        """Reset analysis state before each run."""
        self.issues = []
        self.patterns = self._load_patterns()
        self.loop_stack = []
        self.df_vars = set()              # pandas DataFrame variables
        self.pd_aliases = set()           # pandas module aliases
        self.df_aliases = set()           # DataFrame class aliases
        self.read_csv_aliases = set()     # read_csv function aliases

    def _load_patterns(self):
        path = os.path.join(os.path.dirname(__file__), 'patterns.json')
        try:
            with open(path, encoding='utf-8') as f:
                patterns_list = json.load(f)
        except Exception as e:
            sys.stderr.write(f"Error loading patterns.json: {e}\n")
            return {}
        return {p['id']: p for p in patterns_list if 'id' in p}

    def analyze(self, code):
        """Analyze source code string and return detected issues."""
        self.reset_state()
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            self.issues.append({
                'pattern': 'SYNTAX_ERROR',
                'lineno': e.lineno or 0,
                'description': f"SyntaxError: {e.msg}",
                'suggestion': 'Fix syntax errors before analysis.',
                'complexity': '',
                'hint': ''
            })
            return self.issues
        self.visit(tree)
        return self.issues

    def analyze_file(self, filepath):
        """Read file and analyze, catching I/O errors."""
        try:
            with open(filepath, encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            sys.stderr.write(f"Error reading {filepath}: {e}\n")
            return []
        return self.analyze(code)

    # --- Import tracking ---
    def visit_Import(self, node):
        for alias in node.names:
            name = alias.name
            asname = alias.asname or name
            if name == 'pandas':
                self.pd_aliases.add(asname)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        module = node.module or ''
        if module == 'pandas':
            for alias in node.names:
                name = alias.name
                asname = alias.asname or name
                if name == 'DataFrame':
                    self.df_aliases.add(asname)
                elif name == 'read_csv':
                    self.read_csv_aliases.add(asname)
        self.generic_visit(node)

    # --- Assignment tracking ---
    def visit_Assign(self, node):
        # Detect DataFrame creation: pd.DataFrame(), pd.read_csv(), DataFrame(), read_csv()
        if isinstance(node.value, ast.Call):
            func = node.value.func
            # pd.DataFrame or pd.read_csv
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if func.value.id in self.pd_aliases and func.attr in ('DataFrame', 'read_csv'):
                    for tgt in node.targets:
                        if isinstance(tgt, ast.Name):
                            self.df_vars.add(tgt.id)
            # direct DataFrame() or read_csv()
            elif isinstance(func, ast.Name):
                if func.id in self.df_aliases.union(self.read_csv_aliases):
                    for tgt in node.targets:
                        if isinstance(tgt, ast.Name):
                            self.df_vars.add(tgt.id)
        self.generic_visit(node)

    # --- Loop-based detections ---
    def visit_For(self, node):
        # Nested loops
        if self.loop_stack:
            self._add_issue('NESTED_LOOP_FOR_MATRIX', node.lineno)
        self.loop_stack.append(node)

        # Check subtree for string patterns
        for n in ast.walk(node):
            if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
                left_str = isinstance(n.left, (ast.Constant, ast.Str)) and isinstance(getattr(n.left, 'value', None), str)
                right_str = isinstance(n.right, (ast.Constant, ast.Str)) and isinstance(getattr(n.right, 'value', None), str)
                if left_str or right_str:
                    self._add_issue('STRING_CONCAT_IN_LOOP', n.lineno)
            if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'replace':
                self._add_issue('STRING_REPLACE_IN_LOOP', n.lineno)

        self.generic_visit(node)
        self.loop_stack.pop()

    # --- Function call-based detections ---
    def visit_Call(self, node):
        # Recurse first
        self.generic_visit(node)

        # Only attribute calls
        if not isinstance(node.func, ast.Attribute):
            return
        owner = node.func.value
        attr = node.func.attr

        # Detect DataFrame methods
        if isinstance(owner, ast.Name) and owner.id in self.df_vars:
            if attr == 'iterrows':
                self._add_issue('PANDAS_ITERROWS', node.lineno)
            elif attr == 'apply':
                for kw in node.keywords:
                    if kw.arg == 'axis' and getattr(kw.value, 'value', None) == 1:
                        self._add_issue('PANDAS_APPLY_AXIS1', node.lineno)
            elif attr == 'append':
                self._add_issue('DATAFRAME_APPEND_LOOP', node.lineno)
        # Detect list.append in loops
        elif isinstance(owner, ast.Name) and attr == 'append' and self.loop_stack:
            self._add_issue('LIST_APPEND_IN_LOOP', node.lineno)

        # Additional patterns can be added similarly...

    # --- Comparison-based detections ---
    def visit_Compare(self, node):
        if self.loop_stack and isinstance(node.ops[0], ast.Eq):
            self._add_issue('LINEAR_SEARCH_IN_LOOP', node.lineno)
        self.generic_visit(node)

    # --- Helper ---
    def _add_issue(self, pattern_id, lineno):
        meta = self.patterns.get(pattern_id)
        if not meta:
            return
            
        # 根据语言选择消息
        messages = meta.get('messages', {}).get(self.lang, {})
        if not messages:
            # 提供默认回退
            messages = meta.get('messages', {}).get('en', 
                {'description': 'N/A', 'suggestion': 'N/A', 'hint': 'N/A'}
            )

        issue = {
            'pattern': pattern_id, 
            'lineno': lineno,
            'complexity': meta.get('complexity', ''),
            'description': messages.get('description'),
            'suggestion': messages.get('suggestion'),
            'hint': messages.get('hint')
        }
        self.issues.append(issue)

# Utility

def analyze_code_str(code):
    return CodeAnalyzer().analyze(code)

import ast
import os
import json
import sys

class CodeAnalyzer(ast.NodeVisitor):
    """
    Static code analyzer that detects inefficient code patterns using AST.
    Supports multilingual output and accurate pattern detection.
    """
    def __init__(self, lang='zh'):
        self.lang = lang
        self.reset_state()

    def reset_state(self):
        """Reset analysis state before each run."""
        self.issues = []
        self.loop_stack = []
        # Tracking variables
        self.df_vars = set()
        self.pd_aliases = set()
        self.df_aliases = set()
        self.read_csv_aliases = set()
        self.str_vars = set()  # 新增：追踪字符串类型的变量
        self.patterns = self._load_patterns()

    def _load_patterns(self):
        path = os.path.join(os.path.dirname(__file__), 'patterns.json')
        try:
            with open(path, encoding='utf-8') as f:
                patterns = json.load(f)
        except Exception as e:
            sys.stderr.write(f"Error loading patterns.json: {e}\n")
            return {}
        # index by id
        return {p['id']: p for p in patterns if 'id' in p}

    def analyze(self, code):
        """Analyze code string and return list of detected issues."""
        self.reset_state()
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            self.issues.append(self._make_error_issue(e.lineno or 0, f"SyntaxError: {e.msg}"))
            return self.issues
        self.visit(tree)
        return self.issues

    def analyze_file(self, filepath):
        """Read file, analyze, catch I/O errors."""
        try:
            with open(filepath, encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            sys.stderr.write(f"Error reading {filepath}: {e}\n")
            return []
        return self.analyze(code)

    def _make_error_issue(self, lineno, msg):
        return {
            'pattern': 'SYNTAX_ERROR',
            'lineno': lineno,
            'description': msg,
            'suggestion': 'Fix syntax errors before analysis.',
            'complexity': '',
            'hint': ''
        }

    # --- Imports ---
    def visit_Import(self, node):
        for alias in node.names:
            if alias.name == 'pandas':
                self.pd_aliases.add(alias.asname or 'pandas')
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module == 'pandas':
            for alias in node.names:
                name = alias.name
                asname = alias.asname or name
                if name == 'DataFrame':
                    self.df_aliases.add(asname)
                elif name == 'read_csv':
                    self.read_csv_aliases.add(asname)
        self.generic_visit(node)

    # --- Assignments ---
    def visit_Assign(self, node):
        """处理赋值节点"""
        # DataFrame相关检测
        if isinstance(node.value, ast.Call):
            func = node.value.func
            # pd.DataFrame or pd.read_csv
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if func.value.id in self.pd_aliases and func.attr in ('DataFrame', 'read_csv'):
                    self._track_targets(node.targets)
            # direct DataFrame() or read_csv()
            elif isinstance(func, ast.Name):
                if func.id in self.df_aliases.union(self.read_csv_aliases):
                    self._track_targets(node.targets)

        # 尝试处理 DataFrame 别名, e.g., df2 = df1
        if isinstance(node.value, ast.Name) and node.value.id in self.df_vars:
            self._track_targets(node.targets)

        # 字符串变量追踪与反模式检测
        # 1. 追踪被赋值为字符串字面量的变量
        if isinstance(node.value, (ast.Constant, ast.Str)) and isinstance(getattr(node.value, 'value', None), str):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name):
                    self.str_vars.add(tgt.id)
        
        # 2. 检测累积式字符串拼接: s = s + "..."
        if self.loop_stack and isinstance(node.value, ast.BinOp) and isinstance(node.value.op, ast.Add):
            if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                target_name = node.targets[0].id
                if target_name in self.str_vars:  # 只对已知字符串变量检测
                    left, right = node.value.left, node.value.right
                    is_left_accum = isinstance(left, ast.Name) and left.id == target_name
                    is_right_accum = isinstance(right, ast.Name) and right.id == target_name
                    
                    if is_left_accum or is_right_accum:
                        self._add_issue('STRING_CONCAT_IN_LOOP', node.lineno)
        
        # 3. 检测字典构建模式
        if isinstance(node.targets[0], ast.Subscript) and self.loop_stack:
            if self._is_simple_dict_build(node):
                self._add_issue('DICT_SETITEM_IN_LOOP', node.lineno)
        
        self.generic_visit(node)

    def _track_targets(self, targets):
        for tgt in targets:
            if isinstance(tgt, ast.Name):
                self.df_vars.add(tgt.id)

    # --- For-loop detections ---
    def visit_For(self, node):
        """处理for循环节点"""
        self.loop_stack.append(node)
        
        # 检测嵌套循环
        if len(self.loop_stack) > 1:
            # 检查是否有数组/矩阵访问
            class MatrixAccessVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.has_matrix_access = False
                    
                def visit_Subscript(self, node):
                    # 检查是否是二维下标访问，比如 matrix[i][j]
                    if isinstance(node.value, ast.Subscript):
                        self.has_matrix_access = True
                    self.generic_visit(node)
            
            visitor = MatrixAccessVisitor()
            visitor.visit(node)
            
            if visitor.has_matrix_access:
                self._add_issue('NESTED_LOOP_FOR_MATRIX', node.lineno)
        
        # 检查循环内的字符串replace
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Attribute):
                if child.func.attr == 'replace':
                    self._add_issue('STRING_REPLACE_IN_LOOP', child.lineno)
        
        self.generic_visit(node)
        self.loop_stack.pop()

    def visit_AugAssign(self, node):
        """检测 s += '...' 累积式字符串拼接"""
        if self.loop_stack and isinstance(node.op, ast.Add):
            if isinstance(node.target, ast.Name) and node.target.id in self.str_vars:
                self._add_issue('STRING_CONCAT_IN_LOOP', node.lineno)
        self.generic_visit(node)

    # --- Call detections ---
    def visit_Call(self, node):
        """处理函数调用节点"""
        # Visit children first
        self.generic_visit(node)
        if not isinstance(node.func, ast.Attribute):
            return
        owner = node.func.value
        method = node.func.attr

        # DataFrame methods only on tracked df_vars
        if isinstance(owner, ast.Name) and owner.id in self.df_vars:
            if method == 'iterrows':
                self._add_issue('PANDAS_ITERROWS', node.lineno)
            elif method == 'apply':
                for kw in node.keywords:
                    if kw.arg == 'axis' and getattr(kw.value, 'value', None) == 1:
                        self._add_issue('PANDAS_APPLY_AXIS1', node.lineno)
            elif method == 'append':
                self._add_issue('DATAFRAME_APPEND_LOOP', node.lineno)
        # list.append in loops. 
        elif isinstance(owner, ast.Name) and method == 'append':
            if self._is_simple_append_loop(node):
                self._add_issue('LIST_APPEND_IN_LOOP', node.lineno)

    # --- Compare detections ---
    def visit_Compare(self, node):
        # 改进线性搜索检测：寻找 `var in list_var` 模式
        if self.loop_stack and len(node.ops) == 1 and isinstance(node.ops[0], ast.In):
            # 确保比较的是一个变量，而不是字面量列表
            if isinstance(node.comparators[0], ast.Name):
                self._add_issue('LINEAR_SEARCH_IN_LOOP', node.lineno)
        self.generic_visit(node)

    # --- Issue reporting ---
    def _add_issue(self, pid, lineno):
        meta = self.patterns.get(pid)
        if not meta:
            return
        # choose messages by lang
        msg = meta.get('messages', {}).get(self.lang, {})

        issue = {
            'pattern': pid,
            'lineno': lineno,
            'description': msg.get('description', ''),
            'suggestion': msg.get('suggestion', ''),
            'complexity': meta.get('complexity', ''),
            'hint': msg.get('hint', ''),
            'suggestion_code': msg.get('suggestion_code')
        }
        self.issues.append(issue)

    def _is_simple_append_loop(self, node):
        """
        判断是否是简单的可以用列表推导式替换的append循环。
        返回False的情况包括：
        1. 有多个条件分支
        2. 有复杂的条件表达式
        3. 涉及状态维护（如累加器）
        4. 有函数调用或复杂对象操作
        """
        if not self.loop_stack:
            return False
            
        current_loop = self.loop_stack[-1]
        
        class ComplexityVisitor(ast.NodeVisitor):
            def __init__(self):
                self.is_complex = False
                self.branch_count = 0
                self.assign_count = 0
                self.has_function_call = False
                self.has_attribute_access = False
                self.append_count = 0
                
            def visit_If(self, node):
                self.branch_count += 1
                # 检查if条件的复杂度
                if isinstance(node.test, (ast.BoolOp, ast.Compare)):
                    if isinstance(node.test, ast.Compare) and len(node.test.ops) > 1:
                        self.is_complex = True
                self.generic_visit(node)
                
            def visit_Assign(self, node):
                # 只计算非append的赋值
                if not (isinstance(node.targets[0], ast.Name) and 
                       isinstance(node.value, ast.Call) and 
                       isinstance(node.value.func, ast.Attribute) and 
                       node.value.func.attr == 'append'):
                    self.assign_count += 1
                self.generic_visit(node)
                
            def visit_AugAssign(self, node):
                self.assign_count += 1
                self.generic_visit(node)
                
            def visit_Call(self, node):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'append':
                        self.append_count += 1
                    else:
                        self.has_function_call = True
                else:
                    # 只将非内置函数视为复杂操作
                    if isinstance(node.func, ast.Name):
                        builtin_functions = {'range', 'len', 'str', 'int', 'float', 'list', 'dict', 'set', 'tuple'}
                        if node.func.id not in builtin_functions:
                            self.has_function_call = True
                    else:
                        self.has_function_call = True
                self.generic_visit(node)
                
            def visit_Attribute(self, node):
                # 只有非append的属性访问才算复杂
                if not (isinstance(node.ctx, ast.Load) and node.attr == 'append'):
                    self.has_attribute_access = True
                self.generic_visit(node)

        visitor = ComplexityVisitor()
        visitor.visit(current_loop)
        
        # 简单的append循环应该：
        # 1. 至少有一个append调用
        # 2. 没有或只有一个简单的条件分支
        # 3. 没有其他赋值操作
        # 4. 没有其他函数调用
        # 5. 没有复杂的属性访问
        result = (visitor.append_count >= 1 and
                visitor.branch_count <= 1 and
                not visitor.is_complex and
                visitor.assign_count == 0 and
                not visitor.has_function_call and
                not visitor.has_attribute_access)
        
        return result

    def _is_simple_dict_build(self, node):
        """
        判断是否是简单的字典构建循环，可以用字典推导式替换。
        返回False的情况包括：
        1. 有多个条件分支
        2. 有复杂的条件表达式
        3. 有其他赋值操作
        4. 有函数调用或复杂对象操作
        """
        if not self.loop_stack:
            return False
            
        current_loop = self.loop_stack[-1]
        
        class DictBuildVisitor(ast.NodeVisitor):
            def __init__(self):
                self.is_complex = False
                self.branch_count = 0
                self.assign_count = 0
                self.has_function_call = False
                self.has_attribute_access = False
                self.subscript_assign_count = 0
                self.target_dict = None
                
            def visit_If(self, node):
                self.branch_count += 1
                if isinstance(node.test, (ast.BoolOp, ast.Compare)):
                    if isinstance(node.test, ast.Compare) and len(node.test.ops) > 1:
                        self.is_complex = True
                self.generic_visit(node)
                
            def visit_Assign(self, node):
                if isinstance(node.targets[0], ast.Subscript):
                    if isinstance(node.targets[0].value, ast.Name):
                        if self.target_dict is None:
                            self.target_dict = node.targets[0].value.id
                            self.subscript_assign_count += 1
                        elif self.target_dict == node.targets[0].value.id:
                            self.subscript_assign_count += 1
                else:
                    self.assign_count += 1
                self.generic_visit(node)
                
            def visit_Call(self, node):
                # 只计算非append的函数调用
                if not (isinstance(node.func, ast.Attribute) and node.func.attr == 'append'):
                    self.has_function_call = True
                self.generic_visit(node)
                
            def visit_Attribute(self, node):
                # 只计算非append的属性访问
                if not (isinstance(node.ctx, ast.Load) and node.attr == 'append'):
                    self.has_attribute_access = True
                self.generic_visit(node)

        visitor = DictBuildVisitor()
        visitor.visit(current_loop)
        
        # 简单的字典构建循环应该：
        # 1. 至少有一个下标赋值
        # 2. 没有或只有一个简单的条件分支
        # 3. 没有其他赋值操作
        # 4. 没有函数调用
        # 5. 没有属性访问
        result = (visitor.subscript_assign_count >= 1 and
                visitor.branch_count <= 1 and
                not visitor.is_complex and
                visitor.assign_count == 0 and
                not visitor.has_function_call and
                not visitor.has_attribute_access)
        
        return result

# Utility

def analyze_code_str(code):
    return CodeAnalyzer().analyze(code)

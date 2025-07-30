import ast
from typing import List

class Pattern:
    name: str
    description: str

    def match(self, node: ast.AST) -> bool:
        raise NotImplementedError

    def suggest(self, node: ast.AST) -> str:
        raise NotImplementedError

_patterns: List[Pattern] = []

def register(pattern_cls):
    _patterns.append(pattern_cls())
    return pattern_cls

def all_patterns():
    return _patterns

@register
class BadListMemberCheck(Pattern):
    name = "bad_list_member_check"
    description = "list member check inside loop; use set for O(1) membership"

    def match(self, node):
        if not isinstance(node, ast.If):
            return False
        test = node.test
        return (isinstance(test, ast.Compare)
                and isinstance(test.ops[0], ast.In)
                and isinstance(test.left, ast.Name)
                and isinstance(test.comparators[0], ast.Name))

    def suggest(self, node):
        list_name = node.test.comparators[0].id
        return f"Move '{list_name}' to a set before the loop for O(1) membership checks."

@register
class BadSortTakeFirst(Pattern):
    name = "bad_sort_take_first"
    description = "sorting whole list to take min/max; use min()/max()"

    def match(self, node):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Subscript):
            val = node.value
            if (isinstance(val.value, ast.Call) and
                isinstance(val.value.func, ast.Name) and val.value.func.id == 'sorted'):
                return True
        return False

    def suggest(self, node):
        return "Use min()/max() instead of sorting entire list to retrieve smallest/largest element."

@register
class BadLoopSum(Pattern):
    name = "bad_loop_sum"
    description = "loop-based sum; use built-in sum()"

    def match(self, node):
        return (isinstance(node, ast.AugAssign)
                and isinstance(node.op, ast.Add)
                and isinstance(node.target, ast.Name))

    def suggest(self, node):
        var = node.target.id
        return f"Replace loop-based accumulation of '{var}' with built-in sum()."

@register
class BadStringConcat(Pattern):
    name = "bad_string_concat"
    description = "string concatenation inside loop; use str.join()"

    def match(self, node):
        # match: AugAssign with Add and both target and value are Str or Name
        return (isinstance(node, ast.AugAssign)
                and isinstance(node.op, ast.Add)
                and isinstance(node.value, (ast.Str, ast.Name))
                and isinstance(node.target, ast.Name))

    def suggest(self, node):
        var = node.target.id
        return f"Accumulate strings in a list and use ''.join(list) instead of '{var} += ...' in loop."

@register
class BadNestedLoopFlatten(Pattern):
    name = "bad_nested_loop_flatten"
    description = "nested loops for flattening; use itertools.chain.from_iterable()"

    def match(self, node):
        # match inner For inside a For, appending to single list
        if isinstance(node, ast.For):
            for stmt in node.body:
                if isinstance(stmt, ast.For):
                    inner = stmt
                    for s in inner.body:
                        if (isinstance(s, ast.Expr) and isinstance(s.value, ast.Call)
                            and isinstance(s.value.func, ast.Attribute)
                            and s.value.func.attr == 'append'):
                            return True
        return False

    def suggest(self, node):
        return "Use itertools.chain.from_iterable(your_list) to flatten nested lists more efficiently."

@register
class BadManualIndexLoop(Pattern):
    name = "bad_manual_index_loop"
    description = "loop over range(len()) and index list; use direct iteration"

    def match(self, node):
        # match For with range(len(x))
        if isinstance(node, ast.For) and isinstance(node.iter, ast.Call):
            func = node.iter.func
            if isinstance(func, ast.Name) and func.id == 'range':
                args = node.iter.args
                if len(args) == 1 and isinstance(args[0], ast.Call):
                    inner = args[0]
                    if (isinstance(inner.func, ast.Name) and inner.func.id == 'len'):
                        return True
        return False

    def suggest(self, node):
        list_name = node.iter.args[0].args[0].id
        return f"Iterate directly over '{list_name}' rather than using range(len())."

@register
class BadFilterToList(Pattern):
    name = "bad_filter_to_list"
    description = "list(filter(...)) usage; use list comprehension"

    def match(self, node):
        # match Assign with Call func Name 'list' and first arg is filter()
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            val = node.value
            if (isinstance(val.func, ast.Name) and val.func.id == 'list'
                and val.args and isinstance(val.args[0], ast.Call)
                and isinstance(val.args[0].func, ast.Name)
                and val.args[0].func.id == 'filter'):
                return True
        return False

    def suggest(self, node):
        return "Use list comprehension [x for x in iterable if cond(x)] instead of list(filter())."

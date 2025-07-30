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
        return (
            f"将列表 '{list_name}' 转为集合：\n"
            f"  {list_name}_set = set({list_name})\n"
            f"并在循环中使用集合进行成员检查，提高到 O(1) 复杂度。"
        )


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
        return (
            "无需对整个列表排序后取第一个元素，建议：\n"
            "  # 原代码\n"
            "  min_val = sorted(values)[0]\n"
            "  # 优化后\n"
            "  min_val = min(values)"
        )


@register
class BadSortSlice(Pattern):
    name = "bad_sort_slice"
    description = "sorting then slicing; use heapq.nsmallest/nlargest"

    def match(self, node):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Subscript):
            val = node.value
            if (isinstance(val.value, ast.Call) and
                    isinstance(val.value.func, ast.Name) and val.value.func.id == 'sorted'):
                return True
        return False

    def suggest(self, node):
        return (
            "排序后切片取前 N 项可以使用 heapq：\n"
            "  # 原代码\n"
            "  top_n = sorted(items)[:N]\n"
            "  # 优化后\n"
            "  import heapq\n"
            "  top_n = heapq.nsmallest(N, items)"
        )


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
        return (
            f"循环累加可使用内置 sum()：\n"
            f"  # 原代码\n"
            f"  {var} = 0\n"
            f"  for x in data:\n"
            f"      {var} += x\n"
            f"  # 优化后\n"
            f"  {var} = sum(data)"
        )


@register
class BadStringConcat(Pattern):
    name = "bad_string_concat"
    description = "string concatenation inside loop; use str.join()"

    def match(self, node):
        return (isinstance(node, ast.AugAssign)
                and isinstance(node.op, ast.Add)
                and isinstance(node.value, (ast.Str, ast.Name))
                and isinstance(node.target, ast.Name))

    def suggest(self, node):
        var = node.target.id
        return (
            f"循环中字符串拼接效率低，建议收集后一次性 join：\n"
            f"  # 原代码\n"
            f"  s = ''\n"
            f"  for part in parts:\n"
            f"      s += part\n"
            f"  # 优化后\n"
            f"  result = ''.join(parts)"
        )


@register
class BadNestedLoopFlatten(Pattern):
    name = "bad_nested_loop_flatten"
    description = "nested loops for flattening; use itertools.chain.from_iterable()"

    def match(self, node):
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
        return (
            "嵌套循环扁平化可使用 itertools：\n"
            "  # 原代码\n"
            "  flat = []\n"
            "  for sub in lists:\n"
            "      for x in sub:\n"
            "          flat.append(x)\n"
            "  # 优化后\n"
            "  import itertools\n"
            "  flat = list(itertools.chain.from_iterable(lists))"
        )


@register
class BadManualIndexLoop(Pattern):
    name = "bad_manual_index_loop"
    description = "loop over range(len()) and index list; use direct iteration"

    def match(self, node):
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
        return (
            f"直接迭代列表而非使用索引：\n"
            f"  # 原代码\n"
            f"  for i in range(len({list_name})):\n"
            f"      item = {list_name}[i]\n"
            f"  # 优化后\n"
            f"  for item in {list_name}:"
        )


@register
class BadFilterToList(Pattern):
    name = "bad_filter_to_list"
    description = "list(filter(...)) usage; use list comprehension"

    def match(self, node):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Call):
            val = node.value
            if (isinstance(val.func, ast.Name) and val.func.id == 'list'
                    and val.args and isinstance(val.args[0], ast.Call)
                    and isinstance(val.args[0].func, ast.Name)
                    and val.args[0].func.id == 'filter'):
                return True
        return False

    def suggest(self, node):
        return (
            "使用列表推导替换 filter：\n"
            "  # 原代码\n"
            "  nums = list(filter(lambda x: x>0, numbers))\n"
            "  # 优化后\n"
            "  nums = [x for x in numbers if x > 0]"
        )


@register
class BadDictComprehension(Pattern):
    name = "bad_dict_comprehension"
    description = "building dict in loop; use dict comprehension"

    def match(self, node):
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Dict):
            return False
        # detect pattern: assignment of empty dict followed by loop with dict[key]=value
        return False

    def suggest(self, node):
        return (
            "使用字典推导式简化构建：\n"
            "  # 原代码\n"
            "  d = {}\n"
            "  for x in items:\n"
            "      d[x.key] = x.value\n"
            "  # 优化后\n"
            "  d = {x.key: x.value for x in items}"
        )
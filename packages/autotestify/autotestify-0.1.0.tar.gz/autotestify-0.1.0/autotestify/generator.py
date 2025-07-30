import ast
from pathlib import Path

def get_dummy_value(arg_name: str) -> str:
    """Argument nomiga qarab mos dummy qiymatni qaytaradi."""
    name = arg_name.lower()
    if any(keyword in name for keyword in ("str", "name", "text")):
        return '"example"'
    elif any(keyword in name for keyword in ("list", "items")):
        return '[]'
    elif any(keyword in name for keyword in ("dict", "data", "info")):
        return '{}'
    elif "flag" in name or name.startswith("is_"):
        return 'True'
    else:
        return '1'  # Default — integer

def get_decorator_name(decorator):
    if isinstance(decorator, ast.Name):
        return decorator.id
    elif isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
        return decorator.func.id
    elif isinstance(decorator, ast.Attribute):
        return decorator.attr
    return None

def extract_autotest_functions(filepath):
    """Berilgan fayldan faqat @autotest bilan belgilangan funksiyalarni chiqaradi."""
    functions = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=filepath)
    except FileNotFoundError:
        print(f"❌ Fayl topilmadi: {filepath}")
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            decorator_names = [get_decorator_name(d) for d in node.decorator_list]
            if 'autotest' in decorator_names:
                arg_names = [arg.arg for arg in node.args.args if arg.arg != "self"]
                functions.append({"name": node.name, "args": arg_names})
    return functions


def generate_tests(filepath):
    """Funksiyalar uchun test kodlarini generatsiya qiladi."""
    functions = extract_autotest_functions(filepath)
    if not functions:
        print("⚠️ Hech qanday @autotest funksiyasi topilmadi.")
        return ""

    module_name = Path(filepath).stem
    lines = ["import pytest", f"from {module_name} import *", "", ""]

    for fn in functions:
        dummy_args = ", ".join(get_dummy_value(arg) for arg in fn["args"])
        lines.append(f"def test_{fn['name']}():")
        lines.append(f"    result = {fn['name']}({dummy_args})")
        lines.append(f"    assert result is not None\n")

    return "\n".join(lines)

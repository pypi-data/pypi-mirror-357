# =============================================================================
#  Divengine Python Vault (PyVault)
# =============================================================================
#  Name:        pyvault
#  Version:     1.0.2
#  Author:      rafageist @ Divengine Software Solutions
#  License:     MIT
#
#  Description:
#  PyVault is a tool that parses a Python codebase and generates an Obsidian-
#  compatible vault. It extracts modules, classes, functions, and internal 
#  relationships (such as inheritance and function calls) and outputs a set of 
#  Markdown files with Obsidian wiki-style links.
#
#  This enables developers, educators, and learners to visualize and navigate
#  a codebase as a knowledge graph using Obsidian.
#
#  Usage:
#      python generate.py <project_path> <vault_output_folder>
#
#  Example:
#      python generate.py ../my_project ./vault
#
#  Project website:
#      https://github.com/divengine/pyvault
# =============================================================================

import os
import ast
import argparse
import warnings
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import sys

def resolve_link(path_str):
    return f"[[{path_str.replace(os.sep, '/') }]]"


def _write_note(note_path, content_lines):
    os.makedirs(os.path.dirname(note_path), exist_ok=True)
    with open(note_path, "w", encoding="utf-8") as f:
        f.writelines(content_lines)
    sys.stdout.write("\033[2K\r")

def format_docstring(doc):
    lines = doc.strip().split("\n")
    formatted = []
    table = []
    for line in lines:
        line = line.strip()
        if line.startswith(":param") or line.startswith(":type") or line.startswith(":returns") or line.startswith(":rtype"):
            parts = line.split(" ", 2)
            if len(parts) == 3:
                label, name, desc = parts
                table.append((label.strip(':'), name, desc))
        else:
            formatted.append(line)

    result = "\n".join(formatted)
    if table:
        result += "\n\n### Details:\n"
        result += "| Tag | Name | Description |\n"
        result += "|-----|------|-------------|\n"
        for tag, name, desc in table:
            result += f"| `{tag}` | `{name}` | {desc} |\n"
    return result

def extract_info(filepath, base_folder, ctx):
    rel = os.path.relpath(filepath, base_folder)
    sys.stdout.write("\033[2K\r")
    print(f"🔍 Processing file: {rel}", end="", flush=True)

    with open(filepath, "r", encoding="utf-8", errors="ignore") as file:
        try:
            source_code = file.read()
            node = ast.parse(source_code, filename=filepath)
        except SyntaxError:
            return

    rel_path = os.path.relpath(filepath, base_folder)
    rel_path_no_ext = os.path.splitext(rel_path)[0]

    ctx['stats']['files'] += 1
    ctx['stats']['modules'] += 1

    for item in node.body:
        if isinstance(item, ast.Import):
            for alias in item.names:
                ctx['import_data'][rel_path].append(alias.name)
                ctx['stats']['imports'] += 1

        elif isinstance(item, ast.ImportFrom):
            module = item.module if item.module else ""
            for alias in item.names:
                ctx['import_data'][rel_path].append(f"{module}.{alias.name}")
                ctx['stats']['imports'] += 1

        if isinstance(item, ast.ClassDef):
            ctx['stats']['classes'] += 1
            class_name = item.name
            bases = [base.id if isinstance(base, ast.Name) else ast.unparse(base) for base in item.bases]
            class_path = os.path.join(rel_path_no_ext, class_name)
            ctx['class_index'][class_name] = class_path
            ctx['module_index'][rel_path]["classes"].append(class_path)

            methods = []
            props = []
            for child in item.body:
                if isinstance(child, ast.FunctionDef):
                    ctx['stats']['functions'] += 1
                    methods.append(child.name)
                    ctx['function_index'][child.name] = os.path.join(class_path, child.name)
                    ctx['uses_map'][class_path].add(os.path.join(class_path, child.name))
                    write_function_note(child.name, child.args, rel_path, ctx, os.path.join(class_path, child.name), ast.get_docstring(child))
                    find_calls(child, os.path.join(class_path, child.name), ctx)
                elif isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(target, ast.Name):
                            props.append(target.id)

            write_class_note(class_name, bases, methods, props, rel_path, ctx, class_path, ast.get_docstring(item))

        elif isinstance(item, ast.FunctionDef):
            ctx['stats']['functions'] += 1
            func_name = item.name
            full_func_path = os.path.join(rel_path_no_ext, func_name)
            ctx['function_index'][func_name] = full_func_path
            ctx['module_index'][rel_path]["functions"].append(full_func_path)
            write_function_note(func_name, item.args, rel_path, ctx, full_func_path, ast.get_docstring(item))
            find_calls(item, full_func_path, ctx)


def write_class_note(name, bases, methods, props, rel_path, ctx, full_path, doc):
    dest_path = os.path.join(ctx['VAULT_DIR'], full_path + ".md")
    content = [
        f"# Class `{name}`\n",
        f"#class\n\n",
        f"**File**: `{rel_path}`\n\n"
    ]
    if doc:
        content.append(f"## Docstring:\n\n{doc}\n\n")
    content.append("## Inherits from:\n")
    content += [f"- {resolve_link(ctx['class_index'][b])}\n" for b in bases if b in ctx['class_index']] or ["- None\n"]
    content.append("\n## Methods:\n")
    content += [f"- {resolve_link(os.path.join(full_path, m))}\n" for m in methods] or ["- None\n"]
    content.append("\n## Properties:\n")
    content += [f"- `{p}` #property\n" for p in props] or ["- None\n"]
    _write_note(dest_path, content)


def write_function_note(name, args_obj, rel_path, ctx, full_path, doc):
    dest_path = os.path.join(ctx['VAULT_DIR'], full_path + ".md")
    args = [arg.arg for arg in args_obj.args]
    content = [
        f"# Function `{name}`\n",
        f"#method\n\n" if "/" in full_path else "#function\n\n",
        f"**File**: `{rel_path}`\n\n",
        "## Arguments:\n"
    ]
    content += [f"- `{arg}`\n" for arg in args] or ["- None\n"]
    if doc:
        content.append("\n## Docstring:\n\n")
        content.append(format_docstring(doc))
        content.append("\n")
    if full_path in ctx['uses_map']:
        content.append("\n## Uses:\n")
        content += [f"- {resolve_link(target)}\n" for target in ctx['uses_map'][full_path]]
    _write_note(dest_path, content)


def find_calls(node, current_path, ctx):
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name):
                called = child.func.id
                if called in ctx['function_index']:
                    ctx['uses_map'][current_path].add(ctx['function_index'][called])
                    ctx['stats']['relationships'] += 1
            elif isinstance(child.func, ast.Attribute):
                attr = child.func.attr
                if attr in ctx['function_index']:
                    ctx['uses_map'][current_path].add(ctx['function_index'][attr])
                    ctx['stats']['relationships'] += 1


def write_module_and_import_notes(ctx):
    for rel_path, items in ctx['module_index'].items():
        module_name = os.path.splitext(os.path.basename(rel_path))[0]
        dest_path = os.path.join(ctx['VAULT_DIR'], os.path.splitext(rel_path)[0] + ".md")
        content = [
            f"# Module `{module_name}.py`\n",
            "#module\n\n",
            f"**Path**: `{rel_path}`\n\n",
        ]
        if items["functions"]:
            content.append("## Functions:\n")
            content += [f"- {resolve_link(f)}\n" for f in items["functions"]]
        if items["classes"]:
            content.append("\n## Classes:\n")
            content += [f"- {resolve_link(c)}\n" for c in items["classes"]]
        _write_note(dest_path, content)

    for rel_path, imports in ctx['import_data'].items():
        dest_path = os.path.join(ctx['VAULT_DIR'], os.path.splitext(rel_path)[0], "imports.md")
        content = [
            f"# Imports in `{rel_path}`\n",
            f"#imports\n\n"
        ]
        content += [f"- `{imp}`\n" for imp in imports]
        _write_note(dest_path, content)


def scan_folder(folder, ctx):
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".py"):
                extract_info(os.path.join(root, file), folder, ctx)
    sys.stdout.write("\033[2K\r")
    print("✔️ Done scanning files.")


def main():
    print("=" * 60)
    print("🧠 Divengine Python Vault – Generate Obsidian.md vault from Python project")
    print(f"📦 Version: 1.0.2")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    warnings.filterwarnings("ignore", category=SyntaxWarning)

    parser = argparse.ArgumentParser(
        prog="pyvault",
        description="Divengine Python Vault - Generate an Obsidian-compatible vault from a Python codebase.",
        epilog="Example: pyvault ./my_project ./vault_output"
    )

    parser.add_argument("project_path", help="Path to the root folder of the Python project")
    parser.add_argument("vault_output", help="Path to the output folder for the Obsidian vault")

    args = parser.parse_args()

    ctx = {
        'VAULT_DIR': args.vault_output,
        'class_index': {},
        'function_index': {},
        'uses_map': defaultdict(set),
        'import_data': defaultdict(list),
        'module_index': defaultdict(lambda: {"functions": [], "classes": []}),
        'stats': {
            'files': 0,
            'modules': 0,
            'classes': 0,
            'functions': 0,
            'imports': 0,
            'relationships': 0
        }
    }

    os.makedirs(ctx['VAULT_DIR'], exist_ok=True)
    scan_folder(args.project_path, ctx)
    print("\n🔧 Finishing...")
    write_module_and_import_notes(ctx)

    print();
    print("\n📊 Summary:")
    print("-----------------------------------------------");
    print(f"- 📁 Files scanned:      {ctx['stats']['files']}")
    print(f"- 📦 Modules detected:   {ctx['stats']['modules']}")
    print(f"- 🏷️ Classes detected:   {ctx['stats']['classes']}")
    print(f"- 🔧 Functions detected: {ctx['stats']['functions']}")
    print(f"- 📚 Imports:            {ctx['stats']['imports']}")
    print(f"- 🔗 Relationships:      {ctx['stats']['relationships']}")
    print("-----------------------------------------------");

    print("\n✅ Done.")


if __name__ == "__main__":
    main()

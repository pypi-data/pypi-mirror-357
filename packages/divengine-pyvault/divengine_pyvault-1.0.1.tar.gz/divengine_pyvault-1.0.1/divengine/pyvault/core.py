# =============================================================================
#  Divengine Python Vault (PyVault)
# =============================================================================
#  Name:        pyvault
#  Version:     1.0
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

def extract_info(filepath, base_folder, ctx):
    with open(filepath, "r", encoding="utf-8") as file:
        try:
            node = ast.parse(file.read(), filename=filepath)
        except SyntaxError:
            return

    rel_path = os.path.relpath(filepath, base_folder)
    rel_path_no_ext = os.path.splitext(rel_path)[0]

    for item in node.body:
        if isinstance(item, ast.Import):
            for alias in item.names:
                ctx['import_data'][rel_path].append(alias.name)
        elif isinstance(item, ast.ImportFrom):
            module = item.module if item.module else ""
            for alias in item.names:
                ctx['import_data'][rel_path].append(f"{module}.{alias.name}")

        if isinstance(item, ast.ClassDef):
            class_name = item.name
            bases = [base.id if isinstance(base, ast.Name) else ast.unparse(base) for base in item.bases]
            methods = []
            props = []
            for child in item.body:
                if isinstance(child, ast.FunctionDef):
                    methods.append(child.name)
                    find_calls(child, rel_path_no_ext, class_name, ctx)
                elif isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(target, ast.Name):
                            props.append(target.id)
            ctx['class_data'][rel_path].append({
                "name": class_name,
                "bases": bases,
                "methods": methods,
                "properties": props
            })
            full_class_path = os.path.join(rel_path_no_ext, class_name)
            ctx['class_index'][class_name] = full_class_path
            ctx['module_index'][rel_path]["classes"].append(full_class_path)

        elif isinstance(item, ast.FunctionDef):
            func_name = item.name
            ctx['function_data'][rel_path].append({
                "name": func_name,
                "args": [arg.arg for arg in item.args.args]
            })
            full_func_path = os.path.join(rel_path_no_ext, func_name)
            ctx['function_index'][func_name] = full_func_path
            ctx['module_index'][rel_path]["functions"].append(full_func_path)
            find_calls(item, rel_path_no_ext, func_name, ctx)

def find_calls(node, current_path, current_name, ctx):
    for child in ast.walk(node):
        if isinstance(child, ast.Call):
            if isinstance(child.func, ast.Name):
                called = child.func.id
                if called in ctx['function_index']:
                    ctx['uses_map'][os.path.join(current_path, current_name)].add(ctx['function_index'][called])
            elif isinstance(child.func, ast.Attribute):
                attr = child.func.attr
                if attr in ctx['function_index']:
                    ctx['uses_map'][os.path.join(current_path, current_name)].add(ctx['function_index'][attr])

def _write_note(note_path, content_lines):
    os.makedirs(os.path.dirname(note_path), exist_ok=True)
    with open(note_path, "w", encoding="utf-8") as f:
        f.writelines(content_lines)

def resolve_link(path_str):
    return f"[[{path_str.replace(os.sep, '/') }]]"

def generate_notes(ctx, VAULT_DIR):
    for rel_path, classes in ctx['class_data'].items():
        for cls in classes:
            base_path = os.path.join(os.path.splitext(rel_path)[0], cls['name'])
            dest_path = os.path.join(VAULT_DIR, base_path + ".md")
            content = [
                f"# Class `{cls['name']}`\n",
                f"#class\n\n",
                f"**File**: `{rel_path}`\n\n",
                "## Inherits from:\n"
            ]
            content += [f"- {resolve_link(ctx['class_index'][b])}\n" for b in cls['bases'] if b in ctx['class_index']] or ["- None\n"]
            content.append("\n## Methods:\n")
            content += [f"- `{m}` #method\n" for m in cls['methods']] or ["- None\n"]
            content.append("\n## Properties:\n")
            content += [f"- `{p}` #property\n" for p in cls['properties']] or ["- None\n"]
            if base_path in ctx['uses_map']:
                content.append("\n## Uses:\n")
                content += [f"- {resolve_link(target)}\n" for target in ctx['uses_map'][base_path]]
            _write_note(dest_path, content)

    for rel_path, funcs in ctx['function_data'].items():
        for func in funcs:
            base_path = os.path.join(os.path.splitext(rel_path)[0], func['name'])
            dest_path = os.path.join(VAULT_DIR, base_path + ".md")
            content = [
                f"# Function `{func['name']}`\n",
                f"#function\n\n",
                f"**File**: `{rel_path}`\n\n",
                "## Arguments:\n"
            ]
            content += [f"- `{arg}`\n" for arg in func['args']] or ["- None\n"]
            if base_path in ctx['uses_map']:
                content.append("\n## Uses:\n")
                content += [f"- {resolve_link(target)}\n" for target in ctx['uses_map'][base_path]]
            _write_note(dest_path, content)

    for rel_path, items in ctx['module_index'].items():
        module_name = os.path.splitext(os.path.basename(rel_path))[0]
        dest_path = os.path.join(VAULT_DIR, os.path.splitext(rel_path)[0] + ".md")
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
        dest_path = os.path.join(VAULT_DIR, os.path.splitext(rel_path)[0], "imports.md")
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

def main():
    warnings.filterwarnings("ignore", category=SyntaxWarning)

    parser = argparse.ArgumentParser(description="Generate an Obsidian vault from a Python project.")
    parser.add_argument("project_path", help="Path to the root folder of the Python project")
    parser.add_argument("vault_output", help="Path to the output folder for the Obsidian vault")
    args = parser.parse_args()

    PROJECT_PATH = args.project_path
    VAULT_DIR = args.vault_output
    os.makedirs(VAULT_DIR, exist_ok=True)

    ctx = {
        'class_data': defaultdict(list),
        'function_data': defaultdict(list),
        'import_data': defaultdict(list),
        'uses_map': defaultdict(set),
        'class_index': {},
        'function_index': {},
        'module_index': defaultdict(lambda: {"functions": [], "classes": []}),
    }

    scan_folder(PROJECT_PATH, ctx)
    generate_notes(ctx, VAULT_DIR)

if __name__ == "__main__":
    main()

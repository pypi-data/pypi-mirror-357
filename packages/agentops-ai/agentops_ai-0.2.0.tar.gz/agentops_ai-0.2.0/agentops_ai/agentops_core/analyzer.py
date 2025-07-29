"""Analyzer module for AgentOps.

Provides code analysis utilities for extracting function and class information.
"""

import ast
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


class FunctionInfo:
    """Stores information about a function in the codebase."""

    def __init__(self, name, args, docstring):
        """Initialize FunctionInfo with name, args, and docstring."""
        ...


class ClassInfo:
    """Stores information about a class in the codebase."""

    def __init__(self, name, methods, docstring):
        """Initialize ClassInfo with name, methods, and docstring."""
        ...


class CodeAnalyzer:
    """Performs static analysis on Python code to extract structure and metadata."""

    def analyze_file(self, file_path):
        """Analyze a Python file and extract function and class information."""
        ...

    def analyze_code(self, code):
        """Analyze Python code and extract function and class information."""
        ...

    def _extract_imports(self, tree: ast.AST) -> List[str]:
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        return imports

    def _extract_functions(self, tree: ast.AST) -> List[FunctionInfo]:
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and isinstance(
                node.parent, ast.Module
            ):
                functions.append(self._function_info_from_node(node))
        return functions

    def _extract_classes(self, tree: ast.AST) -> List[ClassInfo]:
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [
                    self._function_info_from_node(n)
                    for n in node.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                bases = [self._get_name(base) for base in node.bases]
                docstring = ast.get_docstring(node)
                classes.append(
                    ClassInfo(
                        name=node.name,
                        methods=methods,
                        docstring=docstring,
                        bases=bases,
                    )
                )
        return classes

    def _function_info_from_node(self, node: ast.AST) -> FunctionInfo:
        params = []
        for arg in node.args.args:
            param = {"name": arg.arg}
            if arg.annotation:
                param["type"] = self._get_name(arg.annotation)
            else:
                param["type"] = None
            params.append(param)
        return_type = (
            self._get_name(node.returns) if getattr(node, "returns", None) else None
        )
        decorators = [self._get_name(d) for d in getattr(node, "decorator_list", [])]
        docstring = ast.get_docstring(node)
        is_async = isinstance(node, ast.AsyncFunctionDef)
        return FunctionInfo(
            name=node.name,
            parameters=params,
            return_type=return_type,
            docstring=docstring,
            decorators=decorators,
            is_async=is_async,
        )

    def _get_name(self, node):
        if node is None:
            return None
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_name(node.value)}[{self._get_name(node.slice)}]"
        elif isinstance(node, ast.Index):
            return self._get_name(node.value)
        elif isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Tuple):
            return ", ".join(self._get_name(elt) for elt in node.elts)
        return str(ast.dump(node))


# Patch ast nodes to add parent references for easier traversal
def _add_parents(node, parent=None):
    # If parent is None, this is the root (module), so use node as parent for its children
    actual_parent = parent if parent is not None else node
    for child in ast.iter_child_nodes(node):
        child.parent = actual_parent
        _add_parents(child, child)


def analyze_tree_with_parents(tree) -> dict:
    """Analyze an AST tree and extract parent relationships.

    Args:
        tree (ast.AST): The AST tree to analyze.
    """
    analyzer = CodeAnalyzer()
    return {
        "imports": analyzer._extract_imports(tree),
        "functions": analyzer._extract_functions(tree),
        "classes": analyzer._extract_classes(tree),
    }


def analyze_file_with_parents(file_path: str) -> dict:
    """Analyze a Python file and extract parent relationships from its AST.

    Args:
        file_path (str): Path to the Python file.
    """
    with open(file_path, "r") as f:
        content = f.read()
    tree = ast.parse(content)
    _add_parents(tree)
    return analyze_tree_with_parents(tree)

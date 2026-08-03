"""
Symbol Extractor Module for Project Astra.
Traverses Python AST trees to extract classes, functions, methods, imports, decorators, docstrings, and type hints.
"""

import ast
from typing import List, Dict, Any, Optional
from app.models.symbol import Symbol, SymbolType
from app.utils.logger import logger


class SymbolExtractor(ast.NodeVisitor):
    """
    AST NodeVisitor extracting code symbols from Python syntax trees.
    """

    def __init__(self, filepath: str = ""):
        self.filepath = filepath
        self.symbols: List[Symbol] = []
        self._current_class: Optional[str] = None

    def extract_symbols(self, tree: ast.AST) -> List[Symbol]:
        """Traverses tree and returns extracted Symbol list."""
        self.symbols.clear()
        self._current_class = None
        self.visit(tree)
        logger.debug(f"Extracted {len(self.symbols)} symbols from '{self.filepath}'.")
        return list(self.symbols)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.symbols.append(Symbol(
                name=alias.name,
                symbol_type=SymbolType.IMPORT,
                filepath=self.filepath,
                line_number=node.lineno,
                end_line_number=getattr(node, "end_lineno", node.lineno)
            ))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        module = node.module or ""
        for alias in node.names:
            full_name = f"{module}.{alias.name}" if module else alias.name
            self.symbols.append(Symbol(
                name=full_name,
                symbol_type=SymbolType.IMPORT,
                filepath=self.filepath,
                line_number=node.lineno,
                end_line_number=getattr(node, "end_lineno", node.lineno)
            ))
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        docstring = ast.get_docstring(node)
        decorators = [ast.unparse(d) for d in node.decorator_list] if hasattr(ast, "unparse") else []
        bases = [ast.unparse(b) for b in node.bases] if hasattr(ast, "unparse") else []

        sig = f"class {node.name}" + (f"({', '.join(bases)})" if bases else "")

        class_symbol = Symbol(
            name=node.name,
            symbol_type=SymbolType.CLASS,
            filepath=self.filepath,
            line_number=node.lineno,
            end_line_number=getattr(node, "end_lineno", node.lineno),
            docstring=docstring,
            signature=sig,
            decorators=decorators,
            parent_symbol=self._current_class
        )
        self.symbols.append(class_symbol)

        prev_class = self._current_class
        self._current_class = node.name
        self.generic_visit(node)
        self._current_class = prev_class

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._process_function(node, is_async=False)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._process_function(node, is_async=True)
        self.generic_visit(node)

    def _process_function(self, node: Any, is_async: bool) -> None:
        docstring = ast.get_docstring(node)
        decorators = [ast.unparse(d) for d in node.decorator_list] if hasattr(ast, "unparse") else []

        # Extract argument names and type hints
        args_list = []
        type_hints = {}
        for arg in node.args.args:
            args_list.append(arg.arg)
            if arg.annotation and hasattr(ast, "unparse"):
                type_hints[arg.arg] = ast.unparse(arg.annotation)

        if node.returns and hasattr(ast, "unparse"):
            type_hints["return"] = ast.unparse(node.returns)

        async_prefix = "async " if is_async else ""
        sig = f"{async_prefix}def {node.name}({', '.join(args_list)})"

        sym_type = SymbolType.METHOD if self._current_class else SymbolType.FUNCTION

        sym = Symbol(
            name=node.name,
            symbol_type=sym_type,
            filepath=self.filepath,
            line_number=node.lineno,
            end_line_number=getattr(node, "end_lineno", node.lineno),
            docstring=docstring,
            signature=sig,
            decorators=decorators,
            type_hints=type_hints,
            parent_symbol=self._current_class,
            is_async=is_async
        )
        self.symbols.append(sym)

"""
AST Parser Module for Project Astra.
Parses Python source code files into Abstract Syntax Trees using Python's native `ast` module.
"""

import ast
from typing import Optional, Tuple
from app.utils.logger import logger


class ASTParser:
    """
    Robust Abstract Syntax Tree (AST) parser for Python code files.
    """

    def parse_code(self, source_code: str, filename: str = "<unknown>") -> Tuple[Optional[ast.AST], Optional[str]]:
        """
        Parses source code string into an ast.AST object.

        Returns:
            Tuple[Optional[ast.AST], Optional[str]]: (ast_node, error_message)
        """
        if not source_code.strip():
            return None, "Empty source code string."

        try:
            tree = ast.parse(source_code, filename=filename)
            logger.debug(f"Successfully parsed AST for '{filename}'.")
            return tree, None
        except SyntaxError as e:
            err_msg = f"SyntaxError in '{filename}' at line {e.lineno}: {e.msg}"
            logger.warning(err_msg)
            return None, err_msg
        except Exception as e:
            err_msg = f"Failed to parse AST for '{filename}': {e}"
            logger.error(err_msg)
            return None, err_msg

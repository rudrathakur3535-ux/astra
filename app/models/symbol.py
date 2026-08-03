"""
Symbol Model for Project Astra.
Represents code symbols (classes, functions, methods, imports, variables, decorators).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid


class SymbolType(str, Enum):
    CLASS = "class"
    FUNCTION = "function"
    METHOD = "method"
    IMPORT = "import"
    VARIABLE = "variable"
    DECORATOR = "decorator"


@dataclass
class Symbol:
    """
    Represents an individual code symbol extracted via AST parsing.
    """
    name: str
    symbol_type: SymbolType
    filepath: str
    line_number: int
    end_line_number: int = 0
    docstring: Optional[str] = None
    signature: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    type_hints: Dict[str, str] = field(default_factory=dict)
    parent_symbol: Optional[str] = None
    is_async: bool = False
    symbol_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "symbol_id": self.symbol_id,
            "name": self.name,
            "symbol_type": self.symbol_type.value if isinstance(self.symbol_type, SymbolType) else self.symbol_type,
            "filepath": self.filepath,
            "line_number": self.line_number,
            "end_line_number": self.end_line_number,
            "docstring": self.docstring,
            "signature": self.signature,
            "decorators": self.decorators,
            "type_hints": self.type_hints,
            "parent_symbol": self.parent_symbol,
            "is_async": self.is_async
        }

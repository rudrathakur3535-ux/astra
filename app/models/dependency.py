"""
Dependency Model for Project Astra.
Represents import, inheritance, and invocation relationships between code entities.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional


class DependencyType(str, Enum):
    IMPORT = "import"
    INHERITANCE = "inheritance"
    CALL = "call"
    INSTANTIATION = "instantiation"


@dataclass
class DependencyEdge:
    """
    Represents a directed dependency edge between source and target code entities.
    """
    source: str
    target: str
    dep_type: DependencyType = DependencyType.IMPORT
    line_number: int = 0
    filepath: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "dep_type": self.dep_type.value if isinstance(self.dep_type, DependencyType) else self.dep_type,
            "line_number": self.line_number,
            "filepath": self.filepath
        }

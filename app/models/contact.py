"""
Contact Model for Project Astra.
Encapsulates contact information and communication channel preferences.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import uuid


@dataclass
class Contact:
    """
    Represents a contact entry in Astra's address book.
    """
    name: str
    email: str
    phone: Optional[str] = None
    preferred_channel: str = "email"
    notes: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    contact_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "contact_id": self.contact_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "preferred_channel": self.preferred_channel,
            "notes": self.notes,
            "tags": self.tags
        }

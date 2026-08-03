"""
Contacts Service Module for Project Astra.
Manages contact directory lookup and communication preferences.
"""

from typing import List, Optional, Dict, Any
from app.models.contact import Contact
from app.utils.logger import logger


class ContactsService:
    """
    Contact directory manager.
    """

    def __init__(self):
        self._contacts: Dict[str, Contact] = {}
        self._populate_demo_contacts()

    def _populate_demo_contacts(self) -> None:
        c1 = Contact(name="Alex Rivera", email="alex@astra.os", phone="+1-555-0192", preferred_channel="email", tags=["colleague"])
        c2 = Contact(name="Rudra Patel", email="rudra@astra.os", phone="+1-555-0100", preferred_channel="email", tags=["owner"])
        self._contacts[c1.email] = c1
        self._contacts[c2.email] = c2

    def get_contact_by_email(self, email: str) -> Optional[Contact]:
        return self._contacts.get(email)

    def search_contacts(self, query: str) -> List[Contact]:
        q = query.lower()
        return [
            c for c in self._contacts.values()
            if q in c.name.lower() or q in c.email.lower() or (c.phone and q in c.phone)
        ]

    def add_contact(self, contact: Contact) -> bool:
        self._contacts[contact.email] = contact
        logger.info(f"[ContactsService] Saved contact '{contact.name}' ({contact.email})")
        return True

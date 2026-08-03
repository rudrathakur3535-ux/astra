"""
Immutable Security Audit Logger for Project Astra OS.
Records, verifies, and exports immutable security audit records.
"""

from typing import List, Dict, Any, Optional
import time
from app.models.audit_record import AuditRecord


class AuditLogger:
    """
    Immutable Security Audit Trail Logger.
    """

    def __init__(self, max_records: int = 5000):
        self._max_records = max_records
        self._records: List[AuditRecord] = []

    def log_action(
        self,
        user_id: str,
        action: str,
        tool_name: str,
        resource: str,
        result: str,
        workflow_id: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None
    ) -> AuditRecord:
        """
        Records an immutable audit entry for a sensitive action.
        """
        record = AuditRecord(
            user_id=user_id,
            action=action,
            tool_name=tool_name,
            resource=resource,
            result=result,
            workflow_id=workflow_id,
            parameters=parameters or {}
        )
        self._records.append(record)

        if len(self._records) > self._max_records:
            self._records.pop(0)

        return record

    def query(
        self,
        user_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        action: Optional[str] = None,
        result: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Queries and filters audit records.
        """
        results = self._records

        if user_id:
            results = [r for r in results if r.user_id == user_id]

        if tool_name:
            results = [r for r in results if r.tool_name.lower() == tool_name.lower()]

        if action:
            results = [r for r in results if r.action.lower() == action.lower()]

        if result:
            results = [r for r in results if r.result.lower() == result.lower()]

        return [r.to_dict() for r in results[-limit:]]

    def verify_integrity(self, record: AuditRecord) -> bool:
        """
        Verifies SHA-256 signature integrity of an audit record.
        """
        expected_sig = record._generate_signature()
        return record.signature == expected_sig

    def get_all_records(self) -> List[Dict[str, Any]]:
        """Returns all audit records."""
        return [r.to_dict() for r in self._records]

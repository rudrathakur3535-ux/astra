"""
Session Manager for Project Astra OS.
Handles session token creation, expiration monitoring, and token revocation.
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass, field
import time
import uuid
from app.models.user_identity import UserIdentity


@dataclass
class Session:
    """Represents an active user session."""
    session_id: str
    token: str
    user_id: str
    username: str
    role: str
    created_at: float = field(default_factory=time.time)
    expires_at: float = field(default_factory=lambda: time.time() + 3600.0)  # Default 1 hour
    is_revoked: bool = False

    @property
    def is_valid(self) -> bool:
        return not self.is_revoked and time.time() < self.expires_at


class SessionManager:
    """
    Manages active user auth session tokens.
    """

    def __init__(self, default_ttl_seconds: float = 3600.0):
        self.default_ttl = default_ttl_seconds
        self._sessions_by_token: Dict[str, Session] = {}

    def create_session(self, user: UserIdentity, ttl_seconds: Optional[float] = None) -> Session:
        """
        Creates a new auth session for a user.
        """
        token = f"astrasess_{uuid.uuid4().hex}"
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl

        session = Session(
            session_id=session_id,
            token=token,
            user_id=user.user_id,
            username=user.username,
            role=user.role.value if hasattr(user.role, "value") else str(user.role),
            created_at=time.time(),
            expires_at=time.time() + ttl
        )
        self._sessions_by_token[token] = session
        return session

    def validate_session(self, token: str) -> Optional[Session]:
        """
        Validates an active session token.
        """
        session = self._sessions_by_token.get(token)
        if session and session.is_valid:
            return session
        return None

    def revoke_session(self, token: str) -> bool:
        """
        Revokes an active session token.
        """
        session = self._sessions_by_token.get(token)
        if session:
            session.is_revoked = True
            return True
        return False

    def cleanup_expired_sessions(self) -> int:
        """
        Removes expired or revoked sessions.
        """
        now = time.time()
        expired_tokens = [
            t for t, s in self._sessions_by_token.items() if s.is_revoked or now >= s.expires_at
        ]
        for t in expired_tokens:
            del self._sessions_by_token[t]
        return len(expired_tokens)

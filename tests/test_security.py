"""
Comprehensive Unit Test Suite for Security, Identity & Secret Management Platform.
"""

import pytest
import time
from unittest.mock import MagicMock

from app.models.user_identity import UserIdentity, UserRole
from app.models.permission import ActionType, ResourceScope, PermissionRule
from app.models.security_event import SecurityEvent, SecuritySeverity
from app.models.audit_record import AuditRecord
from app.security.identity_manager import IdentityManager
from app.security.authentication import AuthenticationEngine
from app.security.session_manager import SessionManager, Session
from app.security.authorization import AuthorizationEngine
from app.security.credential_store import CredentialStore
from app.security.secret_manager import SecretManager
from app.security.audit_logger import AuditLogger
from app.security.policy_engine import PolicyEngine


class TestIdentityAndRBAC:
    """Tests user identity creation, profiles, and roles."""

    def test_default_owner_user_creation(self):
        im = IdentityManager()
        owner = im.get_user("astra_owner")
        assert owner is not None
        assert owner.role == UserRole.OWNER
        assert owner.is_active is True

    def test_create_standard_and_guest_user(self):
        im = IdentityManager()
        user = im.create_user("alice", role=UserRole.STANDARD_USER, email="alice@test.com")
        guest = im.create_user("guest_user", role=UserRole.GUEST)

        assert user.role == UserRole.STANDARD_USER
        assert guest.role == UserRole.GUEST
        assert "read:public" in guest.permissions

    def test_deactivate_user(self):
        im = IdentityManager()
        user = im.create_user("bob", role=UserRole.STANDARD_USER)
        assert im.deactivate_user("bob") is True
        assert user.is_active is False


class TestAuthenticationAndSessions:
    """Tests authentication flows, password checks, and session management."""

    def test_password_authentication(self):
        auth = AuthenticationEngine()
        im = auth.identity_manager
        user = im.create_user("charlie", role=UserRole.STANDARD_USER)
        auth.register_credentials("charlie", "secure_pass_123")

        auth_user = auth.authenticate_password("charlie", "secure_pass_123")
        assert auth_user is not None
        assert auth_user.username == "charlie"

        invalid_auth = auth.authenticate_password("charlie", "wrong_pass")
        assert invalid_auth is None

    def test_api_key_authentication(self):
        auth = AuthenticationEngine()
        im = auth.identity_manager
        user = im.create_user("dev_user", role=UserRole.ADMIN)
        raw_key = "astrak_live_9988776655"
        auth.register_api_key(user.user_id, raw_key)

        authed = auth.authenticate_api_key(raw_key)
        assert authed is not None
        assert authed.user_id == user.user_id

        assert auth.authenticate_api_key("invalid_key") is None

    def test_session_lifecycle(self):
        sm = SessionManager(default_ttl_seconds=10.0)
        im = IdentityManager()
        user = im.get_user("astra_owner")

        session = sm.create_session(user)
        assert session.is_valid is True

        validated = sm.validate_session(session.token)
        assert validated is not None
        assert validated.user_id == user.user_id

        sm.revoke_session(session.token)
        assert sm.validate_session(session.token) is None


class TestAuthorizationEngine:
    """Tests authorization evaluation, rules, and wildcard permissions."""

    def test_owner_superuser_override(self):
        auth_engine = AuthorizationEngine()
        im = IdentityManager()
        owner = im.get_user("astra_owner")

        assert auth_engine.is_authorized(
            owner, ActionType.DELETE, ResourceScope("system", "*")
        ) is True

    def test_guest_restricted_access(self):
        auth_engine = AuthorizationEngine()
        im = IdentityManager()
        guest = im.create_user("guest_1", role=UserRole.GUEST)

        # Guest should fail high-risk execute action
        assert auth_engine.is_authorized(
            guest, ActionType.DELETE, ResourceScope("file", "config.json")
        ) is False

    def test_deactivated_user_denied(self):
        auth_engine = AuthorizationEngine()
        im = IdentityManager()
        user = im.create_user("inactive_user", role=UserRole.ADMIN)
        im.deactivate_user("inactive_user")

        assert auth_engine.is_authorized(
            user, ActionType.READ, ResourceScope("file", "*")
        ) is False


class TestSecretManagerAndCredentialStore:
    """Tests credential storage, secret retrieval, and key masking."""

    def test_credential_store_obfuscation(self):
        store = CredentialStore()
        store.set_credential("MY_KEY", "super_secret_val")

        retrieved = store.get_credential("MY_KEY")
        assert retrieved == "super_secret_val"

        store.delete_credential("MY_KEY")
        assert store.get_credential("MY_KEY") is None

    def test_secret_manager_masking(self):
        store = CredentialStore()
        sm = SecretManager(credential_store=store)
        sm.set_secret("TEST_API_KEY", "sk-1234567890abcdef")

        assert sm.get_secret("TEST_API_KEY") == "sk-1234567890abcdef"
        masked = sm.get_masked_secret("TEST_API_KEY")
        assert masked == "sk-***cdef"


class TestAuditLoggerAndPolicyEngine:
    """Tests immutable audit record generation, SHA-256 signatures, and policy evaluation."""

    def test_audit_record_signature_verification(self):
        logger = AuditLogger()
        record = logger.log_action(
            user_id="usr-123",
            action="delete_file",
            tool_name="file_manager",
            resource="/tmp/test.txt",
            result="APPROVED"
        )

        assert record.signature is not None
        assert logger.verify_integrity(record) is True

    def test_policy_engine_user_confirmation_approval(self):
        im = IdentityManager()
        owner = im.get_user("astra_owner")
        prompt_mock = MagicMock(return_value=True)

        engine = PolicyEngine()
        engine.set_prompt_callback(prompt_mock)

        allowed = engine.evaluate_action(
            user=owner,
            action_name="delete_file",
            resource="/workspace/data.csv",
            parameters={"file": "/workspace/data.csv"}
        )

        assert allowed is True
        prompt_mock.assert_called_once_with("delete_file", {"file": "/workspace/data.csv"})

    def test_policy_engine_user_confirmation_denial(self):
        im = IdentityManager()
        owner = im.get_user("astra_owner")
        prompt_mock = MagicMock(return_value=False)

        engine = PolicyEngine()
        engine.set_prompt_callback(prompt_mock)

        allowed = engine.evaluate_action(
            user=owner,
            action_name="run_terminal_command",
            resource="rm -rf /",
            parameters={"cmd": "rm -rf /"}
        )

        assert allowed is False
        records = engine.audit_logger.query(result="REJECTED_USER_DENIED")
        assert len(records) == 1

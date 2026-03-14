import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from database import db
from app import vault

def test_plaintext_env(monkeypatch):
    monkeypatch.setenv("TEST_SECRET", "plain123")
    val = vault.get_secret("TEST_SECRET")
    assert val == "plain123"

def test_default_when_missing(monkeypatch):
    monkeypatch.delenv("MISSING_SECRET", raising=False)
    val = vault.get_secret("MISSING_SECRET", default="fallback")
    assert val == "fallback"

def test_encrypt_decrypt(monkeypatch):
    secret = "SuperSecret123!"
    token = vault.encrypt_value(secret)
    # token should be in ENC(...) format
    assert token.startswith("ENC(") and token.endswith(")")
    # simulate env
    monkeypatch.setenv("ENC_TEST", token)
    val = vault.get_secret("ENC_TEST")
    assert val == secret

def test_invalid_token(monkeypatch):
    monkeypatch.setenv("BROKEN_SECRET", "ENC(invalidtoken)")
    with pytest.raises(RuntimeError):
        vault.get_secret("BROKEN_SECRET")
import pytest
from teemboom_chat import create_token

def test_create_token_valid():
    token = create_token("secret123", {"id": 1, "username": "Alice"})
    assert isinstance(token, str)
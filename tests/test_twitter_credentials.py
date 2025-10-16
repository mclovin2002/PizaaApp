import os
import importlib
import types

import pytest


def reload_module():
    return importlib.reload(importlib.import_module("twitter_credentials"))


def test_load_credentials_from_constants(monkeypatch):
    # Ensure env vars are absent
    for var in ["API_KEY", "API_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET"]:
        monkeypatch.delenv(var, raising=False)

    # Patch constants to non-placeholder values
    creds = importlib.import_module("twitter_credentials")
    monkeypatch.setattr(creds, "API_KEY", "k1", raising=False)
    monkeypatch.setattr(creds, "API_SECRET", "s1", raising=False)
    monkeypatch.setattr(creds, "ACCESS_TOKEN", "t1", raising=False)
    monkeypatch.setattr(creds, "ACCESS_TOKEN_SECRET", "ts1", raising=False)

    # reload not necessary as we patch attributes directly
    api_key, api_secret, access_token, access_token_secret = creds.load_credentials()
    assert (api_key, api_secret, access_token, access_token_secret) == ("k1", "s1", "t1", "ts1")


def test_load_credentials_from_env(monkeypatch):
    # Set env vars
    monkeypatch.setenv("API_KEY", "ek")
    monkeypatch.setenv("API_SECRET", "es")
    monkeypatch.setenv("ACCESS_TOKEN", "et")
    monkeypatch.setenv("ACCESS_TOKEN_SECRET", "ets")

    creds = reload_module()
    api_key, api_secret, access_token, access_token_secret = creds.load_credentials()
    assert (api_key, api_secret, access_token, access_token_secret) == ("ek", "es", "et", "ets")


@pytest.mark.parametrize(
    "env_vars",
    [
        {"API_KEY": "", "API_SECRET": "s", "ACCESS_TOKEN": "t", "ACCESS_TOKEN_SECRET": "ts"},
        {"API_KEY": "k", "API_SECRET": "", "ACCESS_TOKEN": "t", "ACCESS_TOKEN_SECRET": "ts"},
        {"API_KEY": "k", "API_SECRET": "s", "ACCESS_TOKEN": "", "ACCESS_TOKEN_SECRET": "ts"},
        {"API_KEY": "k", "API_SECRET": "s", "ACCESS_TOKEN": "t", "ACCESS_TOKEN_SECRET": ""},
        {"API_KEY": "YOUR_API_KEY", "API_SECRET": "s", "ACCESS_TOKEN": "t", "ACCESS_TOKEN_SECRET": "ts"},
    ],
)
def test_load_credentials_missing_or_placeholder(monkeypatch, env_vars):
    for var in ["API_KEY", "API_SECRET", "ACCESS_TOKEN", "ACCESS_TOKEN_SECRET"]:
        monkeypatch.delenv(var, raising=False)
    for k, v in env_vars.items():
        monkeypatch.setenv(k, v)

    creds = reload_module()
    with pytest.raises(ValueError):
        creds.load_credentials()

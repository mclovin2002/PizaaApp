import builtins
import importlib
from types import SimpleNamespace

import pytest


def import_fresh_tweet(monkeypatch, tweepy_stub=None, creds=None):
    if tweepy_stub is None:
        class TweepyError(Exception):
            pass
        tweepy_stub = SimpleNamespace(
            TweepyException=TweepyError,
            Unauthorized=type("Unauthorized", (TweepyError,), {}),
            Forbidden=type("Forbidden", (TweepyError,), {}),
            TooManyRequests=type("TooManyRequests", (TweepyError,), {}),
            OAuth1UserHandler=lambda *a, **k: SimpleNamespace(),
            API=lambda auth, wait_on_rate_limit=True: SimpleNamespace(
                verify_credentials=lambda: None,
                update_status=lambda status: None,
            ),
        )

    if creds is None:
        creds = SimpleNamespace(
            load_credentials=lambda: ("k", "s", "t", "ts")
        )

    monkeypatch.setitem(importlib.import_module("sys").modules, "tweepy", tweepy_stub)
    monkeypatch.setitem(importlib.import_module("sys").modules, "twitter_credentials", creds)

    if "twitter_utils" in importlib.import_module("sys").modules:
        del importlib.import_module("sys").modules["twitter_utils"]
    if "tweet" in importlib.import_module("sys").modules:
        del importlib.import_module("sys").modules["tweet"]
    # Provide a simple stub for twitter_utils used by tweet module
    tu = SimpleNamespace(
        get_api=lambda: None,
        compute_delay_seconds=lambda **kwargs: (0.0, "00:00"),
        read_tweets_from_file=lambda path: ["a", "b"],
    )
    monkeypatch.setitem(importlib.import_module("sys").modules, "twitter_utils", tu)
    return importlib.import_module("tweet")


def test_get_message_from_args(monkeypatch):
    tweet = import_fresh_tweet(monkeypatch)
    msg = tweet._get_message_from_argv_or_prompt(["tweet.py", "Hello", "World!"])
    assert msg == "Hello World!"


def test_get_message_from_prompt(monkeypatch):
    tweet = import_fresh_tweet(monkeypatch)
    monkeypatch.setattr(builtins, "input", lambda _: "Hi from prompt")
    msg = tweet._get_message_from_argv_or_prompt(["tweet.py"]) 
    assert msg == "Hi from prompt"


def test_post_tweet_success(monkeypatch):
    calls = {"update": 0, "verify": 0}

    class APIObj:
        def verify_credentials(self):
            calls["verify"] += 1

        def update_status(self, status):
            calls["update"] += 1
            assert status == "Test message"

    tweepy_stub = SimpleNamespace(
        TweepyException=Exception,
        Unauthorized=type("Unauthorized", (Exception,), {}),
        Forbidden=type("Forbidden", (Exception,), {}),
        TooManyRequests=type("TooManyRequests", (Exception,), {}),
        OAuth1UserHandler=lambda *a, **k: SimpleNamespace(),
        API=lambda *a, **k: APIObj(),
    )

    tweet = import_fresh_tweet(monkeypatch, tweepy_stub=tweepy_stub)
    tweet.post_tweet("Test message")
    assert calls["verify"] == 1
    assert calls["update"] == 1


def test_post_tweet_empty_raises(monkeypatch):
    tweet = import_fresh_tweet(monkeypatch)
    with pytest.raises(ValueError):
        tweet.post_tweet("")


def test_main_success(monkeypatch):
    tweepy_stub = SimpleNamespace(
        TweepyException=Exception,
        Unauthorized=type("Unauthorized", (Exception,), {}),
        Forbidden=type("Forbidden", (Exception,), {}),
        TooManyRequests=type("TooManyRequests", (Exception,), {}),
        OAuth1UserHandler=lambda *a, **k: SimpleNamespace(),
        API=lambda *a, **k: SimpleNamespace(
            verify_credentials=lambda: None,
            update_status=lambda status: None,
        ),
    )
    tweet = import_fresh_tweet(monkeypatch, tweepy_stub=tweepy_stub)
    rc = tweet.main(["tweet.py", "OK!"])
    assert rc == 0


def test_main_auth_error(monkeypatch):
    class Unauthorized(Exception):
        pass

    tweepy_stub = SimpleNamespace(
        TweepyException=Exception,
        Unauthorized=Unauthorized,
        Forbidden=type("Forbidden", (Exception,), {}),
        TooManyRequests=type("TooManyRequests", (Exception,), {}),
        OAuth1UserHandler=lambda *a, **k: SimpleNamespace(),
        API=lambda *a, **k: SimpleNamespace(
            verify_credentials=lambda: (_ for _ in ()).throw(Unauthorized("bad auth")),
            update_status=lambda status: None,
        ),
    )
    tweet = import_fresh_tweet(monkeypatch, tweepy_stub=tweepy_stub)
    rc = tweet.main(["tweet.py", "foo"])
    assert rc == 1


def test_main_rate_limit(monkeypatch):
    class TooManyRequests(Exception):
        pass

    tweepy_stub = SimpleNamespace(
        TweepyException=Exception,
        Unauthorized=type("Unauthorized", (Exception,), {}),
        Forbidden=type("Forbidden", (Exception,), {}),
        TooManyRequests=TooManyRequests,
        OAuth1UserHandler=lambda *a, **k: SimpleNamespace(),
        API=lambda *a, **k: SimpleNamespace(
            verify_credentials=lambda: None,
            update_status=lambda status: (_ for _ in ()).throw(TooManyRequests("limit")),
        ),
    )
    tweet = import_fresh_tweet(monkeypatch, tweepy_stub=tweepy_stub)
    rc = tweet.main(["tweet.py", "foo"])
    assert rc == 1


def test_main_no_message(monkeypatch):
    tweet = import_fresh_tweet(monkeypatch)
    # Simulate entering empty message
    monkeypatch.setattr(builtins, "input", lambda _: "")
    rc = tweet.main(["tweet.py"])  # will prompt and get empty
    assert rc == 1

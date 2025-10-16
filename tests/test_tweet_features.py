import importlib
from types import SimpleNamespace

import pytest


def fresh_tweet(monkeypatch):
    # Stub tweepy for import
    tweepy_stub = SimpleNamespace(
        TweepyException=Exception,
        Unauthorized=type("Unauthorized", (Exception,), {}),
        Forbidden=type("Forbidden", (Exception,), {}),
        TooManyRequests=type("TooManyRequests", (Exception,), {}),
    )
    monkeypatch.setitem(importlib.import_module("sys").modules, "tweepy", tweepy_stub)

    if "tweet" in importlib.import_module("sys").modules:
        del importlib.import_module("sys").modules["tweet"]
    return importlib.import_module("tweet")


def test_schedule_tweet_calls_post(monkeypatch, capsys):
    tweet = fresh_tweet(monkeypatch)
    called = {"post": 0}

    # Stub post_tweet
    monkeypatch.setattr(tweet, "post_tweet", lambda msg: called.__setitem__("post", called["post"] + 1))

    # Stub compute_delay_seconds to return immediate execution
    monkeypatch.setattr(tweet, "compute_delay_seconds", lambda **kwargs: (0.0, "10:00"))

    # Fake Timer that runs immediately
    class FakeTimer:
        def __init__(self, seconds, func):
            self.seconds = seconds
            self.func = func
            self.daemon = False

        def start(self):
            self.func()

        def cancel(self):
            pass

    monkeypatch.setattr(tweet.threading, "Timer", FakeTimer)

    t = tweet.schedule_tweet("Hello", delay_minutes=1)
    assert called["post"] == 1
    out = capsys.readouterr().out
    assert "Tweet scheduled for 10:00" in out
    assert "Tweet sent successfully!" in out


def test_bulk_post_from_file(monkeypatch, tmp_path):
    tweet = fresh_tweet(monkeypatch)
    p = tmp_path / "tweets.txt"
    p.write_text("\nFirst\n\nSecond\n", encoding="utf-8")

    # Stub post_tweet and sleep
    calls = []
    monkeypatch.setattr(tweet, "post_tweet", lambda msg: calls.append(msg))
    monkeypatch.setattr(tweet.time, "sleep", lambda s: None)

    tweet.bulk_post_from_file(str(p), delay_minutes=1)
    assert calls == ["First", "Second"]


def test_auto_reply_to_mentions_one_cycle(monkeypatch, tmp_path, capsys):
    tweet = fresh_tweet(monkeypatch)

    class User:
        def __init__(self, screen_name):
            self.screen_name = screen_name

    class Mention:
        def __init__(self, id, screen_name):
            self.id = id
            self.user = User(screen_name)

    mentions = [Mention(1, "alice"), Mention(2, "bob")]

    class APIStub:
        def __init__(self):
            self.replies = []

        def mentions_timeline(self, since_id=None, tweet_mode=None):
            return mentions

        def update_status(self, status, in_reply_to_status_id=None):
            self.replies.append((status, in_reply_to_status_id))

    api_stub = APIStub()

    # Monkeypatch get_api to return our stub
    monkeypatch.setitem(importlib.import_module("sys").modules, "twitter_utils", SimpleNamespace(get_api=lambda: api_stub))
    # Re-import tweet to pick up patched twitter_utils
    if "tweet" in importlib.import_module("sys").modules:
        del importlib.import_module("sys").modules["tweet"]
    tweet = importlib.import_module("tweet")

    # Make the loop exit by raising KeyboardInterrupt on first sleep
    monkeypatch.setattr(tweet.time, "sleep", lambda s: (_ for _ in ()).throw(KeyboardInterrupt()))

    state_file = tmp_path / "state.txt"
    tweet.auto_reply_to_mentions(1, "Thanks!", state_file=str(state_file))

    # Should have replied to both mentions and saved last ID
    assert api_stub.replies == [("@alice Thanks!", 1), ("@bob Thanks!", 2)]
    assert state_file.read_text(encoding="utf-8").strip() == "2"

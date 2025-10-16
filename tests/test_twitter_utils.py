import importlib
from types import SimpleNamespace
from datetime import datetime, timedelta

import pytest


@pytest.fixture(autouse=True)
def stub_tweepy(monkeypatch):
    """Ensure twitter_utils can import even if Tweepy isn't installed."""
    tweepy_stub = SimpleNamespace(
        OAuth1UserHandler=lambda *a, **k: SimpleNamespace(),
        API=lambda *a, **k: "API_OBJ",
    )
    monkeypatch.setitem(importlib.import_module("sys").modules, "tweepy", tweepy_stub)


def test_compute_delay_seconds_minutes(monkeypatch):
    utils = importlib.import_module("twitter_utils")
    secs, when = utils.compute_delay_seconds(delay_minutes=1)
    assert 50 <= secs <= 70  # roughly 60s
    assert len(when) == 5 and ":" in when


def test_compute_delay_seconds_time_future(monkeypatch):
    utils = importlib.import_module("twitter_utils")
    now = datetime.now()
    future = (now + timedelta(minutes=2)).strftime("%H:%M")
    secs, when = utils.compute_delay_seconds(time_hhmm=future)
    assert 60 <= secs <= 180
    assert when == future


def test_compute_delay_seconds_invalid(monkeypatch):
    utils = importlib.import_module("twitter_utils")
    with pytest.raises(ValueError):
        utils.compute_delay_seconds()
    with pytest.raises(ValueError):
        utils.compute_delay_seconds(delay_minutes=1, time_hhmm="12:00")
    with pytest.raises(ValueError):
        utils.compute_delay_seconds(time_hhmm="99:99")


def test_read_tweets_from_file_txt(tmp_path):
    utils = importlib.import_module("twitter_utils")
    p = tmp_path / "lines.txt"
    p.write_text("\nHello\n\nWorld\n", encoding="utf-8")
    out = utils.read_tweets_from_file(str(p))
    assert out == ["Hello", "World"]


def test_read_tweets_from_file_csv(tmp_path):
    utils = importlib.import_module("twitter_utils")
    p = tmp_path / "lines.csv"
    p.write_text("text,other\nhello,1\nworld,2\n", encoding="utf-8")
    out = utils.read_tweets_from_file(str(p))
    assert out == ["text", "hello", "world"]


def test_get_api(monkeypatch):
    utils = importlib.import_module("twitter_utils")

    # Stub credentials loader
    creds = SimpleNamespace(load_credentials=lambda: ("k", "s", "t", "ts"))
    monkeypatch.setitem(importlib.import_module("sys").modules, "twitter_credentials", creds)
    if "twitter_utils" in importlib.import_module("sys").modules:
        del importlib.import_module("sys").modules["twitter_utils"]
    utils = importlib.import_module("twitter_utils")

    api = utils.get_api()
    assert api == "API_OBJ"

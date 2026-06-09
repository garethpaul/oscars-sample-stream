import importlib
import os
import sys
import types
import unittest
from collections import UserDict


class FakeOAuthHandler:
    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.access_key = None
        self.access_secret = None

    def set_access_token(self, access_key, access_secret):
        self.access_key = access_key
        self.access_secret = access_secret


class FakeAPI:
    def __init__(self, auth):
        self.auth = auth


class FakeStreamListener:
    pass


class FakeStream:
    def __init__(self, auth, listener):
        self.auth = auth
        self.listener = listener
        self.filtered_track = None

    def filter(self, track):
        self.filtered_track = track


class FakeTweets:
    def __init__(self):
        self.documents = []

    def insert(self, document):
        self.documents.append(document)


class FakeMongoClient:
    def __init__(self, url):
        self.url = url
        self.TweetDB = types.SimpleNamespace(tweets=FakeTweets())


ENV_NAMES = [
    "consumer_key",
    "consumer_secret",
    "access_key",
    "access_secret",
    "MONGOHQ_URL",
    "CONSUMER_KEY",
    "CONSUMER_SECRET",
    "ACCESS_KEY",
    "ACCESS_SECRET",
    "MONGO_URL",
]


def load_sample_stream(overrides=None):
    values = {
        "consumer_key": "consumer",
        "consumer_secret": "consumer-secret",
        "access_key": "access",
        "access_secret": "access-secret",
        "MONGOHQ_URL": "mongodb://example.invalid/db",
    }
    if overrides:
        values.update(overrides)

    for key in ENV_NAMES:
        os.environ.pop(key, None)
    for key, value in values.items():
        os.environ[key] = value

    fake_tweepy = types.SimpleNamespace(
        OAuthHandler=FakeOAuthHandler,
        API=FakeAPI,
        StreamListener=FakeStreamListener,
        streaming=types.SimpleNamespace(Stream=FakeStream),
    )
    fake_pymongo = types.SimpleNamespace(MongoClient=FakeMongoClient)
    sys.modules["tweepy"] = fake_tweepy
    sys.modules["pymongo"] = fake_pymongo

    for module_name in ["config", "sample_stream"]:
        sys.modules.pop(module_name, None)
    return importlib.import_module("sample_stream")


class SampleStreamTest(unittest.TestCase):
    def test_start_stream_filters_for_oscars(self):
        sample_stream = load_sample_stream()

        stream = sample_stream.start_stream()

        self.assertEqual(["#oscars"], stream.filtered_track)

    def test_start_stream_trims_custom_track_terms(self):
        sample_stream = load_sample_stream()

        stream = sample_stream.start_stream([" #oscars2026 ", "", "best picture"])

        self.assertEqual(["#oscars2026", "best picture"], stream.filtered_track)

    def test_start_stream_accepts_single_custom_track_term(self):
        sample_stream = load_sample_stream()

        stream = sample_stream.start_stream(" #oscars2026 ")

        self.assertEqual(["#oscars2026"], stream.filtered_track)

    def test_start_stream_rejects_empty_custom_track_terms(self):
        sample_stream = load_sample_stream()

        with self.assertRaises(ValueError):
            sample_stream.start_stream([" ", 123, None])

    def test_start_stream_rejects_non_iterable_custom_track_terms(self):
        sample_stream = load_sample_stream()

        with self.assertRaises(ValueError):
            sample_stream.start_stream(123)

    def test_start_stream_rejects_mapping_custom_track_terms(self):
        sample_stream = load_sample_stream()

        with self.assertRaises(ValueError):
            sample_stream.start_stream({"track": "#oscars"})
        with self.assertRaises(ValueError):
            sample_stream.start_stream(UserDict({"track": "#oscars"}))

    def test_config_ignores_blank_env_values_and_uses_fallback(self):
        sample_stream = load_sample_stream(
            {
                "consumer_key": "   ",
                "CONSUMER_KEY": "consumer-fallback",
            }
        )

        self.assertEqual("consumer-fallback", sample_stream.config.consumer_key)

    def test_listener_inserts_minimal_tweet_document(self):
        sample_stream = load_sample_stream()
        client = FakeMongoClient("mongodb://example.invalid/db")
        listener = sample_stream.CustomStreamListener(api=object(), mongo_client=client)

        keep_streaming = listener.on_data(
            '{"text":"  hello oscars  ","user":{"screen_name":" academy "}}'
        )

        self.assertTrue(keep_streaming)
        self.assertEqual(1, len(client.TweetDB.tweets.documents))
        document = client.TweetDB.tweets.documents[0]
        self.assertEqual("hello oscars", document["text"])
        self.assertEqual("academy", document["screen_name"])
        self.assertIn("date", document)
        self.assertIsNotNone(document["date"].tzinfo)

    def test_listener_ignores_malformed_or_incomplete_payloads(self):
        sample_stream = load_sample_stream()
        client = FakeMongoClient("mongodb://example.invalid/db")
        listener = sample_stream.CustomStreamListener(api=object(), mongo_client=client)

        self.assertTrue(listener.on_data("not-json"))
        self.assertTrue(listener.on_data(None))
        self.assertTrue(listener.on_data("[]"))
        self.assertTrue(listener.on_data('{"text":"bad user","user":"academy"}'))
        self.assertTrue(listener.on_data('{"text":123,"user":{"screen_name":"academy"}}'))
        self.assertTrue(listener.on_data('{"text":"bad name","user":{"screen_name":123}}'))
        self.assertTrue(listener.on_data('{"text":"   ","user":{"screen_name":"academy"}}'))
        self.assertTrue(listener.on_data('{"text":"missing user"}'))
        self.assertEqual([], client.TweetDB.tweets.documents)


if __name__ == "__main__":
    unittest.main()

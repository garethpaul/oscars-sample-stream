import importlib
import json
import os
import sys
import types
import unittest
from collections import UserDict


class FakeStreamRule:
    def __init__(self, value=None, tag=None, id=None):
        self.value = value
        self.tag = tag
        self.id = id


class FakeStreamingClient:
    initial_rules = []
    add_errors = None

    def __init__(self, bearer_token, **options):
        self.bearer_token = bearer_token
        self.options = options
        self.deleted_rule_ids = []
        self.added_rules = []
        self.filter_options = None
        self.disconnected = False
        self.rules = list(self.initial_rules)
        self.rule_operations = []

    def get_rules(self):
        return types.SimpleNamespace(data=self.rules)

    def delete_rules(self, ids):
        self.deleted_rule_ids.extend(ids)
        self.rule_operations.append("delete")

    def add_rules(self, rules):
        self.added_rules.append(rules)
        self.rule_operations.append("add")
        return types.SimpleNamespace(
            data=None if self.add_errors else [FakeStreamRule(id="new", tag=rules.tag)],
            errors=self.add_errors,
        )

    def filter(self, **options):
        self.filter_options = options

    def disconnect(self):
        self.disconnected = True


class FakeTweets:
    def __init__(self):
        self.documents = []

    def insert_one(self, document):
        self.documents.append(document)


class FakeMongoClient:
    def __init__(self, url):
        self.url = url
        self.TweetDB = types.SimpleNamespace(tweets=FakeTweets())


class FalsyMongoClient(FakeMongoClient):
    def __bool__(self):
        return False


ENV_NAMES = ["bearer_token", "BEARER_TOKEN", "MONGOHQ_URL", "MONGO_URL"]


def load_sample_stream(overrides=None, rules=None):
    values = {
        "bearer_token": "bearer",
        "MONGOHQ_URL": "mongodb://example.invalid/db",
    }
    if overrides:
        values.update(overrides)

    for key in ENV_NAMES:
        os.environ.pop(key, None)
    for key, value in values.items():
        os.environ[key] = value

    FakeStreamingClient.initial_rules = list(rules or [])
    FakeStreamingClient.add_errors = None
    sys.modules["tweepy"] = types.SimpleNamespace(
        StreamingClient=FakeStreamingClient,
        StreamRule=FakeStreamRule,
    )
    sys.modules["pymongo"] = types.SimpleNamespace(MongoClient=FakeMongoClient)

    for module_name in ["config", "sample_stream"]:
        sys.modules.pop(module_name, None)
    return importlib.import_module("sample_stream")


def stream_payload(text="  hello oscars  ", author_id="42", username=" academy "):
    return json.dumps({
        "data": {"id": "100", "text": text, "author_id": author_id},
        "includes": {"users": [{"id": author_id, "username": username}]},
    })


class SampleStreamTest(unittest.TestCase):
    def test_start_stream_configures_tagged_oscars_rule(self):
        sample_stream = load_sample_stream()

        stream = sample_stream.start_stream()

        self.assertEqual("bearer", stream.bearer_token)
        self.assertEqual("#oscars", stream.added_rules[0].value)
        self.assertEqual("oscars-sample-stream", stream.added_rules[0].tag)
        self.assertEqual(
            {"expansions": ["author_id"], "user_fields": ["username"]},
            stream.filter_options,
        )

    def test_start_stream_replaces_only_worker_tagged_rules(self):
        rules = [
            FakeStreamRule(id="ours", tag="oscars-sample-stream"),
            FakeStreamRule(id="theirs", tag="another-worker"),
        ]
        sample_stream = load_sample_stream(rules=rules)

        stream = sample_stream.start_stream([" #oscars2026 ", "best picture"])

        self.assertEqual(["ours"], stream.deleted_rule_ids)
        self.assertEqual('#oscars2026 OR "best picture"', stream.added_rules[0].value)
        self.assertEqual(["add", "delete"], stream.rule_operations)

    def test_rejected_replacement_rule_preserves_existing_rule(self):
        rules = [FakeStreamRule(id="ours", tag="oscars-sample-stream")]
        sample_stream = load_sample_stream(rules=rules)
        FakeStreamingClient.add_errors = [{"message": "invalid rule"}]

        with self.assertRaisesRegex(RuntimeError, "rejected the replacement"):
            sample_stream.start_stream()

        stream = sample_stream.OscarsStream("bearer", mongo_client=FakeMongoClient("mongodb://example.invalid/db"))
        stream.rules = rules
        FakeStreamingClient.add_errors = [{"message": "invalid rule"}]
        with self.assertRaises(RuntimeError):
            sample_stream.sync_stream_rule(stream, "#oscars")
        self.assertEqual([], stream.deleted_rule_ids)
        self.assertEqual(["add"], stream.rule_operations)

    def test_rule_terms_are_literal_and_bounded(self):
        sample_stream = load_sample_stream()

        self.assertEqual('"oscars OR awards"', sample_stream.stream_rule_value(["oscars OR awards"]))
        self.assertEqual('"best \\"picture\\""', sample_stream.stream_rule_value(['best "picture"']))
        with self.assertRaisesRegex(ValueError, "larger than 512 bytes"):
            sample_stream.start_stream(["x" * 513])

    def test_start_stream_accepts_single_custom_track_term(self):
        sample_stream = load_sample_stream()

        stream = sample_stream.start_stream(" #oscars2026 ")

        self.assertEqual("#oscars2026", stream.added_rules[0].value)

    def test_start_stream_rejects_invalid_track_terms_before_client_setup(self):
        sample_stream = load_sample_stream()
        for key in ENV_NAMES:
            os.environ.pop(key, None)
        for invalid in ([" ", 123, None], 123, {"track": "#oscars"}, UserDict({"track": "#oscars"})):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                sample_stream.start_stream(invalid)

    def test_start_stream_rejects_more_than_one_hundred_track_terms(self):
        sample_stream = load_sample_stream()
        track_terms = ("term-{}".format(index) for index in range(101))

        with self.assertRaisesRegex(ValueError, "more than 100"):
            sample_stream.start_stream(track_terms)

    def test_config_ignores_blank_bearer_token_and_uses_fallback(self):
        sample_stream = load_sample_stream(
            {"bearer_token": "   ", "BEARER_TOKEN": "bearer-fallback"}
        )

        self.assertEqual("bearer-fallback", sample_stream.config.bearer_token())

    def test_stream_inserts_minimal_v2_tweet_document(self):
        sample_stream = load_sample_stream()
        client = FakeMongoClient("mongodb://example.invalid/db")
        stream = sample_stream.OscarsStream("bearer", mongo_client=client)

        stream.on_data(stream_payload())

        self.assertEqual(1, len(client.TweetDB.tweets.documents))
        document = client.TweetDB.tweets.documents[0]
        self.assertEqual("hello oscars", document["text"])
        self.assertEqual("academy", document["screen_name"])
        self.assertIsNotNone(document["date"].tzinfo)

    def test_stream_uses_explicit_falsy_mongo_client(self):
        sample_stream = load_sample_stream()
        client = FalsyMongoClient("mongodb://example.invalid/db")

        stream = sample_stream.OscarsStream("bearer", mongo_client=client)

        self.assertIs(client.TweetDB, stream.db)

    def test_stream_disconnects_on_rate_limits_only(self):
        sample_stream = load_sample_stream()
        stream = sample_stream.OscarsStream(
            "bearer", mongo_client=FakeMongoClient("mongodb://example.invalid/db")
        )

        stream.on_request_error(500)
        self.assertFalse(stream.disconnected)
        stream.on_request_error(429)
        self.assertTrue(stream.disconnected)

        stream.disconnected = False
        stream.on_request_error(420)
        self.assertTrue(stream.disconnected)

    def test_stream_ignores_malformed_or_incomplete_v2_payloads(self):
        sample_stream = load_sample_stream()
        client = FakeMongoClient("mongodb://example.invalid/db")
        stream = sample_stream.OscarsStream("bearer", mongo_client=client)
        invalid_payloads = [
            "not-json",
            None,
            "[]",
            '{"data":"tweet"}',
            stream_payload(text=123),
            stream_payload(author_id=123),
            stream_payload(username=123),
            stream_payload(text="   "),
            '{"data":{"text":"missing author"},"includes":{"users":[]}}',
            '{"data":{"text":"missing user","author_id":"42"},"includes":{"users":[]}}',
            '{"data":{"text":"wrong user","author_id":"42"},"includes":{"users":[{"id":"7","username":"academy"}]}}',
        ]

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                stream.on_data(payload)
        self.assertEqual([], client.TweetDB.tweets.documents)


if __name__ == "__main__":
    unittest.main()

import importlib
import io
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
    get_errors = None
    add_errors = None
    delete_errors = None
    instances = []

    def __init__(self, bearer_token, **options):
        self.bearer_token = bearer_token
        self.options = options
        self.deleted_rule_ids = []
        self.added_rules = []
        self.filter_options = None
        self.disconnected = False
        self.request_errors = []
        self.rules = list(self.initial_rules)
        self.rule_operations = []
        self.instances.append(self)

    def get_rules(self):
        return types.SimpleNamespace(
            data=None if self.get_errors else self.rules,
            errors=self.get_errors,
        )

    def delete_rules(self, ids):
        self.deleted_rule_ids.extend(ids)
        self.rule_operations.append("delete")
        return types.SimpleNamespace(
            data=None if self.delete_errors else {"deleted": list(ids)},
            errors=self.delete_errors,
        )

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

    def on_request_error(self, status_code):
        self.request_errors.append(status_code)


class FakeTweets:
    def __init__(self):
        self.documents = []

    def update_one(self, query, update, upsert=False):
        if not upsert:
            raise AssertionError("tweet persistence must use an upsert")
        fields = update["$set"]
        for index, existing in enumerate(self.documents):
            if all(existing.get(key) == value for key, value in query.items()):
                self.documents[index] = {**existing, **fields}
                return
        self.documents.append({**query, **fields})


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
    FakeStreamingClient.get_errors = None
    FakeStreamingClient.add_errors = None
    FakeStreamingClient.delete_errors = None
    FakeStreamingClient.instances = []
    sys.modules["tweepy"] = types.SimpleNamespace(
        StreamingClient=FakeStreamingClient,
        StreamRule=FakeStreamRule,
    )
    sys.modules["pymongo"] = types.SimpleNamespace(MongoClient=FakeMongoClient)

    for module_name in ["config", "sample_stream"]:
        sys.modules.pop(module_name, None)
    return importlib.import_module("sample_stream")


def stream_payload(
    text="  hello oscars  ",
    author_id="42",
    username=" academy ",
    tweet_id="100",
):
    return json.dumps({
        "data": {"id": tweet_id, "text": text, "author_id": author_id},
        "includes": {"users": [{"id": author_id, "username": username}]},
    })


class SampleStreamTest(unittest.TestCase):
    def test_stream_plan_matches_live_rule_and_filter_options(self):
        sample_stream = load_sample_stream()

        plan = sample_stream.stream_plan([" #oscars2026 ", "best picture"])

        self.assertEqual({
            "rule_tag": "oscars-sample-stream",
            "rule_value": '#oscars2026 OR "best picture"',
            "expansions": ["author_id"],
            "user_fields": ["username"],
        }, plan)

        stream = sample_stream.start_stream([" #oscars2026 ", "best picture"])
        self.assertEqual(plan["rule_value"], stream.added_rules[0].value)
        self.assertEqual(plan["rule_tag"], stream.added_rules[0].tag)
        self.assertEqual({
            "expansions": plan["expansions"],
            "user_fields": plan["user_fields"],
        }, stream.filter_options)

    def test_dry_run_returns_default_plan_without_credentials_or_clients(self):
        sample_stream = load_sample_stream()
        for key in ENV_NAMES:
            os.environ.pop(key, None)

        def unexpected_client(*args, **kwargs):
            self.fail("dry run must not construct a Twitter/X or MongoDB client")

        sample_stream.create_stream = unexpected_client

        self.assertEqual({
            "rule_tag": "oscars-sample-stream",
            "rule_value": "#oscars",
            "expansions": ["author_id"],
            "user_fields": ["username"],
        }, sample_stream.start_stream(dry_run=True))

    def test_main_dry_run_emits_stable_json_for_repeated_track_terms(self):
        sample_stream = load_sample_stream()
        for key in ENV_NAMES:
            os.environ.pop(key, None)
        output = io.StringIO()

        result = sample_stream.main(
            ["--dry-run", "--track-term", " #oscars2026 ", "--track-term", "best picture"],
            output=output,
        )

        expected = {
            "rule_tag": "oscars-sample-stream",
            "rule_value": '#oscars2026 OR "best picture"',
            "expansions": ["author_id"],
            "user_fields": ["username"],
        }
        self.assertEqual(expected, result)
        self.assertEqual(json.dumps(expected, sort_keys=True) + "\n", output.getvalue())

    def test_main_without_dry_run_preserves_live_startup(self):
        sample_stream = load_sample_stream()

        stream = sample_stream.main(["--track-term", "#oscars2026"])

        self.assertEqual("#oscars2026", stream.added_rules[0].value)
        self.assertEqual(
            {"expansions": ["author_id"], "user_fields": ["username"]},
            stream.filter_options,
        )

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

    def test_start_stream_reuses_single_matching_worker_rule(self):
        rules = [
            FakeStreamRule(
                value="#oscars", tag="oscars-sample-stream", id="worker-current"
            ),
            FakeStreamRule(value="#other", tag="another-worker", id="unrelated"),
        ]
        sample_stream = load_sample_stream(rules=rules)

        stream = sample_stream.start_stream()

        self.assertEqual([], stream.rule_operations)
        self.assertEqual([], stream.added_rules)
        self.assertEqual([], stream.deleted_rule_ids)
        self.assertEqual(
            {"expansions": ["author_id"], "user_fields": ["username"]},
            stream.filter_options,
        )

    def test_start_stream_reuses_one_duplicate_matching_worker_rule(self):
        rules = [
            FakeStreamRule(value="#oscars", tag="oscars-sample-stream", id="first"),
            FakeStreamRule(value="#oscars", tag="oscars-sample-stream", id="second"),
        ]
        sample_stream = load_sample_stream(rules=rules)

        stream = sample_stream.start_stream()

        self.assertEqual(["delete"], stream.rule_operations)
        self.assertEqual(["second"], stream.deleted_rule_ids)
        self.assertEqual([], stream.added_rules)

    def test_start_stream_reuses_matching_rule_while_deleting_stale_rule(self):
        rules = [
            FakeStreamRule(value="#oscars2025", tag="oscars-sample-stream", id="stale"),
            FakeStreamRule(value="#oscars", tag="oscars-sample-stream", id="current"),
            FakeStreamRule(value="#other", tag="another-worker", id="unrelated"),
        ]
        sample_stream = load_sample_stream(rules=rules)

        stream = sample_stream.start_stream()

        self.assertEqual(["delete"], stream.rule_operations)
        self.assertEqual(["stale"], stream.deleted_rule_ids)
        self.assertEqual([], stream.added_rules)
        self.assertEqual(
            {"expansions": ["author_id"], "user_fields": ["username"]},
            stream.filter_options,
        )

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

    def test_rule_list_error_aborts_before_remote_mutation(self):
        sample_stream = load_sample_stream()
        FakeStreamingClient.get_errors = [{"message": "authorization failed"}]

        with self.assertRaisesRegex(RuntimeError, "could not list existing"):
            sample_stream.start_stream()

        stream = FakeStreamingClient.instances[-1]
        self.assertEqual([], stream.rule_operations)
        self.assertEqual([], stream.added_rules)
        self.assertEqual([], stream.deleted_rule_ids)
        self.assertIsNone(stream.filter_options)
        self.assertEqual([], stream.db.tweets.documents)

    def test_rule_delete_error_aborts_before_filter_start(self):
        worker_rule = FakeStreamRule(
            value="#oscars2025", tag="oscars-sample-stream", id="worker-old"
        )
        sample_stream = load_sample_stream(rules=[worker_rule])
        FakeStreamingClient.delete_errors = [{"message": "delete rejected"}]

        with self.assertRaisesRegex(RuntimeError, "could not delete existing"):
            sample_stream.start_stream()

        stream = FakeStreamingClient.instances[-1]
        self.assertEqual(["add", "delete"], stream.rule_operations)
        self.assertEqual(["worker-old"], stream.deleted_rule_ids)
        self.assertEqual(1, len(stream.added_rules))
        self.assertIsNone(stream.filter_options)
        self.assertEqual([], stream.db.tweets.documents)

    def test_matching_rule_cleanup_error_aborts_without_adding_or_filtering(self):
        rules = [
            FakeStreamRule(value="#oscars", tag="oscars-sample-stream", id="current"),
            FakeStreamRule(value="#oscars2025", tag="oscars-sample-stream", id="stale"),
        ]
        sample_stream = load_sample_stream(rules=rules)
        FakeStreamingClient.delete_errors = [{"message": "delete rejected"}]

        with self.assertRaisesRegex(RuntimeError, "could not delete existing"):
            sample_stream.start_stream()

        stream = FakeStreamingClient.instances[-1]
        self.assertEqual(["delete"], stream.rule_operations)
        self.assertEqual(["stale"], stream.deleted_rule_ids)
        self.assertEqual([], stream.added_rules)
        self.assertIsNone(stream.filter_options)

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

    def test_stream_persists_minimal_v2_tweet_document(self):
        sample_stream = load_sample_stream()
        client = FakeMongoClient("mongodb://example.invalid/db")
        stream = sample_stream.OscarsStream("bearer", mongo_client=client)

        stream.on_data(stream_payload())

        self.assertEqual(1, len(client.TweetDB.tweets.documents))
        document = client.TweetDB.tweets.documents[0]
        self.assertEqual("100", document["_id"])
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

    def test_stream_reports_request_errors_through_tweepy(self):
        sample_stream = load_sample_stream()
        stream = sample_stream.OscarsStream(
            "bearer", mongo_client=FakeMongoClient("mongodb://example.invalid/db")
        )

        stream.on_request_error(500)
        stream.on_request_error(429)

        self.assertEqual([500, 429], stream.request_errors)

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
            stream_payload(tweet_id=123),
            stream_payload(tweet_id="   "),
            stream_payload(text="   "),
            '{"data":{"text":"missing author"},"includes":{"users":[]}}',
            '{"data":{"text":"missing user","author_id":"42"},"includes":{"users":[]}}',
            # This payload must carry an id. Without one, on_data bails at the
            # tweet_id guard before the author-id match is ever consulted, so the
            # case cannot discriminate: dropping `or user.get("id") != author_id`
            # left the whole suite green while the mutant attributed author 42's
            # tweet to user 7's username.
            '{"data":{"id":"900","text":"wrong user","author_id":"42"},'
            '"includes":{"users":[{"id":"7","username":"academy"}]}}',
        ]

        for payload in invalid_payloads:
            with self.subTest(payload=payload):
                stream.on_data(payload)
        self.assertEqual([], client.TweetDB.tweets.documents)

    def test_stream_replays_replace_the_same_tweet_document(self):
        sample_stream = load_sample_stream()
        client = FakeMongoClient("mongodb://example.invalid/db")
        stream = sample_stream.OscarsStream("bearer", mongo_client=client)

        stream.on_data(stream_payload())
        client.TweetDB.tweets.documents[0]["moderation_state"] = "reviewed"
        stream.on_data(stream_payload(text=" updated winner ", username=" host "))

        self.assertEqual(1, len(client.TweetDB.tweets.documents))
        document = client.TweetDB.tweets.documents[0]
        self.assertEqual("100", document["_id"])
        self.assertEqual("updated winner", document["text"])
        self.assertEqual("host", document["screen_name"])
        self.assertEqual("reviewed", document["moderation_state"])

    def test_stream_persists_distinct_tweet_ids_separately(self):
        sample_stream = load_sample_stream()
        client = FakeMongoClient("mongodb://example.invalid/db")
        stream = sample_stream.OscarsStream("bearer", mongo_client=client)

        stream.on_data(stream_payload(tweet_id="100"))
        stream.on_data(stream_payload(tweet_id="101", text=" second tweet "))

        self.assertEqual(
            {"100", "101"},
            {document["_id"] for document in client.TweetDB.tweets.documents},
        )


if __name__ == "__main__":
    unittest.main()

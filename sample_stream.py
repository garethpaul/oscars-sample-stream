import argparse
import datetime
import json
import re
import sys
from collections.abc import Mapping

import pymongo
import tweepy

import config


TRACK_TERMS = ["#oscars"]
MAX_TRACK_TERMS = 100
MAX_RULE_LENGTH = 512
RULE_TAG = "oscars-sample-stream"
HASHTAG = re.compile(r"^#[A-Za-z0-9_]+$")


def clean_required_text(value):
    if not isinstance(value, str):
        return None
    value = value.strip()
    return value or None


def clean_track_terms(track_terms):
    if track_terms is None:
        return list(TRACK_TERMS)
    if isinstance(track_terms, str):
        track_terms = [track_terms]
    elif isinstance(track_terms, Mapping):
        track_terms = []
    else:
        try:
            iter(track_terms)
        except TypeError:
            track_terms = [track_terms]
    cleaned = []
    for index, term in enumerate(track_terms):
        if index >= MAX_TRACK_TERMS:
            raise ValueError("track_terms must not include more than 100 values")
        clean_term = clean_required_text(term)
        if clean_term:
            cleaned.append(clean_term)
    if not cleaned:
        raise ValueError("track_terms must include at least one non-empty string")
    return cleaned


def stream_rule_value(track_terms):
    terms = []
    for term in track_terms:
        if HASHTAG.fullmatch(term):
            terms.append(term)
        else:
            escaped = term.replace("\\", "\\\\").replace('"', '\\"')
            terms.append('"{}"'.format(escaped))
    value = " OR ".join(terms)
    if len(value.encode("utf-8")) > MAX_RULE_LENGTH:
        raise ValueError("track_terms produce a stream rule larger than 512 bytes")
    return value


def stream_plan(track_terms=None):
    cleaned_track_terms = clean_track_terms(track_terms)
    return {
        "rule_tag": RULE_TAG,
        "rule_value": stream_rule_value(cleaned_track_terms),
        "expansions": ["author_id"],
        "user_fields": ["username"],
    }


def tagged_rule_ids(rules):
    return [rule.id for rule in rules or [] if rule.tag == RULE_TAG]


def sync_stream_rule(stream, rule_value):
    listed_rules = stream.get_rules()
    if listed_rules.errors:
        raise RuntimeError("Twitter/X could not list existing stream rules")
    current = listed_rules.data or []
    existing_ids = tagged_rule_ids(current)
    result = stream.add_rules(tweepy.StreamRule(value=rule_value, tag=RULE_TAG))
    if result.errors or not result.data:
        raise RuntimeError("Twitter/X rejected the replacement stream rule")
    if existing_ids:
        delete_result = stream.delete_rules(existing_ids)
        if delete_result.errors:
            raise RuntimeError("Twitter/X could not delete existing stream rules")


def expanded_username(payload, author_id):
    includes = payload.get("includes") or {}
    if not isinstance(includes, dict):
        return None
    users = includes.get("users") or []
    if not isinstance(users, list):
        return None
    for user in users:
        if not isinstance(user, dict) or user.get("id") != author_id:
            continue
        return clean_required_text(user.get("username"))
    return None


class OscarsStream(tweepy.StreamingClient):
    def __init__(self, bearer_token, mongo_client=None):
        super().__init__(bearer_token, wait_on_rate_limit=False, max_retries=3)
        client = (
            mongo_client
            if mongo_client is not None
            else pymongo.MongoClient(config.mongo_url())
        )
        self.db = client.TweetDB

    def on_data(self, raw_data):
        try:
            payload = json.loads(raw_data)
        except (TypeError, ValueError):
            return
        if not isinstance(payload, dict):
            return

        tweet = payload.get("data") or {}
        if not isinstance(tweet, dict):
            return
        text = clean_required_text(tweet.get("text"))
        author_id = clean_required_text(tweet.get("author_id"))
        username = expanded_username(payload, author_id)
        if not text or not author_id or not username:
            return

        self.db.tweets.insert_one({
            "text": text,
            "date": datetime.datetime.now(datetime.timezone.utc),
            "screen_name": username,
        })

    def on_request_error(self, status_code):
        if status_code in (420, 429):
            self.disconnect()


def create_stream(mongo_client=None):
    return OscarsStream(config.bearer_token(), mongo_client=mongo_client)


def start_stream(track_terms=None, mongo_client=None, dry_run=False):
    plan = stream_plan(track_terms)
    if dry_run:
        return plan

    stream = create_stream(mongo_client=mongo_client)
    sync_stream_rule(stream, plan["rule_value"])
    stream.filter(
        expansions=plan["expansions"],
        user_fields=plan["user_fields"],
    )
    return stream


def main(argv=None, output=None):
    parser = argparse.ArgumentParser(description="Run the Oscars API v2 stream worker")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "print the normalized stream rule without reading credentials "
            "or creating clients"
        ),
    )
    parser.add_argument(
        "--track-term",
        action="append",
        dest="track_terms",
        help="stream term to include; repeat for multiple terms",
    )
    args = parser.parse_args(argv)
    result = start_stream(track_terms=args.track_terms, dry_run=args.dry_run)
    if args.dry_run:
        print(
            json.dumps(result, sort_keys=True),
            file=output if output is not None else sys.stdout,
        )
    return result


if __name__ == "__main__":
    main()

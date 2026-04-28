import json
import os

import requests
import yaml

from requests_oauthlib import OAuth1
from functools import wraps


def auth(filename="~/.twitter-keys.yaml"):
    def inner_function(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            pass
        return wrapper
    return inner_function


class API:
    _protocol: str = "https:/"
    _host: str = "api.twitter.com"
    _version: str = "2"
    _product: str = None
    _endpoint: str = None
    _has_params: bool = None
    _pagination: bool = False
    _params: dict = {}
    _stream: bool = None
    _data: dict = None
    _exclude: list = []

    @auth()
    def api(
        self,
        method: str,
        endpoint: str = None,
        data: dict = None,
        stream: bool = None,
        params: dict = None,
        **kwargs,
    ) -> json:
        pass

    def _query(self) -> dict:
        pass

    def connect(self) -> dict:
        pass


class FilteredStream(API):
    """
    Endpoint: /2/tweets/search/stream
    replaces legacy endpoint v1.1 statuses/filter
    """

    _product = "tweets"
    _endpoint = "search/stream"
    _stream = True
    _has_params = True

    def add_rule(self, data: dict) -> json:
        """Add or Remove upto 25 rules.
        /2/tweets/search/stream/rules

        List of Rules: (https://developer.twitter.com/en/docs/
        twitter-api/tweets/filtered-stream/integrate/build-a-rule)

        :params data: a dict with a list of rules
        :return: json

        Usage:

        stream = FilteredStream()
        rules = {
            "add": [
                {"value": "dog has: images", "tag": "dog pictures"}
            ]
        }
        stream.add_rule(data=rules)
        """
        pass

    def get_rules(self) -> json:
        """Retrieve your stream's rules
        /2/tweets/search/stream/rules
        :return: json
        """
        pass

    def delete_rule(self, data: dict):
        """Add or Remove upto 25 rules.
        /2/tweets/search/stream/rules

        List of Rules: (https://developer.twitter.com/en/docs/
        twitter-api/tweets/filtered-stream/integrate/build-a-rule)

        :params data: a dict with a list rule Ids
        :return: json

        Usage:

        stream = FilteredStream()
        rules = {
            "delete": {
                "ids": ['1331486534579589120'] # example id
            }
        }
        """
        pass

    def delete_all_rules(self) -> json:
        """Deletes all your rules automatically"""
        pass


class SampledStream(API):
    """Endpoint: /2/tweets/sample/stream
    Replacement for: v1.1 statuses/sample

    Subclasses the API class. Overrides variables
    `_product`, `_endpoint`, '_has_params', and
    '_stream'. The inherited `connect()` method
    from the super class does the streaming.

    The inherited connect method also helps in
    evaluating and constructing queries for sampled
    stream.

    List of query parameters
    (https://developer.twitter.com/en/docs/twitter-api/
    tweets/sampled-stream/api-reference/get-tweets-sample-stream)


    Usage:

    Name the query parameter and assign their values in a list.
    The `connect()` method recognizes the query parameters and
    and starts streaming.


    class Stream(SampledStream):
        user_fields = ['name', 'location', 'public_metrics']
        expansions = ['author_id']

    stream = Stream()

    for tweets in stream.connect():
        print(json.dumps(tweets, indent=4, sort_keys=True)))


    """

    _product = "tweets"
    _endpoint = "sample/stream"
    _has_params = True
    _stream = True


class RecentSearch(API):
    """Endpoint: /2/tweets/search/recent
    Legacy endpoint: v1.1 search/tweets

    Behaves the same way as SampledStream.

    List of query parameters
    (https://developer.twitter.com/en/docs/twitter-api/
     tweets/search/api-reference/get-tweets-search-recent)

    """

    _product = "tweets"
    _endpoint = "search/recent"
    _has_params = True
    _stream = True
    _exclude = [
        "end_time",
        "max_results",
        "next_token",
        "since_id",
        "start_time",
        "until_id",
    ]
    _pagination = True


class TweetLookUp(API):
    """Endpoint: /2/tweets
    Legacy endpoint: v1.1 statuses/show, v1.1 status/lookup

    List of query parameters:
    (https://developer.twitter.com/en/docs/twitter-api/tweets/lookup/api-reference)
    """

    @auth()
    def get(self, **kwargs) -> json:
        pass


class UserLookUp(API):
    """Endpoint /2/users
    Legacy Endpoint v1.1 users/lookup
    """

    def _query(self) -> dict:
        pass

    @auth()
    def get(
        self,
        endpoint: str = "https://api.twitter.com/2/users",
        query_params=True,
        **kwargs,
    ) -> json:
        pass

    def get_by_usernames(
        self, endpoint: str = "https://api.twitter.com/2/users/by", query_params=True
    ) -> json:
        pass

    def get_details_by_username(
        self,
        data: str,
        endpoint: str = "https://api.twitter.com/2/users/by/username",
        query_params=True,
    ):
        pass

    @auth()
    def followers(self, username, **kwargs):
        pass


def hide_replies(tweet: str, hidden: dict) -> json:
    """https://api.twitter.com/2/tweets/:id/hidden
    Hides specific tweets from a conversation
    :params: tweet: str = url  of the tweet to hide
    :params: hidden: dict = {"hidden: True}

    :returns json

    Usage:

    hide_replies(
        tweet = 'https://twitter.com/saadmanrafat_/status/1328288598106443776',
        {"hidden": True}
    )

    response =
    {
        "data": {
            "hidden": true
        }
    }
    """
    try:
        with open(os.path.expanduser("~/.twitter-keys.yaml")) as credentials:
            credentials = yaml.safe_load(credentials)["keys"]
    except (FileNotFoundError, KeyError) as e:
        raise e

    auth = OAuth1(
        client_key=credentials["consumer_key"],
        client_secret=credentials["consumer_secret"],
        resource_owner_key=credentials["access_token"],
        resource_owner_secret=credentials["access_token_secret"],
        signature_type="auth_header",
    )
    tweet_id = tweet.split("/")[-1]
    response = requests.put(
        url=f"https://api.twitter.com/2/tweets/{tweet_id}/hidden",
        headers={"Content-Type": "application/json"},
        auth=auth,
        data=json.dumps(hidden),
    )
    return json.dumps(response.json(), indent=4)

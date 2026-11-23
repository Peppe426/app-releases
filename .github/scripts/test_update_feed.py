import base64
import json
import unittest
from urllib.error import HTTPError
from unittest.mock import patch

import update_feed


class AndroidFeedTests(unittest.TestCase):
    def setUp(self):
        self.apk = {
            "name": "Hemloop-Android.apk", "state": "uploaded", "size": 123,
            "digest": "sha256:" + "a" * 64,
        }
        self.release = {"draft": False, "prerelease": False, "assets": [self.apk]}

    @patch.object(update_feed, "github")
    def test_first_hemloop_release_creates_only_its_android_feed(self, github):
        github.side_effect = [self.release, HTTPError("", 404, "Not found", {}, None), {}]
        update_feed.update_feed("hemloop-v0.1.11")
        release_call, existing, write = github.call_args_list
        self.assertEqual(release_call.args, ("releases/tags/hemloop-v0.1.11",))
        self.assertEqual(existing.args, ("contents/products/hemloop/android.json?ref=main",))
        path, change = write.args
        self.assertEqual(path, "contents/products/hemloop/android.json")
        self.assertEqual(json.loads(base64.b64decode(change["content"])), {
            "version": "0.1.11", "asset": "Hemloop-Android.apk", "size": 123, "sha256": "a" * 64,
        })

    @patch.object(update_feed, "github")
    def test_older_release_cannot_roll_back_feed(self, github):
        current = {"version": "0.1.12", "asset": "Hemloop-Android.apk", "size": 234, "sha256": "b" * 64}
        github.side_effect = [self.release, {"content": base64.b64encode(json.dumps(current).encode())}]
        update_feed.update_feed("hemloop-v0.1.11")
        self.assertEqual(github.call_count, 2)

    @patch.object(update_feed, "github")
    def test_hemloop_asset_cannot_advance_another_product(self, github):
        github.return_value = self.release
        with self.assertRaisesRegex(ValueError, "No supported installer"):
            update_feed.update_feed("meetinghand-v0.1.11")
        github.assert_called_once()

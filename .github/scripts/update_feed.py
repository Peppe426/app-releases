"""Advance each platform feed that has an installer in a stable release."""

import base64
import json
import os
import re
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen


def github(path, payload=None):
    request = Request(
        f"https://api.github.com/repos/{os.environ['GITHUB_REPOSITORY']}/{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ['GH_TOKEN']}",
            "User-Agent": "app-releases-feed",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload).encode() if payload is not None else None,
        method="PUT" if payload is not None else "GET",
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def version_tuple(version):
    return tuple(int(part) for part in version.split("."))


def update_feed(tag):
    release = github(f"releases/tags/{quote(tag, safe='')}")
    if release["draft"] or release["prerelease"]:
        print("Only stable releases advance the feed.")
        return

    match = re.fullmatch(r"([a-z0-9]+(?:-[a-z0-9]+)*)-v((?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*)){2})", tag)
    if not match:
        raise ValueError("Use a product tag such as journeydeck-v1.3.0.")
    product, version = match.groups()
    stem = f"{product}-setup-win-x64"
    names = {stem + ".exe", stem + ".msix"}
    uploaded = [a for a in release["assets"] if a["state"] == "uploaded"]
    windows = [a for a in uploaded if a["name"].lower() in names]
    android = [a for a in uploaded if product == "meetinghand" and a["name"] == "MeetingHand-Android.apk"]
    if len(windows) > 1 or len(android) > 1:
        raise ValueError("Publish one installer per platform.")
    if not windows and not android:
        raise ValueError(f"No supported installer was uploaded for {product}.")
    if windows:
        publish_asset(product, version, "windows-x64", windows[0])
    if android:
        publish_asset(product, version, "android", android[0])


def publish_asset(product, version, platform, asset):
    digest = re.fullmatch(r"sha256:([0-9a-f]{64})", asset.get("digest") or "")
    if not digest or asset["size"] <= 0:
        raise ValueError("GitHub must report a SHA-256 digest and a positive size for the installer.")
    manifest = {"version": version, "asset": asset["name"], "sha256": digest[1], "size": asset["size"]}
    path = f"contents/products/{product}/{platform}.json"

    # Two releases can finish out of order. Re-read the version on a conflicting write.
    for attempt in range(3):
        change = {
            "branch": "main",
            "message": f"release({product}): publish {platform} {version}",
            "content": base64.b64encode((json.dumps(manifest, indent=2) + "\n").encode()).decode(),
        }
        try:
            entry = github(path + "?ref=main")
        except HTTPError as error:
            if error.code != 404:
                raise
        else:
            current = json.loads(base64.b64decode(entry["content"]))
            if version_tuple(current["version"]) > version_tuple(version) or current == manifest:
                print(f"{product} {platform} already advertises {current['version']}.")
                return
            if current["version"] == version:
                raise ValueError("The installer changed for an existing version. Publish a new version.")
            if current["asset"] != asset["name"]:
                raise ValueError(f"Keep the published installer filename {current['asset']!r} for this product.")
            change["sha"] = entry["sha"]
        try:
            github(path, change)
            print(f"{product} now advertises {platform} {version}.")
            return
        except HTTPError as error:
            if error.code not in (409, 422) or attempt == 2:
                raise


if __name__ == "__main__":
    update_feed(os.environ["RELEASE_TAG"])

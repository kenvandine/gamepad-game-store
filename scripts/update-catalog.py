#!/usr/bin/env python3
"""Regenerate catalog.json from static game metadata and live Snap Store info.

Mirrors kenvandine/nimbus-app-store's scripts/update-catalog.py, but reads
version/channel/confinement from the Snap Store's public API
(api.snapcraft.io) instead of GitHub releases, since every game here is
expected to be published to the store rather than side-loaded.
"""

import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

STORE_BASE_URL = "https://raw.githubusercontent.com/kenvandine/gamepad-game-store/main"
SNAP_STORE_API = "https://api.snapcraft.io/v2/snaps/info/{name}"
REPO_ROOT = Path(__file__).parent.parent


def store_info(name):
    """Look up the current stable-channel version/confinement for a snap.

    Returns None (not fatal - see main()) if the snap has no stable release
    yet, or the store is unreachable (e.g. no network in a local dev run).
    """
    req = urllib.request.Request(
        SNAP_STORE_API.format(name=name),
        headers={"Snap-Device-Series": "16"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
    except Exception as exc:
        print(f"NOTE: could not query store for {name}: {exc}", file=sys.stderr)
        return None

    channel_map = data.get("channel-map", [])
    stable = next(
        (c for c in channel_map if c["channel"]["risk"] == "stable"
         and c["channel"]["architecture"] == "amd64"),
        None,
    )
    if not stable:
        return None

    return {
        "version": stable.get("version"),
        "confinement": stable.get("confinement"),
        "published_at": stable["channel"].get("released-at"),
    }


def main():
    games_dir = REPO_ROOT / "games"
    game_files = sorted(games_dir.glob("*.json"))

    games = []
    for game_file in game_files:
        with open(game_file) as f:
            game = json.load(f)

        name = game["name"]

        icon_path = game.get("icon", "")
        if icon_path:
            game["icon_url"] = f"{STORE_BASE_URL}/{icon_path}"

        for shot in game.get("screenshots", []):
            if "path" in shot and "url" not in shot:
                shot["url"] = f"{STORE_BASE_URL}/{shot['path']}"

        info = store_info(name)
        if info:
            game.update({k: v for k, v in info.items() if v is not None})

        channel = game.get("channel", "stable")
        flags = game.get("install_flags", [])
        flag_str = f"{' '.join(flags)} " if flags else ""
        game["install_command"] = (
            f"sudo snap install {flag_str}--channel={channel} {name}".replace("  ", " ")
        )

        games.append(game)

    catalog = {
        "schema_version": 1,
        "store_name": "Ubuntu Store",
        "store_description": (
            "Curated, gamepad-shell-tested game snaps for handheld devices "
            "running gamepad-shell."
        ),
        "base_url": STORE_BASE_URL,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "games": games,
    }

    catalog_path = REPO_ROOT / "catalog.json"
    with open(catalog_path, "w") as f:
        json.dump(catalog, f, indent=2)
        f.write("\n")

    print(f"catalog.json updated: {len(games)} games", file=sys.stderr)


if __name__ == "__main__":
    main()

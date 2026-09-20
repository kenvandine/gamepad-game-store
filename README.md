# Ubuntu Store catalog (gamepad-game-store)

A curated, machine-readable catalog of game snaps that have been tested and
verified to work in the [gamepad-shell](https://github.com/kenvandine/gamepad-shell)
handheld experience. Powers the "Ubuntu Store" view built into gamepad-shell
(Guide/Legion-button chord) — games are installed straight from the Snap
Store via snapd's REST API, not side-loaded.

This mirrors the structure of [kenvandine/nimbus-app-store](https://github.com/kenvandine/nimbus-app-store),
adapted for games instead of AI agent snaps.

## Catalog

The main metadata file is [`catalog.json`](catalog.json), served at:

```
https://raw.githubusercontent.com/kenvandine/gamepad-game-store/main/catalog.json
```

It is regenerated automatically every day and whenever game metadata or
icons change, pulling each game's current stable-channel version straight
from the Snap Store's public API.

## Games

| Snap | Title | License |
|------|-------|---------|
| `antsy-alien-attack-pico` | Antsy Alien Attack Pico | CC-BY-NC-SA-4.0 OR MIT |
| `gamepad-minecraft` | Minecraft - Gamepad | GPL-3.0 |
| `supertux` | SuperTux | GPL-3.0 |
| `supertuxkart` | SuperTuxKart | GPL-3.0+ |

## Schema

`catalog.json` has this top-level shape:

```json
{
  "schema_version": 1,
  "store_name": "Ubuntu Store",
  "store_description": "...",
  "base_url": "https://raw.githubusercontent.com/kenvandine/gamepad-game-store/main",
  "updated_at": "<ISO 8601>",
  "games": [ ... ]
}
```

Each game entry:

| Field | Type | Description |
|-------|------|--------------|
| `name` | string | Snap package name |
| `title` | string | Human-readable title |
| `summary` | string | One-line description |
| `description` | string | Full description (newline-separated paragraphs) |
| `version` | string | Latest stable-channel version (from the Snap Store) |
| `confinement` | string | `strict` or `classic` |
| `license` | string | SPDX license identifier |
| `categories` | array | Category tags |
| `icon` | string | Relative path to icon asset |
| `icon_url` | string | Absolute URL to icon asset |
| `screenshots` | array | List of `{path, url}` screenshot objects |
| `links.website` | string | Upstream project/publisher page |
| `links.source_code` | string | Game/packaging source repository URL |
| `links.store_page` | string | snapcraft.io listing |
| `publisher` | string | Snap Store publisher display name |
| `channel` | string | Channel to install from (usually `stable`) |
| `install_flags` | array | Extra flags required for `snap install` (e.g. `--classic`) |
| `interfaces_to_connect` | array | Interfaces gamepad-shell must `snap connect` after install (always includes `wayland`/`joystick` as applicable) |
| `removable` | boolean | Whether the Store UI offers a Remove action. `false` for games that ship as part of the device's base image/seed |
| `builtin` | boolean | Whether this game is part of the on-device seed model (shown with a "System Game" badge) |
| `install_command` | string | Full `snap install` command for the current version |
| `published_at` | string | ISO 8601 timestamp of the current stable release |

## Adding a game

1. Create `games/<name>.json` with the static metadata (see
   `games/antsy-alien-attack-pico.json` for the schema).
2. Add the icon to `assets/<name>/icon.png` (or `.svg`) and any screenshots
   to `assets/<name>/screenshots/`.
3. Open a pull request — the update workflow regenerates `catalog.json` on
   merge, pulling the live version from the Snap Store.

Only add games that have actually been tested end-to-end in gamepad-shell
(controller input via the `joystick` interface, Wayland output, and — for
Legion Go S and similar handhelds — on-screen legibility).

## Updating the catalog locally

```
python3 scripts/update-catalog.py
```

No authentication is required — this only reads the public Snap Store API.

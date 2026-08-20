# blueprint library -> data/blueprints.json
# shared across all 3 save slots on purpose (its not in menu.py's _SLOT_FILES)
# machine dict: dx dy type rotation recipe_mode power_links
import base64
import json
import os
import zlib

from settings import MACHINE_STATS

# Exchange-string format. The prefix is versioned so a future layout change can
# be detected rather than silently mis-read.
BP_PREFIX = "IC1"

BLUEPRINT_FILE = "data/blueprints.json"


def _copy_machine(m):
    """dict(m) is not enough. power_links is a list of lists so a shallow copy
    means the clipboard and the saved one share the same list and editing one
    edits the other. took me forever to work that out"""
    out = dict(m)
    if isinstance(out.get("power_links"), list):
        out["power_links"] = [list(l) for l in out["power_links"]]
    return out


class BlueprintLibrary:
    def __init__(self, path=BLUEPRINT_FILE):
        self.path = path
        self.blueprints = []
        self.load()

    def load(self):
        if not os.path.exists(self.path):
            return
        try:
            with open(self.path) as f:
                data = json.load(f)
            entries = data.get("blueprints", [])
            self.blueprints = [b for b in entries if self._valid(b)]
        except (json.JSONDecodeError, ValueError, OSError):
            print("blueprints.json corrupted. Starting with an empty library.")
            self.blueprints = []

    def save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump({"blueprints": self.blueprints}, f)

    @staticmethod
    def _valid(bp):
        return (isinstance(bp, dict) and bp.get("name")
                and isinstance(bp.get("machines"), list)
                and bp.get("w", 0) > 0 and bp.get("h", 0) > 0)

    def add(self, name, bp):
        """Store a captured blueprint under `name`. Returns the stored entry."""
        entry = {
            "name": self._unique_name(name.strip() or "Blueprint"),
            "w": bp["w"], "h": bp["h"],
            "machines": [_copy_machine(m) for m in bp["machines"]],
        }
        self.blueprints.append(entry)
        self.save()
        return entry

    def delete(self, index):
        if 0 <= index < len(self.blueprints):
            removed = self.blueprints.pop(index)
            self.save()
            return removed
        return None

    def rename(self, index, name):
        if 0 <= index < len(self.blueprints) and name.strip():
            self.blueprints[index]["name"] = self._unique_name(name.strip(), skip=index)
            self.save()
            return True
        return False

    def _unique_name(self, name, skip=None):
        existing = {b["name"] for i, b in enumerate(self.blueprints) if i != skip}
        if name not in existing:
            return name
        n = 2
        while f"{name} ({n})" in existing:
            n += 1
        return f"{name} ({n})"

    # -- exchange strings --------
    @staticmethod
    def encode(bp, name=None):
        """blueprint -> string you can paste in discord"""
        # lists not dicts, the keys made it about 3x longer for nothing
        machines = []
        for m in bp.get("machines", []):
            machines.append([
                int(m.get("dx", 0)), int(m.get("dy", 0)), int(m.get("type", 0)),
                int(m.get("rotation", 0)) % 360,
                m.get("recipe_mode") or 0,
                [[int(a), int(b)] for a, b in (m.get("power_links") or [])],
            ])
        payload = {
            "n": (name or bp.get("name") or "Blueprint")[:40],
            "w": int(bp.get("w", 1)), "h": int(bp.get("h", 1)),
            "m": machines,
        }
        raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        packed = base64.urlsafe_b64encode(zlib.compress(raw, 9)).decode("ascii")
        return f"{BP_PREFIX}:{packed.rstrip('=')}"

    @staticmethod
    def decode(text):
        """string -> blueprint, ValueError if its junk"""
        # these messages go straight on screen, keep them readable
        if not text:
            raise ValueError("Nothing to import")
        text = "".join(text.split())
        if ":" not in text:
            raise ValueError("Not a blueprint string")
        prefix, _, packed = text.partition(":")
        if prefix.upper() != BP_PREFIX:
            raise ValueError(f"Unsupported blueprint version '{prefix}'")
        try:
            pad = "=" * (-len(packed) % 4)
            raw = zlib.decompress(base64.urlsafe_b64decode(packed + pad))
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            raise ValueError("Blueprint string is corrupt")
        machines = []
        for entry in payload.get("m", []):
            try:
                dx, dy, ttype, rot, mode, links = (list(entry) + [0] * 6)[:6]
            except TypeError:
                raise ValueError("Blueprint string is corrupt")
            if int(ttype) not in MACHINE_STATS:
                raise ValueError(f"Blueprint uses unknown machine id {ttype}")
            machines.append({
                "dx": int(dx), "dy": int(dy), "type": int(ttype),
                "rotation": int(rot) % 360,
                "recipe_mode": mode if isinstance(mode, str) else None,
                "power_links": [[int(a), int(b)] for a, b in (links or [])],
            })
        if not machines:
            raise ValueError("Blueprint string contains no machines")
        bp = {"name": str(payload.get("n", "Imported"))[:40],
              "w": max(1, int(payload.get("w", 1))),
              "h": max(1, int(payload.get("h", 1))),
              "machines": machines}
        if not BlueprintLibrary._valid(bp):
            raise ValueError("Blueprint string is not a valid layout")
        return bp

    def import_string(self, text):
        """Decode and store. Returns the stored entry."""
        bp = self.decode(text)
        return self.add(bp["name"], bp)

    def export_string(self, index):
        if not (0 <= index < len(self.blueprints)):
            return None
        bp = self.blueprints[index]
        return self.encode(bp, bp.get("name"))

    @staticmethod
    def cost(bp):
        return sum(MACHINE_STATS.get(m["type"], {}).get("cost", 0)
                   for m in bp.get("machines", []))

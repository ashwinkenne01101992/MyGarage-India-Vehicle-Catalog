#!/usr/bin/env python3
"""Validate catalogue invariants and generate a checksum manifest (stdlib only)."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "catalog.json"
MANIFEST = ROOT / "manifest.json"
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
CATEGORIES = {"CAR", "SUV", "MPV", "MOTORCYCLE", "SCOOTER", "ELECTRIC_CAR", "ELECTRIC_TWO_WHEELER"}
POWERTRAINS = {"PETROL", "DIESEL", "CNG", "LPG", "HYBRID", "STRONG_HYBRID", "ELECTRIC", "FLEX_FUEL", "OTHER"}
STATUSES = {"OEM_VERIFIED", "GOVERNMENT_VERIFIED", "LICENSED_DATA", "SECONDARY_UNVERIFIED"}


def fail(message):
    raise SystemExit("ERROR: " + message)


def check_provenance(p, where):
    if not isinstance(p, dict):
        fail(f"{where}: provenance must be an object")
    for key in ("source_name", "source_url", "verified_on", "status"):
        if not p.get(key):
            fail(f"{where}: missing provenance.{key}")
    parsed = urlparse(p["source_url"])
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        fail(f"{where}: source_url must be an http(s) URL")
    try:
        datetime.strptime(p["verified_on"], "%Y-%m-%d")
    except ValueError:
        fail(f"{where}: verified_on must use YYYY-MM-DD")
    if p["status"] not in STATUSES:
        fail(f"{where}: invalid provenance status")


def main():
    try:
        data = json.loads(CATALOG.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"cannot parse catalog.json: {exc}")
    if data.get("catalogue_id") != "mygarage-india" or data.get("market") != "IN":
        fail("catalogue_id/market must identify India catalogue")
    if data.get("schema_version") != 1:
        fail("unsupported schema_version")
    version = data.get("catalogue_version", "")
    if not VERSION_RE.fullmatch(version):
        fail("catalogue_version must be semantic x.y.z")
    vehicles = data.get("vehicles")
    if not isinstance(vehicles, list):
        fail("vehicles must be an array")

    seen_vehicle_ids, seen_variant_ids = set(), set()
    for v in vehicles:
        where = f"vehicle {v.get('id', '<missing>')}"
        for key in ("id", "make", "model"):
            if not v.get(key):
                fail(f"{where}: missing {key}")
        if v["id"] in seen_vehicle_ids:
            fail(f"duplicate vehicle id: {v['id']}")
        seen_vehicle_ids.add(v["id"])
        if v.get("category") not in CATEGORIES:
            fail(f"{where}: invalid category")
        check_provenance(v.get("provenance"), where)
        variants = v.get("variants")
        if not isinstance(variants, list) or not variants:
            fail(f"{where}: at least one variant is required")
        for variant in variants:
            vw = f"{where}, variant {variant.get('id', '<missing>')}"
            for key in ("id", "name", "powertrain"):
                if not variant.get(key):
                    fail(f"{vw}: missing {key}")
            if variant["powertrain"] not in POWERTRAINS:
                fail(f"{vw}: invalid powertrain")
            if variant["id"] in seen_variant_ids:
                fail(f"duplicate variant id: {variant['id']}")
            seen_variant_ids.add(variant["id"])
            check_provenance(variant.get("provenance"), vw)

    raw = CATALOG.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    manifest = {
        "catalogue_id": "mygarage-india",
        "market": "IN",
        "schema_version": 1,
        "catalogue_version": version,
        "generated_at": now,
        "catalogue_url": "https://raw.githubusercontent.com/ashwinkenne01101992/MyGarage-India-Vehicle-Catalog/main/data/catalog.json",
        "sha256": digest,
        "vehicle_count": len(vehicles),
        "variant_count": sum(len(v["variants"]) for v in vehicles)
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Validated {len(vehicles)} vehicles / {manifest['variant_count']} variants")
    print(f"SHA-256: {digest}")


if __name__ == "__main__":
    main()

# MyGarage India Vehicle Catalogue

Versioned, provenance-aware catalogue data for the My Garage Android app.

## Scope

- Market: India only
- Vehicle classes: cars/SUVs/MPVs, motorcycles, scooters and electric vehicles
- Detail level: variant-level specifications where verified
- Delivery: offline catalogue bundled in the app, with periodic manifest-based updates from this repository
- Update cadence: monthly scheduled validation/publication; manual workflow dispatch is also available

## Data integrity and sourcing

The initial catalogue is intentionally empty. It does **not** claim complete Indian-market coverage. Records will be added only when source accuracy and redistribution rights are established. OEM India product pages and brochures are preferred. Government datasets may help cross-check identity and registration fields, but are not assumed to provide complete variant-level specifications.

Unknown values must remain null/omitted rather than guessed. Do not scrape or redistribute third-party datasets unless their terms explicitly permit it. Every vehicle and variant must include source name, source URL, verification date and evidence/status.

## Repository layout

- `data/catalog.json` — canonical catalogue data
- `schema/catalog.schema.json` — catalogue JSON Schema
- `manifest.json` — version/checksum metadata for Android
- `sources/README.md` — source approval and attribution rules
- `scripts/validate_catalog.py` — validation and manifest generation
- `.github/workflows/monthly-catalog.yml` — monthly scheduled validation

## Monthly workflow — current scope

The GitHub Actions workflow runs at 03:17 UTC on the first day of each month and can also be started manually from the Actions tab. It currently validates the committed catalogue and regenerates the checksum manifest. It does **not** discover, scrape or import new vehicle models automatically. Catalogue additions require approved source material and a reviewed data commit. This avoids silently publishing inaccurate or unlicensed specifications.

## Android update contract

The app should download `manifest.json`, verify the SHA-256 of the referenced catalogue file, check the schema version, then import changes in a Room transaction. Updates must be idempotent and must never overwrite user-owned garage records. If download, checksum or import fails, retain the currently installed catalogue.

The app should check approximately every 30 days using WorkManager with a connected-network constraint. Android may defer execution; this is not an exact clock-time guarantee.

## Contributing data

1. Confirm the source permits the intended reuse/redistribution.
2. Add a record with stable IDs and complete provenance.
3. Include variant-level engine, transmission, dimensions, performance, features, colours and tyre details only where supported by the source.
4. Run `python scripts/validate_catalog.py`.
5. Review the generated manifest and submit the change.

See [sources/README.md](sources/README.md) before adding data.

---
name: rema1000-weekly-offers
description: Use when the user wants REMA 1000 offers from etilbudsavis.dk for the week/time period that matches the day of execution, saved as offers/rema1000/rema1000_{year}_week-{weekNumber}.json.
---

# REMA 1000 Weekly Offers (eTilbudsavis)

## Workflow
1. Run:
```bash
bash /workspace/skills/rema1000-weekly-offers/scripts/save_weekly_offers.sh
```
2. Let the script:
- query eTilbudsavis/Tjek APIs for REMA 1000 catalogs,
- select the weekly catalog (`Uge NN`) valid for current Copenhagen time,
- fall back to nearest weekly catalog if no active weekly catalog exists,
- extract all offers from catalog hotspots,
- save JSON to `offers/rema1000/rema1000_{year}_week-{weekNumber}.json`.

## Optional arguments
- `--date YYYY-MM-DD` to resolve the catalog for a specific Copenhagen date.
- `--catalog-id <id>` to force one publication.
- `--output-dir <path>` to customize output location.

## Validation
- Confirm file exists at `offers/rema1000/rema1000_{year}_week-{weekNumber}.json`.
- Confirm payload includes `catalog.id`, `catalog.label`, `catalog.run_from`, and `catalog.run_till`.
- Confirm payload includes `offerCount` and an `offers` array.

---
name: bilka-weekly-offers
description: Use when the user wants Bilka offers from etilbudsavis.dk for the week/time period that matches the day of execution, saved as offers/bilka/bilka_{year}_week-{weekNumber}.json.
---

# Bilka Weekly Offers (eTilbudsavis)

## Workflow
1. Run:
```bash
bash /workspace/skills/bilka-weekly-offers/scripts/save_weekly_offers.sh
```
2. Let the script:
- query eTilbudsavis/Tjek APIs for Bilka catalogs,
- select the weekly catalog valid for current Copenhagen time,
- fall back to nearest weekly catalog if no active weekly catalog exists,
- extract all offers from catalog hotspots,
- save JSON to `offers/bilka/bilka_{year}_week-{weekNumber}.json`.

## Optional arguments
- `--date YYYY-MM-DD` to resolve the catalog for a specific Copenhagen date.
- `--catalog-id <id>` to force one publication.
- `--output-dir <path>` to customize output location.

## Validation
- Confirm file exists at `offers/bilka/bilka_{year}_week-{weekNumber}.json`.
- Confirm payload includes `catalog.id`, `catalog.label`, `catalog.run_from`, and `catalog.run_till`.
- Confirm payload includes `offerCount` and an `offers` array.

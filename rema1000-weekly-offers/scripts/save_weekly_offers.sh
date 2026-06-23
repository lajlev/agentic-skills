#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../../.."
python3 /workspace/skills/rema1000-weekly-offers/scripts/fetch_rema1000_offers.py "$@"

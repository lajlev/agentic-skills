#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../../.."
/workspace/scripts/venv_run.sh /workspace/skills/bilka-weekly-offers/scripts/fetch_bilka_offers.py "$@"

#!/bin/bash
# Rebuild every real-image data file in src/ (real_ct, real_pet, real_nm, real_mr, real_dx, real_4d) from the open TCIA collections. See tools/tcia.py and requirements-tools.txt.
# Usage: bash tools/make_real_all.sh [preview-folder]      Set TCIA_CACHE to keep the downloads between runs (about 1 GB).
cd "$(dirname "$0")/.."
for t in ct pet nm mr dx 4d; do python3 tools/make_real_$t.py "$@" || exit 1; done
echo "done: $(ls src/real_*.json | wc -l) data files"

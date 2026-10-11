#!/bin/bash
# Run the whole pipeline over every recording, in order. Resumable: finished stages are skipped.
# Usage: bash tools/run_all.sh /path/to/videos OUTROOT
VID=${1:-/mnt/user-data/uploads}; OUT=${2:-/home/claude/book}
cd "$(dirname "$0")/.."
i=0
for f in $(ls $VID/2026-10-09_16-*.mp4); do
  i=$((i+1)); d=$OUT/v$i
  [ -f $d/frames.json ] || python3 tools/book_pipeline.py frames "$f" $d
  [ -f $d/lines.json ]  || python3 tools/book_pipeline.py ocr $d
  [ -f $d/text.txt ]    || python3 tools/book_pipeline.py text $d
  echo "done v$i $(date +%T)"
done
echo "ALL DONE $(date +%T)"

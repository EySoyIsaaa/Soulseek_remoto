#!/usr/bin/env bash
set -euo pipefail

DOWNLOAD_DIR="/home/server/slskd/downloads"

if [[ ! -d "$DOWNLOAD_DIR" ]]; then
  exit 0
fi

find "$DOWNLOAD_DIR" -type f -mmin +15 -delete
find "$DOWNLOAD_DIR" -type d -empty -delete

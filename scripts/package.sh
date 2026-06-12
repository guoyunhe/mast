#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

rm -rf "${ROOT_DIR}/build" "${ROOT_DIR}/dist"
python3 -m pip install --upgrade build
python3 -m build --outdir "${ROOT_DIR}/dist" "${ROOT_DIR}"

echo "Package artifacts written to ${ROOT_DIR}/dist"

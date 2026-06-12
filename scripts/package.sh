#!/usr/bin/env bash

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

python3 -m pip install --upgrade build
python3 -m build --outdir "${ROOT_DIR}/dist" "${ROOT_DIR}"

echo "Package artifacts written to ${ROOT_DIR}/dist"

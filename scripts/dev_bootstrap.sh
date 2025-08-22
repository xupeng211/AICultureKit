#!/usr/bin/env bash
set -euo pipefail
python -m pip install -U pip
pip install -r requirements.txt || true
pip install pre-commit ruff black isort bandit detect-secrets
pre-commit install
pre-commit install --hook-type commit-msg
echo "[OK] pre-commit 已安装。试运行：pre-commit run --all-files"

#!/usr/bin/env bash
set -euo pipefail
OUT_DIR="artifacts/security"; mkdir -p "$OUT_DIR"

scan() {
  local pat="$1"; local name="$2"
  find . -name "*.py" -type f \
    -not -path "./venv/*" \
    -not -path "./.venv/*" \
    -not -path "./node_modules/*" \
    -not -path "./artifacts/*" \
    -not -path "./dist/*" \
    -not -path "./build/*" \
    -not -path "./.git/*" \
    -not -path "./*/__pycache__/*" \
    -not -path "./.pytest_cache/*" \
    -not -path "./.mypy_cache/*" \
    -not -path "./.ruff_cache/*" \
    | xargs grep -l -E "$pat" 2>/dev/null > "$OUT_DIR/$name.files" || true
  
  # 扫描非Python文件（md、json等）
  find . -type f \
    -not -path "./venv/*" \
    -not -path "./.venv/*" \
    -not -path "./node_modules/*" \
    -not -path "./artifacts/*" \
    -not -path "./dist/*" \
    -not -path "./build/*" \
    -not -path "./.git/*" \
    -not -path "./*/__pycache__/*" \
    -not -name "*.py" \
    | xargs grep -l -E "$pat" 2>/dev/null >> "$OUT_DIR/$name.files" || true
}

echo "=== P0 Security Scan (Source Code Only) ==="

scan 'hashlib\.md5\(|\bmd5\('          md5
scan 'Environment\([^)]*autoescape\s*=\s*False' jinja_autoescape  
scan 'requests\.(get|post|put|patch|delete)\([^)]*verify\s*=\s*False' requests_verify
scan 'subprocess\.(run|Popen)\([^)]*shell\s*=\s*True' subprocess_shell
scan '(^|[^_])\b(eval|exec)\('        eval_exec

# 合并并去重，只保留源代码文件
cat "$OUT_DIR"/*.files 2>/dev/null | sort -u | grep -E '\.(py|md|yml|yaml|json|sh)$' > "$OUT_DIR/p0_targets.list" || true

echo ""
echo "[P0] Source code targets found:"
if [ -s "$OUT_DIR/p0_targets.list" ]; then
    cat "$OUT_DIR/p0_targets.list"
    echo ""
    echo "Total files: $(wc -l < "$OUT_DIR/p0_targets.list")"
else
    echo "No P0 targets found in source code."
fi 
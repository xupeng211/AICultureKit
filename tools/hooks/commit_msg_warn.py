import pathlib
import re
import sys

p = pathlib.Path(sys.argv[-1])
msg = (
    p.read_text(encoding="utf-8", errors="ignore").strip().splitlines()[0]
    if p.exists()
    else ""
)
pat = re.compile(
    r"^(feat|fix|docs|style|refactor|perf|test|chore)(\([\w\-\.]+\))?:\s.+"
)
if not pat.match(msg):
    print(f"[AICultureKit][WARN] Commit message 不符合 conventional 规范：'{msg}'")
    print("  建议格式：feat(scope): subject")
sys.exit(0)  # 仅提醒，不阻塞

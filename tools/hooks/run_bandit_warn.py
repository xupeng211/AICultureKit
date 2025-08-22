#!/usr/bin/env python3
import pathlib
import subprocess
import sys

art = pathlib.Path("artifacts")
art.mkdir(parents=True, exist_ok=True)
res = subprocess.run(["bandit", "-q", "-r", ".", "-f", "json"], text=True, capture_output=True)
(pathlib.Path("artifacts") / "bandit_report.json").write_text(res.stdout or "{}", encoding="utf-8")
print(res.stdout)  # 控制台仍打印
sys.exit(0)  # 永远不阻塞

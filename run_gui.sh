#!/bin/bash
# macOS: 用 Rosetta 2 (x86_64) 运行 GUI，避免 segfault
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
if [ "$(uname)" = "Darwin" ]; then
  if arch -x86_64 python gui.py 2>/dev/null; then
    :
  else
    echo "Rosetta 模式失败，尝试直接运行..."
    python gui.py
  fi
else
  python gui.py
fi

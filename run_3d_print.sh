#!/bin/bash
# macOS: 优先用 Rosetta 2 (x86_64) 运行，避免 CadQuery segfault
# 若 arch 失败，需安装 x86_64 Python：arch -x86_64 brew install python
cd "$(dirname "$0")"
source venv/bin/activate 2>/dev/null || true
if [ "$(uname)" = "Darwin" ]; then
  if arch -x86_64 python "3D print.py" 2>/dev/null; then
    :
  else
    echo "Rosetta 模式失败，尝试直接运行..."
    python "3D print.py"
  fi
else
  python "3D print.py"
fi

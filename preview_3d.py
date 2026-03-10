#!/usr/bin/env python3
"""
在窗口中预览当前参数的 3D 模型（不导出文件）。
使用 CadQuery 的 VTK 查看器，可旋转、缩放。
用法: echo '<json>' | python preview_3d.py
或直接运行查看默认零件: python preview_3d.py
"""

import json
import os
import sys
from pathlib import Path

if sys.platform == "darwin":
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("MPLBACKEND", "Agg")

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import importlib.util
from parts_config import PARTS

MAIN_SCRIPT = SCRIPT_DIR / "3D print.py"
spec = importlib.util.spec_from_file_location("cad_models", MAIN_SCRIPT)
cad_models = importlib.util.module_from_spec(spec)
sys.modules["cad_models"] = cad_models
spec.loader.exec_module(cad_models)
from cadquery.vis import show


def main():
    if sys.stdin.isatty():
        # 无管道输入时使用默认零件预览
        data = {
            "part_key": "Optical test fixture",
            "param_values": {
                "sensor_width": 10,
                "sensor_height": 8,
                "lens_diameter": 12,
                "working_distance": 5,
                "export_name": "optical_test_fixture",
            },
        }
    else:
        data = json.loads(sys.stdin.read())

    part_key = data["part_key"]
    param_values = data["param_values"]
    info = PARTS[part_key]
    fn = getattr(cad_models, info["fn"])
    params = dict(param_values)
    if info.get("export_inside") and "export_name" not in params:
        params["export_name"] = "preview"

    part = fn(**params)
    # CadQuery 2.4+ 内置 VTK 查看器，会阻塞直到用户关闭窗口
    show(part)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

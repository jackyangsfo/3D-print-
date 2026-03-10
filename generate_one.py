#!/usr/bin/env python3
"""
由 GUI 在子进程中调用，根据 JSON 参数生成单个零件并导出。
macOS 上避免在主进程（Tk）中加载 CadQuery，防止 segfault。
用法: echo '<json>' | python generate_one.py
"""

import json
import os
import sys
from pathlib import Path

if sys.platform == "darwin":
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("MPLBACKEND", "Agg")

import importlib.util

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from parts_config import PARTS

MAIN_SCRIPT = SCRIPT_DIR / "3D print.py"
spec = importlib.util.spec_from_file_location("cad_models", MAIN_SCRIPT)
cad_models = importlib.util.module_from_spec(spec)
sys.modules["cad_models"] = cad_models
spec.loader.exec_module(cad_models)
cq = __import__("cadquery")


def main():
    raw = sys.stdin.read()
    data = json.loads(raw)
    part_key = data["part_key"]
    param_values = data["param_values"]
    out_dir = Path(data["out_dir"])
    export_name = data["export_name"]
    export_gcode = data.get("export_gcode", False)

    info = PARTS[part_key]
    fn_name = info["fn"]
    params = dict(param_values)
    if info.get("export_inside") and "export_name" not in params:
        params["export_name"] = export_name
    cad_models.OUTPUT_DIR = out_dir
    fn = getattr(cad_models, fn_name)
    part = fn(**params)
    if info.get("export_stl_step"):
        stl_path = out_dir / f"{export_name}.stl"
        step_path = out_dir / f"{export_name}.step"
        cq.exporters.export(part, str(stl_path))
        cq.exporters.export(part, str(step_path))
        if export_gcode:
            try:
                from gcode_export import export_part_to_gcode
                gcode_path = out_dir / f"{export_name}.gcode"
                export_part_to_gcode(part, str(gcode_path))
                print(str(gcode_path))
            except ImportError:
                print(str(stl_path))
        else:
            print(str(stl_path))
    else:
        if export_gcode:
            try:
                from gcode_export import export_part_to_gcode
                gcode_path = out_dir / f"{export_name}.gcode"
                export_part_to_gcode(part, str(gcode_path))
                print(str(gcode_path))
            except ImportError:
                print(str(out_dir / f"{export_name}.stl"))
        else:
            print(str(out_dir / f"{export_name}.stl"))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(str(e), file=sys.stderr)
        sys.exit(1)

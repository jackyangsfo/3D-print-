#!/usr/bin/env python3
"""
光学测试夹具 — 快速生成脚本
仅需三参数：sensor size、lens mount、working distance，
自动生成完整的相机测试座 STL，适用于 AnkerMake 等打印机。

镜头规格：M8=8mm, M12=12mm, M16=16mm, C/CS=25.4mm

用法:
  python m12_optical_fixture.py
  python m12_optical_fixture.py --sensor 12 10 --mount M16 --wd 8
  python m12_optical_fixture.py -s 10 8 -m M12 -w 5 -o my_fixture
"""

import argparse
import sys
from pathlib import Path

LENS_MOUNTS = {"M8": 8, "M12": 12, "M16": 16, "C/CS": 25.4}

sys.path.insert(0, str(Path(__file__).parent))
from importlib.util import spec_from_file_location, module_from_spec
spec = spec_from_file_location("cad_models", Path(__file__).parent / "3D print.py")
mod = module_from_spec(spec)
spec.loader.exec_module(mod)

def main():
    p = argparse.ArgumentParser(description="光学测试夹具 — 参数化生成 (M8/M12/M16/C/CS)")
    p.add_argument("-s", "--sensor", nargs=2, type=float, default=[10, 8], metavar=("W", "H"),
                   help="Sensor size (mm): width height, default 10 8")
    p.add_argument("-m", "--mount", choices=list(LENS_MOUNTS.keys()), default="M12",
                   help="Lens mount: M8, M12, M16, C/CS (default M12)")
    p.add_argument("-l", "--lens", type=float, default=None,
                   help="Lens diameter (mm), overrides --mount if set")
    p.add_argument("-w", "--wd", "--working-distance", dest="wd", type=float, default=5,
                   help="Working distance (mm), default 5")
    p.add_argument("-o", "--output", default="optical_test_fixture", help="Output filename (no ext)")
    args = p.parse_args()

    lens_diameter = args.lens if args.lens is not None else LENS_MOUNTS[args.mount]

    mod.generate_m12_optical_test_fixture(
        sensor_width=args.sensor[0],
        sensor_height=args.sensor[1],
        lens_diameter=lens_diameter,
        working_distance=args.wd,
        export_name=args.output,
    )
    out_dir = mod.OUTPUT_DIR
    print(f"Done: {out_dir / args.output}.stl")
    print(f"      {out_dir / args.output}.step")
    print(f"Lens mount: {args.mount} ({lens_diameter}mm)")
    print("Ready for AnkerMake / Cura / PrusaSlicer.")

if __name__ == "__main__":
    main()

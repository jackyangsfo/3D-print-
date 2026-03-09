#!/usr/bin/env python3
"""
参数化 3D 打印件生成脚本 (Parametric 3D printable parts)
Pipeline: Python → 几何体 → STL/STEP → 切片软件 → G-code → 打印机

适用于: 镜头座、相机夹具、MTF 测试治具、光学支架等。
依赖: pip install cadquery
"""

# macOS 上设置环境变量，减少 OpenGL/图形栈初始化导致的 segfault
import os
import sys
if sys.platform == "darwin":
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    os.environ.setdefault("MPLBACKEND", "Agg")

import cadquery as cq
from pathlib import Path

# 输出目录
OUTPUT_DIR = Path(__file__).resolve().parent / "exports"
OUTPUT_DIR.mkdir(exist_ok=True)

# G-code 导出（可选，需 meshcut）
def _export_gcode_if_available(part, path_stem: Path, export_gcode: bool = True, **kwargs):
    """若 export_gcode 且已安装 meshcut，则导出 G-code。"""
    if not export_gcode:
        return None
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from gcode_export import export_part_to_gcode
        gcode_path = path_stem.with_suffix(".gcode")
        export_part_to_gcode(part, str(gcode_path), **kwargs)
        return gcode_path
    except ImportError:
        return None


# =============================================================================
# 1. 简单圆柱体示例 (Simple cylinder)
# =============================================================================
def make_simple_cylinder(diameter: float = 20, height: float = 10) -> cq.Workplane:
    """生成简单圆柱体，可做垫片、 spacer 等。"""
    part = (
        cq.Workplane("XY")
        .circle(diameter / 2)
        .extrude(height)
    )
    return part


# =============================================================================
# 2. M12 镜头座 (M12 lens holder)
# =============================================================================
def make_m12_lens_holder(
    lens_diameter: float = 12,
    body_diameter: float = 20,
    height: float = 15,
    wall_thickness: float = 2,
) -> cq.Workplane:
    """参数化 M12 镜头座：外径 body，内孔 lens_diameter，高度 height。"""
    outer_r = body_diameter / 2
    inner_r = lens_diameter / 2
    model = (
        cq.Workplane("XY")
        .circle(outer_r)
        .extrude(height)
        .faces(">Z")
        .circle(inner_r)
        .cutThruAll()
    )
    return model


# =============================================================================
# 2b. M12 光学测试夹具（参数化，三参数即可）
# =============================================================================
def generate_m12_optical_test_fixture(
    sensor_width: float = 10,
    sensor_height: float = 8,
    lens_diameter: float = 12,
    working_distance: float = 5,
    wall_thickness: float = 2,
    base_height: float = 3,
    mounting_hole_diameter: float = 2.2,
    export_name: str = "m12_optical_test_fixture",
) -> cq.Workplane:
    """
    参数化 M12 光学测试夹具：仅需 sensor size、lens diameter、working distance 三参数，
    自动生成完整的 M12 相机测试座 STL，适用于 AnkerMake 等打印机。
    面向 camera module 实验室的 MTF、分辨率测试。
    """
    pcb_margin = 4
    pcb_width = sensor_width + 2 * pcb_margin
    pcb_height = sensor_height + 2 * pcb_margin
    pcb_thickness = 1.6
    hole_spacing = min(pcb_width, pcb_height) - 4
    return generate_camera_fixture(
        sensor_width=sensor_width,
        sensor_height=sensor_height,
        lens_diameter=lens_diameter,
        pcb_width=pcb_width,
        pcb_height=pcb_height,
        pcb_thickness=pcb_thickness,
        working_distance=working_distance,
        wall_thickness=wall_thickness,
        mounting_hole_diameter=mounting_hole_diameter,
        mounting_hole_spacing_x=hole_spacing,
        mounting_hole_spacing_y=hole_spacing,
        base_height=base_height,
        export_name=export_name,
    )


# =============================================================================
# 3. 相机模块外壳 / 夹具 (M12 camera module housing)
# =============================================================================
def generate_camera_fixture(
    sensor_width: float = 10,
    sensor_height: float = 8,
    lens_diameter: float = 12,
    pcb_width: float = 20,
    pcb_height: float = 20,
    pcb_thickness: float = 1.6,
    working_distance: float = 5,
    wall_thickness: float = 2,
    mounting_hole_diameter: float = 2.2,
    mounting_hole_spacing_x: float = 16,
    mounting_hole_spacing_y: float = 16,
    base_height: float = 3,
    export_name: str = "camera_fixture",
) -> cq.Workplane:
    """
    根据传感器尺寸、镜头直径、PCB 尺寸、安装孔等参数，
    自动生成可 3D 打印的相机模块外壳/夹具。
    适用于 MTF 测试治具、光学平台安装。
    """
    # 外壳整体尺寸：以 PCB 为底，留出壁厚和安装孔
    box_w = pcb_width + 2 * wall_thickness
    box_d = pcb_height + 2 * wall_thickness
    # 总高：底座 + PCB 槽 + 镜头筒高度（working_distance + 一点余量）
    lens_tube_height = working_distance + 10
    total_h = base_height + pcb_thickness + lens_tube_height

    # 底座 + 主体块
    body = (
        cq.Workplane("XY")
        .box(box_w, box_d, total_h, centered=(True, True, False))
    )

    # PCB 槽：挖空内部，留出 PCB 厚度
    cavity = (
        cq.Workplane("XY")
        .workplane(offset=base_height)
        .box(
            box_w - 2 * wall_thickness,
            box_d - 2 * wall_thickness,
            pcb_thickness + 0.2,
            centered=(True, True, False),
        )
    )
    body = body.cut(cavity)

    # 顶部镜头孔（通孔）
    body = (
        body.faces(">Z")
        .circle(lens_diameter / 2)
        .cutThruAll()
    )

    # 四个安装孔（M2 常用 2.2mm 孔径）
    sx, sy = mounting_hole_spacing_x / 2, mounting_hole_spacing_y / 2
    body = (
        body.faces(">Z")
        .workplane(offset=-total_h + 1)
        .pushPoints([(-sx, -sy), (sx, -sy), (sx, sy), (-sx, sy)])
        .hole(mounting_hole_diameter, total_h + 2)
    )

    # 导出（CadQuery 需要字符串路径）
    cq.exporters.export(body, str(OUTPUT_DIR / f"{export_name}.stl"))
    cq.exporters.export(body, str(OUTPUT_DIR / f"{export_name}.step"))
    return body


# =============================================================================
# 4. 简单镜头垫圈 / spacer (Lens spacer)
# =============================================================================
def make_lens_spacer(
    outer_diameter: float = 20,
    inner_diameter: float = 12,
    thickness: float = 2,
) -> cq.Workplane:
    """镜头垫圈：外径、内径、厚度可调。"""
    part = (
        cq.Workplane("XY")
        .circle(outer_diameter / 2)
        .circle(inner_diameter / 2)
        .extrude(thickness)
    )
    return part


# =============================================================================
# 5. 矩形夹具块 + 中心圆孔 (Test jig block)
# =============================================================================
def make_test_jig_block(
    width: float = 40,
    depth: float = 30,
    height: float = 15,
    hole_diameter: float = 12,
) -> cq.Workplane:
    """矩形块 + 中心圆孔，适合做测试治具、对齐块。"""
    part = (
        cq.Workplane("XY")
        .box(width, depth, height, centered=(True, True, False))
        .faces(">Z")
        .circle(hole_diameter / 2)
        .cutThruAll()
    )
    return part


# =============================================================================
# 6. PCBA 底板 (PCBA holder plate)
# =============================================================================
def make_pcba_holder(
    length: float = 100,
    width: float = 80,
    thickness: float = 2,
    hole_diameter: float = 2.2,
    hole_inset: float = 5,
    export_name: str | None = "pcba_holder",
) -> cq.Workplane:
    """
    矩形 PCBA 底板：四角各一个安装孔（默认 M2，孔径 2.2mm）。
    length: 长 (mm), width: 宽 (mm), thickness: 板厚 (mm)
    hole_inset: 孔中心距边缘距离 (mm)
    """
    L, W, t = length, width, thickness
    part = (
        cq.Workplane("XY")
        .box(L, W, t, centered=(True, True, False))
        .faces(">Z")
        .pushPoints(
            [
                (-L / 2 + hole_inset, -W / 2 + hole_inset),
                (L / 2 - hole_inset, -W / 2 + hole_inset),
                (L / 2 - hole_inset, W / 2 - hole_inset),
                (-L / 2 + hole_inset, W / 2 - hole_inset),
            ]
        )
        .hole(hole_diameter, t + 2)
    )
    if export_name:
        cq.exporters.export(part, str(OUTPUT_DIR / f"{export_name}.stl"))
        cq.exporters.export(part, str(OUTPUT_DIR / f"{export_name}.step"))
    return part


# =============================================================================
# Main: 生成并导出所有示例
# =============================================================================
def main(export_gcode: bool = True):
    print("生成参数化 3D 模型并导出到:", OUTPUT_DIR)

    # 1. 简单圆柱
    cyl = make_simple_cylinder(diameter=20, height=10)
    cq.exporters.export(cyl, str(OUTPUT_DIR / "part_cylinder.stl"))
    cq.exporters.export(cyl, str(OUTPUT_DIR / "part_cylinder.step"))
    g1 = _export_gcode_if_available(cyl, OUTPUT_DIR / "part_cylinder", export_gcode=export_gcode)
    print("  - part_cylinder.stl / .step" + (" / .gcode" if g1 else ""))

    # 2. M12 镜头座
    m12 = make_m12_lens_holder(lens_diameter=12, body_diameter=20, height=15)
    cq.exporters.export(m12, str(OUTPUT_DIR / "m12_holder.stl"))
    cq.exporters.export(m12, str(OUTPUT_DIR / "m12_holder.step"))
    g2 = _export_gcode_if_available(m12, OUTPUT_DIR / "m12_holder", export_gcode=export_gcode)
    print("  - m12_holder.stl / .step" + (" / .gcode" if g2 else ""))

    # 3. 相机夹具（可改参数）
    cam = generate_camera_fixture(
        sensor_width=10,
        sensor_height=8,
        lens_diameter=12,
        pcb_width=20,
        pcb_height=20,
        pcb_thickness=1.6,
        working_distance=5,
        mounting_hole_diameter=2.2,
        mounting_hole_spacing_x=16,
        mounting_hole_spacing_y=16,
        export_name="camera_fixture",
    )
    g3 = _export_gcode_if_available(cam, OUTPUT_DIR / "camera_fixture", export_gcode=export_gcode)
    print("  - camera_fixture.stl / .step" + (" / .gcode" if g3 else ""))

    # 4. 镜头垫圈
    spacer = make_lens_spacer(outer_diameter=20, inner_diameter=12, thickness=2)
    cq.exporters.export(spacer, str(OUTPUT_DIR / "lens_spacer.stl"))
    g4 = _export_gcode_if_available(spacer, OUTPUT_DIR / "lens_spacer", export_gcode=export_gcode)
    print("  - lens_spacer.stl" + (" / .gcode" if g4 else ""))

    # 5. 测试治具块
    jig = make_test_jig_block(width=40, depth=30, height=15, hole_diameter=12)
    cq.exporters.export(jig, str(OUTPUT_DIR / "test_jig_block.stl"))
    g5 = _export_gcode_if_available(jig, OUTPUT_DIR / "test_jig_block", export_gcode=export_gcode)
    print("  - test_jig_block.stl" + (" / .gcode" if g5 else ""))

    # 6b. M12 光学测试夹具（三参数：sensor、lens、working_distance）
    m12_fixture = generate_m12_optical_test_fixture(
        sensor_width=10,
        sensor_height=8,
        lens_diameter=12,
        working_distance=5,
        export_name="m12_optical_test_fixture",
    )
    g6b = _export_gcode_if_available(m12_fixture, OUTPUT_DIR / "m12_optical_test_fixture", export_gcode=export_gcode)
    print("  - m12_optical_test_fixture.stl / .step" + (" / .gcode" if g6b else ""))

    # 6. PCBA 底板 (10cm x 8cm, 2mm 厚, 四角 M2 孔)
    pcba = make_pcba_holder(
        length=100,
        width=80,
        thickness=2,
        hole_diameter=2.2,
        hole_inset=5,
        export_name="pcba_holder",
    )
    g6 = _export_gcode_if_available(pcba, OUTPUT_DIR / "pcba_holder", export_gcode=export_gcode)
    print("  - pcba_holder.stl / .step" + (" / .gcode" if g6 else ""))

    print("完成。STL 可导入切片软件，或直接使用 Python 生成的 .gcode 打印。")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--no-gcode", action="store_true", help="不导出 G-code，仅 STL/STEP")
    args = p.parse_args()
    main(export_gcode=not args.no_gcode)

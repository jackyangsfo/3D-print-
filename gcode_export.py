#!/usr/bin/env python3
"""
Python 生成 G-code：从 CadQuery 几何体直接导出可打印的 G-code。
Pipeline: CadQuery → tessellate → slice → G-code
依赖: pip install meshcut numpy
"""

from pathlib import Path

try:
    import meshcut
    import numpy as np
    HAS_MESHCUT = True
except ImportError:
    HAS_MESHCUT = False


def export_part_to_gcode(
    part,
    filepath,
    layer_height: float = 0.2,
    line_width: float = 0.4,
    filament_diameter: float = 1.75,
    print_speed: int = 60,
    travel_speed: int = 120,
    bed_temp: int = 60,
    hotend_temp: int = 200,
) -> Path:
    """
    将 CadQuery 零件 tessellate、切片后导出为 G-code。
    part: CadQuery Workplane (含 .val() 的 shape)
    filepath: 输出 .gcode 路径
    """
    if not HAS_MESHCUT:
        raise ImportError("需要安装 meshcut: pip install meshcut")

    shape = part.val()
    vertices, triangles = shape.tessellate(0.1, 0.1)
    verts = np.array([[v.x, v.y, v.z] for v in vertices])
    faces = np.array(triangles, dtype=np.int32)

    z_min, z_max = float(verts[:, 2].min()), float(verts[:, 2].max())
    layers = []
    z = z_min + layer_height / 2
    while z < z_max:
        try:
            contours = meshcut.cross_section(
                verts, faces,
                plane_orig=(0, 0, z),
                plane_normal=(0, 0, 1),
            )
            if contours is not None and len(contours) > 0:
                layers.append((z, contours))
        except Exception:
            pass
        z += layer_height

    # 挤出量计算：体积 = 线宽 * 层高 * 线段长度
    cross_section = line_width * layer_height
    e_per_mm = cross_section / (np.pi * (filament_diameter / 2) ** 2)

    lines = []
    lines.append("; Python-generated G-code")
    lines.append("; Layer height: {} mm".format(layer_height))
    lines.append("G21 ; mm")
    lines.append("G90 ; absolute")
    lines.append("M104 S{} ; hotend temp".format(hotend_temp))
    lines.append("M140 S{} ; bed temp".format(bed_temp))
    lines.append("G28 ; home")
    lines.append("G1 Z5 F{} ; lift".format(travel_speed * 60))
    lines.append("M109 S{} ; wait hotend".format(hotend_temp))
    lines.append("M190 S{} ; wait bed".format(bed_temp))
    lines.append("G1 Z0.2 F{} ; first layer".format(print_speed * 60))

    e_total = 0.0
    for z, contours in layers:
        lines.append("; Layer Z={:.3f}".format(z))
        lines.append("G1 Z{:.3f} F{}".format(z, travel_speed * 60))
        for contour in contours:
            if len(contour) < 2:
                continue
            # 移到起点
            x, y = contour[0][0], contour[0][1]
            lines.append("G0 X{:.3f} Y{:.3f} F{}".format(x, y, travel_speed * 60))
            for i in range(1, len(contour)):
                x, y = contour[i][0], contour[i][1]
                dx, dy = contour[i][0] - contour[i - 1][0], contour[i][1] - contour[i - 1][1]
                dist = (dx ** 2 + dy ** 2) ** 0.5
                e_total += dist * e_per_mm
                lines.append("G1 X{:.3f} Y{:.3f} E{:.5f} F{}".format(x, y, e_total, print_speed * 60))

    lines.append("G1 Z{:.3f} F{} ; retract".format(z_max + 5, travel_speed * 60))
    lines.append("M104 S0 ; hotend off")
    lines.append("M140 S0 ; bed off")
    lines.append("G28 X Y ; home XY")
    lines.append("M84 ; motors off")

    path = Path(filepath)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path

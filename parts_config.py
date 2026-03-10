#!/usr/bin/env python3
"""
零件配置：GUI 与 generate_one 共用。
新增零件时只需在此维护一份 PARTS。
"""

PARTS = {
    "Simple cylinder": {
        "fn": "make_simple_cylinder",
        "params": [("diameter", 20, "Diameter (mm)"), ("height", 10, "Height (mm)")],
        "export_stl_step": True,
    },
    "M12 lens holder": {
        "fn": "make_m12_lens_holder",
        "params": [
            ("lens_diameter", 12, "Lens hole diameter (mm)"),
            ("body_diameter", 20, "Body diameter (mm)"),
            ("height", 15, "Height (mm)"),
        ],
        "export_stl_step": True,
    },
    "Optical test fixture": {
        "fn": "generate_m12_optical_test_fixture",
        "params": [
            ("sensor_width", 10, "Sensor width (mm)"),
            ("sensor_height", 8, "Sensor height (mm)"),
            ("lens_mount", "M12 (12mm)", "Lens mount"),
            ("working_distance", 5, "Working distance (mm)"),
            ("export_name", "optical_test_fixture", "Export filename (no ext)"),
        ],
        "export_inside": True,
        "lens_mount_choices": {"M8 (8mm)": 8, "M12 (12mm)": 12, "M16 (16mm)": 16, "C/CS (25.4mm)": 25.4},
    },
    "Camera fixture": {
        "fn": "generate_camera_fixture",
        "params": [
            ("sensor_width", 10, "Sensor width (mm)"),
            ("sensor_height", 8, "Sensor height (mm)"),
            ("lens_diameter", 12, "Lens diameter (mm)"),
            ("pcb_width", 20, "PCB width (mm)"),
            ("pcb_height", 20, "PCB height (mm)"),
            ("pcb_thickness", 1.6, "PCB thickness (mm)"),
            ("working_distance", 5, "Working distance (mm)"),
            ("mounting_hole_diameter", 2.2, "Mounting hole Ø (mm)"),
            ("mounting_hole_spacing_x", 16, "Hole spacing X (mm)"),
            ("mounting_hole_spacing_y", 16, "Hole spacing Y (mm)"),
            ("export_name", "camera_fixture", "Export filename (no ext)"),
        ],
        "export_inside": True,
    },
    "Lens spacer": {
        "fn": "make_lens_spacer",
        "params": [
            ("outer_diameter", 20, "Outer diameter (mm)"),
            ("inner_diameter", 12, "Inner diameter (mm)"),
            ("thickness", 2, "Thickness (mm)"),
        ],
        "export_stl_step": True,
    },
    "Test jig block": {
        "fn": "make_test_jig_block",
        "params": [
            ("width", 40, "Width (mm)"),
            ("depth", 30, "Depth (mm)"),
            ("height", 15, "Height (mm)"),
            ("hole_diameter", 12, "Center hole Ø (mm)"),
        ],
        "export_stl_step": True,
    },
    "PCBA holder": {
        "fn": "make_pcba_holder",
        "params": [
            ("length", 100, "Length (mm)"),
            ("width", 80, "Width (mm)"),
            ("thickness", 2, "Thickness (mm)"),
            ("hole_diameter", 2.2, "Hole Ø (mm)"),
            ("hole_inset", 5, "Hole inset from edge (mm)"),
            ("export_name", "pcba_holder", "Export filename (no ext)"),
        ],
        "export_inside": True,
    },
}

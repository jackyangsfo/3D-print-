#!/usr/bin/env python3
"""
3D 打印参数化零件 — Tkinter 图形界面
运行: python gui.py  （需 cadquery，与 3D print.py 同目录）
"""

import importlib.util
import json
import platform
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

SCRIPT_DIR = Path(__file__).resolve().parent
MAIN_SCRIPT = SCRIPT_DIR / "3D print.py"
GENERATE_ONE_SCRIPT = SCRIPT_DIR / "generate_one.py"

ON_MACOS = platform.system() == "Darwin"
cad_models = None
cq = None
OUTPUT_DIR = SCRIPT_DIR / "exports" if ON_MACOS else None


def _ensure_cadquery():
    global cad_models, cq, OUTPUT_DIR
    if ON_MACOS or cad_models is not None:
        return
    spec = importlib.util.spec_from_file_location("cad_models", MAIN_SCRIPT)
    cad_models = importlib.util.module_from_spec(spec)
    sys.modules["cad_models"] = cad_models
    spec.loader.exec_module(cad_models)
    cq = __import__("cadquery")
    OUTPUT_DIR = cad_models.OUTPUT_DIR


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


def parse_float(s, default):
    try:
        return float(str(s).strip())
    except (ValueError, TypeError):
        return default


def do_generate():
    part_key = app.part_var.get()
    if not part_key or part_key not in PARTS:
        app.status_var.set("Please select a part type.")
        return
    out_dir = Path(app.out_dir_var.get().strip() or str(OUTPUT_DIR or SCRIPT_DIR / "exports"))
    export_name = app.export_name_var.get().strip() or "export"
    out_dir.mkdir(parents=True, exist_ok=True)
    info = PARTS[part_key]
    params = {}
    for item in info["params"]:
        key, default, _ = item[0], item[1], item[2]
        if key not in app.entries:
            continue
        val = app.entries[key].get().strip()
        if key == "lens_mount" and "lens_mount_choices" in info:
            params["lens_diameter"] = info["lens_mount_choices"].get(val, 12)
        elif isinstance(default, (int, float)):
            params[key] = parse_float(val, default)
        else:
            params[key] = val or default

    app.generate_btn.config(state=tk.DISABLED)
    app.status_var.set("Generating...")
    app.root.update_idletasks()

    def run():
        try:
            if ON_MACOS:
                data = {"part_key": part_key, "param_values": params, "out_dir": str(out_dir), "export_name": export_name, "export_gcode": app.export_gcode_var.get()}
                cmd = ["arch", "-x86_64", sys.executable, str(GENERATE_ONE_SCRIPT)]
                result = subprocess.run(cmd, input=json.dumps(data), capture_output=True, text=True, cwd=str(SCRIPT_DIR), timeout=120)
                if result.returncode != 0 and ("bad CPU" in (result.stderr or "") or "posix_spawn" in (result.stderr or "")):
                    result = subprocess.run([sys.executable, str(GENERATE_ONE_SCRIPT)], input=json.dumps(data), capture_output=True, text=True, cwd=str(SCRIPT_DIR), timeout=120)
                if result.returncode != 0:
                    app.root.after(0, lambda: (app.status_var.set(f"Error: {result.stderr or result.returncode}"), messagebox.showerror("Error", result.stderr or str(result.returncode))))
                else:
                    path = (result.stdout or "").strip()
                    app.root.after(0, lambda: app.status_var.set(f"Done: {path}" if path else "Done."))
            else:
                _ensure_cadquery()
                cad_models.OUTPUT_DIR = out_dir
                info = PARTS[part_key]
                fn = getattr(cad_models, info["fn"])
                p = dict(params)
                if info.get("export_inside") and "export_name" not in p:
                    p["export_name"] = export_name
                part = fn(**p)
                if info.get("export_stl_step"):
                    stl_path = out_dir / f"{export_name}.stl"
                    cq.exporters.export(part, str(stl_path))
                    cq.exporters.export(part, str(out_dir / f"{export_name}.step"))
                    done_msg = str(stl_path)
                    if app.export_gcode_var and app.export_gcode_var.get():
                        try:
                            sys.path.insert(0, str(SCRIPT_DIR))
                            from gcode_export import export_part_to_gcode
                            gcode_path = out_dir / f"{export_name}.gcode"
                            export_part_to_gcode(part, str(gcode_path))
                            done_msg = str(gcode_path)
                        except ImportError:
                            pass
                    app.root.after(0, lambda m=done_msg: app.status_var.set(f"Done: {m}"))
                else:
                    done_msg = str(out_dir / export_name)
                    if app.export_gcode_var and app.export_gcode_var.get():
                        try:
                            sys.path.insert(0, str(SCRIPT_DIR))
                            from gcode_export import export_part_to_gcode
                            gcode_path = out_dir / f"{export_name}.gcode"
                            export_part_to_gcode(part, str(gcode_path))
                            done_msg = str(gcode_path)
                        except ImportError:
                            pass
                    app.root.after(0, lambda m=done_msg: app.status_var.set(f"Done: {m}"))
        except Exception as e:
            app.root.after(0, lambda: (app.status_var.set(f"Error: {e}"), messagebox.showerror("Error", str(e))))
        app.root.after(0, lambda: app.generate_btn.config(state=tk.NORMAL))

    threading.Thread(target=run, daemon=True).start()


def on_part_change(*args):
    part_key = app.part_var.get()
    for w in app.params_frame.winfo_children():
        w.destroy()
    app.entries.clear()
    if part_key not in PARTS:
        return
    info = PARTS[part_key]
    for i, item in enumerate(info["params"]):
        key = item[0]
        default = item[1]
        label = item[2]
        ttk.Label(app.params_frame, text=label).grid(row=i, column=0, sticky=tk.W, padx=(0, 8), pady=2)
        if key == "lens_mount" and "lens_mount_choices" in info:
            choices = list(info["lens_mount_choices"].keys())
            e = ttk.Combobox(app.params_frame, values=choices, state="readonly", width=16)
            e.set(default if default in choices else (choices[1] if len(choices) > 1 else choices[0]))
        else:
            e = ttk.Entry(app.params_frame, width=14)
            e.insert(0, str(default))
        e.grid(row=i, column=1, sticky=tk.W, pady=2)
        app.entries[key] = e


def choose_dir():
    path = filedialog.askdirectory(initialdir=app.out_dir_var.get())
    if path:
        app.out_dir_var.set(path)


def build_ui(root):
    root.title("3D Print — Parametric Parts")
    root.minsize(380, 420)
    root.geometry("420x500")

    main = ttk.Frame(root, padding=12)
    main.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main, text="Part type", font=("", 10, "bold")).pack(anchor=tk.W)
    app.part_var = tk.StringVar(value="Optical test fixture")
    combo = ttk.Combobox(main, textvariable=app.part_var, values=list(PARTS.keys()), state="readonly", width=28)
    combo.pack(fill=tk.X, pady=(0, 8))
    app.part_var.trace_add("write", on_part_change)

    ttk.Label(main, text="Parameters", font=("", 10, "bold")).pack(anchor=tk.W, pady=(8, 0))
    app.params_frame = ttk.Frame(main)
    app.params_frame.pack(fill=tk.BOTH, expand=True, pady=4)

    ttk.Separator(main, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=8)

    ttk.Label(main, text="Export name (without .stl)", font=("", 10, "bold")).pack(anchor=tk.W)
    app.export_name_var = tk.StringVar(value="export")
    ttk.Entry(main, textvariable=app.export_name_var, width=30).pack(fill=tk.X, pady=(0, 4))

    ttk.Label(main, text="Output folder", font=("", 10, "bold")).pack(anchor=tk.W, pady=(4, 0))
    out_row = ttk.Frame(main)
    out_row.pack(fill=tk.X, pady=2)
    app.out_dir_var = tk.StringVar(value=str(OUTPUT_DIR or SCRIPT_DIR / "exports"))
    ttk.Entry(out_row, textvariable=app.out_dir_var, width=36).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
    ttk.Button(out_row, text="Browse", command=choose_dir).pack(side=tk.RIGHT)

    app.export_gcode_var = tk.BooleanVar(value=False)
    ttk.Checkbutton(main, text="Also export G-code (Python-generated)", variable=app.export_gcode_var).pack(anchor=tk.W, pady=4)

    app.generate_btn = ttk.Button(main, text="Generate STL / STEP / G-code", command=do_generate)
    app.generate_btn.pack(pady=12)

    app.status_var = tk.StringVar(value="Choose part, set parameters, then Generate.")
    ttk.Label(main, textvariable=app.status_var, foreground="gray").pack(anchor=tk.W)

    on_part_change()


class App:
    root = None
    part_var = None
    params_frame = None
    entries = {}
    out_dir_var = None
    export_name_var = None
    export_gcode_var = None
    status_var = None
    generate_btn = None


def main():
    app.root = tk.Tk()
    build_ui(app.root)
    app.root.mainloop()


if __name__ == "__main__":
    app = App()
    main()

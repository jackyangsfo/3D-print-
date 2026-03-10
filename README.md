# 参数化 3D 打印件生成 — 使用说明

用 Python 生成 3D 模型并导出为可打印的 STL/STEP/G-code 文件，适合镜头座、相机夹具、MTF 治具、光学支架等参数化零件。支持 **Python 直接生成 G-code**，无需切片软件。支持 **在 Python 内预览 3D 模型**（CadQuery VTK 查看器），无需额外软件。

**参数化光学测试夹具**：输入 sensor size、lens diameter、working distance 三参数，自动生成完整 M12 相机测试座 STL，适用于 AnkerMake 等打印机，面向 camera module 实验室。

**获取项目：** `git clone https://github.com/jackyangsfo/3D-print-.git`

---

## 一、环境准备

- **Python**：建议 **3.11 或 3.12**（cadquery-ocp 暂不支持 Python 3.14）。Windows 可用 `winget install Python.Python.3.12` 安装。

### 1. 创建并激活虚拟环境（如尚未创建）

**Windows (PowerShell)：**
```powershell
cd "path\to\3D print"
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
```

**macOS / Linux：**
```bash
cd "/path/to/3D print"
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

或直接安装全部依赖：

```bash
pip install cadquery meshcut numpy
```

`requirements.txt` 已包含：cadquery、meshcut（G-code 切片）、numpy。

---

## 二、运行脚本生成所有示例模型

在项目目录下、**已激活 venv** 时执行：

```bash
python "3D print.py"
```

默认会生成 STL、STEP 和 G-code。仅需 STL/STEP 时加 `--no-gcode`：

```bash
python "3D print.py" --no-gcode
```

运行后会在项目下生成 **`exports/`** 文件夹，其中包含：

**或用 Tkinter 图形界面：**

```bash
python gui.py
```

- 选择零件类型、修改参数后，可先点 **Preview 3D** 在 CadQuery VTK 窗口中旋转、缩放预览模型（不导出文件）。
- 点 **Generate STL / STEP / G-code** 导出；勾选 **Also export G-code** 可同时生成 Python 切片得到的 G-code。  
Tkinter 为 Python 内置，无需额外安装。

macOS 上若出现 segfault，改用：`./run_gui.sh`（通过 Rosetta 2 运行）。

**仅预览 3D（命令行）：** 不打开 GUI，直接弹出默认零件预览窗口：
```bash
python preview_3d.py
```

| 文件 | 说明 |
|------|------|
| `part_cylinder.stl` / `.step` / `.gcode` | 简单圆柱（垫片/ spacer） |
| `m12_holder.stl` / `.step` / `.gcode` | M12 镜头座 |
| `camera_fixture.stl` / `.step` / `.gcode` | 相机模块外壳/夹具（PCB+镜头孔+安装孔） |
| `lens_spacer.stl` / `.gcode` | 镜头垫圈 |
| `test_jig_block.stl` / `.gcode` | 矩形测试治具块（中心圆孔） |
| `pcba_holder.stl` / `.step` / `.gcode` | PCBA 底板（10×8 cm，2 mm 厚，四角 M2 孔） |
| `m12_optical_test_fixture.stl` / `.step` / `.gcode` | 光学测试夹具（支持 M8/M12/M16/C/CS 镜头规格） |

**光学测试夹具快速生成（支持 M8/M12/M16/C/CS）：**

```bash
python m12_optical_fixture.py
python m12_optical_fixture.py --sensor 12 10 --mount M16 --wd 8 -o my_fixture
python m12_optical_fixture.py -m M8 -s 10 8 -w 5
```

---

## 三、整体流程：从 Python 到打印机

**方式 A（经切片软件）：**
```
Python 脚本 → 生成几何 → 导出 STL/STEP → 切片软件 → G-code → 打印机
```

**方式 B（Python 直接生成 G-code）：**
```
Python 脚本 → 生成几何 → tessellate → meshcut 切片 → 导出 .gcode → 打印机
```
运行 `python "3D print.py"` 或勾选 GUI 中的 "Also export G-code" 即可。需安装 meshcut。

---

## 四、如何把 STL 切片并打印（详细步骤）

### 第一步：打开切片软件并导入 STL

任选其一（按你的打印机品牌选更省事）：

| 软件 | 适用 | 官方下载 |
|------|------|----------|
| **Cura** | 通用，尤其 Ultimaker | **[ultimaker.com/software/cura](https://ultimaker.com/software/cura)** — 选 Windows / macOS (Intel 或 Apple Silicon) / Linux |
| **PrusaSlicer** | 通用，尤其 Prusa | **[prusa3d.com/prusaslicer](https://www.prusa3d.com/prusaslicer/)** — 页内选系统后下载，或 [GitHub Releases](https://github.com/prusa3d/PrusaSlicer/releases) |
| **Bambu Studio** | 通用，尤其 Bambu Lab | **[bambulab.com](https://bambulab.com)** → 顶部 **Support** → **Software** / **Download**，或 [GitHub Releases](https://github.com/bambulab/BambuStudio/releases) |

**直接打开下载页：**

- **Cura**：<https://ultimaker.com/software/cura>
- **PrusaSlicer**：<https://www.prusa3d.com/prusaslicer/>
- **Bambu Studio**：<https://bambulab.com/en/download/studio>（按地区选 en-us / en-ca 等）

下载后安装（Windows 用 .exe，macOS 用 .dmg，Linux 用 AppImage 或包管理器），然后按下面步骤导入 STL。

**导入 STL：**

- **Cura**：菜单 **File → Open File(s)...**，选 `exports` 里的 `.stl`（如 `pcba_holder.stl`）；或把 STL 文件**拖进** Cura 窗口。
- **PrusaSlicer**：**File → Import → Import STL**，选你的 `.stl`；或拖拽 STL 到窗口。
- **Bambu Studio**：**File → Open** 或拖拽 STL 到工作区。

STL 会出现在中间的**预览区**，可旋转、缩放查看。

---

### 第二步：选打印机和材料

1. 在切片软件里选择**你的打印机型号**（若没有，选相近型号或“通用 FDM”）。
2. 选择**材料类型**（如 PLA、PETG、ABS），通常软件会给出预设（温度、速度等）。

---

### 第三步：设置切片参数（常用）

在「标准 / Standard」或「自定义」里可调：

- **层高 (Layer height)**：0.2 mm 常用，要更细腻可 0.12～0.16 mm。
- **填充 (Infill)**：10%～20% 对多数零件够用；受力件可 30%～50%。
- **壁厚 / 轮廓 (Wall line count)**：一般 2～3 层即可。
- **支撑 (Support)**：本项目的零件多为简单几何，多数**不需要**支撑；若有悬空部位，可勾选「Generate support」。

改完后点 **Slice / 切片**（或类似按钮），软件会生成 G-code。

---

### 第四步：切片并得到 G-code

- 点击 **Slice**（或 **切片**）后，软件会计算路径并显示预估**打印时间**和**耗材用量**。
- 预览里可逐层查看，确认没问题再继续。

---

### 第五步：把 G-code 送到打印机

**方式 A：USB 直连**

- 打印机用 USB 连电脑，在切片软件里选 **Print** / **Send to printer**，将 G-code 直接发送到打印机。

**方式 B：SD 卡 / U 盘**

- 切片完成后选 **Save to removable drive** 或 **Export G-code**，把生成的 `.gcode` 文件存到 SD 卡或 U 盘。
- 将卡/盘插入打印机，在打印机屏幕上选择该 G-code 文件，开始打印。

**方式 C：局域网（部分机型）**

- Bambu Lab、部分 Creality 等支持 WiFi，在切片软件里添加打印机后可直接**发送打印**到机器。

---

### 小结

1. 打开 Cura / PrusaSlicer / Bambu Studio → **File → Open** 或拖入 `exports/xxx.stl`  
2. 选打印机 + 材料 → 设层高、填充等 → 点 **Slice**  
3. **Print** 或 **Export G-code** 到 U 盘/SD → 上机打印  

STL 文件路径示例：项目目录下 `exports/pcba_holder.stl`（如 Windows：`C:\...\3D print\exports\pcba_holder.stl`）。

---

## 五、只生成某一种零件或自定义尺寸

在 Python 里可以只调用需要的函数，并传入自己的参数。  
**方式一：** 直接改 `3D print.py` 里 `main()` 的参数后运行。  
**方式二：** 新建脚本，与 `3D print.py` 同目录，先 `import cadquery as cq`，再把下面用到的函数从 `3D print.py` 复制过去，或把 `3D print.py` 重命名为不含空格的模块（如 `model_utils.py`）后 `from model_utils import make_simple_cylinder` 等。

### 1. 简单圆柱

```python
import cadquery as cq

cyl = make_simple_cylinder(diameter=25, height=15)  # 直径 25mm，高 15mm
cq.exporters.export(cyl, "exports/my_cylinder.stl")
```

### 2. M12 镜头座

```python
m12 = make_m12_lens_holder(
    lens_diameter=12,   # 内孔直径 (mm)
    body_diameter=24,   # 外径 (mm)
    height=20,          # 高度 (mm)
)
cq.exporters.export(m12, "exports/my_m12.stl")
```

### 3. 相机夹具（按你的 PCB/镜头/安装孔定制）

```python
generate_camera_fixture(
    sensor_width=10,
    sensor_height=8,
    lens_diameter=12,
    pcb_width=20,
    pcb_height=20,
    pcb_thickness=1.6,
    working_distance=5,
    mounting_hole_diameter=2.2,      # M2 常用 2.2
    mounting_hole_spacing_x=16,
    mounting_hole_spacing_y=16,
    export_name="my_camera_jig",     # 导出 my_camera_jig.stl / .step
)
```

### 4. 镜头垫圈

```python
spacer = make_lens_spacer(
    outer_diameter=20,
    inner_diameter=12,
    thickness=2,
)
cq.exporters.export(spacer, "exports/my_spacer.stl")
```

### 5. 测试治具块

```python
jig = make_test_jig_block(
    width=40,
    depth=30,
    height=15,
    hole_diameter=12,
)
cq.exporters.export(jig, "exports/my_jig.stl")
```

### 6. 光学测试夹具（支持 M8/M12/M16/C/CS）

```python
# M12 (12mm)
generate_m12_optical_test_fixture(sensor_width=10, sensor_height=8, lens_diameter=12, working_distance=5, export_name="m12_fixture")
# M8 (8mm)
generate_m12_optical_test_fixture(sensor_width=8, sensor_height=6, lens_diameter=8, working_distance=5, export_name="m8_fixture")
# M16 (16mm)
generate_m12_optical_test_fixture(sensor_width=12, sensor_height=10, lens_diameter=16, working_distance=8, export_name="m16_fixture")
# C/CS (25.4mm)
generate_m12_optical_test_fixture(sensor_width=16, sensor_height=12, lens_diameter=25.4, working_distance=10, export_name="cs_fixture")
```

### 7. PCBA 底板

```python
make_pcba_holder(
    length=100,
    width=80,
    thickness=2,
    hole_diameter=2.2,
    hole_inset=5,
    export_name="my_pcba",
)
```

**注意：** 导出路径请用**字符串**，例如 `"exports/xxx.stl"`，或 `str(Path("exports") / "xxx.stl")`，否则 CadQuery 会报错。

---

## 六、修改默认参数后一次性生成

直接编辑 **`3D print.py`** 里的 `main()` 函数：

- 改 `make_simple_cylinder(diameter=20, height=10)` 的数字
- 改 `make_m12_lens_holder(...)`、`make_lens_spacer(...)`、`make_test_jig_block(...)` 的参数
- 改 `generate_camera_fixture(...)` 里 PCB 尺寸、镜头直径、安装孔等

保存后重新运行：

```bash
python "3D print.py"
```

新文件会覆盖 `exports/` 里同名的 STL/STEP/G-code。

---

## 七、常见问题

- **`ModuleNotFoundError: No module named 'cadquery'`**  
  先激活 venv，再执行：`pip install cadquery` 或 `pip install -r requirements.txt`。

- **`AttributeError: 'PosixPath' object has no attribute 'split'`**  
  导出时路径必须是字符串，例如 `str(OUTPUT_DIR / "file.stl")`，脚本中已按此修复。

- **macOS 上 segmentation fault**  
  CadQuery/OCP 在 Apple Silicon (arm64) 上可能崩溃。建议：
  1. **GUI**：用 `./run_gui.sh` 替代 `python gui.py`，通过 Rosetta 2 运行。
  2. **命令行**：用 `./run_3d_print.sh` 替代 `python "3D print.py"`。
  3. 安装 x86_64 Python：`arch -x86_64 brew install python`，用该 Python 创建 venv 并安装 cadquery。

- **`ModuleNotFoundError: No module named 'meshcut'`**  
  安装 meshcut：`pip install meshcut`。未安装时脚本仅导出 STL/STEP，不生成 G-code。

- **想导出 OBJ**  
  CadQuery 主要支持 STL/STEP；若需要 OBJ，可用其他库（如 `trimesh`）对 STL 做格式转换。

---

## 八、文件结构

```
3D print/
├── 3D print.py       # 主脚本：定义函数 + main() 生成示例
├── gui.py           # Tkinter 图形界面（含 Preview 3D / Generate）
├── preview_3d.py    # 3D 预览脚本（CadQuery VTK 查看器）
├── parts_config.py   # 零件配置（GUI 与 generate_one 共用）
├── gcode_export.py  # Python G-code 生成（meshcut 切片）
├── generate_one.py  # 子进程生成脚本（macOS GUI 用）
├── m12_optical_fixture.py  # M12 光学测试夹具快速 CLI（三参数）
├── run_gui.sh       # macOS GUI 启动脚本（Rosetta 2）
├── run_3d_print.sh  # macOS 命令行启动脚本（Rosetta 2）
├── requirements.txt # 依赖（cadquery, meshcut, numpy）
├── README.md        # 本说明
├── docs/            # 文档（如 STEP-vs-STL.md）
└── exports/         # 运行脚本后生成
    ├── *.stl        # STL 模型
    ├── *.step       # STEP 模型（部分零件）
    └── *.gcode      # Python 生成的 G-code（可选）
```

---

## 九、M12 光学测试夹具（Camera Module 实验室）

面向 camera module 实验室的 **参数化光学测试夹具**：仅需三参数即可生成完整相机测试座，支持多种镜头规格。

**镜头规格对照：**

| 规格 | 直径 | 常见用途 |
|------|------|----------|
| M8 | 8 mm | 更小的工业镜头 |
| M12 | 12 mm | 工业相机、车载、树莓派相机等 |
| M16 | 16 mm | 稍大的工业镜头 |
| C/CS | 25.4 mm | 监控、安防相机 |

| 参数 | 说明 | 默认 |
|------|------|------|
| sensor_width, sensor_height | 传感器尺寸 (mm) | 10×8 |
| lens_mount | 镜头规格：**M8** (8mm)、**M12** (12mm)、**M16** (16mm)、**C/CS** (25.4mm) | M12 |
| working_distance | 工作距离 (mm) | 5 |

**CLI 快速生成：**
```bash
python m12_optical_fixture.py
python m12_optical_fixture.py -s 12 10 --mount M16 -w 8 -o anker_m16
python m12_optical_fixture.py -s 10 8 -m M8 -w 5
```

**GUI**：选择 "Optical test fixture"，在 **Lens mount** 下拉框选 M8/M12/M16/C/CS，输入参数后 Generate。

**输出**：STL/STEP 可直接导入 AnkerMake、Cura、PrusaSlicer 等切片软件，或勾选 G-code 直接生成可打印文件。

---

## 十、Python 生成 G-code 说明

- **层高**：默认 0.2 mm，可在 `gcode_export.py` 的 `export_part_to_gcode()` 中修改。
- **温度**：默认热床 60°C、喷头 200°C，可按材料调整。
- **适用场景**：简单零件、快速原型；复杂模型建议用 Cura / PrusaSlicer 等专业切片软件。
- **直接打印**：将 `.gcode` 复制到 U 盘/SD 卡，插入打印机即可打印。

---

按上述步骤即可从「改参数 → 运行脚本 → 切片/直接 G-code → 打印」完成参数化 3D 打印流程。M12 光学测试夹具特别适合 camera module 实验室的 MTF、分辨率测试工作流。

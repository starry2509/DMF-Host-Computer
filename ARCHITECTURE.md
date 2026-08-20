# 玻璃基驱动线路板专用驱动器 V2.1.0 — 程序架构

## 1. 总览

本程序为 **PyQt5 桌面应用**，用于 DMF（数字微流控）芯片电极驱动、自动脚本执行、液滴位置检测、三通道温度监控及可选摄像头采集。入口为 `main_windows.py`。

```
main_windows.py (MainWindow)
├── main_window/ui2.py          # 界面布局（UI 类，无业务逻辑）
├── chip/                       # 芯片电极场景
├── serial_driver/              # 串口协议与驱动板通信
├── cam/                        # 摄像头（CAM_ENABLE=1 时加载）
├── logger/                     # 日志
└── utils/path_helper.py        # 资源路径（开发/打包兼容）
```

## 2. 模块职责

| 模块 | 文件 | 职责 |
|------|------|------|
| 入口 | `main_windows.py` | 串口/参数/手动移动/自动表格/液滴检测/温度曲线；连接 UI 与底层 |
| 界面 | `main_window/ui2.py` | 左侧串口与参数、中间 Tab（手动/自动/液滴）、右侧摄像头与温度 |
| 芯片场景 | `chip/DMF_Chip.py` | `QGraphicsScene`：电极加载、鼠标交互、点位编码 `data_transfer` |
| 电极图元 | `chip/Electrode.py` | 单电极绘制；青绿/蓝/绿/橙表示默认/选中/驱动/同时选中驱动 |
| 布局数据 | `chip/chip_layout.py` | 从 `chip_point.csv` 读取电极坐标 |
| 拓扑映射 | `chip/chip_array.py` | `id_array`（行列→电极 ID）、`id_position`（ID→行列） |
| 串口 | `serial_driver/Serialdriver.py` | 封包收发；`drive_cmd*` / `temp_cmd*` / `bottom_cmd*` |
| 摄像头 | `cam/cam_module.py` | 打开/关闭/拍照/录像 |
| 日志 | `logger/log.py` | 界面日志与文件日志 |
| 工具 | `utils/path_helper.py` | `get_resource_path()` |

## 3. 数据流

### 3.1 手动驱动

```
用户操作芯片 (DMF_Chip.mousePressEvent)
  → serialDataSignal（右键/Ctrl 释放后）
  → MainWindow._send_drive_bitmap
  → SerialDriver.drive_cmd6(16 字节位图)
```

移动：↑↓←→ 或界面按钮 → `_move_droplets` → 按 `chip_array` 邻接切换驱动电极 → `drive_cmd6`。

### 3.2 自动脚本

```
Tab2 表格 → QTimer → timer_send_data
  → 解析帧列表 → 清空后按帧设置驱动 → drive_cmd6
  → 可选 camera_logic 开/关
```

支持 Excel（`.xlsx`）保存/加载。

### 3.3 液滴检测

```
drive_cmd3 读当前驱动位图 → 对每位点 3×3 扫描
  → drive_cmd8 单点 + bottom_cmd2 ADC
  → 概率计算 → pyqtgraph 曲线
```

### 3.4 温度（三通道）

```
QTimer(100ms) → temp_cmd7/8/… 读温度与功率
  → pyqtgraph 双 Y 轴曲线；PID/目标温度经 temp_cmd* 下发
```

## 4. 芯片交互约定

| 操作 | 行为 |
|------|------|
| 左键 | 切换选中 |
| Shift+左键 | 切换**固定**：固定后为选中+驱动（紫色），不参与移动，ID 每次下发均包含 |
| 右键 | 单电极驱动（清除其它非固定驱动），立即发串口 |
| Ctrl+右键（可多次） | 入队；**松开 Ctrl** 后清空原非固定驱动，仅对队列内电极驱动并发一次串口 |
| ↑↓←→ / 移动按钮 | 已驱动（非固定）液滴向邻格移动；边界外则清除驱动（消失）；固定电极始终留在位图内 |

颜色：蓝=选中，绿=驱动，橙=选中且驱动；左侧红条=左右逻辑，下侧蓝条=上下逻辑。

## 5. 资源与打包

- 运行时电极布局：`chip/chip_point.csv`
- 图标：`icon/`
- 打包：`build_exe.spec`（PyInstaller）→ 产物勿纳入版本库，执行 `pyinstaller build_exe.spec` 重新生成

## 6. 开发工具（非运行时）

- `tools/dxf_to_csv.py`：从 `chip/chip_shape.dxf` 生成 `chip/chip_point.csv`（需 `dxfgrabber`）

## 7. 文档

- `readme.txt`：操作速查
- `软件操作手册.md`：面向操作人员的完整说明
- `serial_driver/通信协议.md`：串口协议说明

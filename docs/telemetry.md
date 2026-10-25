# 遥测协议与原有Pygame路径

本页保留真实数据协议及旧脚本说明。新版./app的live通过examples/live.json中的input_file配置，默认原生GTK/Cairo；下文./run.sh命令仅对应显式安装的旧Pygame路径。

## 通过 JSON 快照接入真实遥测

```bash
./run.sh automotive --windowed --input-file examples/telemetry.json
```

示例文件只是静态协议样本，文件修改时间超过三秒后会显示 **DATA STALE**。真实适配器至少每三秒发布一次原子快照，建议以 5 Hz 更新。以下六个有限数值字段全部必填：

| 字段 | 单位 / 允许范围 |
| --- | --- |
| `speed` | km/h，0–300 |
| `rpm` | RPM，0–9,000（可视转速环在 8,000 饱和） |
| `temperature` | °C，−40–150 |
| `pressure` | bar，0–20 |
| `voltage` | V，0–60 |
| `signal` | 归一化幅度，−1–1 |

`TelemetrySource` 最多读取 64 KiB，拒绝缺失、非有限或超范围字段，出错时保留上次有效值并标记过期，绝不会把失效的真实数据悄悄换成模拟。请保持树莓派时间准确，数据新鲜度由文件修改时间判断。写入时，在**同一文件系统**创建临时文件，再调用 `os.replace`：

```python
import json
import os
from pathlib import Path

def publish_snapshot(destination, values):
    destination = Path(destination)
    temporary = destination.with_name(destination.name + ".tmp")
    temporary.write_text(json.dumps(values, allow_nan=False))
    os.replace(temporary, destination)
```

每个目标文件只保留一个写入进程。辅助函数接收 `examples/telemetry.json` 所示的完整字典，真实测量由采集适配器提供。渲染留在主线程，串口/蓝牙/USB 读取应放在独立进程中，不能让 GUI 等待 ECU 或 PLC。

## OBD-II、工业与 LVGL 移植

OBD-II 可通过独立适配器结合 `python-obd` 和兼容 ELM327 设备，在支持时读取车速、转速、冷却液温度和电压，明确换算单位后发布快照。压力和归一化信号必须来自真实可用传感器或有明确意义的映射，不能将虚构值标为实时数据。缺失 PID 应显示不可用/过期，协议请求应有超时和重连处理。仓库不提供 OBD-II 驱动，也不会发送车辆控制命令。此演示用于台架原型，行车仪表需要独立验证。

工业遥测可使用独立 Modbus/MQTT/串口适配器，明确工程单位、边界和采样时间戳，再映射到相同协议，或扩展 `Telemetry` 及校验。内置告警阈值只是示例，不是认证控制或保护逻辑。

移植到 LVGL 时，保留采集/校验边界，用 LVGL scale/arc/label/chart 对象替换 `Painter` 与视图绘制方法，在 LVGL 事件/定时器循环中更新，适用时保留单帧缓冲区的 SBS 拆分。MCU 上还需要真实显示/输入驱动、flush 回调、颜色格式和内存预算。仓库名称不代表包含 Python-LVGL 绑定。

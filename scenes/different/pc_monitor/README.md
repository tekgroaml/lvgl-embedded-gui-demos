# 机箱电脑状态屏

--view pc-monitor，双圆：左CPU/内存、右GPU/散热。model.py分别提供自主模拟与真实电脑JSON读取；panels.py只负责显示；scene.py登记工厂/布局/能力，layouts/维护480/720/800映射。

仓库根目录执行：

```bash
./app start --port 1 --shape round --panels 2 --input none --view pc-monitor --layout pc-monitor-sbs-480 --content different --data-source demo
```

演示数据明确标注SIMULATED，不读取Pi自身指标来假装目标电脑。真实CPU/内存/GPU/温度来自目标电脑产生的快照，缺传感器显示“—”。

[完整使用及数据协议](../../../docs/pc-monitor.md)

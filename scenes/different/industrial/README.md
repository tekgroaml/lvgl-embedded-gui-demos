# 双方形泵站

scene.py、model.py、panels.py和layouts/维护软启动/运行/卸载/冷却及过程趋势。卡片等基础组件来自common/components.py。仅demo。

仓库根目录：

```bash
./app start --port 1 --shape square --panels 2 --input none --view industrial --layout industrial-sbs-480 --content different --data-source demo
```

[泵站场景说明](../../../docs/scenarios.md) · [代码结构](../../../docs/architecture.md)

0.7.0中industrial-sbs-480映射升为1.1.0，接受60Hz和约62.825Hz；720/800仍60Hz。不改变信号。已保存旧映射的实例需先stop，再显式start。

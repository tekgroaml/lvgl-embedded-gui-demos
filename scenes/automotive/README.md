# 双圆汽车

scene.py声明功能、布局和工厂，model.py生成联动行驶数据，panels.py绘制车速/RPM与发动机状态；layouts/包含480/720/800映射。

```bash
./app start --port 1 --shape round --panels 2 --input none --view automotive --layout automotive-sbs-480 --content different --data-source demo
```

命令在仓库根目录执行。480布局允许60Hz或当前屏幕原生约62.825Hz，不改信号。汽车仅demo，不使用真实OBD。

[完整场景说明](../../docs/automotive.md) · [代码结构](../../docs/architecture.md)

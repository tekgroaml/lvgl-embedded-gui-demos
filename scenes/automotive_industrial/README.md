# 原有左圆右方混合场景

保留--view automotive-industrial及其原有demo/live JSON协议，不将其改成新的双圆汽车模式。

- model.py：原有混合模拟数据。
- automotive_panel.py / industrial_panel.py：原仪表逻辑唯一实现。
- scene.py：面板、数据能力和布局声明。
- layouts/：三个原有完整SBS映射。
- 共享live JSON读取、校验及新鲜度在common/telemetry.py。

旧gauges/模块仅重新导出这些类，因此旧Pygame启动路径与新原生入口不复制业务实现。

[原数据协议](../../docs/telemetry.md) · [代码结构](../../docs/architecture.md)

# 场景目录

每个场景独立拥有scene.py（声明/工厂）、model.py（模型/模拟数据）、panels.py或面板模块、layouts/（SBS布局）。场景不管理SSH、进程、HDMI配置或锁，不直接访问另一个场景。

| 目录 | --view | 形状 | 数据 |
| --- | --- | --- | --- |
| pc_monitor/ | pc-monitor | 双圆 | PC负载联动demo／目标电脑JSON，可选Windows采集 |
| automotive/ | automotive | 双圆 | 汽车联动demo |
| flight/ | flight | 双圆 | 飞行联动demo |
| industrial/ | industrial | 双方形 | 泵站联动demo |
| automotive_industrial/ | automotive-industrial | 左圆右方 | 保留混合demo/live JSON |

scenes/registry.py显式登记scene.py导出的SCENE。运行器通过统一工厂取得两个面板和数据源，不加入按场景名分支。common/提供配色、绘图组件、SBS裁剪、公共数据读取和声明类型。

新增场景步骤见[架构与扩展规范](../docs/architecture.md)。

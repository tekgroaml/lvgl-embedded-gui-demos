# 公共代码

| 模块 | 职责 |
| --- | --- |
| definition.py | 场景声明、工厂、数据能力及布局版本/刷新率规则 |
| theme.py | 公共配色 |
| drawing.py | CairoPainter、整张SBS画布与各面板形状裁剪 |
| components.py | 圆形底框、模拟标记和指标卡片 |
| simulation.py | 平滑函数与模拟时间有效性检查 |
| snapshots.py | 公共有界普通JSON快照读取，拒绝FIFO/设备和超大文件 |
| telemetry.py | 原混合视图的遥测类型、有界普通JSON文件读取、校验与新鲜度 |

公共代码不包含飞行、汽车或泵站的具体运动规则；它们由各自scenes/<名称>/model.py维护。原生运行器在scene_app/，数据读取在后台线程进行，标准库测试不需要导入GTK/Cairo。

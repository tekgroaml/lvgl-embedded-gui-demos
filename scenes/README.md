# 实际应用场景：同显与异显分目录

每个应用独立拥有scene.py（能力与工厂）、model.py（模拟／数据）、panels.py（界面）和layouts/（明确输入映射）。应用不管理SSH、进程或HDMI设置。

| 分组 | 目录 | --view | 用途 |
| --- | --- | --- | --- |
| 同显／圆形 | [same/round/music_ambient](same/round/music_ambient/README.md) | music-ambient / music-ambient-clone | 音乐律动 |
| 同显／圆形 | [same/round/ambient_light](same/round/ambient_light/README.md) | ambient-light / ambient-light-clone | RGB氛围 |
| 同显／圆形 | [same/round/ambient_clock](same/round/ambient_clock/README.md) | ambient-clock / ambient-clock-clone | 信息钟 |
| 同显／方形 | [same/square/store_signage](same/square/store_signage/README.md) | store-signage / store-signage-clone | 门店促销 |
| 同显／方形 | [same/square/meeting_room](same/square/meeting_room/README.md) | meeting-room / meeting-room-clone | 会议室状态 |
| 同显／方形 | [same/square/parcel_status](same/square/parcel_status/README.md) | parcel-status / parcel-status-clone | 物流取件 |
| 异显／圆形 | [different/flight](different/flight/README.md) | flight | 飞机仪表 |
| 异显／圆形 | [different/automotive](different/automotive/README.md) | automotive | 汽车仪表 |
| 异显／圆形 | [different/pc_monitor](different/pc_monitor/README.md) | pc-monitor | PC机箱 |
| 异显／方形 | [different/smart_home](different/smart_home/README.md) | smart-home | 智能家居 |
| 异显／方形 | [different/pc_monitor_square](different/pc_monitor_square/README.md) | pc-monitor-square | PC机箱 |
| 异显／方形 | [different/industrial](different/industrial/README.md) | industrial | 工业泵站 |
| 异显／混合 | [different/automotive_industrial](different/automotive_industrial/README.md) | automotive-industrial | 原左圆右方 |

同显业务要求--content same，异显要求different。同显的-clone视图输入单幅图像，由硬件复制；不带-clone使用对应*-sbs-*布局。输入不能混用，不按产品名称猜分辨率。

四类串联脚本在[demos/](../demos/README.md)。场景注册使用canonical包路径，能力清单由scripts/update_manifest.py生成。旧scenes/<名称>目录只保留导入转接与迁移说明，不复制model或layouts。旧Python导入仍指向同一实现类。

[架构与扩展](../docs/architecture.md)。

# 按场景分目录与公共代码边界

v0.4.0起将原来堆在gauges目录中的场景拆开；公开命令、已有view、布局ID和JSON协议保持兼容。

## 分层

```text
app + screen-app.json
│
├── scene_app/                        通用运行管理
│   ├── cli.py / runtime.py           命令、启动/停止、日志、锁与socket
│   ├── config.py                     标准参数、私有配置与布局校验
│   ├── display.py                    Wayland/HDMI读取、monitor定位
│   └── worker.py                     GTK生命周期、共用时钟、异步读数、健康
│
├── common/                           可复用基础代码
│   ├── definition.py                 声明结构、面板/数据工厂
│   ├── drawing.py / theme.py          Cairo绘图、SBS裁剪、统一配色
│   ├── components.py                 底框、卡片、模拟标记
│   ├── simulation.py                 平滑与时间校验
│   └── telemetry.py                  有界只读JSON遥测与失效处理
│
├── scenes/
│   ├── registry.py                   显式注册，提供统一工厂
│   ├── pc_monitor/                   双圆机箱PC监控及可选Windows采集
│   ├── automotive/                   双圆汽车
│   ├── flight/                       双圆飞行
│   ├── industrial/                   双方形泵站
│   └── automotive_industrial/         原混合场景
│       （各目录都有声明、模型、面板和自己的layouts/）
│
├── gauges/                           原路径的薄兼容转接与Pygame旧入口
├── scripts/update_manifest.py        从注册表同步能力清单
└── tests/                            模型关系、布局、生命周期、兼容、真实绘图
```

独立项目不导入相邻圆形看板仓库。GUI仍为系统Python+GTK/Cairo，没有新增浏览器、pip、Node或运行框架。场景注册是少量Python声明，不动态扫描或执行任意客户插件。

## 统一场景契约

每个scene.py导出SCENE（common.definition.SceneDefinition），声明：稳定ID、标题、两个面板形状、布局前缀、两页ID、面板工厂、demo工厂、可选live工厂、尺寸、布局版本和已接受刷新率。

面板实现update(dt,snapshot)与draw(painter,snapshot)。数据源实现read(elapsed_seconds)，返回有stale/simulated字段的dataclass。两个面板接收同一快照。标准入口按注册表匹配shape/view/layout/source，不能把某场景的触摸或live能力与另一个场景的布局拼接。

worker不判断汽车/飞行/工业名字，通过注册声明创建面板和数据源。它只负责桌面窗口、全局模拟时钟、线程、就绪/健康和退出。

真实数据模式在首次后台读取前不生成可当作live的模拟占位；失效保留stale状态，不回退demo。通用JSON读取拒绝非普通文件、超过64KiB、缺字段、非有限或越界数据。

## 布局归属与迁移

物理映射从根layouts/迁入scenes/<名称>/layouts/，所有布局ID、映射版本和有效矩形保持原值。新automotive-sbs-*为单独ID，不替代原automotive-industrial-sbs-*。

manifest的layouts路径是包内相对路径；CLI和scene记录引用稳定布局ID，所以文件迁移不要求用户修改既有启动命令。新版加载器只读新目录，升级复制整个仓库，包括common和scenes。旧副本中遗留根layouts文件不会成为第二数据源。

旧gauges.automotive_gauge、industrial_panel、flight_panels、process_panels及scenarios保留兼容导出，相同类只有一个真实实现。run.sh仍可在显式安装旧Pygame依赖后使用。scene_app.painter也只转接common.drawing，避免两套渲染器漂移。

## 新增场景的步骤

1. 新建scenes/<新名称>/model.py、panels.py、scene.py和layouts/。
2. 定义清晰的数据范围、自动模拟关系和真实数据能力；没有实现live就不登记。
3. 在scene.py声明SCENE，在registry.py显式加入注册元组。
4. 为实际支持的尺寸提供布局文件，版本与接受刷新率写在声明中；不猜测硬件能力。
5. 执行python3 scripts/update_manifest.py生成能力清单；CI/开发可用--check验证同步。
6. 增加场景数据关系、兼容和布局测试，并执行tests/render_native.py做实际Cairo检查，更新中英文说明。

这个过程不需要修改worker、CLI参数解析或公共Cairo裁剪。不为每个新场景重复添加进程、日志或SSH连接代码。

## 版本和证据

应用版本升为0.4.0，旧版本实例先正常stop，再更新代码并start。配置结构仍为1，旧布局ID/版本保留；内置context必须使用当前app_version。

2026-11-01飞行双480的物理验收是历史记录，只覆盖其flight设置。本轮汽车与结构重构的软件测试/预览不冒充新实体汽车验收，当前hardware_verified=false。应用与布局不会自动改HDMI时序。

v0.5.0新增pc_monitor，demo/live均由本目录model.py实现；真实数据只来自目标电脑快照，不在通用worker读取Pi传感器。common/snapshots.py提取有界文件读取，原混合场景继续使用相同协议和新鲜度规则。

## v0.6.0产品演示目录

普通场景仍在scenes/，面向卖家拍摄的编排放到demos/product_showcase/，独立维护playlist、矢量图标、标题卡和便捷脚本。通过SceneDefinition.package指定其所属目录，沿用同一标准运行管理，不复制进程/锁/HDMI定位代码。

product-showcase仅demo，数据源按单调时钟生成标题或效果状态，效果页用原场景工厂取得模型/面板。三段共享一个surface，不通过sleep和逐个启动子进程切换。可选on_ready数据源钩子让首张标题卡从可见就绪后起算；其他场景没有此钩子，原来时间规则不变。

播放文件摘要参与幂等配置；requires_real_time让普通demo_speed无法意外缩短产品拍摄时长。来源和场景顺序经过校验，不执行客户提供的shell或live数据。详见[脚本目录说明](../demos/product_showcase/README.md)。

## v0.7.0方形产品演示

scenes/smart_home和scenes/pc_monitor_square拥有方形面板及布局，industrial保留泵站实现。PC方屏通过本目录命名的demo工厂复用pc_monitor模型，不复制散热积分。common/square.py共享页头、风扇、条形指标与10秒有界历史。

demos/square_showcase独立保存playlist及方形介绍框，继承已有产品时间轴、source与品牌／用途分屏介绍。形状校验随source声明，仍只允许各自固定三种demo，禁止递归编排。新的product-showcase-square注册声明有独立布局，worker不加场景分支。原product-showcase默认round不变。

industrial-sbs-480布局升为1.1.0，增加当前输入约62.825Hz的接受；其余映射和全局信号设置不变。不同app版本先stop旧实例，再更新并显式start。

# 单线双屏汽车与工业仪表演示

**v0.7.0 软件预览版**：已按统一规范提供./app入口，默认采用原生Python+GTK/Cairo，和圆形触摸看板使用同类运行方式。无需浏览器、WebKit、LVGL、Pygame、pip或虚拟环境；只有旧run.sh路径需要另装Pygame。

![原生双屏离屏预览](docs/preview-native-sbs.png)

[English](README.md) · [复制到Pi并通过SSH运行](docs/raspberry-pi-ssh.md) · [标准命令](docs/standard-app.md) · [遥测协议](docs/telemetry.md) · [验证记录](docs/verification.md) · [版本记录](CHANGELOG.md) · [双圆汽车](docs/automotive.md) · [场景目录与公共代码](docs/architecture.md)

## 新增：方形双屏三用途演示

智能家居（环境／能源）→PC机箱（CPU／GPU散热）→工业设备（泵站／趋势），每段3秒品牌与应用分屏介绍＋10秒动态效果，一轮39秒循环。页面使用完整方形区域，数据自动变化并明确标为模拟。

```bash
./app stop --port 1
./demos/square_showcase/demo check --port 1
./demos/square_showcase/demo start --port 1
```

[方形演示、安装、独立场景命令和预览](demos/square_showcase/README.md)。默认两块480×480／一个960×480信号，接受60Hz或约62.825Hz，不改显示设置。圆屏原有命令保留；切换前先stop。

## 新增：产品用途串联演示

独立目录demos/product_showcase/，顺序展示“飞机仪表→汽车/摩托仪表→PC机箱监控”。每段图标与文案3秒，然后动态效果10秒，一轮39秒自动循环。全部模拟，一张全屏窗口连续切换。

```bash
./app stop --port 1
./demos/product_showcase/demo check --port 1
./demos/product_showcase/demo start --port 1
./demos/product_showcase/demo stop --port 1
```

上面start用于开始拍摄，stop在结束后执行，不能整段一键粘贴后立即停止。详见[演示脚本与39秒预览](demos/product_showcase/README.md)。支持当前双480圆屏原生约62.825Hz，不新增运行依赖。

## 电脑机箱状态屏

--view pc-monitor，双圆左CPU/内存、右GPU/散热，可自主模拟，也可显示被监控PC的真实JSON。温度与风扇随负载有延迟地变化；缺传感器显示“—”，不会拿Pi数据冒充台式机数据。

```bash
./app stop --port 1
./app start --port 1 --shape round --panels 2 --input none --view pc-monitor --layout pc-monitor-sbs-480 --content different --data-source demo
```

![机箱电脑状态屏](docs/preview-pc-monitor-480.png)

[机箱场景、可选Windows采集与live协议](docs/pc-monitor.md)。Windows脚本只使用系统CIM及已有NVIDIA工具，不要求Python；Pi仍是原生GTK/Cairo。真实Windows/NVIDIA和新实体场景尚待测试。

## 双圆汽车仪表

左屏车速、RPM、挡位和里程；右屏水温、油量、电压和油压。启动demo后自动经历怠速/加速/巡航/制动，数据按场景联动；详情和动态预览见[汽车场景](docs/automotive.md)。

```bash
./app stop --port 1
./app start --port 1 --shape round --panels 2 --input none --view automotive --layout automotive-sbs-480 --content different --data-source demo
```

![双圆汽车](docs/preview-automotive-480.png)

新汽车480布局已接受当前双圆屏960×480@约62.825Hz和60Hz，不强制改信号。汽车实体显示尚待验证，本轮未切换设备上的飞行演示。

## 已接入双480圆屏的实际模式

本次屏幕在接口1上报960×480、约62.825Hz，EDID像素时钟44.43MHz。flight-sbs-480布局v1.1.0已增加对此原生刷新率的接受，不强行改为60Hz。当前树莓派已成功启动飞行演示，用户已确认两屏完整、内容不同且数据自动变化；结果仅适用于这次实测配置，见[验证记录](docs/verification.md)。

## 飞行与泵站自动演示

| 形状 | --view | 双屏内容 | 自动数据逻辑 |
| --- | --- | --- | --- |
| 双圆 | flight | 人工地平仪 + 空速/高度/升降率 | 爬升/巡航/下降/平飞循环，航向与倾角联动 |
| 双方形 | industrial | 泵站运行示意 + 趋势/设备健康 | 待机/启动/运行/卸载/冷却循环，温度滞后、累计流量递增 |

启动demo后无需外接数据或点击，表盘与趋势会持续变化，明确标注模拟。详细布局、数据关系和演示加速见[场景说明](docs/scenarios.md)，其中含加速动态预览。旧左圆右方automotive-industrial仍保留。

```bash
# 双圆飞行，双480×480：一个960×480输入
./app start --port 1 --shape round --panels 2 --input none --view flight --layout flight-sbs-480 --content different --data-source demo

# 双方形泵站：先停止上一场景，再启动
./app stop --port 1
./app start --port 1 --shape square --panels 2 --input none --view industrial --layout industrial-sbs-480 --content different --data-source demo
```

新automotive/flight/industrial仅demo；旧混合视图仍支持demo和live JSON。每种layout另有720/800版本，完整输入为1440×720/1600×800、60Hz。flight-sbs-480另允许本次观察到的约62.825Hz；实体驱动板映射按实测范围确认。

![双圆飞行仪表](docs/preview-flight-480.png)

![双方形泵站](docs/preview-industrial-480.png)

## 原有混合场景

一根HDMI信号线连接双屏驱动板，一个完整画布分成左右两块：左边汽车速度/转速仪表，右边工业波形/指标面板。两个面板显示不同内容，但可使用同一份遥测数据。

原有混合组合为round,square + automotive-industrial；新的双圆使用flight视图，双方形可用smart-home、pc-monitor-square或industrial视图，各有专用绘图而非简单裁切。单屏、触摸和同显暂不支持，传入这些请求会明确拒绝。

仓库名保留lvgl-embedded-gui-demos，不代表使用LVGL。标准入口重新使用原有仪表/遥测业务代码，通过Cairo绘图适配器渲染；旧Pygame入口仍保留。

## 树莓派启动

先按驱动板要求配置好完整输入画布，在Raspberry Pi OS Bookworm/labwc桌面用户的SSH终端执行：

```bash
cd ~/apps/lvgl-embedded-gui-demos
./setup.sh --install-only
./app --version
./app info --json
./app check --port 1 --shape round,square --panels 2 --input none --layout automotive-industrial-sbs-480 --content different
./app start --port 1 --shape round,square --panels 2 --input none --layout automotive-industrial-sbs-480 --content different --data-source demo
./app status --port 1
./app logs --port 1 --follow
./app stop --port 1
```

接口2接线时统一改--port 2。port1/2对应HDMI-A-1/2（Pi4板子HDMI0/1），不是SDL显示索引。panels2代表该**一个输出**内两个面板，不代表两根HDMI线。

原有混合视图布局如下；新flight-sbs-*与industrial-sbs-*使用同样的完整画布尺寸：

| layout | 完整画布与信号 | 每面板 |
| --- | --- | --- |
| automotive-industrial-sbs-480 | 960×480、60Hz | 480×480 |
| automotive-industrial-sbs-720 | 1440×720、60Hz | 720×720 |
| automotive-industrial-sbs-800 | 1600×800、60Hz | 800×800 |

它们是已实现的软件分区，**未认证具体驱动板/产品**。必须先确认硬件接受该完整信号且按左右分区；仅有两个480面板并不保证支持960×480。程序不会改分辨率、刷新率、时序、EDID、缩放或USB映射。不匹配时拒绝启动，不自动拉伸。

## 依赖、桌面和运行管理

默认安装器只补缺失的发行版Python、GTK3/Cairo、GTK layer-shell和wlr-randr包；全已有时无需下载。它不自动启动、不默认安装Pygame，也不需要pip编译。运行以普通用户执行，不加sudo。

SSH自动发现同一用户的唯一Wayland桌面；Pi须已经登录桌面。标准入口按连接器读取几何并将全屏surface绑定唯一monitor，不依赖枚举顺序。镜像歧义、缩放非100%、输出旋转或错误模式会拒绝。

./app start后台启动并等待绘图/数据/窗口定位就绪，SSH断开后可继续运行，前提是图形桌面保持登录；./app run使用相同参数前台调试。日志Ctrl+C只退出查看，stop只停止本项目，不关闭别的屏幕或其他Python程序。

./app restart --port 1使用保存的配置和布局版本。相同参数重复start幂等；同项目同版本可--replace并在失败时尝试恢复；其他项目占口必须先由原项目正常stop。没有自动安装开机启动。

## 从屏幕测试切换

如已装可选screen-test，可先执行screen-test tap-cycle --screen 1，手动观察点击切色；完成后screen-test stop --screen 1，再执行上面的./app start。反过来测试前先./app stop --port 1。screen-test/pi-setting不是本项目依赖。

## 真实JSON遥测

默认demo始终模拟，不根据环境或配置偷偷选择真实数据。live明确读取外部采集器持续更新的JSON文件，不提供采集驱动或任何车辆/工业控制写入。

```bash
cp examples/live.json ~/instruments-live.json
nano ~/instruments-live.json
./app start --port 1 --shape round,square --panels 2 --input none --layout automotive-industrial-sbs-480 --content different --data-source live --config ~/instruments-live.json
```

先将input_file设置为真实采集器的快照路径；相对路径按配置文件目录解析。示例telemetry.json只是一份静态协议样本，三秒后过期，不能当作真实采集器。初次没有新鲜有效数据不报告ready；运行后失效保留最后值并标记DATA STALE/健康degraded，不切回demo。文件读取放在后台线程，不阻塞绘图。

配置支持config_version=1、fps（10～60，默认30）、demo_speed（0.25～4，默认1）和input_file。fps是渲染目标，不是HDMI刷新率。协议、范围、原子更新和采集扩展见[数据文档](docs/telemetry.md)。

## 代码结构与旧入口

```text
app / screen-app.json       标准入口、从注册表生成的精确能力
scene_app/                 通用命令、进程/锁、HDMI与GTK运行管理
common/                    公共配色、Cairo绘图、组件、时间/遥测校验
scenes/
  pc_monitor/              机箱PC状态、demo/live、可选Windows采集
  automotive/              双圆汽车：scene/model/panels/layouts
  flight/                  双圆飞行：scene/model/panels/layouts
  industrial/              双方形泵站：scene/model/panels/layouts
  automotive_industrial/    原混合场景及demo/live声明
  registry.py              统一场景注册和工厂
gauges/                    旧导入路径转接和Pygame兼容入口
scripts/update_manifest.py 同步能力清单，支持--check
tests/                     场景关系、公共运行管理与真实绘图检查
```

如需旧路径，显式./setup.sh --legacy-pygame，再./run.sh automotive --sbs --size 480；该路径仍用SDL索引，不能声称支持标准--port定位。旧临时服务tekgroaml-instruments.service运行时，先systemctl --user stop tekgroaml-instruments.service，再用./app。

v0.2.0曾在Pi完成三种混合画布离屏检查；v0.3.0本机38项测试、六种新场景/尺寸离屏绘图和不同阶段动画检查通过，详情见验证记录。尚未打开新标准入口的实体双屏窗口，也未确认驱动板分割/长期性能。软件预览不等于硬件认证，详见验证记录。

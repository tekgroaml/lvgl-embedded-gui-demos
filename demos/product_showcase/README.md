# 三种产品用途串联演示

这是面向亚马逊客户的产品演示入口，目录独立于scenes/中的实际应用逻辑。使用同一个原生Python/GTK/Cairo窗口，按顺序展示飞机仪表、汽车/摩托仪表和PC机箱监控，切换时不反复启动应用、不退出到桌面。

[English](README_EN.md) · [真实时间循环预览](preview-loop.gif)

## 1. 默认脚本：一轮39秒

| 时间 | 画面 | 两屏信息 |
| --- | --- | --- |
| 0～3秒 | 飞机图标＋FLIGHT SIMULATOR文案 | 左品牌/飞机图标，右飞机仪表用途与两屏指标说明 |
| 3～13秒 | 飞行仪表动态效果 | 复用flight场景，两屏不同仪表 |
| 13～16秒 | 汽车/摩托图标＋CAR / MOTORCYCLE文案 | 左品牌/汽车摩托图标，右仪表用途与两屏指标说明 |
| 16～26秒 | 双圆汽车仪表动态效果 | 复用automotive场景，加速阶段自动变化 |
| 26～29秒 | 机箱图标＋PC CASE MONITOR文案 | 左品牌/机箱图标，右PC监控用途与两屏指标说明 |
| 29～39秒 | PC机箱状态动态效果 | 复用pc-monitor场景，负载、温度和风扇联动 |
| 39秒起 | 返回第一段图标文案 | 持续循环，直到正常stop |

3秒从第一张标题卡实际就绪后起算；软件时间点按单调时钟确定，不依赖帧计数。实际屏幕切换量化到绘制帧，可能有约一个数据/绘制周期的偏差。

全部效果为模拟，标题卡和效果页都有模拟标识。汽车/摩托用途段复用已实现的汽车仪表，用于表达自定义仪表用途，不声称已经连接真实摩托ECU或获得车型适配认证。PC段也不采集真实电脑数据，避免拍摄时混入隐私或离线空白。

## 2. 树莓派上启动

先复制/更新完整仓库到Pi，包含demos、scenes、common和scene_app；项目版本应为0.6.1。更新前先用原版本停止正在运行的实例，不在运行中覆盖代码。

在Pi的SSH终端执行：

```bash
cd ~/apps/lvgl-embedded-gui-demos
./setup.sh --install-only
./app --version
# 停止本项目先前占用的飞行、汽车或PC场景
./app stop --port 1

# 检查和启动产品串联演示，默认每面板480
./demos/product_showcase/demo check --port 1
./demos/product_showcase/demo start --port 1
```

默认完整画布960×480。当前双480圆屏的原生约62.825Hz和60Hz均接受，输出缩放100%、不旋转。不改EDID、像素时钟或显示设置；图标与文案都在各圆形安全区内。

信号线接接口2时统一改--port 2；这是一个HDMI输出的两个圆屏，不是两根HDMI。每面板720/800可加--size 720/800，要求实际完整信号1440×720/1600×800、60Hz且驱动板真正支持。

SSH不能替代桌面登录。Pi须已有同一用户登录的Wayland/labwc会话；程序和现有场景一样自动寻找唯一桌面，不用ssh -X。依赖仍是系统Python/GTK/Cairo，不新增浏览器、视频播放器、pip或图标字体包。

## 3. 状态、日志和停止

```bash
./demos/product_showcase/demo status --port 1
./demos/product_showcase/demo logs --port 1 --follow
./demos/product_showcase/demo stop --port 1
```

status中的telemetry.scene为flight/automotive/pc-monitor，phase为intro/effect，stage_index从0开始，cycle_index为轮次，phase_duration是当前3或10秒；payload为正在演示的模拟快照。

日志Ctrl+C只退出跟随，不停止演示。start后台运行，SSH断开后仍可继续，前提是桌面会话保持登录。未安装开机自启动。前台拍摄/调试可用demo run --port 1，Ctrl+C退出。

演示与单独场景共用标准占用锁。另一个项目占口时不会被强杀；应先正常停止原项目。相同演示重复start幂等；修改文案/节奏后先stop再start，或对本项目显式--replace。

## 4. 等价标准命令

目录入口是标准./app命令的简写，不是另一个运行管理系统：

```bash
./app start --port 1 --shape round --panels 2 --input none --view product-showcase --layout product-showcase-sbs-480 --content different --data-source demo
```

三段共享一个窗口和一个实例。不会通过shell依次执行三个./app start，也不会用sleep、killall或重启桌面来切场景。原有单独flight/automotive/pc-monitor命令保持不变。

## 5. 改文案与演示节奏

playlist.json集中保存英文文案、两屏用途说明、图标名、intro_seconds=3与effect_seconds=10。场景顺序固定为flight→automotive→pc-monitor，防止误引用live或递归演示。修改后正常重启演示；文件内容参与幂等配置摘要。

每段demo_start_seconds只是底层场景模拟的起始时刻：flight35、automotive28、pc-monitor74。由此10秒效果一开始就进入有变化的状态，而不是把整个汽车段耗在怠速、PC段耗在待机。标题卡仍独立显示3秒，效果仍显示10秒，不加快拍摄时钟。

普通应用的demo_speed不能用于此产品演示（必须1），避免把3秒/10秒意外缩短。需要调整产品节奏直接修改playlist时长。文案默认英文；若改成中文，需要目标Pi已有能显示对应字符的字体，未额外下载字体。

## 6. 目录与验证范围

```text
demos/product_showcase/
├── demo / cli.py       便捷标准入口
├── playlist.json       三种用途、标题文案、3秒/10秒节奏
├── playback.py         单调时间轴与现有demo数据源编排
├── panels.py           标题卡和现有场景页面的转接
├── icons.py            本地矢量飞机/汽车摩托/机箱图标
├── scene.py            标准运行器注册声明
├── layouts/            双圆480/720/800软件映射
└── preview-*.png/gif    软件预览，不作为实体屏认证
```

79项标准库测试包括边界时序、39秒循环、第一帧后计时、有效模拟数据、场景重置、文案校验、配置摘要和标准命令分发。三种尺寸的标题/效果/循环边界共21次实际Cairo绘图通过，另生成一轮真实39秒时长GIF。

后续已在目标Pi部署并启动，78项测试通过，44秒监测确认六个阶段和下一轮循环均正常，信号保持960×480@约62.825Hz。实际圆形边缘和相机拍摄仍需现场观察，GIF本身不代替实体显示结果。完整项目复制说明见[项目SSH指南](../../docs/raspberry-pi-ssh.md)。

## v0.6.1介绍页双屏分工

3秒介绍阶段明确异显：左屏只做品牌主视觉（TEKGROAML字标+用途图标+品牌口号），右屏只做用途说明（场景标题、副标题、两块屏幕的指标列表与倒计时），不在两屏重复整套图标和文案。10秒功能页仍直接使用原场景，内容、数据和时长不变。一轮仍为39秒。

本轮逐像素比较三种功能页，修改前后图像完全一致。仅标题卡分工及预览更新，不改变playlist顺序、3秒/10秒时间或设备信号。

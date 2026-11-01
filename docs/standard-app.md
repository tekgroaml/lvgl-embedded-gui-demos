# v0.10.2 双屏标准命令

[演示总目录](../demos/README.md) · [架构](architecture.md) · [安装指南](raspberry-pi-ssh.md)

## 先选择关系和形状

| 关系／形状 | 示例启动命令 | 默认完整输入 |
| --- | --- | --- |
| 同显圆形 | ./demos/same/round/demo start --port 1 | 480×480硬件clone |
| 同显方形 | ./demos/same/square/demo start --port 1 | 480×480硬件clone |
| 异显圆形 | ./demos/different/round/demo start --port 1 | 960×480 SBS |
| 异显方形 | ./demos/different/square/demo start --port 1 | 960×480 SBS |

四种脚本均为品牌与场景介绍3秒、动态效果10秒、三场景39秒循环。同显介绍／效果两屏一致；异显介绍左品牌、右用途，效果两屏不同。方形同显为门店促销、会议室状态和物流取件；圆形同显为音乐、RGB氛围、信息钟。

## 生命周期

完整仓库根目录、已登录桌面的普通用户在SSH中执行：

```bash
./app --version
./app info --json
# 切换前停止原实例
./app stop --port 1
./demos/same/square/demo check --port 1
./demos/same/square/demo start --port 1
```

后续按需分别执行：

```bash
./demos/same/square/demo status --port 1
./demos/same/square/demo logs --port 1 --follow
./demos/same/square/demo restart --port 1
./demos/same/square/demo stop --port 1
```

run与start参数相同，用于前台调试。start后台运行，SSH断开后继续，但桌面要保持登录。restart使用保存参数，不猜新接屏幕；换板先stop、check、start。同项目同版本可显式--replace，失败尝试回退；跨版本先停止旧版。另一个项目占端口时不强杀。

每个脚本接受--size 480/720/800。同显可加--signal clone或sbs，默认clone；异显始终SBS。--port 1/2指HDMI-A-1/2（Pi4板标HDMI0/1），不是左／右屏，两个面板共享一根HDMI。

## 标准等价命令

```bash
# 方形同显，硬件复制
./app start --port 1 --shape square --panels 2 --input none --view product-showcase-same-square --layout product-showcase-same-square-clone-480 --content same --data-source demo
```

```bash
# 圆形同显，硬件复制
./app start --port 1 --shape round --panels 2 --input none --view product-showcase-same --layout product-showcase-same-clone-480 --content same --data-source demo
```

```bash
# 方形异显
./app start --port 1 --shape square --panels 2 --input none --view product-showcase-square --layout product-showcase-square-sbs-480 --content different --data-source demo
```

```bash
# 圆形异显
./app start --port 1 --shape round --panels 2 --input none --view product-showcase --layout product-showcase-sbs-480 --content different --data-source demo
```

每条命令是独立选择，切换前stop；不要整段全部粘贴。旧入口demos/product_showcase/demo、square_showcase/demo、same_showcase/demo仍可用，推荐新分组路径。

## 单独应用

所有应用使用--panels 2 --input none，shape/content必须与profile匹配。省略view可从显式layout推导，不能仅按形状猜业务。

| 形状／content | view | layout前缀 | source |
| --- | --- | --- | --- |
| 圆形／same | music-ambient | music-ambient-sbs-* | demo |
| 圆形／same | ambient-light | ambient-light-sbs-* | demo |
| 圆形／same | ambient-clock | ambient-clock-sbs-* | demo |
| 方形／same | store-signage | store-signage-sbs-* | demo |
| 方形／same | meeting-room | meeting-room-sbs-* | demo |
| 方形／same | parcel-status | parcel-status-sbs-* | demo |
| 圆形／different | flight | flight-sbs-* | demo |
| 圆形／different | automotive | automotive-sbs-* | demo |
| 圆形／different | pc-monitor | pc-monitor-sbs-* | demo/live |
| 方形／different | smart-home | smart-home-sbs-* | demo |
| 方形／different | pc-monitor-square | pc-monitor-square-sbs-* | demo |
| 方形／different | industrial | industrial-sbs-* | demo |
| round,square／different | automotive-industrial | automotive-industrial-sbs-* | demo/live |

同显应用均另有view=<名称>-clone和layout=<名称>-clone-*，输入单幅方形图像。比如：

```bash
./app start --port 1 --shape square --panels 2 --input none --view meeting-room-clone --layout meeting-room-clone-480 --content same --data-source demo
```

## 几何和刷新率

SBS完整尺寸为960×480／1440×720／1600×800；clone为480×480／720×720／800×800。同显矩形通过硬件复制或同一软件光栅保证同帧；异显为两个独立区域。

方形同显只声明60Hz，尚无硬件验收。圆形同显480的clone接受60／约62.811／约71.295Hz，SBS接受60／约62.825Hz；新版本不将这些速率自动用于方形。其他具体profile以info清单与布局为准。scale必须1、输出无旋转。程序不修改HDMI时序、EDID、分辨率、背光或USB触摸映射。

同显／异显、形状、view、布局、source不匹配会拒绝。单屏和触摸暂不实现。布局version与app_version独立，旧私有context仍受版本校验。方形硬件需先配置正确完整输入，不能把软件布局当硬件识别。

## 数据与可选工具

demo始终使用模拟值，不联网真实价格、日历、物流、天气或声音。产品脚本demo_speed须为1。独立PC和混合场景的live为显式JSON协议，失效标记stale，不回退demo，详见[PC指南](pc-monitor.md)与[遥测](telemetry.md)。

可选screen-test已占用时先screen-test stop --screen 1，再启动应用。pi-setting并非本项目依赖。

0.10.1补充：此次新接入方形同显板上报480×480@62.811001Hz。clone-480布局现接受60和约62.811Hz，映射升为1.1.0；SBS与720/800仍保持60Hz。使用当前实际输入启动，不更改时序。

0.10.2圆屏兼容：本次新接入板首选480×480@约71.295Hz，EDID像素时钟25.21MHz。圆形clone-480映射升为1.1.0，接受60／约62.811／约71.295Hz；方形、SBS和其他尺寸不扩大范围。启动保留现有信号，不改时序。

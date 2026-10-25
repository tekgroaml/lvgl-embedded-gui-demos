# 将双屏异显应用复制到树莓派，通过SSH运行

本指南与本仓库一起发布，可单独使用，不依赖application总仓库、圆形看板、pi-setting或未来screen-app。复制的是应用程序，**不是重新烧录TF卡**。

[English](raspberry-pi-ssh_EN.md) · [项目README](../README_CN.md) · [标准命令](standard-app.md)

## 1. 准备和执行位置

Pi已经联网、启用SSH，并用同一普通用户登录Bookworm/labwc Wayland图形桌面。SSH/控制台本身不会创建桌面。驱动板已按产品资料配置正确输入与左右区域，100%缩放、不旋转整张画布。

本项目当前左圆形汽车仪表、右方形工业面板，不支持双圆、触摸或同显。以双480软件布局举例，完整输入为960×480、60Hz；必须确认真实驱动板支持，不能只因有两块480面板就假设它接受960×480。

下例pi@raspberrypi.local是部署占位，替换成自己的用户名、主机名/IP。第一次连接核对主机指纹并正常认证，不把密码写进命令。

| 执行位置 | 用途 |
| --- | --- |
| Mac终端 | 上传项目、建立SSH |
| Pi的SSH终端 | 安装、预检、启动、日志、停止与更新 |

## 2. Mac：复制整个项目

在Mac进入包含lvgl-embedded-gui-demos文件夹的父目录：

```bash
ssh pi@raspberrypi.local 'mkdir -p ~/apps/lvgl-embedded-gui-demos'
rsync -av --exclude=.git --exclude=.venv --exclude=__pycache__ --exclude=secrets lvgl-embedded-gui-demos/ pi@raspberrypi.local:~/apps/lvgl-embedded-gui-demos/
ssh pi@raspberrypi.local
```

必须复制app、scene_app、gauges、layouts和screen-app.json等完整代码，不只复制一张图或一个.py。源目录尾部/表示复制内容；不复制Mac虚拟环境。私有采集数据放在Pi用户目录的单独位置。

只有远端已发布的版本才可通过Git取得。若选择Git方式，作为rsync的替代，在Pi执行：

```bash
sudo apt-get update
sudo apt-get install -y git
mkdir -p ~/apps
git clone https://github.com/tekgroaml/lvgl-embedded-gui-demos.git ~/apps/lvgl-embedded-gui-demos
```

只在目标目录不存在时clone。尚未推送的本地改造必须复制，不能假设git pull已经能下载。

## 3. Pi SSH：安装和核对版本

```bash
cd ~/apps/lvgl-embedded-gui-demos
chmod +x app setup.sh run.sh
./setup.sh --install-only
./app --version
./app info --json
```

本版版本0.2.0。安装器只补缺失的发行版Python/GTK/Cairo/layer-shell/wlr-randr包；全部已有则无需下载。APT可能请求sudo，但运行app不要sudo。默认不安装Pygame，不创建虚拟环境，也不自动启动。

如果以前使用过旧文档的临时Pygame服务，先停止该服务；没有旧服务则跳过：

```bash
systemctl --user stop tekgroaml-instruments.service
```

前台旧run.sh也应正常退出，避免不经过标准租约的旧窗口覆盖新画面。新版./app能发现旧临时服务活跃并拒绝冲突。

## 4. Pi SSH：预检与启动

假设信号线接在接口1、硬件已设置960×480、60Hz：

```bash
./app check --port 1 --shape round,square --panels 2 --input none --layout automotive-industrial-sbs-480 --content different
./app start --port 1 --shape round,square --panels 2 --input none --layout automotive-industrial-sbs-480 --content different --data-source demo
```

端口1/2对应Linux HDMI-A-1/2（Pi4板子HDMI0/1）。如果接接口2，将所有命令--port改为2。panels2是同一信号口内的左右面板，不是连接两个HDMI。

双720/双800软件布局分别用automotive-industrial-sbs-720/800，完整画布分别1440×720/1600×800，均要求实际60Hz、100%缩放。只在驱动板和产品实际支持时选择。check不改分辨率，错误模式会打印期望值并拒绝，不强制套用兼容时序。

新版不需要指定SDL --display，也不需要虚拟环境。启动自动寻找同用户唯一Wayland会话。如多会话，可只读列出socket：

```bash
python3 - <<'PY'
import os
from pathlib import Path
for item in sorted((Path('/run/user')/str(os.getuid())).glob('wayland-*')):
    if item.is_socket():
        print(item.name)
PY
```

确认目标后设置实际的WAYLAND_DISPLAY，例如export WAYLAND_DISPLAY=wayland-0；无socket则先登录桌面，不猜DISPLAY=:0，不用ssh -X。仅有SSH连接不代表图形应用可用。

## 5. 状态、日志和停止

```bash
./app status --port 1
./app logs --port 1 --follow
```

日志跟随Ctrl+C只退出查看，应用不停止。继续执行：

```bash
./app restart --port 1
./app stop --port 1
```

start在后台等待实际绘图、数据和窗口定位就绪后返回。保持桌面用户登录时，SSH断开后可继续运行；重新SSH进入同目录即可管理。Pi重启或退出桌面后不承诺恢复，本版不自动安装开机启动。

前台调试可先stop，再把同一启动参数中的start换成run；Ctrl+C结束前台run。不要把run当作断开SSH后的持续方案，也不要killall python。stop关闭该口的整个SBS画布，即两面板一起退出，只影响本项目拥有的实例。

## 6. 先测试显示，再切换到演示

若已装可选screen-test，可先./app stop --port 1，再screen-test pattern --screen 1或screen-test cycle --screen 1 --interval 5。手动观察完整画布和实体面板；测试完成后：

```bash
screen-test stop --screen 1
./app start --port 1 --shape round,square --panels 2 --input none --layout automotive-industrial-sbs-480 --content different --data-source demo
```

工具只是可选准备方法，程序不依赖它。单线双屏的--screen 1仍指一个HDMI输出，不是panel1。若另一个项目正在该口运行，先用原项目的正常停止命令退出，本项目不会强杀。

## 7. 真实遥测、更新与排查

live通过--config指定的JSON中input_file读取采集快照，示例examples/live.json。路径相对该配置文件目录，需用户填写真实位置；六个字段须持续原子更新。examples/telemetry.json是静态样本，三秒后会变旧，不能作为真实采集器。首次无有效新鲜数据不ready，运行后失效标DATA STALE，不换模拟。完整协议见[数据文档](telemetry.md)。

更新先在Pi停止本项目，再回Mac重复rsync；重新SSH检查版本、布局和依赖，执行check/start。不要更新正在运行的代码后声称还能恢复旧二进制；保留采集器及私有配置。

| 现象 | 处理 |
| --- | --- |
| 缺依赖 | 在Pi运行新版安装脚本；不要复制Mac的.venv或改用sudo运行 |
| SSH能连但无桌面 | 确认同一用户已登录Wayland桌面，socket真实存在 |
| 输出/模式不符 | 按实际产品资料先配置完整SBS信号，应用不会强制修改 |
| 布局不支持 | 使用info声明的左圆右方布局，双圆/触摸/同显尚未实现 |
| 口被别的应用占用 | 用原项目正常stop，不能用本项目强制替换它 |
| 旧临时服务冲突 | 停止tekgroaml-instruments.service；不重复创建旧systemd-run服务 |
| 左右颠倒、边缘缺失 | 对照驱动板分区/排线；物理映射未认证，不能只凭软件PNG判断 |
| JSON过期 | 检查真实采集器的六字段、范围、文件时间与持续更新 |

## 8. 软件验证与旧入口

```bash
python3 -m unittest discover -s tests -v
python3 tests/render_native.py --size 480 --output /tmp/instruments-480.png
```

离屏生成PNG不显示在实体面板，也不证明驱动板拆分正确。当前只有软件预览，物理双屏窗口及长期表现待验收。

仍需原有Pygame时，显式./setup.sh --legacy-pygame，随后./run.sh automotive --sbs --size 480。这个旧路径仍依赖SDL从0枚举，不能将其--display直接按port减一映射；默认./app不使用它。详情见[标准命令](standard-app.md)。

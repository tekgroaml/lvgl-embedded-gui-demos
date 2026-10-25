# 将单线双屏仪表部署到树莓派，通过SSH运行

本指南独立于application总仓库，不要求安装pi-setting或未来screen-app。复制的是应用文件，不是重新烧录TF卡。

[English](raspberry-pi-ssh_EN.md) · [项目说明](../README_CN.md)

当前真实入口是run.sh，**尚未提供标准./app命令**。实际渲染器为Pygame；--sbs是一张宽画布，左汽车仪表、右工业面板，固定异显，没有同显或触摸操作逻辑。

## 1. 准备

以下步骤以Raspberry Pi OS Bookworm桌面、labwc/Wayland为例。Pi联网并启用SSH，目标用户已登录图形桌面；SSH本身不会创建桌面。

双480×480的SBS软件模式要求桌面为960×480、100%缩放、不旋转整张画布。单线双屏驱动板须真正支持该输入/分割方式；实际产品可能需要其他模式，先按厂家说明配置，不从两个面板尺寸直接推断。右工业页面使用方形四角，双圆面板可能裁掉内容。

Mac负责复制文件和建立SSH连接；安装、运行和日志命令在Pi的SSH终端中执行。下例pi@raspberrypi.local必须替换成实际Pi用户名与主机名/IP，文档不包含密码。

## 2. Mac：复制完整项目

Mac终端进入包含lvgl-embedded-gui-demos目录的父目录：

```bash
ssh pi@raspberrypi.local 'mkdir -p ~/apps/lvgl-embedded-gui-demos'
rsync -av --exclude=.git --exclude=.venv --exclude=__pycache__ --exclude=secrets lvgl-embedded-gui-demos/ pi@raspberrypi.local:~/apps/lvgl-embedded-gui-demos/
ssh pi@raspberrypi.local
```

不要只传gauges中的某一个.py。项目依赖run.sh、gauges包及requirements.txt；不要复制Mac上的.venv，Pi需要安装自身架构的依赖。首次SSH请按本机提示核对指纹并认证。

远端已发布时也可在Pi安装git后，使用`git clone https://github.com/tekgroaml/lvgl-embedded-gui-demos.git ~/apps/lvgl-embedded-gui-demos`替代复制。目标目录必须尚不存在；未推送的本地代码无法通过clone/pull获取。

若选择GitHub获取方式，先在Pi SSH终端执行下面步骤；不要在已完成rsync的同名目录再次clone：

```bash
sudo apt-get update
sudo apt-get install -y git
mkdir -p ~/apps
git clone https://github.com/tekgroaml/lvgl-embedded-gui-demos.git ~/apps/lvgl-embedded-gui-demos
```

## 3. Pi：安装，不自动启动

现在位于Pi的SSH终端：

```bash
cd ~/apps/lvgl-embedded-gui-demos
chmod +x setup.sh run.sh
./setup.sh --install-only
.venv/bin/python -c 'import pygame; print(pygame.version.ver)'
```

安装器通过sudo安装APT依赖并创建Pi本地.venv，必要时安装固定版本Pygame。运行不要加sudo，不要把Pi虚拟环境复制回Mac。没有--install-only时旧安装器会立即启动单屏，初次SSH部署不要省略。

## 4. Pi：明确目标Wayland桌面

本项目还没有自动发现会话的标准入口。先查看当前用户真正存在的Wayland socket：

```bash
export XDG_RUNTIME_DIR="/run/user/$(id -u)"
python3 - <<'PY'
import os
from pathlib import Path
for item in sorted(Path(os.environ['XDG_RUNTIME_DIR']).glob('wayland-*')):
    if item.is_socket():
        print(item.name)
PY
```

如果输出wayland-0，下面可按原样使用；否则将其替换为实际目标socket名。多个会话需先确认目标，无socket需先登录桌面，不能通过猜测变量创建桌面。

```bash
export WAYLAND_DISPLAY=wayland-0
export SDL_VIDEODRIVER=wayland
export DBUS_SESSION_BUS_ADDRESS="unix:path=$XDG_RUNTIME_DIR/bus"
```

不使用ssh -X，不填猜测的DISPLAY=:0。本说明只覆盖Wayland；X11需要另外核实实际DISPLAY/XAUTHORITY，不能照抄这里的会话变量。

读取SDL能看到的画布：

```bash
.venv/bin/python - <<'PY'
import pygame
pygame.display.init()
for index, size in enumerate(pygame.display.get_desktop_sizes()):
    print(index, size)
pygame.display.quit()
PY
```

下面示例假设**已确认SDL索引0是960×480的目标**。--display从0开始，是SDL索引，不等于Linux HDMI编号；不能用接口1减一自动认定目标。相同尺寸多个输出时，当前程序不能提供可靠的连接器映射，需先人工确认，首轮可只连接待测产品。

## 5. Pi：前台运行，确认实际画面

```bash
./run.sh automotive --sbs --size 480 --display 0
```

确认左汽车/右工业、边缘完整。此命令占用SSH前台；Ctrl+C或屏幕上的键盘Esc/Q退出，SSH断开后不承诺继续运行。

--size 720要求实际桌面/驱动板支持1440×720。--fps 30只限制渲染负载，不是HDMI刷新率设置，不能用来修复信号闪烁。没有--input-file时使用模拟遥测，不控制实际车辆或工业设备。

## 6. Pi：后台运行，断开SSH后继续

确认前台已退出后，用用户systemd托管**本项目**。仍在同一个已设置Wayland变量的Pi SSH终端与项目目录执行：

```bash
systemd-run --user --unit=tekgroaml-instruments --collect --property=Type=exec --property="WorkingDirectory=$PWD" --setenv="XDG_RUNTIME_DIR=$XDG_RUNTIME_DIR" --setenv="WAYLAND_DISPLAY=$WAYLAND_DISPLAY" --setenv="SDL_VIDEODRIVER=$SDL_VIDEODRIVER" --setenv="DBUS_SESSION_BUS_ADDRESS=$DBUS_SESSION_BUS_ADDRESS" "$PWD/run.sh" automotive --sbs --size 480 --display 0
```

创建的是临时用户服务，不是项目已实现./app，也不是开机自启动。命令返回表示进程已执行，不证明图像正确；仍需查看实体屏幕和日志。桌面保持登录时，断开SSH后服务可继续运行。Pi重启或用户桌面退出后的恢复不在此方案承诺内。

```bash
systemctl --user status tekgroaml-instruments.service
journalctl --user -u tekgroaml-instruments.service -n 50 --no-pager
journalctl --user -u tekgroaml-instruments.service -f
```

日志跟随按Ctrl+C退出不会停止服务。停止本项目：

```bash
systemctl --user stop tekgroaml-instruments.service
```

--collect使停止后的临时unit可被回收；status提示unit不存在可表示它已结束，历史journal仍可查询。再次启动可重新执行本节systemd-run命令；不要重复启动同名仍运行unit，也不使用killall python。若改变配置，先stop再重新启动。

## 7. 更新与排查

更新前在Pi停止上述unit及前台实例，回Mac重复rsync，再SSH进入项目。依赖变化时重跑安装步骤，重新设置/确认实际会话与SDL索引，再运行。

```bash
# 无桌面软件检查，不会显示实体屏幕
./run.sh automotive --sbs --headless --frames 180 --screenshot /tmp/instruments-sbs.png
```

| 现象 | 检查 |
| --- | --- |
| 找不到Pygame/.venv | 在Pi执行安装，不复制Mac虚拟环境 |
| SSH运行无显示设备 | 当前用户是否已登录Wayland桌面，socket和SDL变量是否正确 |
| 桌面尺寸不符 | SDL所选输出是否为960×480/1440×720，缩放与驱动板模式是否正确 |
| 左右内容裁切或颠倒 | 对照驱动板A/B区域及接线；右工业页不是圆形安全布局 |
| 临时unit已存在 | 查看旧服务状态，停止后再启动 |
| systemctl --user无法连接总线 | 确认是桌面同一普通用户、有用户systemd/DBus会话，不改用sudo运行 |
| JSON数据过期 | 检查真实采集快照的内容、权限和持续原子更新，示例文件不是数据采集器 |

真实遥测协议与告警边界见[README](../README_CN.md#通过-json-快照接入真实遥测)。本指南没有自动配置显示时序或触摸映射，也不代表已通过特定Pi/驱动板实测。

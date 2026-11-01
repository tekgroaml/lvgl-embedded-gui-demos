# 将完整项目写入树莓派并通过SSH运行

[English](raspberry-pi-ssh_EN.md) · [四类演示](../demos/README.md) · [标准命令](standard-app.md)

v0.10.0应用代码已经区分同显／异显、圆形／方形。先按驱动板说明配置正确HDMI完整输入；本项目不修改显示分辨率、时序、EDID或触摸映射。

## 1. 前提

树莓派安装带桌面的Raspberry Pi OS Bookworm/labwc，普通用户已登录Wayland桌面。SSH与桌面使用同一用户。无鼠标也可由SSH操作，但只有SSH登录不能代替图形桌面登录。当前仅实现两个无触摸面板共享一个HDMI输入。

--port 1/2对应HDMI-A-1/2（Pi4板标HDMI0/1），不是左／右屏。SBS和硬件clone需要不同输入，详见后文。

## 2. 首次从GitHub安装

SSH到自己的Pi地址后：

```bash
git clone https://github.com/tekgroaml/lvgl-embedded-gui-demos.git ~/apps/lvgl-embedded-gui-demos
cd ~/apps/lvgl-embedded-gui-demos
./setup.sh --install-only
./app --version
./app info --json
```

须为包含所选场景的版本，方形同显需要0.10.0及后续兼容版。安装器只补缺失的系统Python、GTK、Cairo、layer-shell和wlr-randr，全部已有时无需下载。安装APT可能请求sudo；运行app不用sudo。默认不安装Pygame、pip、浏览器或虚拟环境。

## 3. 已有安装升级

先在Pi用旧版本正常停止，不要覆盖正在运行的代码：

```bash
cd ~/apps/lvgl-embedded-gui-demos
./app stop --port 1
# 另一接口若也运行本项目，则也先正常stop
```

Git克隆副本可git pull --ff-only，再./setup.sh --install-only。建议备份旧目录，出错时可恢复。若有自己的改动先保存，不用强制reset。

开发副本可从Mac／Linux完整仓库根目录复制，用自己的Pi地址替换raspberrypi.local：

```bash
ssh pi@raspberrypi.local 'mkdir -p ~/apps/lvgl-embedded-gui-demos'
rsync -av --exclude=.git --exclude=.venv --exclude=__pycache__ --exclude=secrets ./ pi@raspberrypi.local:~/apps/lvgl-embedded-gui-demos/
```

必须包含common、scenes、demos、scene_app、scripts和screen-app.json，不能只复制一个程序文件。旧目录中的多余文件不会作为布局来源，新注册表只引用canonical目录。不要将运行数据、密码或私有配置放入公共仓库。

## 4. 选择四类演示

| 形状／显示关系 | 脚本 | 三种用途 |
| --- | --- | --- |
| 圆形同显 | ./demos/same/round/demo | 音乐、RGB氛围、信息钟 |
| 方形同显 | ./demos/same/square/demo | 门店促销、会议室、物流取件 |
| 圆形异显 | ./demos/different/round/demo | 飞机、汽车、PC机箱 |
| 方形异显 | ./demos/different/square/demo | 家居、PC机箱、工业泵站 |

每种都有独立README安装说明。统一为品牌与场景介绍3秒、动态应用10秒、三组39秒循环。例如方形同显：

```bash
cd ~/apps/lvgl-embedded-gui-demos
./demos/same/square/demo check --port 1
./demos/same/square/demo start --port 1
```

同显默认--signal clone，单幅480×480由板子复制到两屏。实际是960×480 SBS板时，两条命令都加--signal sbs。异显始终使用SBS。同显介绍和效果两屏相同；异显保留左品牌、右用途介绍。

--size 480/720/800表示每面板尺寸，完整输入分别是size×size（clone）或2×size×size（SBS）。方形同显软件只声明60Hz，尚未实测硬件；圆形480保留历史实测的clone约62.811Hz或SBS约62.825Hz。不同硬件先按实际信号匹配，程序不会自动调整。要求缩放100%、输出不旋转。

## 5. 状态、日志、重启和停止

```bash
./demos/same/square/demo status --port 1
./demos/same/square/demo logs --port 1 --follow
./demos/same/square/demo restart --port 1
```

start后台启动并等待真实窗口、数据及定位就绪。SSH退出后继续播放，图形桌面须保持登录。Ctrl+C退出日志查看，不停止应用。restart按保存的配置，不按新硬件自动更换布局。换板先stop，再check/start。结束时单独执行：

```bash
./app stop --port 1
```

同项目同版本可显式--replace；失败尝试恢复旧场景。不同app版本先正常停止旧版，不能以--replace绕过升级规则。另一个项目占端口时由原项目正常stop，不强杀不明进程。没有安装开机自动启动。

## 6. 常见问题

- 无唯一Wayland会话：先登录图形桌面。同一用户有多个会话时检查/run/user/自己的UID/wayland-*，明确设置实际WAYLAND_DISPLAY，不猜DISPLAY=:0，也不用ssh -X。
- 输入宽高不匹配：确认是SBS还是clone；单幅480×480和双宽960×480不可混用。错误时应用拒绝启动，不自动拉伸。
- 刷新率／缩放不匹配：先按驱动板资料配置系统输出，再运行应用；不要因为面板尺寸相同而复制另一个产品时序。
- 端口占用：先正常停止旧场景。若装有可选screen-test，先screen-test stop --screen 1；pi-setting不是本项目依赖。
- layout/app_version变化：重新明确选择新布局启动；私有context仍要求当前版本，不直接改版本字段绕过校验。
- 同显只有一块亮：软件截图不能证明两个实体面板都收到了信号。检查供电、驱动板和两面板排线；硬件clone只有一个逻辑输出是正常的。

所有产品脚本使用标识清楚的模拟数据，不读取真实音乐、天气、价格、日历或订单。需要真实PC数据时使用专门的[PC JSON协议与采集说明](pc-monitor.md)，不要把demo当真实传感器。[验证范围](verification.md)区分软件预览和实体验收。

0.10.0本轮在显示屏断开后仅本地实现、验证和提交，未连接、更新或启动树莓派。

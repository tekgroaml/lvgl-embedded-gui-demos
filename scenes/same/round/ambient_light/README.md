# 双圆同显RGB氛围灯

三条鲜艳RGB光带流动、颜色渐变、呼吸亮度模拟。亮度百分比不控制屏幕硬件背光。

按[SSH指南](../../../../docs/raspberry-pi-ssh.md)复制完整0.9.0仓库到~/apps/lvgl-embedded-gui-demos并执行./setup.sh --install-only，不要只复制本目录。Pi桌面保持登录，普通用户在SSH中：

```bash
cd ~/apps/lvgl-embedded-gui-demos
./app stop --port 1
./app start --port 1 --shape round --panels 2 --input none --view ambient-light-clone --layout ambient-light-clone-480 --content same --data-source demo
```

停止用./app stop --port 1。默认示例适合单幅480×480、60／约62.811／约71.295Hz的硬件同显板。SBS板使用view=ambient-light、layout=ambient-light-sbs-480，输入960×480、60或约62.825Hz。另有720/800软件布局，须实际硬件兼容。程序不改变显示信号。

自动变化，无触摸、联网、音频采集或播放。代码按scene/model/panels/layouts分层，公共组件来自common/neon.py。[三用途同显脚本与预览](../../../../demos/same/round/README.md)。

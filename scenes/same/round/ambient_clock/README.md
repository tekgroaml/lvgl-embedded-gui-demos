# 双圆同显桌面信息钟

彩色表盘、模拟指针和数字时间、示例天气。不是树莓派真实时区或网络天气，界面明确标记DEMO TIME。

按[SSH指南](../../../../docs/raspberry-pi-ssh.md)复制完整0.9.0仓库到~/apps/lvgl-embedded-gui-demos并执行./setup.sh --install-only，不要只复制本目录。Pi桌面保持登录，普通用户在SSH中：

```bash
cd ~/apps/lvgl-embedded-gui-demos
./app stop --port 1
./app start --port 1 --shape round --panels 2 --input none --view ambient-clock-clone --layout ambient-clock-clone-480 --content same --data-source demo
```

停止用./app stop --port 1。默认示例适合单幅480×480、60／约62.811／约71.295Hz的硬件同显板。SBS板使用view=ambient-clock、layout=ambient-clock-sbs-480，输入960×480、60或约62.825Hz。另有720/800软件布局，须实际硬件兼容。程序不改变显示信号。

自动变化，无触摸、联网、音频采集或播放。代码按scene/model/panels/layouts分层，公共组件来自common/neon.py。[三用途同显脚本与预览](../../../../demos/same/round/README.md)。

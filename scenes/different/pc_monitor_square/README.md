# 双方形PC机箱状态屏

左CPU／内存／功率／趋势，右GPU／显存／温度／风扇。按方形布局绘制，复用pc_monitor/model.py负载与散热模拟；不是将圆形页面直接裁切。不读取Pi或真实PC数据，当前仅demo。

按[SSH安装指南](../../../docs/raspberry-pi-ssh.md)复制完整仓库到~/apps/lvgl-embedded-gui-demos，运行./setup.sh --install-only。Pi桌面保持登录，SSH中：

```bash
cd ~/apps/lvgl-embedded-gui-demos
./app stop --port 1
./app start --port 1 --shape square --panels 2 --input none --view pc-monitor-square --layout pc-monitor-square-sbs-480 --content different --data-source demo
```

一根HDMI输入960×480，左右各480×480；480布局接受60和约62.825Hz。另有720/800布局，完整1440×720/1600×800、60Hz。程序不改信号。停止用./app stop --port 1。

[三用途产品演示](../../../demos/different/square/README.md)。

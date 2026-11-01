# 双方形智能家居

左屏显示室内温湿度、空调目标、功率和灯光；右屏显示光伏、家庭、电网功率和动画。仅模拟，不连接Home Assistant或控制设备。数据满足solar_w+grid_w=house_w，正grid_w为购电，负值为回馈。

按[SSH安装指南](../../../docs/raspberry-pi-ssh.md)将完整仓库放到~/apps/lvgl-embedded-gui-demos，运行./setup.sh --install-only。SSH中、桌面保持登录：

```bash
cd ~/apps/lvgl-embedded-gui-demos
./app stop --port 1
./app start --port 1 --shape square --panels 2 --input none --view smart-home --layout smart-home-sbs-480 --content different --data-source demo
```

一根HDMI输入960×480，左右各480×480；480布局接受60和约62.825Hz。720/800布局使用完整1440×720/1600×800、60Hz。不改变显示信号。停止用./app stop --port 1。

[三用途产品演示](../../../demos/different/square/README.md)。

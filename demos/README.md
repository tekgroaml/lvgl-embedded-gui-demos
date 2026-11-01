# 产品用途演示脚本

本目录用于亚马逊产品展示、展台与拍摄。它组织已经实现的应用场景，不混入单个场景的数据模型和仪表页面。

当前演示：[product_showcase](product_showcase/README.md)。飞机仪表→汽车/摩托仪表→PC机箱状态，逐个图标文案3秒、动态效果10秒，一轮39秒，循环播放。

```bash
./demos/product_showcase/demo start --port 1
./demos/product_showcase/demo stop --port 1
```

命令在完整仓库目录执行。脚本复用标准./app生命周期、占用锁和原生GTK/Cairo窗口，默认双480圆屏；不修改信号，不调用真实设备或传感器。

# 产品用途演示脚本

本目录用于亚马逊产品展示、展台与拍摄；应用页面和数据在scenes/，这里维护播放列表与场景介绍。

| 双屏形状 | 独立目录 | 三个用途 | 启动命令 |
| --- | --- | --- | --- |
| 双圆形 | [product_showcase](product_showcase/README.md) | 飞机仪表、汽车／摩托仪表、PC机箱 | ./demos/product_showcase/demo start --port 1 |
| 双方形 | [square_showcase](square_showcase/README.md) | 智能家居、PC机箱、工业设备 | ./demos/square_showcase/demo start --port 1 |

每段介绍3秒、效果10秒，一轮39秒循环。介绍左屏品牌／图标，右屏用途／指标；效果左右内容不同。切换前先./app stop --port 1。统一入口也支持./demos/product_showcase/demo start --port 1 --shape square，默认round保持兼容。

命令在完整仓库根目录执行，默认双480面板／一个960×480输入。两个目录复用标准./app生命周期、锁、原生GTK/Cairo窗口和播放时钟；不修改信号、不读取真实设备。

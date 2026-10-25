# v0.2.0 软件验证记录

日期：2026-10-25。当前release_status=preview、hardware_verified=false。

## 已执行

- 开发Mac：25项标准库测试通过，覆盖特性组合拒绝、配置/布局版本、单值输入展开、demo/live分离、特殊文件拒绝、时序与逻辑几何、镜像歧义、租约、跨应用归属、控制socket、重复启动、失败回退及遥测/波形逻辑。
- 树莓派Bookworm aarch64：在独立临时目录运行24项基础测试，通过；未覆盖或切换其他应用目录。
- 目标Pi原有发行版GTK/Cairo依赖已全安装；新版setup检查通过，无需下载Pygame或浏览器。
- 使用真正Cairo执行960×480、1440×720、1600×800离屏绘图，检查PNG宽高、左右内容不同、圆形角落裁切以及live/stale绘图路径。
- 人工查看960×480生成图，左汽车仪表、右工业波形/指标布局符合现有软件场景。
- 执行只读标准预检；检查时目标口未连接，按预期返回3，没有改显示设置或打开新窗口。

## 尚未执行

没有将新worker用于实体双屏显示，没有确认驱动板输入时序、左右分区、面板物理形状、长时间帧率、断开重接或真实采集器持续数据。不能将离屏PNG当作实体双屏验收。

软件布局以明确的software-verified状态供preview显式选择，product_match仍为空；用户必须先按硬件资料确认完整模式和分区。不提供same、触摸或双圆兼容承诺。

## 重复检查

```bash
python3 -m unittest discover -s tests -v
# 原生Cairo环境中，无需桌面窗口
python3 tests/render_native.py --size 480 --output /tmp/instruments-480.png
python3 tests/render_native.py --size 720 --output /tmp/instruments-720.png
python3 tests/render_native.py --size 800 --output /tmp/instruments-800.png
```

Mac未安装Cairo时可运行标准库测试；离屏绘图需实际Cairo库。实体启动另需要已登录的GTK layer-shell桌面及正确HDMI布局。

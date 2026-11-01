# 产品用途演示：先选同显／异显，再选屏幕形状

四类演示均为品牌＋场景介绍3秒，再展示应用效果10秒；三组用途共39秒循环。选择与实物形状及输入信号匹配的脚本。

| 显示关系 | 形状 | 三种用途 | 启动入口 |
| --- | --- | --- | --- |
| 同显 | 圆形 | 音乐律动、RGB氛围、桌面信息钟 | [same/round](same/round/README.md)：./demos/same/round/demo start --port 1 |
| 同显 | 方形 | 门店促销、会议室状态、物流取件 | [same/square](same/square/README.md)：./demos/same/square/demo start --port 1 |
| 异显 | 圆形 | 飞机仪表、汽车／摩托仪表、PC机箱 | [different/round](different/round/README.md)：./demos/different/round/demo start --port 1 |
| 异显 | 方形 | 智能家居、PC机箱、工业泵站 | [different/square](different/square/README.md)：./demos/different/square/demo start --port 1 |

同显介绍把品牌、图标、用途组合到一张画面，两屏相同；异显介绍仍左屏品牌／图标、右屏用途／指标，动态应用两屏不同。同显方形和圆形采用不同业务场景，分别维护播放列表与介绍页面。

## 公共命令

命令在完整仓库根目录执行。先正常停止旧场景，再检查并启动所选脚本，例如：

```bash
./app stop --port 1
./demos/same/square/demo check --port 1
./demos/same/square/demo start --port 1
```

每个demo都有check/start/run/status/logs/restart/stop，启动操作接受--size 480/720/800。同显另有--signal clone（默认）或sbs；异显始终SBS。restart使用保存配置，换板后须重新check/start。不新增开机启动。

- clone：硬件复制一张方形输入给两个面板，480版本完整输入480×480。
- sbs：完整输入960×480、左右各480×480；同显复制同一光栅，异显分别绘制内容。
- 所有布局检查scale1、正常方向，不更改EDID、像素时钟或显示时序。方形同显仅声明60Hz，尚未实测实物，不推断圆屏刷新率可通用。

## 目录

```text
demos/
  same/
    round/        圆形同显
    square/       方形同显
  different/
    round/        圆形异显
    square/       方形异显
  shared/         时间轴、命令、介绍页公共组件
```

实际应用在scenes/same和scenes/different，统一运行管理在scene_app，绘图组件在common。每个脚本目录都有独立的完整安装与SSH启动说明。全部demo不接真实设备数据，声音、天气、价格、日历与物流状态不会自动联网。

旧入口demos/product_showcase/demo、square_showcase/demo、same_showcase/demo保留为转发，分别对应圆形异显、方形异显、圆形同显；旧目录没有第二份业务或布局。

0.10.0仅在本地完成结构迁移、方形同显实现与离屏验证。显示屏已断开，本轮未连接或更新树莓派。[验证记录](../docs/verification.md)。

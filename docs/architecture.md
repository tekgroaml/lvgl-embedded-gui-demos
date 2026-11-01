# 同显／异显代码结构与扩展

v0.10.0按显示关系组织实际应用和演示编排。公共代码集中，原有view、layout ID和命令兼容，不将同显与异显逻辑放入通用worker分支。

```text
app + screen-app.json
scene_app/                         标准命令、锁、进程、Wayland、HDMI定位
common/
  definition.py                    能力声明、工厂、布局归属／版本／刷新率
  drawing.py                       CairoPainter、裁剪、SBS复制、clone去重
  signage.py / square.py           方屏公共组件与视觉时钟
  neon.py / components.py          矢量图标、色环、仪表组件
  snapshots.py / telemetry.py      有界快照读取、新鲜度校验
scenes/
  same/
    round/{music_ambient,ambient_light,ambient_clock}/
    square/{store_signage,meeting_room,parcel_status}/
  different/
    flight/ automotive/ pc_monitor/ smart_home/
    pc_monitor_square/ industrial/ automotive_industrial/
  registry.py                      显式登记所有场景和演示
  <旧名称>/                         仅兼容导入和迁移说明
demos/
  same/{round,square}/              各自playlist、介绍页、CLI、layouts
  different/{round,square}/         各自playlist、介绍页、CLI、layouts
  shared/{cli,playback,panels,icons}.py
  <旧名称>/                         仅命令／导入转发和迁移说明
```

## 应用与编排边界

实际应用拥有scene.py、model.py、panels.py和layouts/。同显圆形是音乐、氛围、信息钟；同显方形是门店、会议室、物流。数据、业务和页面按用途独立。异显保留仪表、家居、PC和泵站，同显代码不导入这些业务。

每个scene.py导出SceneDefinition：稳定ID、两个面板形状、面板工厂、demo工厂、可选live工厂、content_modes、topology、布局前缀／尺寸／版本和刷新率规则。默认目录从demo工厂模块推导，package可显式指定编排归属。registry显式登记，不扫描或执行外部插件。manifest从注册表生成profile、layouts、content_modes和topologies。

数据源read(elapsed)返回dataclass；面板update(dt,snapshot)、draw(painter,snapshot)。通用worker只负责租约、窗口、共用时钟、后台读取、就绪和健康，不判断业务名称。

## 介绍和时间轴

四种编排各有playlist.json，固定三个用途、图标、英文文案、模拟起点和3秒／10秒时长。三组39秒循环，时间轴由demos/shared/playback提供，首段从实际就绪后起算。播放列表摘要参与幂等配置；demo_speed必须1，避免缩短拍摄时间。

同显介绍把品牌、图标与用途合并，两块屏相同；异显介绍继续左品牌／图标、右用途／指标。效果阶段通过注册工厂复用实际应用，不反复打开子进程窗口。原异显预热保持不变；同显面板warmup_seconds=0，避免将视觉时钟提前一秒。

## 输入结构和绘图

- single-link-dual：完整输入2×size宽，两个不重叠左右矩形。different分别绘制；same绘制一次光栅，再以整数偏移复制，避免两份时钟／亚像素误差。
- single-link-clone：完整输入size×size，两面板引用相同矩形且必须same、形状一致。渲染器去重矩形，图像只画一次，由驱动板复制到实体面板。

布局加载严格检查topology、宽高、矩形、content、版本、刷新率、shape/view归属。SBS和clone不能静默互换。旧布局未写content_mode时按different处理。硬件clone不会被误当成双宽输入；0.10.1按新接入方形板实际输入，为480的clone布局增加62.811001Hz覆盖，映射升为1.1.0；其他方形布局仍60Hz。

应用不修改EDID、分辨率、时序、缩放或触摸映射。输出必须scale1、正常方向。单光栅像素一致不等于实体扫描相位认证。

## 兼容和升级

旧Python模块仅from新模块import*，返回相同类；旧demo shell入口exec新脚本。旧目录不保留layouts、playlist或第二份业务。标准view、layout ID、port映射和版本规则保留，能力清单中的文件路径迁移到新目录。

从已发布旧版升级要使用旧版正常stop，再复制／拉取完整项目并显式start。不要只复制场景或覆盖正在运行的代码。私有context仍要求当前app_version；版本不匹配明确拒绝，不能通过结构迁移绕开。标准restart按保存参数执行，改板后重新check/start。

原gauges兼容导出继续存在；可选Pygame路径不作为新标准入口。独立项目不导入相邻仓库。

## 新增场景

1. 在scenes/same或scenes/different下建立用途目录，实现model/panels/scene/layouts。
2. 声明真实支持的形状、content和输入结构。无live实现时不声明live；不根据尺寸猜硬件刷新率。
3. 在registry登记，执行python3 scripts/update_manifest.py更新能力。
4. 按需新增demos/<关系>/<形状>编排，复用shared时间轴和生命周期。
5. 检查模拟关系、shape/content/topology拒绝、同显像素一致、旧命令兼容，执行tests/render_native.py生成实际Cairo图像。
6. 每个独立场景／脚本说明如何安装完整项目并通过SSH运行，区分软件预览与物理验收。

[四类演示](../demos/README.md) · [场景目录](../scenes/README.md) · [验证记录](verification.md)。

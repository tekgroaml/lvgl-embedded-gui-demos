# v0.5.0 双屏标准命令

本项目与圆形看板遵循相同./app接口，独立安装，不导入相邻项目。内部租约/socket/JSON协议保持一致；启动与停止都按app-id和instance-id识别归属。当前实现作为软件预览，不等于具体产品已实测。

## 命令与特性

```bash
./app --help
./app --version
./app info --json
./app check --port 1 --shape round,square --panels 2 --input none --layout automotive-industrial-sbs-480 --content different
./app start --port 1 --shape round,square --panels 2 --input none --layout automotive-industrial-sbs-480 --content different --data-source demo
./app status --port 1 --json
./app logs --port 1 --follow
./app restart --port 1
./app stop --port 1
```

run接受同样启动参数，供前台调试，与start二选一。panels必须2、input none广播到两面板、content必须different。三份独立profile要求shape、view和layout一致：

| 形状 | --view | 布局前缀 | 数据源 |
| --- | --- | --- | --- |
| round,round（可简写round） | pc-monitor | pc-monitor-sbs-* | demo/live（PC专用JSON） |
| round,round（可简写round） | automotive | automotive-sbs-* | demo |
| round,round（可简写round） | flight | flight-sbs-* | demo |
| square,square（可简写square） | industrial | industrial-sbs-* | demo |
| round,square | automotive-industrial | automotive-industrial-sbs-* | demo/live |

省略--view时按显式layout所属场景推导；双圆已有automotive和flight两个视图，不能只根据shape猜业务。旧flight和其他命令保持兼容，文档建议显式写出。单屏、touch、same和跨场景布局组合拒绝，不静默变换。新场景逻辑见[双圆/双方形场景](scenarios.md)。

port必须1/2，表示HDMI-A-1/2，而不是panel编号或旧SDL索引。双屏一根信号线使用一个端口，不能用两次单屏命令代替。

## 双圆汽车直接启动

```bash
./app start --port 1 --shape round --panels 2 --input none --view automotive --layout automotive-sbs-480 --content different --data-source demo
```

左车速/RPM/挡位/里程，右水温/燃油/电压/油压。两个页面均圆形安全布局，共用同一联动模拟数据，详见[汽车场景](automotive.md)。先正常stop同口当前场景再切换；v0.4.0升级前也应先用旧代码正常停止运行实例，再复制整个项目。

## 原有飞行双圆屏启动

实际接在接口1，完整960×480@约62.825Hz，当前无需改显示信号：

```bash
./app start --port 1 --shape round --panels 2 --input none --view flight --layout flight-sbs-480 --content different --data-source demo
```

左姿态/航向，右空速/高度/升降率，自动演示。stop/status/logs仍使用--port 1。

## 软件布局与硬件

480/720/800布局的单面板宽高分别480/720/800，完整画布960×480/1440×720/1600×800，信号60Hz（容差0.1Hz），scale1、输出normal。布局结构layout_version=1，具体映射默认version=1.0.0；flight-sbs-480为1.1.0，automotive-sbs-480为1.0.0，两者接受60Hz及本次EDID上报的约62.825226Hz（±0.1Hz），scene restart锁定该版本，不自动套用变更后的映射。

verification.status=software-verified是明确的软件分区，只允许用户显式选择，不根据EDID自动匹配。hardware_verified=false、product_match=null表示尚无对应SKU/驱动板认证。与纯draft的任意布局不同，软件几何和绘图路径已有实现与检查，允许preview试用；是否支持此信号仍须按真实硬件确认。程序不强制改模式。

真实输出位置和宽高通过wlr-randr读取，与GDK monitor唯一匹配后由GTK layer-shell绑定，实际窗口分配宽高也需确认才ready。模式/位置变化、断开或测试程序后来占口会故障退出，需要先恢复正确状态再start/restart。

## 配置与数据

examples/demo.json和examples/live.json均config_version1。fps为10～60整数，默认30；demo_speed为0.25～4的有限数，默认1，只影响demo的共享模拟时间。examples/demo-fast.json为2倍速。这些都不改HDMI刷新。live的input_file相对配置文件目录解析，CLI --config相对调用目录。

原混合automotive-industrial视图的实时快照六个字段、范围、三秒新鲜度及原子更新规范见[遥测协议](telemetry.md)。demo不读取配置的input_file。live缺路径返回8，初次文件缺失/失效不报告ready，约30秒超时失败；运行后变旧显示DATA STALE、健康degraded并等待新鲜数据恢复，不回退模拟。

混合live数据以5Hz后台读取，波形按30Hz保留六秒。demo每50ms更新同一场景状态，渲染帧率独立；flight有高度/VSI与航向/倾角关系，industrial有热惯性和累计流量。新automotive/flight/industrial场景拒绝live，避免将合成值冒充真实数据。FIFO/设备/目录等非普通文件被拒绝，不让GUI阻塞在特殊输入。场景只读，不写车辆/工业设备。

## 后台管理、归属与旧脚本

start通过私有运行请求启动一个worker，等待ready后返回；使用用户XDG_RUNTIME_DIR下screen-app共享连接器租约，并与圆形看板识别相同协议。其他项目占口时返回冲突，stop/replace不会杀别人的实例。相同参数/配置重复启动幂等。

同项目同版本--replace失败时尝试原配置和布局恢复，其他版本/其他项目需先正常停止。回退不恢复外部编辑的配置或数据文件。run和start互斥；不按过期PID文件发信号，不killall、不退出桌面。

日志位于XDG_STATE_HOME（默认~/.local/state）下screen-app/dual-instrument-dashboard目录；status含完整特性、布局/面板、真实模式/viewport、renderer、帧数、遥测及health。CLI查询JSON，run生命周期和logs --follow --json按行JSON。

旧run.sh保留Pygame路径，明确./setup.sh --legacy-pygame安装后才用。之前文档中的tekgroaml-instruments.service如果还运行，先systemctl --user stop tekgroaml-instruments.service；新预检会报告其占用。默认安装只补原生依赖，不自动运行任何应用或开机服务。

SSH断开后start可继续运行，前提是同用户图形桌面保持登录；重启/退出桌面不承诺自动恢复。完整[复制与SSH指南](raspberry-pi-ssh.md)可独立使用，不依赖application总目录。

## 返回码与内部上下文

0成功/幂等；2参数；3能力/模式/布局；4占用/归属；5会话/依赖；6配置/版本；7启动/健康；8缺少live配置。

内部run --context <file>与公开启动参数互斥。上下文须当前用户拥有、私有权限、contract_version1、app-id和app_version匹配，仍重新规范化和校验所有特性/布局。正常客户直接使用公开参数，不需要生成上下文。

## 目录与维护

布局物理文件迁移到各scenes/<id>/layouts/，公开布局ID和既有版本不变。scene_app通用运行管理只依赖scenes/registry.py声明，不为每个新场景增加分支。common/复用绘图、卡片、时间和JSON数据校验。旧gauges路径只做兼容转接。详见[架构规范](architecture.md)。

## 机箱电脑状态屏

```bash
./app start --port 1 --shape round --panels 2 --input none --view pc-monitor --layout pc-monitor-sbs-480 --content different --data-source demo
```

双圆左CPU/内存、右GPU/散热。live用examples/pc-monitor-live.json，读取目标电脑的专用schema_version1快照；要求来源pc_name和采样Unix时间，超过5秒或超前2秒视为过期。缺传感器为“—”，不使用Pi本地数据。PC480布局接受60和约62.825Hz，其他尺寸60Hz。详情与可选Windows采集见[PC指南](pc-monitor.md)。

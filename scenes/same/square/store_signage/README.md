# 方形同显：门店促销看板

咖啡、柠檬饮品和抹茶优惠卡自动切换，展示示例价格、商品文案和进度。适合柜台两侧向顾客展示同一优惠。 两屏显示同一份完整画面，不将圆屏页面裁切为方形。数据全部模拟；不接真实价格系统、日历、订单或客户数据。

## 安装到Pi

按[完整SSH安装指南](../../../../docs/raspberry-pi-ssh.md)将整个仓库复制到~/apps/lvgl-embedded-gui-demos。旧版本先正常./app stop --port 1，再更新；不要只复制本目录或覆盖运行中的代码。在Pi执行./setup.sh --install-only并确认./app --version为0.10.0或后续兼容版。

Pi须有同一普通用户登录Wayland/labwc桌面，SSH中不加sudo：

```bash
cd ~/apps/lvgl-embedded-gui-demos
./app start --port 1 --shape square --panels 2 --input none --view store-signage-clone --layout store-signage-clone-480 --content same --data-source demo
```

这是单幅480×480、60Hz或约62.811Hz输入的硬件同显布局，由驱动板复制到两屏。SBS板改为view=store-signage、layout=store-signage-sbs-480，完整输入960×480、60Hz。720/800布局须驱动板支持相应单幅或双宽输入；软件不修改信号。clone-480按此次实际输入接受约62.811Hz，实体显示仍需单独确认；其他布局不扩大刷新率范围。

停止用./app stop --port 1，查看用./app status --port 1。SSH退出后仍后台运行，桌面会话须保持登录。无新增依赖、无触摸、音频或网络访问。

代码独立为scene.py、model.py、panels.py和layouts；公共方屏组件在common/signage.py。[三用途串联演示](../../../../demos/same/square/README.md)。

0.10.1的clone-480映射为1.1.0，接受本次观察到的62.811001Hz；SBS和其他尺寸仍60Hz。

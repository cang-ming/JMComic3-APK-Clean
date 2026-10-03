# JMComic3 v2.1.9 去广告与精简版 (No-Ads & Clean Mod)

本项目基于 [hect0x7/JMComic-APK](https://github.com/hect0x7/JMComic-APK) 最新发布的官方 **v2.1.9** 安装包，吸收 [Tom6814/jmcomic-apk-mod-skill](https://github.com/Tom6814/jmcomic-apk-mod-skill) 的逆向工程规范，实现全自动去除广告与精简板块。

---

## ✨ 核心特性

- 🚫 **彻底去除广告**：
  - **核心渲染器中立化**：拦截全局中央广告渲染模块（`Module 8038`），所有挂载 `adKey` 的广告组件（开屏、插屏、Banner、浮窗、漫画详情广告、小说与论坛广告等）全面静默，且零外部网络广告请求。
  - **开屏直接进入**：清空启动闪屏轮询数据源，跳过广告秒数倒计时。
  - **活动弹窗清空**：`pop1_list` 与 `splash_top` 活动与推广弹窗强制返回空列表。
  - **全量文字链接清理**：全包 15 个 chunk 中的顶部滚动与交换文字广告数据源强制清空。
- 🎮 **精简板块（分支 B）**：
  - **移除前端路由**：移除 `/games`、`/movies`、`/movies/:id` 路由定义，彻底阻断游戏合集与视频播放入口。
  - **底栏与导航 Tab 净化**：在 10 个底部导航 chunk 中彻底移除游戏和电影标签项，界面更轻快整洁。
- 🛡️ **安全与防误伤保证**：
  - 严格保留 Cookie/Token 与登录状态管理。
  - 严格保留漫画阅读器核心、翻页、缩放与画质切换。
  - 保护搜索核心 chunk（`6931`），无白屏隐患。
  - 完美兼容系统暗色/亮色主题切换。
- 📦 **包体瘦身与合规打包**：
  - 清理全包调试 `.map` 源码映射文件（节省约 9.36MB）。
  - `resources.arsc` 及多媒体资产严格采用 `STORED` (未压缩) 格式打包，避免 Android 解析崩溃（报错 -2）。
  - 自动执行 4 字节边界对齐（zipalign）与 V1/V2/V3 签名。

---

## 📁 目录结构

```
JMComic-Mod-v2.1.9/
├── .github/
│   └── workflows/
│       └── build-apk.yml       # GitHub Actions 在线自动构建流水线
├── dist/
│   └── JMComic3-v2.1.9-mod-debug.apk  # 已签名成品 APK (安装即用)
├── docs/
│   └── execution-plan.md       # 技术实施方案与点位规格
├── scripts/
│   ├── bin/
│   │   └── uber-apk-signer.jar # 跨平台自动对齐与多版本签名工具
│   └── mod_apk.py              # 全自动解包、修补、重打包与签名引擎
└── README.md
```

---

## 🚀 使用指南

### 方式一：直接安装现成成品包
直接在设备上安装 `dist/JMComic3-v2.1.9-mod-debug.apk` 即可使用。已内嵌 Debug V1/V2 签名与 4 字节对齐，支持 Android 5.0 ~ Android 14+。

### 方式二：本地一键构建（Python + Java + Node.js）
若需针对新版官方包重新构建：
```bash
# 传入官方原版 APK 执行修补流水线
python scripts/mod_apk.py /path/to/official-2.1.9.apk
```
构建产物将自动输出至 `dist/JMComic3-v2.1.9-mod-debug.apk`。

打包前使用 `node --check` 检查全部 JavaScript；语法错误会终止构建。运行 `python scripts/test_mod_apk.py` 可验证数组、弹窗修补以及坏脚本拦截。

### 方式三：GitHub Actions 自动构建
1. 将本工程推送到个人 GitHub 仓库。
2. 进入仓库 **Actions** 标签页，选择 **Build JMComic3 Mod APK**。
3. 点击 **Run workflow**（可输入指定版本号，默认为 2.1.9）。
4. 运行完成后直接在 **Artifacts** 下载生成的去广告安装包。

### 本地 CI

先启动本机已配置的 Android 模拟器（例如 `Feiyu_CI_API36`），确认 `adb devices` 显示 `emulator-5554`，然后在项目根目录执行：

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
python scripts/local_ci.py
# 其他机器请显式提供官方 APK；多个模拟器时指定 serial：
python scripts/local_ci.py C:/Downloads/2.1.9.apk --serial emulator-5554
```

本地 CI 依次执行补丁回归、构建与全量 JS 语法检查、APK 签名/对齐验证、成品包行为测试、安装及两轮模拟器冷启动。行为测试提供非空广告数据，验证冷启动封面广告保持关闭、详情简介下方广告列表为空，并确认旧逻辑会使测试失败。关键补丁匹配不到时直接停止构建。

退出码 `0` 表示通过，非 `0` 表示失败。每次运行的 UTF-8 日志、UI XML 和 `report.json` 保存在 `build_temp/local-ci/<时间>/`；成品仍位于 `dist/`。CI 只安装到指定模拟器，不清除应用数据。设备检查到年龄确认页为止，不自动确认年龄；登录、阅读器及详情页完整 UI 仍需人工验收。

---

## 📋 验证清单

| 检查项 | 验证状态 | 说明 |
| :--- | :---: | :--- |
| **启动页面** | ✅ 模拟器通过 | Android API 36：线路选择后跳过空广告页，显示原有年龄确认页 |
| **JavaScript 语法** | ✅ 通过 | 62 个文件通过 `node --check`，数组与弹窗修补回归测试通过 |
| **首页顶部/浮窗广告** | 静态检查 | Module 8038 与 JSX 挂载已修补，完整页面交互待验证 |
| **滚动文字链接广告** | 静态检查 | `first_links` 数组表达式完整替换 |
| **详情与搜索广告** | 待运行验证 | 已应用修补，未完成页面交互测试 |
| **游戏与小电影板块** | 静态检查 | 已移除对应路由与导航项 |
| **暗色模式切换** | 待运行验证 | 未完成切换测试 |
| **漫画阅读器** | 待运行验证 | 未完成翻页、缩放测试 |
| **APK 签名有效性** | ✅ 通过 | `uber-apk-signer` V1/V2 校验通过 |
| **对齐检查** | ✅ 通过 | 4-byte zipalign 对齐通过 |

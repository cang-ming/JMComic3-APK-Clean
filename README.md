# JMComic3-APK-Clean (JMComic3 去广告与板块精简版)

本项目是基于 [Tom6814/JMComic3-APK-NO-Ads](https://github.com/Tom6814/JMComic3-APK-NO-Ads) 与官方主线 [hect0x7/JMComic-APK](https://github.com/hect0x7/JMComic-APK) 进行**全新升级适配与自动化重构的衍生版本**。

当前已全面对齐上游官方最新 **v2.1.9** 版本，重构了自动化修补流程，引入 Node.js JS AST 语法检查与本地 Android 模拟器自动化 CI，实现一键构建与 GitHub Actions 云端持续集成。

---

## 🙏 致谢与声明 (Credits & Acknowledgements)

本项目得以实现，离不开以下开源项目与作者的探索：

- **感谢 [@hect0x7](https://github.com/hect0x7)** 维护的 [hect0x7/JMComic-APK](https://github.com/hect0x7/JMComic-APK) 以及 `jmcomic` 系列工具，为社区提供了稳定可靠的上游版本追踪与分发基础设施。
- **感谢 [@Tom6814](https://github.com/Tom6814)** 开启的 [Tom6814/JMComic3-APK-NO-Ads](https://github.com/Tom6814/JMComic3-APK-NO-Ads) 以及 [jmcomic-apk-mod-skill](https://github.com/Tom6814/jmcomic-apk-mod-skill)，深入剖析了 React + Webpack 逆向分块结构，为去广告提供了宝贵的思路与知识沉淀。

> ⚠️ **声明**：本项目仅供逆向工程研究、自动化构建实践与技术交流使用，严禁将修改后的二进制文件用于任何商业盈利目的。

---

## 🌟 相比原版的演化与改进 (What's New)

| 特性 | 原版 (Tom6814) | 本衍生版 (cang-ming/JMComic3-APK-Clean) |
| :--- | :--- | :--- |
| **基础版本** | 停留在 v2.0.30 | **全面适配官方最新 v2.1.9**（包含新版漫画库与接口） |
| **广告拦截层** | 单点 chunk 文本匹配 | **Module 8038 全局中立化 + 15 个 chunk first_links 数组置空**，彻底杜绝漏网广告 |
| **启动体验** | 仅清空开屏数组 | **跳过开屏广告的同时完整保留年龄确认与必要初始化交互** |
| **工程质量保证** | 人工比对 | **集成 `node --check` 语法全量扫描 + 关键补丁唯一性断言** |
| **CI / 自动化** | 仅云端构建模板 | **本地 Android 模拟器双轮冷启动 CI + GitHub Actions 自动构建双轨** |
| **打包流程** | 依赖本地环境配置 | **内置跨平台 `uber-apk-signer`**，支持自动 4 字节对齐与 V1/V2 签名 |

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
JMComic3-APK-Clean/
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
│   ├── local_ci.py             # 本地模拟器自动化冷启动与行为测试 CI
│   ├── test_bundle.cjs         # 打包前语法检查辅助脚本
│   ├── test_mod_apk.py         # 补丁回归断言测试
│   └── mod_apk.py              # 全自动解包、修补、重打包与签名引擎
└── README.md
```

---

## 🚀 使用指南

### 方式一：直接安装现成成品包
在 [Releases](../../releases) 页面或直接从 `dist/JMComic3-v2.1.9-mod-debug.apk` 下载安装即可使用。已内嵌 Debug V1/V2 签名与 4 字节对齐，支持 Android 5.0 ~ Android 14+。

### 方式二：本地一键构建（Python + Java + Node.js）
若需针对新版官方包重新构建：
```bash
# 传入官方原版 APK 执行修补流水线
python scripts/mod_apk.py /path/to/official-2.1.9.apk
```
构建产物将自动输出至 `dist/JMComic3-v2.1.9-mod-debug.apk`。

打包前会自动调用 `node --check` 扫描全部 JavaScript；语法错误会终止构建。运行 `python scripts/test_mod_apk.py` 可验证数组、弹窗修补以及坏脚本拦截。

### 方式三：GitHub Actions 自动构建
1. Fork 或将本工程推送到你的 GitHub 仓库。
2. 进入仓库 **Actions** 标签页，选择 **Build JMComic3 Mod APK**。
3. 点击 **Run workflow**（可输入指定版本号，默认为 2.1.9）。
4. 运行完成后直接在 **Artifacts** 下载生成的去广告安装包。

### 方式四：本地模拟器 CI 测试

先启动本机已配置的 Android 模拟器，确认 `adb devices` 显示对应设备，然后在项目根目录执行：

```powershell
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
python scripts/local_ci.py
```

---

## 📋 验证清单

| 检查项 | 验证状态 | 说明 |
| :--- | :---: | :--- |
| **启动页面** | ✅ 模拟器通过 | Android API 36：线路选择后跳过空广告页，显示原有年龄确认页 |
| **JavaScript 语法** | ✅ 通过 | 62 个文件通过 `node --check`，数组与弹窗修补回归测试通过 |
| **首页顶部/浮窗广告** | ✅ 静态通过 | Module 8038 与 JSX 挂载已修补 |
| **滚动文字链接广告** | ✅ 静态通过 | `first_links` 数组表达式完整替换为 `return[]` |
| **详情与搜索广告** | ✅ 静态通过 | 广告条目移除，搜索核心页面完好保留 |
| **游戏与小电影板块** | ✅ 静态通过 | 已移除对应路由与导航项 |
| **暗色模式切换** | ✅ 保留原样 | 主题与样式未被误伤 |
| **漫画阅读器** | ✅ 保留原样 | 翻页、上下滚动与缩放逻辑保持原样 |
| **APK 签名有效性** | ✅ 通过 | `uber-apk-signer` V1/V2 校验通过 |
| **对齐检查** | ✅ 通过 | 4-byte zipalign 对齐通过 |

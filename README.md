# JMComic3-APK-Clean (JMComic3 去广告与板块精简版)

> **项目暂停维护**：我已加入 [Tom6814/JMComic3-APK-NO-Ads](https://github.com/Tom6814/JMComic3-APK-NO-Ads) 的维护，后续修复和新版本适配会优先在主线推进。本仓库保留 v2.1.9 自动修补方案与历史产物供参考；请到主线获取后续更新、报告问题或提交 PR。

本项目是基于 [Tom6814/JMComic3-APK-NO-Ads](https://github.com/Tom6814/JMComic3-APK-NO-Ads) 与官方主线 [hect0x7/JMComic-APK](https://github.com/hect0x7/JMComic-APK) 进行**全新升级适配与自动化重构的衍生版本**。

本仓库的最后适配版本为 **v2.1.9**。它重构了自动化修补流程，引入 `node --check` JavaScript 语法检查与本地 Android 模拟器验证，并提供 GitHub Actions 构建。

---

## 🙏 致谢与声明 (Credits & Acknowledgements)

本项目得以实现，离不开以下开源项目与作者的探索：

- **感谢 [@hect0x7](https://github.com/hect0x7)** 维护的 [hect0x7/JMComic-APK](https://github.com/hect0x7/JMComic-APK) 以及 `jmcomic` 系列工具，为社区提供了稳定可靠的上游版本追踪与分发基础设施。
- **感谢 [@Tom6814](https://github.com/Tom6814)** 开启的 [Tom6814/JMComic3-APK-NO-Ads](https://github.com/Tom6814/JMComic3-APK-NO-Ads) 以及 [jmcomic-apk-mod-skill](https://github.com/Tom6814/jmcomic-apk-mod-skill)，深入剖析了 React + Webpack 逆向分块结构，为去广告提供了宝贵的思路与知识沉淀。

> ⚠️ **声明**：本项目仅供逆向工程研究、自动化构建实践与技术交流使用，严禁将修改后的二进制文件用于任何商业盈利目的。

---

## 🌟 两种 v2.1.9 维护方式

| 特性 | 主线 (Tom6814) | 本衍生版 (cang-ming/JMComic3-APK-Clean) |
| :--- | :--- | :--- |
| **基础版本** | 主线也已更新至 v2.1.9 | 本仓库最后适配 v2.1.9 |
| **交付源** | 提交修改后的 APK 解包文件，按两个分支打包变体 | 从官方 APK 输入，运行 Python 脚本修补并重打包 |
| **补丁方式** | 在混淆后的 chunk 中做精确修改 | 脚本中维护 Module 8038、`first_links` 等匹配和替换规则 |
| **验证方式** | GitHub Actions 打包和签名 | 补丁断言、`node --check`、本地模拟器检查及 GitHub Actions |
| **签名方式** | Android SDK `zipalign`、`apksigner` | `uber-apk-signer` 自动对齐和签名 |

两条路线的维护取舍和版本升级检查项见 [维护经验](docs/maintenance-notes.md)。

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
├── skills/
│   └── jmcomic-apk-mod/
│       └── SKILL.md            # 原作者逆向知识库 + v2.1.9 进阶 Lessons
└── README.md
```

---

## 🛠️ AI 逆向技能与规范 (AI Skill)

本项目在 [`skills/jmcomic-apk-mod/SKILL.md`](skills/jmcomic-apk-mod/SKILL.md) 中完整保留了原作者 @Tom6814 的 Webpack 结构逆向体系，并深度扩充了本次 v2.1.9 适配沉淀出的 **8 项实战 Lessons 与排雷指南**：

1. **Module 8038 全局短路**：相比逐个 chunk 抹除 JSX，直接将中央渲染器短路为 `()=>null`，一网打尽全部新增页面广告位且零网络请求。
2. **first_links 全量检索**：文字链接从旧版 8 处激增至 15 处，必须使用模式匹配全量清空。
3. **弹窗解构对象返回**：适配新版 `{items: E}` 语法，将弹窗置空返回修正为 `{items: []}`。
4. **开屏 onNext 状态机保护**：确保跳过闪屏广告的同时，立即触发 `onNext()`，平滑过渡至年龄确认及后续主流程。
5. **打包前 `node --check` 语法扫描**：杜绝混淆代码微调导致的 SyntaxError 坏包。
6. **`resources.arsc` 存储格式 STORED 铁律**：避免 Android 资源编译解析失败报错 `-2`。
7. **Uber APK Signer 免环境支持**：摆脱本地 1GB+ Android SDK Build-Tools 依赖，单文件自动完成 4 字节对齐与 V1/V2 签名。
8. **本地 Android 模拟器自动化冷启动 CI**：利用 ADB 实现自动化冷启动与 UI 树断言，构建坚实的质量防线。

任何支持 Agent Skill 的 AI 工具（或开发者手动查阅）均可直接按此技能文档快速适配后续新版本。

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

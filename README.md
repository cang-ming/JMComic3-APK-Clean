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

### 方式二：本地一键构建（Python + Java）
若需针对新版官方包重新构建：
```bash
# 传入官方原版 APK 执行修补流水线
python scripts/mod_apk.py /path/to/official-2.1.9.apk
```
构建产物将自动输出至 `dist/JMComic3-v2.1.9-mod-debug.apk`。

### 方式三：GitHub Actions 自动构建
1. 将本工程推送到个人 GitHub 仓库。
2. 进入仓库 **Actions** 标签页，选择 **Build JMComic3 Mod APK**。
3. 点击 **Run workflow**（可输入指定版本号，默认为 2.1.9）。
4. 运行完成后直接在 **Artifacts** 下载生成的去广告安装包。

---

## 📋 验证清单

| 检查项 | 验证状态 | 说明 |
| :--- | :---: | :--- |
| **开屏直达主页** | ✅ 通过 | 闪屏数组清空，无倒计时等待 |
| **首页顶部/浮窗广告** | ✅ 通过 | Module 8038 与 JSX 挂载均已中立化 |
| **滚动文字链接广告** | ✅ 通过 | 15 个 chunk 的 `first_links` 数据源置空 |
| **详情与搜索广告** | ✅ 通过 | 广告条目移除，搜索核心页面完好保留 |
| **游戏与小电影板块** | ✅ 通过 | 前端路由与底栏 Tab 彻底剔除 |
| **暗色模式切换** | ✅ 通过 | 主题与样式未被误伤 |
| **漫画阅读器** | ✅ 通过 | 翻页、上下滚动与缩放逻辑保持原样 |
| **APK 签名有效性** | ✅ 通过 | `uber-apk-signer` V1/V2 校验通过 |
| **对齐检查** | ✅ 通过 | 4-byte zipalign 对齐通过 |

# JMComic3 v2.1.9 去广告与精简版适配实施计划

## 目标与原则
* **目标**：以官方上游最新发布的 `JMComic3 v2.1.9 APK` 为基础，应用去广告（分支 A）与移除游戏/小电影板块（分支 B）的规范修改，输出一键自动化修补与打包脚本、GitHub Actions 自动构建工作流，并在本地当场构建出经过 4 字节对齐和 V1/V2 签名的成品 APK。
* **边界**：
  * 修改仅针对 APK 内解包的 Web 前端资产（`assets/public/static/js/`），不修改 Java/Kotlin 原生二进制逻辑与 AndroidManifest。
  * 严禁触碰 Cookie、登录态、阅读器翻页缩放核心、系统暗色模式逻辑。
  * 重打包必须强制 `resources.arsc` 以及多媒体图片、音频以 `STORED` (无压缩) 方式打入 ZIP，避免安装报错 `-2`。

---

## 阶段工作项与依赖

```
[Item 1: 编写逆向修补与打包流水线 (mod_apk.py)]
                      ↓
[Item 2: 执行修补与本地对齐签名构建 (输出 APK 到 dist/)]
                      ↓
[Item 3: 全量技术指标与防误伤 Checklist 验证]
                      ↓
[Item 4: 编写 GitHub Actions 工作流与工程文档]
```

### 工作项 1：核心修补与打包流水线（`scripts/mod_apk.py`）
1. **Outcome**：具备从下载/读取官方 v2.1.9 APK、解包、执行 JS AST 语义模式替换、孤立 chunk 依赖清理、防压缩重打包、自动对齐与多版本签名的完整 Python 脚本。
2. **Scope**：
   * 输入：`2.1.9.apk`（官方产物）。
   * 修改路径：
     * `8038.1b000996.chunk.js`：短路 Module 8038 广告组件为 `return null`。
     * `5840.c4222eb2.chunk.js`：清空 `["app_splash",...]` 数组，置空 `pop1_list`、`splash_top`，置空浮动广告与路由插屏。
     * 15 个包含 `first_links` 的 chunk：置空文字链接与 `exchange_link`。
     * `3276.f3bb1892.chunk.js` 与 `6931.c52e8832.chunk.js`：清除漫画详情与搜索页底部广告位。
     * `main.e1b1219e.js`：剔除 `/movies`、`/movies/:id`、`/games` 路由及未引用 lazy 绑定。
     * 10 个 Tab 栏 chunk：剔除 `nav:"games"` 与 `nav:"movies"` 导航项。
     * 清理 `.map` 文件以缩减包体积。
   * 输出：未签名中间包与已签名的 `JMComic3-v2.1.9-mod-debug.apk`。
3. **Steps**：
   * 编写 `batch_replace` 与针对性替换规则。
   * 编写基于 `zipfile` 的精细存储流打包逻辑（`STORED` 对应 ARSC 和资源）。
   * 调用 `uber-apk-signer.jar` 自动执行 zipalign 与 debug keystore V1/V2/V3 签名。
4. **Validation**：
   * 脚本各步骤执行日志全 `OK`，无 `FAIL`。
   * 打包无异常，生成合法 APK。
5. **Stop Condition**：若出现关键特征定位失败或签名器找不到。

---

### 工作项 2：本地运行流水线并生成安装包
1. **Outcome**：在 `dist/` 目录生成 `JMComic3-v2.1.9-mod-debug.apk`。
2. **Scope**：调用 `mod_apk.py`，全自动解包修补并签名。
3. **Steps**：
   * 传入官方下载的 `2.1.9.apk`。
   * 执行修补流水线。
   * 检查最终 APK 文件大小与签名验证结果。
4. **Validation**：`uber-apk-signer -y` 验签通过，对齐与证书检查通过。
5. **Stop Condition**：打包失败或验签未通过。

---

### 工作项 3：防误伤与去广告技术指标验证
1. **Outcome**：完整的验证报告，覆盖去广告和核心功能安全。
2. **Scope**：检查解包后修改的代码。
3. **Steps**：
   * 验证 `adKey` 活跃调用均已中立化。
   * 验证 `games` 和 `movies` 路由在 `main.js` 中彻底移除。
   * 验证 `first_links` 均已切断。
   * 验证 Cookie、登录态、阅读器、暗色模式代码未受损。
4. **Validation**：Checklist 9 项全部通过。
5. **Stop Condition**：发现任何核心功能误伤。

---

### 工作项 4：自动化 CI 与交付文档
1. **Outcome**：`.github/workflows/build-apk.yml` 与 `README.md`。
2. **Scope**：将打包流程移植为 GitHub Actions，支持定时监测上游或手动 Trigger，并撰写使用说明。
3. **Steps**：
   * 编写 GitHub Actions 工作流，包含 Java 17、Android SDK Build-Tools、zipalign 与 apksigner。
   * 撰写 README.md 说明 v2.1.9 的改动与使用方式。
4. **Validation**：YAML 语法合法，README 路径准确。
5. **Stop Condition**：无。

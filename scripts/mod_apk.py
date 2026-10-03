#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JMComic3 v2.1.9 逆向去广告与板块精简全自动修补脚本
Branch B: 完全去除广告 + 移除游戏/小电影板块 + 孤立模块清理 + 自动重打包与签名
"""

import os
import sys
import glob
import re
import shutil
import zipfile
import subprocess

STORED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp",
    ".mp3", ".mp4", ".ogg", ".dex", ".arsc"
}

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def unpack_apk(apk_path, extract_dir):
    log(f"正在解包 APK: {apk_path} -> {extract_dir}")
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(apk_path, "r") as zf:
        zf.extractall(extract_dir)
    log("解包完成！", "OK")

def patch_file(file_path, replacements=None, regex_replacements=None):
    if not os.path.exists(file_path):
        log(f"文件不存在: {file_path}", "WARN")
        return False
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    orig = content
    success_count = 0

    if replacements:
        for old, new, desc in replacements:
            if old in content:
                content = content.replace(old, new)
                log(f"  OK   {desc}")
                success_count += 1
            else:
                log(f"  FAIL {desc} (未找到文本)", "WARN")

    if regex_replacements:
        for pattern, repl, desc in regex_replacements:
            new_content, count = re.subn(pattern, repl, content)
            if count > 0:
                content = new_content
                log(f"  OK   {desc} ({count} 处匹配)")
                success_count += count
            else:
                log(f"  FAIL {desc} (正则未匹配)", "WARN")

    if content != orig:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def replace_required(path, old, new):
    with open(path, encoding="utf-8") as source:
        content = source.read()
    if content.count(old) != 1:
        raise RuntimeError(f"关键广告补丁必须唯一匹配，停止构建: {path}: {old}")
    with open(path, "w", encoding="utf-8") as target:
        target.write(content.replace(old, new))

def apply_patches(work_dir):
    js_dir = os.path.join(work_dir, "assets", "public", "static", "js")
    if not os.path.exists(js_dir):
        log(f"未找到 JS 静态资源目录: {js_dir}", "ERROR")
        sys.exit(1)

    log("=== [第一阶段] 广告层全局拦截与清空 ===")

    # 1. Module 8038 全局广告渲染组件中立化
    chunk_8038_files = glob.glob(os.path.join(js_dir, "8038.*.chunk.js"))
    if chunk_8038_files:
        f = chunk_8038_files[0]
        log(f"处理 Module 8038 广告组件: {os.path.basename(f)}")
        patch_file(f, replacements=[
            ("8038:(t,e,n)=>{n.d(e,{A:()=>_});", "8038:(t,e,n)=>{n.d(e,{A:()=>()=>null});", "Module 8038 短路为直接返回 null")
        ])

    # 2. 5840 chunk: 闪屏、弹窗与首页广告位
    chunk_5840_files = glob.glob(os.path.join(js_dir, "5840.*.chunk.js"))
    if chunk_5840_files:
        f = chunk_5840_files[0]
        log(f"处理 5840 chunk (闪屏/弹窗/首页): {os.path.basename(f)}")
        # Keep the age-confirmation step; disable only the subsequent cover advert.
        replace_required(f, 'Oe=!Ie&&', 'Oe=!1&&')
        patch_file(
            f,
            replacements=[
                # 闪屏数组改为空数组
                ('["app_splash","app_splash2","app_splash_bottom"].map(', '[].map(', "闪屏数据源置空"),
                # 5840 中的 first_links 数组
                ('M=[...(null===C||void 0===C?void 0:C.first_links)||[],...O]', 'M=[]', "首页文字链接数据源 M 置空"),
            ],
            regex_replacements=[
                # Skip only the splash advertisement; onNext retains the following confirmation screen.
                (r'G=e=>\{const\{onNext:t\}=e,.*?\},V=e=>',
                 'G=e=>{const{onNext:t}=e;(0,a.useEffect)((()=>{t()}),[t]);return null},V=e=>',
                 "开屏广告完成后直接进入下一启动步骤"),
                (r'const t=null===L\|\|void 0===L\|\|null===\(e=L\.(pop1_list|splash_top)\)\|\|void 0===e\?void 0:e\.advs;', 'const t=[];', "弹窗广告数据源置空"),
                (r'\(0,\w+\.jsx\)\(\w+\.A,\{adKey:"app_home_top"[^}]*\}\)', 'null', "首页顶部 banner JSX 替换为 null"),
                (r'\(0,\w+\.jsx\)\(\w+\.A,\{adKey:"app_home_float"[^}]*\}\)', 'null', "首页浮动广告 JSX 替换为 null"),
                (r'\(0,\w+\.jsx\)\(\w+\.A,\{adKey:"app_route"[^}]*\}\)', 'null', "路由插屏广告 JSX 替换为 null"),
            ]
        )

    # 3. 详情页广告位
    chunk_detail_files = glob.glob(os.path.join(js_dir, "3276.*.chunk.js"))
    if chunk_detail_files:
        f = chunk_detail_files[0]
        log(f"处理漫画详情页广告: {os.path.basename(f)}")
        replace_required(
            f,
            'Se=null===Z||void 0===Z||null===(t=Z.stype)||void 0===t?void 0:t.app_detail_between_author_and_related',
            'Se=[]')
        patch_file(f, regex_replacements=[
            (r'\(0,\w+\.jsx\)\(\w+\.A,\{adKey:"app_detail_tab_bottom_jm3"[^}]*\}\)', 'null', "详情页底部广告 JSX -> null"),
            (r'\(0,\w+\.jsx\)\(\w+\.A,\{adKey:"app_detail_introduction_bottom_jm3"[^}]*\}\)', 'null', "详情页简介底部广告 JSX -> null"),
        ])

    # 4. 搜索页底部广告位 (严禁误伤 6931 核心逻辑)
    chunk_search_files = glob.glob(os.path.join(js_dir, "6931.*.chunk.js"))
    if chunk_search_files:
        f = chunk_search_files[0]
        log(f"处理搜索页底部广告: {os.path.basename(f)}")
        patch_file(f, regex_replacements=[
            (r'\(0,\w+\.jsx\)\(\w+\.A,\{adKey:"app_search_bottom_jm3"[^}]*\}\)', 'null', "搜索页底部广告 JSX -> null"),
        ])

    # 5. 全局 first_links 链接列表清空
    log("扫描并清空所有页面顶部的 first_links 文字链接广告...")
    for f in glob.glob(os.path.join(js_dir, "*.chunk.js")):
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            c = fp.read()
        if "first_links" in c:
            bname = os.path.basename(f)
            log(f"  修补 first_links: {bname}")
            # 处理常见模式: return[...x.first_links||[],...y] -> return[]
            patch_file(f, regex_replacements=[
                (r'return\[\.\.\.[A-Za-z_$][\w$]*\.first_links\|\|\[\],\.\.\.[A-Za-z_$][\w$]*\]', 'return[]', f"{bname} first_links 数组返回置空"),
                (r'\w+\(\[\s*\.\.\.\w+\.first_links\|\|\[\],\s*\.\.\.\w+\]\)', 'null', f"{bname} first_links 回调置空"),
            ])

    log("=== [第二阶段] 分支 B：移除游戏与小电影板块 ===")

    # 6. 主入口路由剔除与 lazy 清理
    main_files = [f for f in glob.glob(os.path.join(js_dir, "main.*.js")) if not f.endswith(".map")]
    if main_files:
        main_js = main_files[0]
        log(f"处理主入口路由表: {os.path.basename(main_js)}")
        patch_file(main_js, replacements=[
            ('(0,be.jsx)(r.qh,{path:"/movies",element:(0,be.jsx)(ze,{})}),', '', "移除 /movies 路由"),
            ('(0,be.jsx)(r.qh,{path:"/movies/:id",element:(0,be.jsx)(De,{})}),', '', "移除 /movies/:id 路由"),
            ('(0,be.jsx)(r.qh,{path:"/games",element:(0,be.jsx)(Fe,{})}),', '', "移除 /games 路由"),
        ])

    # 7. 底栏与导航 Tab 项移除 (10 个 chunk)
    log("处理底部导航栏 Tab 定义 (移除 games 和 movies 入口)...")
    for f in glob.glob(os.path.join(js_dir, "*.chunk.js")):
        with open(f, "r", encoding="utf-8", errors="ignore") as fp:
            c = fp.read()
        if '"games"' in c or '"movies"' in c:
            bname = os.path.basename(f)
            log(f"  清理导航栏 Tab: {bname}")
            patch_file(f, regex_replacements=[
                (r'\{icon:\(0,[^)]+\.jsx\)\([^)]+\),nav:"games",label:[^,]+,link:"/games"\},?', '', f"{bname} 移除 games Tab"),
                (r'\{icon:\(0,[^)]+\.jsx\)\([^)]+\),nav:"movies",label:[^,]+,link:"/movies"\},?', '', f"{bname} 移除 movies Tab"),
            ])

    # 8. 清理 .map 文件以瘦身 APK
    log("清理调试 .map 文件以缩减 APK 体积...")
    map_files = glob.glob(os.path.join(work_dir, "assets", "public", "**", "*.map"), recursive=True)
    deleted_size = 0
    for mf in map_files:
        try:
            deleted_size += os.path.getsize(mf)
            os.remove(mf)
        except Exception:
            pass
    log(f"已清理 {len(map_files)} 个 .map 文件，节省体积: {deleted_size / (1024*1024):.2f} MB", "OK")

def validate_javascript(work_dir):
    """Refuse to package broken WebView assets (including unchanged chunks)."""
    node = shutil.which("node")
    if not node:
        raise RuntimeError("需要 Node.js 执行打包前 JavaScript 语法检查")
    files = glob.glob(os.path.join(work_dir, "assets", "public", "**", "*.js"), recursive=True)
    if not files:
        raise RuntimeError("未找到待验证的 JavaScript 文件")
    failures = []
    for path in files:
        result = subprocess.run([node, "--check", path], capture_output=True,
                                text=True, encoding="utf-8", errors="replace")
        if result.returncode:
            reason = next((line for line in result.stderr.splitlines()
                           if "SyntaxError:" in line), result.stderr[-500:])
            failures.append(f"{os.path.basename(path)}: {reason}")
    if failures:
        raise RuntimeError("JavaScript 语法检查失败，停止打包：\n" + "\n".join(failures))
    log(f"JavaScript 语法检查通过：{len(files)} 个文件", "OK")


def repack_apk(work_dir, output_unsigned_apk):
    log(f"正在打包未签名 APK -> {output_unsigned_apk}")
    if os.path.exists(output_unsigned_apk):
        os.remove(output_unsigned_apk)

    # 移除旧的签名文件
    meta_inf = os.path.join(work_dir, "META-INF")
    if os.path.exists(meta_inf):
        for sig_file in ["CERT.RSA", "CERT.SF", "MANIFEST.MF", "ANDROIDD.SF", "ANDROIDD.RSA"]:
            sp = os.path.join(meta_inf, sig_file)
            if os.path.exists(sp):
                os.remove(sp)

    # 按照 Android 规范精细压缩打包
    with zipfile.ZipFile(output_unsigned_apk, "w") as zf:
        for root, dirs, files in os.walk(work_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, work_dir).replace("\\", "/")
                
                # 排除系统与开发多余文件
                if rel_path.endswith(".DS_Store") or rel_path.startswith("__MACOSX"):
                    continue
                if rel_path.endswith(".apk") or rel_path.endswith(".keystore"):
                    continue

                _, ext = os.path.splitext(file.lower())
                # 核心资源与多媒体文件严格 STORED (不压缩)，其他文件 DEFLATED
                if ext in STORED_EXTENSIONS or file == "resources.arsc":
                    compress_type = zipfile.ZIP_STORED
                else:
                    compress_type = zipfile.ZIP_DEFLATED

                zf.write(full_path, rel_path, compress_type=compress_type)

    log(f"中间包打包完成，大小: {os.path.getsize(output_unsigned_apk) / (1024*1024):.2f} MB", "OK")

def sign_and_align_apk(unsigned_apk, output_signed_apk, uber_signer_jar):
    log(f"正在进行 4 字节对齐与 V1/V2 签名: {unsigned_apk} -> {output_signed_apk}")
    out_dir = os.path.dirname(os.path.abspath(output_signed_apk))
    os.makedirs(out_dir, exist_ok=True)

    cmd = [
        "java", "-jar", uber_signer_jar,
        "-a", unsigned_apk,
        "-o", out_dir
    ]
    log(f"执行命令: {' '.join(cmd)}")
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        log(f"签名失败:\n{res.stdout}\n{res.stderr}", "ERROR")
        sys.exit(1)
    
    # 找到输出的对齐签名包并重命名为目标成品名称
    candidates = glob.glob(os.path.join(out_dir, "*aligned*debugSigned.apk"))
    if not candidates:
        candidates = glob.glob(os.path.join(out_dir, "*debugSigned.apk"))

    if candidates:
        src = candidates[0]
        if os.path.abspath(src) != os.path.abspath(output_signed_apk):
            if os.path.exists(output_signed_apk):
                os.remove(output_signed_apk)
            os.rename(src, output_signed_apk)
            if os.path.exists(src + ".idsig"):
                os.replace(src + ".idsig", output_signed_apk + ".idsig")

    if os.path.exists(output_signed_apk):
        log(f"最终签名成品包生成成功: {output_signed_apk} ({os.path.getsize(output_signed_apk) / (1024*1024):.2f} MB)", "OK")
    else:
        log("未找到最终签名包，请检查输出日志！", "ERROR")
        sys.exit(1)

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)

    default_apk = r"C:\Users\CYZ\.gemini\antigravity\brain\22f465af-b673-4572-b3eb-cd270c653a5f\scratch\v2.1.9\2.1.9.apk"
    apk_input = sys.argv[1] if len(sys.argv) > 1 else default_apk

    if not os.path.exists(apk_input):
        log(f"输入 APK 不存在: {apk_input}", "ERROR")
        sys.exit(1)

    work_dir = os.path.join(project_root, "build_temp", "unpacked")
    unsigned_apk = os.path.join(project_root, "build_temp", "app-unsigned.apk")
    final_apk = os.path.join(project_root, "dist", "JMComic3-v2.1.9-mod-debug.apk")
    uber_signer = os.path.join(script_dir, "bin", "uber-apk-signer.jar")

    unpack_apk(apk_input, work_dir)
    apply_patches(work_dir)
    validate_javascript(work_dir)
    repack_apk(work_dir, unsigned_apk)
    sign_and_align_apk(unsigned_apk, final_apk, uber_signer)
    log("=== [全部流程完成！] ===", "OK")

if __name__ == "__main__":
    main()

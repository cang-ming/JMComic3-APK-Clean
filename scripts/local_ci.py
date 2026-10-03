"""Local build + packaged-bundle regression + emulator cold-start smoke test."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = "com.a7m3p9xv.t6qk2z8.app"
ACTIVITY = PACKAGE + "/com.JMComic3.app.MainActivity"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", nargs="?", help="Official 2.1.9 APK; omitted uses the build script default")
    parser.add_argument("--serial", default="emulator-5554")
    args = parser.parse_args()
    if not re.fullmatch(r"emulator-\d+", args.serial):
        parser.error("CI only installs on an emulator; tablet acceptance is separate")
    report_dir = ROOT / "build_temp" / "local-ci" / datetime.now().strftime("%Y%m%d-%H%M%S")
    report_dir.mkdir(parents=True)
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    report = {"status": "running", "serial": args.serial, "checks": [],
              "limits": "Device smoke stops at age confirmation; login/reader/detail UI are not tested."}

    def run(label, command, timeout=180):
        print(f"[CI] {label}", flush=True)
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                                text=True, encoding="utf-8", errors="replace", timeout=timeout)
        (report_dir / f"{label}.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        if result.returncode:
            raise RuntimeError(f"{label} exited {result.returncode}: {result.stderr[-500:]}")
        return result.stdout

    def adb(*command):
        result = subprocess.run(["adb", "-s", args.serial, *command], capture_output=True,
                                timeout=30, text=True, encoding="utf-8", errors="replace")
        if result.returncode:
            raise RuntimeError(f"adb {command}: {result.stdout}{result.stderr}")
        return result.stdout

    try:
        for tool in ("node", "java", "adb"):
            if not shutil.which(tool):
                raise RuntimeError(f"Missing tool: {tool}")
        if adb("get-state").strip() != "device":
            raise RuntimeError("Start the configured AVD before running local CI")
        run("regressions", [sys.executable, "scripts/test_mod_apk.py"])
        run("build", [sys.executable, "scripts/mod_apk.py", *([args.apk] if args.apk else [])])
        artifact = ROOT / "dist/JMComic3-v2.1.9-mod-debug.apk"
        run("signature", ["java", "-jar", "scripts/bin/uber-apk-signer.jar", "-a", str(artifact), "-y"])
        with tempfile.TemporaryDirectory(dir=report_dir) as scratch:
            with zipfile.ZipFile(artifact) as apk:
                for name in apk.namelist():
                    if name.startswith("assets/public/static/js/") and name.endswith(".js"):
                        (Path(scratch) / Path(name).name).write_bytes(apk.read(name))
            run("bundle-behavior", ["node", "scripts/test_bundle.cjs", scratch])
        report["checks"].extend(["regressions", "build-and-js-syntax", "signature-and-alignment", "packaged-bundle-behavior"])
        installed = run("install", ["adb", "-s", args.serial, "install", "--no-incremental", "-r", str(artifact)])
        if "Success" not in installed:
            raise RuntimeError("APK installation did not report Success")
        adb("shell", "input", "keyevent", "KEYCODE_WAKEUP")
        adb("shell", "wm", "dismiss-keyguard")
        for attempt in (1, 2):
            print(f"[CI] Cold start {attempt}: waiting for confirmation page (up to 90s)", flush=True)
            adb("shell", "am", "force-stop", PACKAGE)
            started = adb("shell", "am", "start", "-W", "-n", ACTIVITY)
            (report_dir / f"start-{attempt}.log").write_text(started, encoding="utf-8")
            if "Status: ok" not in started:
                raise RuntimeError("Activity failed to start")
            deadline = time.monotonic() + 90
            dump_failures = 0
            while time.monotonic() < deadline:
                try:
                    adb("shell", "uiautomator", "dump", "/sdcard/jm-ci.xml")
                except RuntimeError as error:
                    # WebView startup can temporarily leave UIAutomator without an idle root.
                    dump_failures += 1
                    print(f"[CI] UI dump retry {dump_failures}/3: {error}", flush=True)
                    if dump_failures >= 3:
                        raise
                    time.sleep(3)
                    continue
                xml = adb("shell", "cat", "/sdcard/jm-ci.xml")
                (report_dir / f"ui-{attempt}.xml").write_text(xml, encoding="utf-8")
                tree = ET.fromstring(xml)
                texts = [n.get("text", "") for n in tree.iter("node")]
                if any("關閉廣告" in t or "关闭广告" in t for t in texts):
                    raise AssertionError("Cold start still requires closing an advertisement")
                if any("18歲" in t or "18岁" in t for t in texts):
                    report["checks"].append(f"cold-start-{attempt}-confirmation-visible")
                    break
                for node in tree.iter("node"):
                    if re.match(r"[線线]路\d", node.get("text", "")):
                        bounds = list(map(int, re.findall(r"\d+", node.get("bounds", ""))))
                        if len(bounds) == 4:
                            x1, y1, x2, y2 = bounds
                            adb("shell", "input", "tap", str((x1+x2)//2), str((y1+y2)//2))
                            break
                time.sleep(3)
            else:
                raise AssertionError("No confirmation page within 90 seconds; inspect saved UI/logs")
        report["status"] = "passed"
    except Exception as error:
        report["status"] = "failed"
        report["error"] = str(error)
        print(f"[CI] FAIL: {error}", file=sys.stderr)
    finally:
        try:
            pid = adb("shell", "pidof", PACKAGE).strip()
            if pid:
                logs = adb("logcat", "-d", f"--pid={pid}")
                (report_dir / "logcat.log").write_text(logs, encoding="utf-8")
                if "SyntaxError" in logs or "FATAL EXCEPTION" in logs:
                    report["status"] = "failed"
                    report["error"] = "Runtime error found in logcat.log"
        except Exception as error:
            report["logcat_error"] = str(error)
        (report_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"[CI] Report: {report_dir / 'report.json'}", flush=True)
    print(f"[CI] Final status: {report['status']}", flush=True)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

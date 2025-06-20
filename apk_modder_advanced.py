import os
import subprocess

APKTOOL_PATH = "tools/apktool.jar"

def mod_apk(apk_path):
    decompiled = "decompiled_apk"
    cleaned_apk = "cleaned_app.apk"

    # 1. Decompile APK
    subprocess.run(["java", "-jar", APKTOOL_PATH, "d", apk_path, "-o", decompiled, "-f"])

    # 2. Remove common ad SDKs (like AdMob, UnityAds, etc.)
    ad_keywords = ["com.google.android.gms.ads", "com.unity3d.ads", "facebook.ads", "adcolony", "applovin"]
    smali_dir = os.path.join(decompiled, "smali")
    for root, dirs, files in os.walk(smali_dir):
        for file in files:
            if file.endswith(".smali"):
                fpath = os.path.join(root, file)
                with open(fpath, "r+", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    for keyword in ad_keywords:
                        if keyword in content:
                            content = content.replace(keyword, "// removed ad sdk")
                    f.seek(0)
                    f.write(content)
                    f.truncate()

    # 3. Remove webview-based redirects to ad sites
    for root, dirs, files in os.walk(smali_dir):
        for file in files:
            if file.endswith(".smali"):
                fpath = os.path.join(root, file)
                with open(fpath, "r+", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if "loadUrl(\"http" in content:
                        content = content.replace("loadUrl", "// removed webview ad")
                    f.seek(0)
                    f.write(content)
                    f.truncate()

    # 4. Remove watch-to-unlock logic (patch ad check to always true)
    for root, dirs, files in os.walk(smali_dir):
        for file in files:
            if file.endswith(".smali"):
                fpath = os.path.join(root, file)
                with open(fpath, "r+", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if "if-eqz" in content or "if-nez" in content:
                        content = content.replace("if-eqz", "const/4 v0, 0x1  # always true")
                    f.seek(0)
                    f.write(content)
                    f.truncate()

    # 5. Remove trackers and malicious domains (if strings.xml has known URLs)
    trackers = ["firebase", "onesignal", "adjust", "google-analytics", "doubleclick"]
    strings_path = os.path.join(decompiled, "res", "values", "strings.xml")
    if os.path.exists(strings_path):
        with open(strings_path, "r+", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            for t in trackers:
                if t in content:
                    content = content.replace(t, "blocked-tracker")
            f.seek(0)
            f.write(content)
            f.truncate()

    # 6. Remove unwanted permissions
    manifest = os.path.join(decompiled, "AndroidManifest.xml")
    if os.path.exists(manifest):
        with open(manifest, "r+", encoding="utf-8", errors="ignore") as f:
            content = f.read()
            danger_perms = ["READ_SMS", "RECEIVE_SMS", "READ_CONTACTS", "ACCESS_FINE_LOCATION"]
            for p in danger_perms:
                content = content.replace(f'android.permission.{p}', "REMOVED")
            f.seek(0)
            f.write(content)
            f.truncate()

    # 7. Rebuild APK
    subprocess.run(["java", "-jar", APKTOOL_PATH, "b", decompiled, "-o", cleaned_apk])

    # 8. Sign APK (optional for installation)
    # subprocess.run(["java", "-jar", "tools/apksigner.jar", "--ks", "debug.keystore", "--out", "signed.apk", cleaned_apk])

    return cleaned_apk

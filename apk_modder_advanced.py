import os
import re
import shutil
import subprocess

APKTOOL_PATH = "tools/apktool.2.11.1.jar"  # Adjust if needed

def mod_apk(input_apk):
    if not os.path.exists("tools"):
        os.makedirs("tools")

    # Step 1: Decompile APK
    subprocess.run(["java", "-jar", APKTOOL_PATH, "d", input_apk, "-o", "decompiled", "-f"], check=True)

    smali_path = "decompiled/smali"
    logs = []

    # Step 2: Scan for Ads & Malware Strings
    ad_keywords = ["admob", "ads", "com.google.android.gms.ads", "facebook.ads", "unityads"]
    malware_keywords = ["coinhive", "payload", "auto_downloader", "bootreceiver"]

    for root, dirs, files in os.walk(smali_path):
        for file in files:
            if file.endswith(".smali"):
                full_path = os.path.join(root, file)
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                original_content = content

                for kw in ad_keywords + malware_keywords:
                    content = re.sub(rf'.*{re.escape(kw)}.*\n?', '', content)

                if content != original_content:
                    logs.append(f"[CLEANED] {full_path}")
                    with open(full_path, "w", encoding="utf-8") as f:
                        f.write(content)

    # Step 3: Clean AndroidManifest.xml
    manifest = "decompiled/AndroidManifest.xml"
    if os.path.exists(manifest):
        with open(manifest, "r", encoding="utf-8") as f:
            manifest_data = f.read()
        original_manifest = manifest_data

        dangerous_permissions = [
            "RECEIVE_SMS", "READ_SMS", "SEND_SMS", "READ_CALL_LOG",
            "RECEIVE_BOOT_COMPLETED", "SYSTEM_ALERT_WINDOW"
        ]
        for perm in dangerous_permissions:
            manifest_data = re.sub(rf'<uses-permission[^>]*{perm}[^>]*>', '', manifest_data)

        if manifest_data != original_manifest:
            logs.append("[CLEANED] Dangerous permissions removed from Manifest")
            with open(manifest, "w", encoding="utf-8") as f:
                f.write(manifest_data)

    # Step 4: Recompile APK
    subprocess.run(["java", "-jar", APKTOOL_PATH, "b", "decompiled", "-o", "cleaned_output.apk"], check=True)

    # Step 5: Save logs
    with open("detected_trackers.txt", "w") as log_file:
        log_file.write("\n".join(logs) if logs else "✅ No trackers/ads found.")

    return "cleaned_output.apk"

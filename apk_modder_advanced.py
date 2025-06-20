
import os
import shutil
import subprocess

APKTOOL_PATH = "apktool"  # Ensure this is in your system path
SIGNED_APK = "signed_output.apk"
TRACKER_LOG = "detected_trackers.txt"

def mod_apk(apk_path):
    app_name = "decompiled_app"
    cleaned_apk = "recompiled.apk"

    # Step 1: Decompile APK
    if os.path.exists(app_name):
        shutil.rmtree(app_name)
    subprocess.run([APKTOOL_PATH, "d", apk_path, "-o", app_name, "-f"], check=True)

    # Step 2: Clean the Manifest (remove bad permissions)
    manifest_path = os.path.join(app_name, "AndroidManifest.xml")
    if os.path.exists(manifest_path):
        with open(manifest_path, "r") as f:
            content = f.read()
        bad_permissions = [
            "RECORD_AUDIO", "READ_CONTACTS", "WRITE_CONTACTS", "ACCESS_FINE_LOCATION",
            "ACCESS_COARSE_LOCATION", "READ_SMS", "SEND_SMS", "RECEIVE_SMS"
        ]
        for perm in bad_permissions:
            content = content.replace(f'android.permission.{perm}', "REMOVED_BY_MAJDOOR")
        with open(manifest_path, "w") as f:
            f.write(content)

    # Step 3: Scan and remove ad SDK & tracker references
    ad_keywords = ["admob", "facebook.ads", "chartboost", "unityads", "startapp"]
    tracker_keywords = ["track", "analytics", "crashlytics", "adjust", "flurry", "firebase", "segment"]
    found_trackers = []

    for root, _, files in os.walk(app_name):
        for file in files:
            if file.endswith(".smali"):
                path = os.path.join(root, file)
                with open(path, "r") as f:
                    lines = f.readlines()
                new_lines = []
                for line in lines:
                    if any(ad in line.lower() for ad in ad_keywords):
                        continue  # Remove ads
                    if any(tk in line.lower() for tk in tracker_keywords):
                        found_trackers.append(line.strip())
                    new_lines.append(line)
                with open(path, "w") as f:
                    f.writelines(new_lines)

    # Write found trackers to file
    with open(TRACKER_LOG, "w") as f:
        if found_trackers:
            f.write("Detected tracker-related code:\n")
            for tracker in found_trackers:
                f.write(tracker + "\n")
        else:
            f.write("No trackers found.")

    # Step 4: Inject branding into app_name in strings.xml
    strings_xml_path = os.path.join(app_name, "res", "values", "strings.xml")
    if os.path.exists(strings_xml_path):
        with open(strings_xml_path, "r", encoding="utf-8") as f:
            strings_content = f.read()
        strings_content = strings_content.replace("<string name=\"app_name\">", "<string name=\"app_name\">Majdoor_")
        with open(strings_xml_path, "w", encoding="utf-8") as f:
            f.write(strings_content)

    # Step 5: Rebuild APK
    subprocess.run([APKTOOL_PATH, "b", app_name, "-o", cleaned_apk], check=True)

    # Step 6: Sign APK
    try:
        subprocess.run([
            "apksigner", "sign",
            "--ks", "debug.keystore",
            "--ks-pass", "pass:android",
            "--key-pass", "pass:android",
            "--out", SIGNED_APK,
            cleaned_apk
        ], check=True)
        return SIGNED_APK
    except Exception as e:
        print("Signing failed. Returning unsigned APK.")
        return cleaned_apk

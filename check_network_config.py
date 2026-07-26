import os

manifest_path = "app/src/main/AndroidManifest.xml"
with open(manifest_path, "r", encoding="utf-8") as f:
    manifest = f.read()

print("=== networkSecurityConfig ב-manifest? ===")
if "networkSecurityConfig" in manifest:
    idx = manifest.find("networkSecurityConfig")
    print(manifest[max(0,idx-100):idx+200])
else:
    print("לא נמצא הפניה ל-networkSecurityConfig")

print("\n=== usesCleartextTraffic ב-manifest? ===")
if "usesCleartextTraffic" in manifest:
    idx = manifest.find("usesCleartextTraffic")
    print(manifest[max(0,idx-100):idx+150])
else:
    print("לא נמצא")

print("\n=== קובץ network_security_config.xml קיים? ===")
nsc_path = "app/src/main/res/xml/network_security_config.xml"
if os.path.exists(nsc_path):
    with open(nsc_path, "r", encoding="utf-8") as f:
        print(f.read())
else:
    print("הקובץ לא קיים")

print("\n=== הרשאת INTERNET ב-manifest? ===")
print("android.permission.INTERNET" in manifest)

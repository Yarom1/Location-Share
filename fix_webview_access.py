import shutil

path = "app/src/main/java/com/locationshare/MainActivity.kt"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = """            allowFileAccess = true
            allowContentAccess = true"""
new = """            allowFileAccess = true
            allowContentAccess = true
            allowFileAccessFromFileURLs = true
            allowUniversalAccessFromFileURLs = true"""

count = content.count(old)
if count == 0:
    print("❌ לא נמצא")
elif count > 1:
    print(f"⚠️ {count} מופעים")
else:
    shutil.copy(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.replace(old, new))
    print("✅ נוספו allowFileAccessFromFileURLs ו-allowUniversalAccessFromFileURLs")

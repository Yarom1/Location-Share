import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '<div class="modal" id="cropModal">'
new = '<div class="modal" id="cropModal" style="z-index:600">'

count = content.count(old)
if count == 0:
    print("❌ לא נמצא")
elif count > 1:
    print(f"⚠️ {count} מופעים")
else:
    shutil.copy(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.replace(old, new))
    print("✅ נוסף z-index:600 ל-cropModal - יופיע תמיד מעל מודאלים אחרים")

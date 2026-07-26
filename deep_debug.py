import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "showToast('שגיאה: '+(e&&e.message?e.message:JSON.stringify(e)),'error');"
new = "showToast('שגיאה: '+(e&&e.errors?e.errors.map(x=>x&&x.message).join(' | '):(e&&e.message?e.message:JSON.stringify(e))),'error');"

count = content.count(old)
if count == 0:
    print("❌ לא נמצא")
elif count > 1:
    print(f"⚠️ {count} מופעים")
else:
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.replace(old, new))
    print("✅ עכשיו יוצגו השגיאות הפרטניות מכל שרת")

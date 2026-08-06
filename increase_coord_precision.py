import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "el.textContent='📍 '+addPointCoords.lat.toFixed(5)+', '+addPointCoords.lng.toFixed(5)+' — הזז את המפה לדיוק';"
new = "el.textContent='📍 '+addPointCoords.lat.toFixed(6)+', '+addPointCoords.lng.toFixed(6)+' — הזז את המפה לדיוק';"

count = content.count(old)
if count == 0:
    print("❌ לא נמצא עוגן מדויק")
elif count > 1:
    print(f"⚠️ {count} מופעים")
else:
    shutil.copy(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.replace(old, new))
    print("✅ תצוגה עודכנה ל-6 ספרות")

import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "map.flyTo({center:[lng,lat],zoom:17});"
new = "map.flyTo({center:[lng,lat],zoom:17,padding:{top:0,bottom:0,left:0,right:0}});"

count = content.count(old)
if count == 0:
    print("❌ לא נמצא עוגן מדויק - בדוק ידנית")
elif count > 1:
    print(f"⚠️ {count} מופעים - צריך לצמצם")
else:
    shutil.copy(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.replace(old, new))
    print("✅ padding מאופס במפורש בכניסה לדיוק נקודה")

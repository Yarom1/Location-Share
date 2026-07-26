import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "fetch(url,{method:'POST',body:query,signal:controller.signal})"
new = "fetch(url,{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:query,signal:controller.signal})"

count = content.count(old)
if count == 0:
    print("❌ לא נמצא")
elif count > 1:
    print(f"⚠️ {count} מופעים")
else:
    shutil.copy(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.replace(old, new))
    print("✅ נוסף Content-Type: application/x-www-form-urlencoded")

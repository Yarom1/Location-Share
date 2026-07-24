import re

kpath = "app/src/main/java/com/locationshare/MainActivity.kt"
spath = "app/src/main/java/com/locationshare/LocationService.kt"

def show(path, keyword, label, span=400):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"\n{'='*15} {label} ({keyword}) ב-{path.split('/')[-1]} {'='*15}")
    matches = list(re.finditer(re.escape(keyword), content))
    if not matches:
        print("(לא נמצא)")
        return
    for m in matches[:2]:
        start = max(0, m.start() - 150)
        end = min(len(content), m.end() + span)
        print(content[start:end])
        print("---")

show(kpath, "startService", "הפעלת השירות")
show(kpath, "startForegroundService", "הפעלת foreground service")
show(spath, "onStartCommand", "onStartCommand בשירות")
show(spath, "stopSelf", "עצירה עצמית של השירות")
show(spath, "onDestroy", "onDestroy בשירות")
show(kpath, "class WebAppInterface", "תחילת הגשר (לבדוק פונקציות קיימות)")

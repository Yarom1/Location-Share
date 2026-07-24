import re

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def show(keyword, label, span=500, max_matches=2):
    print(f"\n{'='*15} {label} ({keyword}) {'='*15}")
    matches = list(re.finditer(re.escape(keyword), content))
    if not matches:
        print("(לא נמצא)")
        return
    for m in matches[:max_matches]:
        start = max(0, m.start() - 150)
        end = min(len(content), m.end() + span)
        print(content[start:end])
        print("---")

show("id=\"settingsPanel\"", "פאנל הגדרות - id")
show("panel-settings", "פאנל הגדרות - class אפשרי")
show("online:false", "כתיבת online:false (יציאה מקבוצה)")
show("setOnlineStatus", "פונקציית עדכון סטטוס")
show("selfViewOnly", "כפתור תצוגה עצמית (לזיהוי אזור קוד קשור)")

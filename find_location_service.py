import re

path = "app/src/main/java/com/locationshare/LocationService.kt"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def show(keyword, label, span=500, max_matches=3):
    print(f"\n{'='*15} {label} ({keyword}) {'='*15}")
    matches = list(re.finditer(re.escape(keyword), content))
    print(f"מספר מופעים: {len(matches)}")
    for m in matches[:max_matches]:
        start = max(0, m.start() - 150)
        end = min(len(content), m.end() + span)
        print(content[start:end])
        print("---")

show("LocationRequest", "בקשת מיקום")
show("setInterval", "אינטרוול")
show("Priority", "עדיפות דיוק")
show("interval", "interval - כל התייחסות")

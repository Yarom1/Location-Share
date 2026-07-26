import re

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def show(keyword, label, span=500, max_matches=3):
    print(f"\n{'='*15} {label} ({keyword}) {'='*15}")
    matches = list(re.finditer(re.escape(keyword), content))
    print(f"מספר מופעים: {len(matches)}")
    for m in matches[:max_matches]:
        start = max(0, m.start() - 150)
        end = min(len(content), m.end() + span)
        print(f"[אינדקס {m.start()}]")
        print(content[start:end])
        print("---")

show("overpass", "התייחסויות ל-Overpass (lowercase)")
show("Overpass", "Overpass (עם אות גדולה)")
show("localStorage", "שימוש קיים ב-localStorage")
show("indexedDB", "שימוש קיים ב-IndexedDB")
show("toggleAllPoints", "toggleAllPoints")

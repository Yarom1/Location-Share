import re

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def show(keyword, label, span=600, max_matches=2):
    print(f"\n{'='*15} {label} ({keyword}) {'='*15}")
    matches = list(re.finditer(re.escape(keyword), content))
    print(f"מספר מופעים: {len(matches)}")
    for m in matches[:max_matches]:
        start = max(0, m.start() - 150)
        end = min(len(content), m.end() + span)
        print(content[start:end])
        print("---")

show("photoInput", "אינפוט קובץ לתמונה")
show("FileReader", "קריאת קובץ")
show("photoURL", "photoURL - שימוש כללי")
show("function openEditProfile", "פתיחת עריכת פרופיל")

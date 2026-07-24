import re

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def show(keyword, label, span=500, max_matches=3):
    print(f"\n{'='*15} {label} ({keyword}) {'='*15}")
    matches = list(re.finditer(re.escape(keyword), content))
    if not matches:
        print("(לא נמצא)")
        return
    for m in matches[:max_matches]:
        start = max(0, m.start() - 300)
        end = min(len(content), m.end() + span)
        print(content[start:end])
        print("---")

show("saveAuthCredentials", "קריאה ל-saveAuthCredentials מה-JS")
show("onAuthStateChanged", "מאזין למצב אימות")

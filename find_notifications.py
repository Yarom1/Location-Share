import re

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def show(keyword, label, span=600, max_matches=2):
    print(f"\n{'='*15} {label} ({keyword}) {'='*15}")
    matches = list(re.finditer(re.escape(keyword), content))
    print(f"מספר מופעים: {len(matches)}")
    for m in matches[:max_matches]:
        start = max(0, m.start() - 200)
        end = min(len(content), m.end() + span)
        print(content[start:end])
        print("---")

show("showAlertNotification", "קריאה להתראה נייטיבית")
show("checkForNewChatMessages", "בדיקת הודעות חדשות (צ'אט קבוצתי)")
show("function openDM", "פתיחת צ'אט פרטי")

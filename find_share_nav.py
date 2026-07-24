import re

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def show_context(keyword, label, span=600):
    print(f"\n{'='*20} חיפוש: {label} ({keyword}) {'='*20}")
    for m in re.finditer(re.escape(keyword), content):
        start = max(0, m.start() - span)
        end = min(len(content), m.end() + span)
        print(f"\n--- מופע באינדקס {m.start()} ---")
        print(content[start:end])
        print("--- סוף מופע ---")

show_context("navigator.share", "navigator.share (שימוש קיים)")
show_context("shareGroup", "פונקציית שיתוף קבוצה")
show_context("geo:", "כפתור ניווט (geo: intent)")

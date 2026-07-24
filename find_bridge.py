import re

path = "app/src/main/java/com/locationshare/MainActivity.kt"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def show_context(keyword, label, span=500):
    print(f"\n{'='*20} חיפוש: {label} ({keyword}) {'='*20}")
    matches = list(re.finditer(re.escape(keyword), content))
    if not matches:
        print("(לא נמצא)")
        return
    m = matches[0]
    start = max(0, m.start() - 200)
    end = min(len(content), m.end() + span)
    print(content[start:end])

show_context("class AndroidBridge", "הגדרת מחלקת הגשר")
show_context("@JavascriptInterface", "פונקציית גשר לדוגמה")
show_context("addJavascriptInterface", "רישום הגשר ל-WebView")

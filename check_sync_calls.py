import re

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

print("=== כל המקומות שבהם syncAuthToNative() נקרא ===")
for m in re.finditer(re.escape("syncAuthToNative()"), content):
    start = max(0, m.start() - 200)
    end = min(len(content), m.end() + 100)
    print(f"\n--- אינדקס {m.start()} ---")
    print(content[start:end])

print("\n\n=== חיפוש startApp (איפה זה נקרא ומה בפנים) ===")
idx = content.find("function startApp(")
if idx != -1:
    print(content[idx:idx+800])

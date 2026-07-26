import re

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

for m in re.finditer(re.escape("handleProfileImage"), content):
    start = max(0, m.start()-300)
    end = min(len(content), m.end()+150)
    print(f"\n[אינדקס {m.start()}]")
    print(content[start:end])
    print("---")

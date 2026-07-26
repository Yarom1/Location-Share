import re

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

for m in re.finditer(re.escape("usersList"), content):
    start = max(0, m.start()-250)
    end = min(len(content), m.end()+250)
    print(f"\n[אינדקס {m.start()}]")
    print(content[start:end])
    print("---")

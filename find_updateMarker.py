import re

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("function updateMarker(")
if idx == -1:
    print("(לא נמצא updateMarker)")
else:
    print(content[idx:idx+1500])

print("\n\n=== קריאות ל-updateMarker(myUID ===")
for m in re.finditer(re.escape("updateMarker(myUID"), content):
    start = max(0, m.start()-300)
    end = min(len(content), m.end()+100)
    print(f"\n[אינדקס {m.start()}]")
    print(content[start:end])

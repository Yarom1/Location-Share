import re

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("function showUserPopup")
print("=== showUserPopup מלא ===")
print(content[idx:idx+1600])

print("\n\n=== חיפוש usersList / user-item ===")
for kw in ["usersList", "renderUsers", "class=\"user-item\""]:
    matches = list(re.finditer(re.escape(kw), content))
    print(f"{kw}: {len(matches)} מופעים")

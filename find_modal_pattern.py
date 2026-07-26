import re

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find('id="editProfileModal"')
print(content[max(0,idx-100):idx+900])

print("\n\n=== openModal/closeModal definitions ===")
idx2 = content.find("function openModal")
print(content[idx2:idx2+400])

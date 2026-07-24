import re

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find('id="settingsPanel"')
print(content[idx:idx+3500])

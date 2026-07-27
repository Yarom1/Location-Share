import re

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("window.addEventListener('beforeunload'")
print(content[max(0,idx-100):idx+700])

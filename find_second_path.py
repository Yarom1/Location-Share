path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

print(content[62800:64300])

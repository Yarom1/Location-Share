path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

print(content[70800:73000])

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("// ===== POI LAYERS")
print(content[idx:idx+5500])

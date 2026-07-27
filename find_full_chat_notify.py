path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("function listenGroupChat(){")
print("=== listenGroupChat מלא ===")
print(content[idx:idx+2400])

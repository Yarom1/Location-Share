import re

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("let lastSpeed")
print("=== סביבת lastSpeed ===")
print(content[max(0,idx-100):idx+100])

print("\n\n=== watchPosition המלא ===")
idx2 = content.find("navigator.geolocation.watchPosition")
print(content[idx2:idx2+1800])

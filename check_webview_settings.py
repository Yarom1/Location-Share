path = "app/src/main/java/com/locationshare/MainActivity.kt"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("webView.settings")
if idx == -1:
    idx = content.find(".settings.apply")
print(content[max(0,idx-200):idx+1800])

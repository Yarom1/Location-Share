path = "app/src/main/java/com/locationshare/LocationService.kt"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("private fun startLocationUpdates")
if idx == -1:
    idx = content.find("fun startLocationUpdates")
print(content[max(0,idx-400):idx+2200])

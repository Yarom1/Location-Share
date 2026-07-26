import re

path = "app/src/main/java/com/locationshare/LocationService.kt"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

for m in re.finditer(re.escape("requestLocationUpdates"), content):
    start = max(0, m.start()-400)
    end = min(len(content), m.end()+400)
    print(f"\n[אינדקס {m.start()}]")
    print(content[start:end])
    print("---")

print("\n\n=== heartbeat ===")
idx = content.find("heartbeatRunnable")
print(content[max(0,idx-200):idx+1200])

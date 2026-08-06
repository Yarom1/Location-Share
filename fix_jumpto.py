import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def report(ok, label, extra=""):
    print(("✅ " if ok else "❌ ")+label+" "+extra)

old1 = "map.flyTo({center:[lng,lat],zoom:17,pitch:0,bearing:0,padding:{top:0,bottom:0,left:0,right:0}});"
new1 = "map.jumpTo({center:[lng,lat],zoom:17,pitch:0,bearing:0,padding:{top:0,bottom:0,left:0,right:0}});"
if content.count(old1) == 0:
    report(False, "jumpTo ב-startCenterPinRefine", "- לא נמצא עוגן מדויק")
elif content.count(old1) > 1:
    report(False, "jumpTo ב-startCenterPinRefine", f"- {content.count(old1)} מופעים")
else:
    shutil.copy(path, path + ".bak")
    content = content.replace(old1, new1)
    report(True, "jumpTo ב-startCenterPinRefine", "- קפיצה מיידית")

old2 = "map.flyTo({center:[p.lng,p.lat],zoom:17,pitch:0,bearing:0,padding:{top:0,bottom:0,left:0,right:0}});"
new2 = "map.jumpTo({center:[p.lng,p.lat],zoom:17,pitch:0,bearing:0,padding:{top:0,bottom:0,left:0,right:0}});"
if content.count(old2) == 0:
    report(False, "jumpTo ב-startEditLocation", "- לא נמצא עוגן מדויק")
elif content.count(old2) > 1:
    report(False, "jumpTo ב-startEditLocation", f"- {content.count(old2)} מופעים")
else:
    content = content.replace(old2, new2)
    report(True, "jumpTo ב-startEditLocation", "- קפיצה מיידית")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

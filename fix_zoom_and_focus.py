import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def report(ok, label, extra=""):
    print(("✅ " if ok else "❌ ")+label+" "+extra)

old1 = "let locating=false;let lastLat=0,lastLng=0;function locateMe(){\n  stopTrackingAndCompass();\n"
new1 = "let locating=false;let lastLat=0,lastLng=0;function locateMe(){\n"
if content.count(old1) == 0:
    report(False, "הסרת stopTrackingAndCompass מ-locateMe", "- לא נמצא עוגן מדויק")
elif content.count(old1) > 1:
    report(False, "הסרת stopTrackingAndCompass מ-locateMe", f"- {content.count(old1)} מופעים")
else:
    content = content.replace(old1, new1)
    report(True, "הסרת stopTrackingAndCompass מ-locateMe", "- כפתור פוקוס כבר לא מכבה מעקב/מצפן")

old2 = "map.easeTo({center:[smoothLng,smoothLat],duration:400,padding:{top:window.innerHeight*TRACK_PAD_TOP_FRAC,bottom:0,left:0,right:0},pitch:navModeActive?map.getMaxPitch():0});"
new2 = "map.easeTo({center:[smoothLng,smoothLat],zoom:17,duration:400,padding:{top:window.innerHeight*TRACK_PAD_TOP_FRAC,bottom:0,left:0,right:0},pitch:navModeActive?map.getMaxPitch():0});"
if content.count(old2) == 0:
    report(False, "נעילת zoom:17 בטיקים הרציפים", "- לא נמצא עוגן מדויק")
elif content.count(old2) > 1:
    report(False, "נעילת zoom:17 בטיקים הרציפים", f"- {content.count(old2)} מופעים")
else:
    content = content.replace(old2, new2)
    report(True, "נעילת zoom:17 בטיקים הרציפים", "- כל טיק מבטיח התכנסות לזום הנכון")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

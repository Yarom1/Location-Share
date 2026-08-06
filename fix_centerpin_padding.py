import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '''function startCenterPinRefine(lat,lng){
  map.flyTo({center:[lng,lat],zoom:17});
  document.getElementById('centerPinFixed').style.display='block';'''

new = '''function startCenterPinRefine(lat,lng){
  map.flyTo({center:[lng,lat],zoom:17,padding:{top:0,bottom:0,left:0,right:0}});
  document.getElementById('centerPinFixed').style.display='block';'''

count = content.count(old)
if count == 0:
    print("❌ לא נמצא עוגן מדויק")
elif count > 1:
    print(f"⚠️ {count} מופעים")
else:
    shutil.copy(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.replace(old, new))
    print("✅ padding מאופס במפורש בכניסה לדיוק נקודה")

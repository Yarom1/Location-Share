import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def report(ok, label, extra=""):
    print(("✅ " if ok else "❌ ")+label+" "+extra)

old1 = '''map.flyTo({center:[lng,lat],zoom:17,padding:{top:0,bottom:0,left:0,right:0}});
  document.getElementById('centerPinFixed').style.display='block';
  centerPinActive=true;
  addPointCoords={lat,lng};
  updateCenterPinCoordsDisplay();
  map.on('move',onCenterPinMove);'''

new1 = '''map.flyTo({center:[lng,lat],zoom:17,padding:{top:0,bottom:0,left:0,right:0}});
  document.getElementById('centerPinFixed').style.display='block';
  positionCenterPinFixed();
  centerPinActive=true;
  addPointCoords={lat,lng};
  updateCenterPinCoordsDisplay();
  map.on('move',onCenterPinMove);
  map.on('moveend',onCenterPinMove);'''

count1 = content.count(old1)
if count1 == 0:
    report(False, "startCenterPinRefine מלא", "- לא נמצא עוגן מדויק")
elif count1 > 1:
    report(False, "startCenterPinRefine מלא", f"- {count1} מופעים")
else:
    shutil.copy(path, path + ".bak")
    content = content.replace(old1, new1)
    report(True, "startCenterPinRefine מלא", "- positionCenterPinFixed + moveend נוספו")

old2 = '''map.flyTo({center:[p.lng,p.lat],zoom:17});
  document.getElementById('centerPinFixed').style.display='block';
  centerPinActive=true;
  addPointCoords={lat:p.lat,lng:p.lng};
  map.on('move',onCenterPinMove);'''

new2 = '''map.flyTo({center:[p.lng,p.lat],zoom:17,padding:{top:0,bottom:0,left:0,right:0}});
  document.getElementById('centerPinFixed').style.display='block';
  positionCenterPinFixed();
  centerPinActive=true;
  addPointCoords={lat:p.lat,lng:p.lng};
  map.on('move',onCenterPinMove);
  map.on('moveend',onCenterPinMove);'''

count2 = content.count(old2)
if count2 == 0:
    report(False, "startEditLocation מלא", "- לא נמצא עוגן מדויק")
elif count2 > 1:
    report(False, "startEditLocation מלא", f"- {count2} מופעים")
else:
    content = content.replace(old2, new2)
    report(True, "startEditLocation מלא", "- padding + positionCenterPinFixed + moveend נוספו")

old3 = "map.off('move',onCenterPinMove);"
new3 = "map.off('move',onCenterPinMove);\n  map.off('moveend',onCenterPinMove);"
count3 = content.count(old3)
if count3 == 0:
    report(False, "ניתוק moveend", "- לא נמצא עוגן מדויק")
elif count3 > 1:
    report(False, "ניתוק moveend", f"- {count3} מופעים")
else:
    content = content.replace(old3, new3)
    report(True, "ניתוק moveend", "- נוסף")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

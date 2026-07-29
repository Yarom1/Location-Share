import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '''  await addDoc(gCol('savedPoints'),{
    name,desc,
    lat:addPointCoords.lat,
    lng:addPointCoords.lng,
    creatorUid:myUID,
    creatorName:currentUser?currentUser.name:'',
    createdAt:serverTimestamp()
  });
  closeAddPointSheet();'''

new = '''  const newPointRef=await addDoc(gCol('savedPoints'),{
    name,desc,
    lat:addPointCoords.lat,
    lng:addPointCoords.lng,
    creatorUid:myUID,
    creatorName:currentUser?currentUser.name:'',
    createdAt:serverTimestamp()
  });
  visiblePoints[newPointRef.id]=true;
  renderPointsList();
  renderPointMarkers();
  closeAddPointSheet();'''

count = content.count(old)
if count == 0:
    print("❌ לא נמצא עוגן מדויק")
elif count > 1:
    print(f"⚠️ {count} מופעים")
else:
    shutil.copy(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.replace(old, new))
    print("✅ נקודה חדשה תוצג אוטומטית מיד עם היצירה")

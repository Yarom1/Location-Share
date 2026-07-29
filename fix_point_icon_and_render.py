import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def report(ok, label, extra=""):
    print(("✅ " if ok else "❌ ")+label+" "+extra)

old1 = "  el.innerHTML='<div style=\"font-size:28px;filter:drop-shadow(0 2px 4px rgba(0,0,0,.5))\">📍</div>';"
new1 = '''  el.innerHTML=`<svg width="22" height="28" viewBox="0 0 22 28" style="filter:drop-shadow(0 2px 3px rgba(0,0,0,.4))">
    <path d="M11 0C4.9 0 0 4.9 0 11c0 8.25 11 17 11 17s11-8.75 11-17C22 4.9 17.1 0 11 0z" fill="#00d4aa"/>
    <circle cx="11" cy="11" r="4.5" fill="#0d1117"/>
  </svg>`;'''
if content.count(old1) == 0:
    report(False, "תיקון אייקון תצוגה מקדימה", "- לא נמצא עוגן מדויק")
elif content.count(old1) > 1:
    report(False, "תיקון אייקון תצוגה מקדימה", f"- {content.count(old1)} מופעים")
else:
    shutil.copy(path, path + ".bak")
    content = content.replace(old1, new1)
    report(True, "תיקון אייקון תצוגה מקדימה", "- פין ירוק תואם במקום 📍")

old2 = '''  const newPointRef=await addDoc(gCol('savedPoints'),{
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

new2 = '''  const newPointData={
    name,desc,
    lat:addPointCoords.lat,
    lng:addPointCoords.lng,
    creatorUid:myUID,
    creatorName:currentUser?currentUser.name:''
  };
  const newPointRef=await addDoc(gCol('savedPoints'),{...newPointData,createdAt:serverTimestamp()});
  savedPoints[newPointRef.id]=newPointData;
  visiblePoints[newPointRef.id]=true;
  renderPointsList();
  renderPointMarkers();
  closeAddPointSheet();'''

count2 = content.count(old2)
if count2 == 0:
    report(False, "רינדור מיידי אמיתי של הנקודה החדשה", "- לא נמצא עוגן מדויק")
elif count2 > 1:
    report(False, "רינדור מיידי אמיתי של הנקודה החדשה", f"- {count2} מופעים")
else:
    content = content.replace(old2, new2)
    report(True, "רינדור מיידי אמיתי של הנקודה החדשה", "- נתוני הנקודה מוזנים מקומית לפני הרינדור")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

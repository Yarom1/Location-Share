import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '''  window.onBackgroundLocation=async function(lat,lng){
    if(!myUID||!currentUser)return;
    const dist=Math.abs(lat-lastLat)+Math.abs(lng-lastLng);
    if(dist<0.00005)return;
    lastLat=lat;lastLng=lng;
    if(activeGroupId){
      await setDoc(gDoc('locations',myUID),{lat,lng,online:true,lastSeen:serverTimestamp()},{merge:true});
    }
    if(currentUser&&!trackingMode)updateMarker(myUID,{...currentUser,lat,lng});
  };'''

new = '''  window.onBackgroundLocation=async function(lat,lng){
    if(!myUID||!currentUser)return;
    const dist=Math.abs(lat-lastLat)+Math.abs(lng-lastLng);
    if(dist<0.00005)return;
    lastLat=lat;lastLng=lng;
    if(activeGroupId){
      await setDoc(gDoc('locations',myUID),{lat,lng,online:true,lastSeen:serverTimestamp()},{merge:true});
    }
    // הוסר מכוון: אין כאן עדכון סמן מקומי - watchPosition של ה-JS כבר אחראי בלעדית על זה
    // (שני מסלולים שמעדכנים את אותו סמן במקביל גרמו לקפיצות אחורה/קדימה בחזרה מרקע)
  };'''

count = content.count(old)
if count == 0:
    print("❌ לא נמצא עוגן מדויק")
elif count > 1:
    print(f"⚠️ {count} מופעים")
else:
    shutil.copy(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.replace(old, new))
    print("✅ הוסר עדכון הסמן הכפול מ-onBackgroundLocation - נשארה רק כתיבת Firestore")

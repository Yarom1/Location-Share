import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def report(ok, label, extra=""):
    print(("✅ " if ok else "❌ ")+label+" "+extra)

old1 = "let lastSpeed=0;"
if "navModeActive" in content and "NAV_SPEED_MS" in content:
    report(False, "משתנים גלובליים", "- כבר קיימים, מדלג")
elif content.count(old1) != 1:
    report(False, "משתנים גלובליים", f"- עוגן נמצא {content.count(old1)} פעמים")
else:
    new1 = "let lastSpeed=0;\nlet navModeActive=false;\nconst NAV_SPEED_MS=3.5/3.6;"
    content = content.replace(old1, new1)
    report(True, "משתנים גלובליים", "- נוספו navModeActive, NAV_SPEED_MS")

anchor2 = "function updateTrackingMarkerFixed(){"
if "function createNavMarkerHTML(" in content:
    report(False, "createNavMarkerHTML", "- כבר קיים, מדלג")
elif content.count(anchor2) != 1:
    report(False, "createNavMarkerHTML", f"- עוגן נמצא {content.count(anchor2)} פעמים")
else:
    nav_html_func = '''function createNavMarkerHTML(){
  return '<div style="position:relative;width:64px;height:64px;display:flex;align-items:center;justify-content:center">'
    +'<div style="position:absolute;width:64px;height:64px;border-radius:50%;background:rgba(0,212,170,0.22);box-shadow:0 0 16px 4px rgba(0,212,170,0.35)"></div>'
    +'<div style="width:34px;height:34px;filter:drop-shadow(0 2px 5px rgba(0,0,0,.5))">'
    +'<svg width="34" height="34" viewBox="0 0 24 24"><path d="M12 1.5 L21 21 L12 16.5 L3 21 Z" fill="#00d4aa" stroke="#ffffff" stroke-width="1.3" stroke-linejoin="round"/></svg>'
    +'</div></div>';
}
'''
    content = content.replace(anchor2, nav_html_func + anchor2)
    report(True, "createNavMarkerHTML", "- נוסף (ללא סיבוב עצמי - המפה מסתובבת במקום)")

old3 = '''function updateTrackingMarkerFixed(){
  const el=document.getElementById('trackingMarkerFixed');
  if(!el||!currentUser)return;
  el.innerHTML=createMarkerHTML({...currentUser});
  const topPx=window.innerHeight*TRACK_PAD_TOP_FRAC+(window.innerHeight-window.innerHeight*TRACK_PAD_TOP_FRAC)/2;
  el.style.top=topPx+'px';
}'''
new3 = '''function updateTrackingMarkerFixed(){
  const el=document.getElementById('trackingMarkerFixed');
  if(!el||!currentUser)return;
  el.innerHTML=navModeActive?createNavMarkerHTML():createMarkerHTML({...currentUser});
  const topPx=window.innerHeight*TRACK_PAD_TOP_FRAC+(window.innerHeight-window.innerHeight*TRACK_PAD_TOP_FRAC)/2;
  el.style.top=topPx+'px';
}'''
if content.count(old3) == 0:
    report(False, "עדכון updateTrackingMarkerFixed", "- לא נמצא עוגן מדויק")
elif content.count(old3) > 1:
    report(False, "עדכון updateTrackingMarkerFixed", f"- {content.count(old3)} מופעים")
else:
    content = content.replace(old3, new3)
    report(True, "עדכון updateTrackingMarkerFixed", "- בוחר בין מארקר רגיל למשולש ניווט")

old4 = '''    lastSpeed=speed||0;
    // החלקת קואורדינטות (ממוצע נע) לתצוגה חלקה - לא משפיע על מה שנשמר ב-Firestore/היסטוריה
    if(smoothLat===null){smoothLat=lat;smoothLng=lng;}
    else{
      smoothLat+=0.35*(lat-smoothLat);
      smoothLng+=0.35*(lng-smoothLng);
    }
    // עדכון חזותי מיידי בכל קריאת GPS - למעקב חלק ורציף בלי קפיצות
    if(currentUser&&!trackingMode)updateMarker(myUID,{...currentUser,lat:smoothLat,lng:smoothLng});
    if(trackingMode)map.easeTo({center:[smoothLng,smoothLat],duration:400,padding:{top:window.innerHeight*TRACK_PAD_TOP_FRAC,bottom:0,left:0,right:0}});'''
new4 = '''    lastSpeed=speed||0;
    // החלקת קואורדינטות (ממוצע נע) לתצוגה חלקה - לא משפיע על מה שנשמר ב-Firestore/היסטוריה
    if(smoothLat===null){smoothLat=lat;smoothLng=lng;}
    else{
      smoothLat+=0.35*(lat-smoothLat);
      smoothLng+=0.35*(lng-smoothLng);
    }
    // עדכון חזותי מיידי בכל קריאת GPS - למעקב חלק ורציף בלי קפיצות
    if(currentUser&&!trackingMode)updateMarker(myUID,{...currentUser,lat:smoothLat,lng:smoothLng});
    if(trackingMode){
      navModeActive=compassMode&&lastSpeed>=NAV_SPEED_MS;
      map.easeTo({center:[smoothLng,smoothLat],duration:400,padding:{top:window.innerHeight*TRACK_PAD_TOP_FRAC,bottom:0,left:0,right:0},pitch:navModeActive?map.getMaxPitch():0});
      updateTrackingMarkerFixed();
    }'''
if content.count(old4) == 0:
    report(False, "עדכון watchPosition", "- לא נמצא עוגן מדויק")
elif content.count(old4) > 1:
    report(False, "עדכון watchPosition", f"- {content.count(old4)} מופעים")
else:
    content = content.replace(old4, new4)
    report(True, "עדכון watchPosition", "- דורש מעקב+מצפן+מהירות יחד, מעדכן pitch")

old5 = '''function toggleTracking(){
  trackingMode=!trackingMode;'''
new5 = '''function toggleTracking(){
  trackingMode=!trackingMode;
  navModeActive=false;'''
if content.count(old5) == 0:
    report(False, "איפוס navModeActive ב-toggleTracking", "- לא נמצא עוגן")
elif content.count(old5) > 1:
    report(False, "איפוס navModeActive ב-toggleTracking", f"- {content.count(old5)} מופעים")
else:
    content = content.replace(old5, new5)
    report(True, "איפוס navModeActive ב-toggleTracking", "- נוסף")

old6 = '''    map.easeTo({padding:{top:0,bottom:0,left:0,right:0},duration:300});
    if(fixedEl)fixedEl.style.display='none';
    if(currentUser&&smoothLat&&smoothLng)updateMarker(myUID,{...currentUser,lat:smoothLat,lng:smoothLng});'''
new6 = '''    map.easeTo({padding:{top:0,bottom:0,left:0,right:0},pitch:0,duration:300});
    if(fixedEl)fixedEl.style.display='none';
    if(currentUser&&smoothLat&&smoothLng)updateMarker(myUID,{...currentUser,lat:smoothLat,lng:smoothLng});'''
if content.count(old6) == 0:
    report(False, "איפוס pitch בכיבוי מעקב", "- לא נמצא עוגן")
elif content.count(old6) > 1:
    report(False, "איפוס pitch בכיבוי מעקב", f"- {content.count(old6)} מופעים")
else:
    content = content.replace(old6, new6)
    report(True, "איפוס pitch בכיבוי מעקב", "- נוסף")

old7 = '''function toggleCompass(){
  compassMode=!compassMode;'''
new7 = '''function toggleCompass(){
  compassMode=!compassMode;
  if(!compassMode){
    navModeActive=false;
    if(trackingMode)map.easeTo({pitch:0,duration:300});
  }'''
if content.count(old7) == 0:
    report(False, "איפוס navModeActive ב-toggleCompass", "- לא נמצא עוגן")
elif content.count(old7) > 1:
    report(False, "איפוס navModeActive ב-toggleCompass", f"- {content.count(old7)} מופעים")
else:
    content = content.replace(old7, new7)
    report(True, "איפוס navModeActive ב-toggleCompass", "- נוסף (כשמכבים מצפן תוך כדי מעקב)")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

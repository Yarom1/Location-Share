import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def report(ok, label, extra=""):
    print(("✅ " if ok else "❌ ")+label+" "+extra)

old1 = '''function shareLocation(){
  if(!lastLat||!lastLng){showToast('אין מיקום זמין','error');return;}
  const url='https://www.google.com/maps?q='+lastLat+','+lastLng;
  if(navigator.share){
    navigator.share({title:'המיקום שלי',url:url}).catch(()=>{});
  }else{
    const el=document.createElement('textarea');
    el.value=url;document.body.appendChild(el);el.select();
    document.execCommand('copy');document.body.removeChild(el);
    showToast('קישור הועתק ✓','success');
  }
}
window.shareLocation=shareLocation;'''

new1 = '''function getFreshPosition(){
  return new Promise((resolve,reject)=>{
    if(!navigator.geolocation){reject(new Error('no geolocation'));return;}
    navigator.geolocation.getCurrentPosition(
      pos=>resolve(pos.coords),
      err=>reject(err),
      {enableHighAccuracy:true,timeout:10000,maximumAge:0}
    );
  });
}

async function shareLocation(){
  showToast('מאתר מיקום מדויק...','');
  let lat,lng;
  try{
    const coords=await getFreshPosition();
    lat=coords.latitude;lng=coords.longitude;
  }catch(e){
    if(!lastLat||!lastLng){showToast('אין מיקום זמין','error');return;}
    lat=lastLat;lng=lastLng;
  }
  const url='https://www.google.com/maps?q='+lat+','+lng;
  if(window.AndroidBridge&&AndroidBridge.shareText){
    AndroidBridge.shareText(url);
  }else if(navigator.share){
    navigator.share({title:'המיקום שלי',url:url}).catch(()=>{});
  }else{
    const el=document.createElement('textarea');
    el.value=url;document.body.appendChild(el);el.select();
    document.execCommand('copy');document.body.removeChild(el);
    showToast('קישור הועתק ✓','success');
  }
}

async function copyCoordinates(){
  showToast('מאתר מיקום מדויק...','');
  let lat,lng;
  try{
    const coords=await getFreshPosition();
    lat=coords.latitude;lng=coords.longitude;
  }catch(e){
    if(!lastLat||!lastLng){showToast('אין מיקום זמין','error');return;}
    lat=lastLat;lng=lastLng;
  }
  const text=lat.toFixed(6)+','+lng.toFixed(6);
  const done=()=>showToast('נ.צ. הועתק: '+text,'success');
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(done).catch(()=>{
      const el=document.createElement('textarea');
      el.value=text;document.body.appendChild(el);el.select();
      document.execCommand('copy');document.body.removeChild(el);
      done();
    });
  }else{
    const el=document.createElement('textarea');
    el.value=text;document.body.appendChild(el);el.select();
    document.execCommand('copy');document.body.removeChild(el);
    done();
  }
}
window.shareLocation=shareLocation;
window.copyCoordinates=copyCoordinates;'''

count1 = content.count(old1)
if count1 == 0:
    report(False, "shareLocation + copyCoordinates", "- לא נמצא עוגן מדויק")
elif count1 > 1:
    report(False, "shareLocation + copyCoordinates", f"- {count1} מופעים")
else:
    shutil.copy(path, path + ".bak")
    content = content.replace(old1, new1)
    report(True, "shareLocation + copyCoordinates", "- מיקום טרי ומדויק + שיתוף נייטיבי + פונקציית העתקה")

anchor2 = '''<div onclick="shareLocation()" id="fullscreenBtn" style="width:50px;height:50px;border-radius:50%;background:rgba(13,17,23,0.8);border:1px solid rgba(255,255,255,0.2);display:flex;align-items:center;justify-content:center;box-shadow:0 3px 10px rgba(0,0,0,.5);cursor:pointer;touch-action:manipulation"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg></div>'''

new_btn = '''
      <div onclick="copyCoordinates()" id="copyCoordsBtn" style="width:50px;height:50px;border-radius:50%;background:rgba(13,17,23,0.8);border:1px solid rgba(255,255,255,0.2);display:flex;align-items:center;justify-content:center;box-shadow:0 3px 10px rgba(0,0,0,.5);cursor:pointer;touch-action:manipulation"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></div>'''

count2 = content.count(anchor2)
if count2 == 0:
    report(False, "כפתור העתק נ.צ.", "- לא נמצא עוגן מדויק")
elif count2 > 1:
    report(False, "כפתור העתק נ.צ.", f"- {count2} מופעים")
else:
    content = content.replace(anchor2, anchor2 + new_btn)
    report(True, "כפתור העתק נ.צ.", "- נוסף לסרגל הכלים")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

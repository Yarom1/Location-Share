import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "function startCenterPinRefine(lat,lng){\n  map.flyTo({center:[lng,lat],zoom:17,pitch:0,bearing:0,padding:{top:0,bottom:0,left:0,right:0}});"

new = '''function startCenterPinRefine(lat,lng){
  map.flyTo({center:[lng,lat],zoom:17,pitch:0,bearing:0,padding:{top:0,bottom:0,left:0,right:0}});
  map.once('moveend',()=>{
    const c=map.getCenter();
    const dLat=(lat-c.lat).toFixed(6);
    const dLng=(lng-c.lng).toFixed(6);
    showToast('יעד:'+lat.toFixed(6)+','+lng.toFixed(6)+' | קיבל:'+c.lat.toFixed(6)+','+c.lng.toFixed(6)+' | Δ:'+dLat+','+dLng+' | zoom:'+map.getZoom().toFixed(2)+' pitch:'+map.getPitch().toFixed(2)+' bearing:'+map.getBearing().toFixed(2),'error');
  });'''

count = content.count(old)
if count == 0:
    print("❌ לא נמצא עוגן מדויק")
elif count > 1:
    print(f"⚠️ {count} מופעים")
else:
    shutil.copy(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.replace(old, new))
    print("✅ טוסט דיבאג נוסף")

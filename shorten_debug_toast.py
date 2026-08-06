import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "showToast('יעד:'+lat.toFixed(6)+','+lng.toFixed(6)+' | קיבל:'+c.lat.toFixed(6)+','+c.lng.toFixed(6)+' | Δ:'+dLat+','+dLng+' | zoom:'+map.getZoom().toFixed(2)+' pitch:'+map.getPitch().toFixed(2)+' bearing:'+map.getBearing().toFixed(2),'error');"

new = "showToast('Δlat:'+dLat+' Δlng:'+dLng+' z:'+map.getZoom().toFixed(1)+' p:'+map.getPitch().toFixed(1)+' b:'+map.getBearing().toFixed(1),'error');"

count = content.count(old)
if count == 0:
    print("❌ לא נמצא עוגן מדויק")
elif count > 1:
    print(f"⚠️ {count} מופעים")
else:
    shutil.copy(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.replace(old, new))
    print("✅ טוסט מקוצר")

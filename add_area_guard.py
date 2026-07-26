import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

anchor = "const cached=await poiCacheGetByType(type);"
idx = content.find(anchor)
if idx == -1:
    print("❌ לא נמצא עוגן")
else:
    guard_code = '''const MAX_POI_SPAN_DEG=0.5;
  if((north-south)>MAX_POI_SPAN_DEG||(east-west)>MAX_POI_SPAN_DEG){
    const cachedNear=await poiCacheGetByType(type);
    const inViewNear=cachedNear.filter(p=>p.lat>=south&&p.lat<=north&&p.lon>=west&&p.lon<=east);
    inViewNear.forEach(p=>renderPoiMarker(type,p));
    if(inViewNear.length===0){
      showToast('התקרב יותר במפה כדי לטעון שכבה זו 🔍','error');
      document.getElementById('poi'+type.charAt(0).toUpperCase()+type.slice(1)).checked=false;
    }
    return;
  }
  '''
    new_content = content[:idx] + guard_code + content[idx:]
    shutil.copy(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✅ נוספה הגנת גודל-שטח לפני שאילתת Overpass")

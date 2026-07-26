path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

guard_block = '''  const MAX_POI_SPAN_DEG=0.5;
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

count = content.count(guard_block)
print(f"נמצאו {count} עותקים של בלוק ההגנה")

if count <= 1:
    print("אין כפילות לתקן")
else:
    combined = guard_block * count
    if combined not in content:
        print("❌ העותקים לא רצופים בדיוק כמו שציפיתי - נדרשת בדיקה ידנית")
    else:
        new_content = content.replace(combined, guard_block)
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"✅ צומצם מ-{count} עותקים לעותק בודד אחד")

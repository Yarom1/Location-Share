import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def report(ok, label, extra=""):
    print(("✅ " if ok else "❌ ")+label+" "+extra)

anchor1 = "// הוסר מכוון: visibilitychange כבר לא מסמן לא-מחובר, כי מעקב ברקע אמור להמשיך לשתף מיקום"
if "smoothLat=null;smoothLng=null" in content and "visibilitychange" in content and "'visible'" in content:
    report(False, "listener איפוס החלקה", "- כבר קיים, מדלג")
elif content.count(anchor1) != 1:
    report(False, "listener איפוס החלקה", f"- עוגן נמצא {content.count(anchor1)} פעמים")
else:
    reset_listener = '''document.addEventListener('visibilitychange',()=>{
  if(document.visibilityState==='visible'){
    smoothLat=null;smoothLng=null;
  }
});
'''
    content = content.replace(anchor1, reset_listener + anchor1)
    report(True, "listener איפוס החלקה", "- נוסף")

old2 = '''    if(smoothLat===null){smoothLat=lat;smoothLng=lng;}
    else{
      smoothLat+=0.35*(lat-smoothLat);
      smoothLng+=0.35*(lng-smoothLng);
    }'''
new2 = '''    if(smoothLat===null||Math.abs(lat-smoothLat)+Math.abs(lng-smoothLng)>0.05){
      smoothLat=lat;smoothLng=lng;
    }else{
      smoothLat+=0.35*(lat-smoothLat);
      smoothLng+=0.35*(lng-smoothLng);
    }'''
if content.count(old2) == 0:
    report(False, "רשת ביטחון מרחק", "- לא נמצא עוגן מדויק")
elif content.count(old2) > 1:
    report(False, "רשת ביטחון מרחק", f"- {content.count(old2)} מופעים")
else:
    content = content.replace(old2, new2)
    report(True, "רשת ביטחון מרחק", "- נוספה")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

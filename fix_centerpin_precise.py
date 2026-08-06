import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def report(ok, label, extra=""):
    print(("✅ " if ok else "❌ ")+label+" "+extra)

anchor1 = "function startCenterPinRefine(lat,lng){"
if "function positionCenterPinFixed" in content:
    report(False, "positionCenterPinFixed", "- כבר קיים, מדלג")
elif content.count(anchor1) != 1:
    report(False, "positionCenterPinFixed", f"- עוגן נמצא {content.count(anchor1)} פעמים")
else:
    new_func = '''function positionCenterPinFixed(){
  const el=document.getElementById('centerPinFixed');
  if(!el)return;
  const rect=map.getContainer().getBoundingClientRect();
  el.style.left=(rect.left+rect.width/2)+'px';
  el.style.top=(rect.top+rect.height/2)+'px';
}
'''
    content = content.replace(anchor1, new_func + anchor1)
    report(True, "positionCenterPinFixed", "- נוספה")

old2 = '''  document.getElementById('centerPinFixed').style.display='block';
  centerPinActive=true;'''
new2 = '''  document.getElementById('centerPinFixed').style.display='block';
  positionCenterPinFixed();
  centerPinActive=true;'''
if content.count(old2) == 0:
    report(False, "קריאה ב-startCenterPinRefine", "- לא נמצא עוגן מדויק")
elif content.count(old2) > 1:
    report(False, "קריאה ב-startCenterPinRefine", f"- {content.count(old2)} מופעים")
else:
    content = content.replace(old2, new2)
    report(True, "קריאה ב-startCenterPinRefine", "- נוספה")

old3 = '''function onCenterPinMove(){
  if(!centerPinActive)return;
  const c=map.getCenter();'''
new3 = '''function onCenterPinMove(){
  if(!centerPinActive)return;
  positionCenterPinFixed();
  const c=map.getCenter();'''
if content.count(old3) == 0:
    report(False, "קריאה ב-onCenterPinMove", "- לא נמצא עוגן מדויק")
elif content.count(old3) > 1:
    report(False, "קריאה ב-onCenterPinMove", f"- {content.count(old3)} מופעים")
else:
    content = content.replace(old3, new3)
    report(True, "קריאה ב-onCenterPinMove", "- נוספה")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

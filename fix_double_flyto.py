import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '''function goToSearchResult(lat,lng,name){
  map.flyTo({center:[lng,lat],zoom:16});
  closeModal('searchModal');
  document.getElementById('searchInput').value='';
  document.getElementById('searchResults').innerHTML='';

  if(searchThenPinMode){
    searchThenPinMode=false;
    startCenterPinRefine(lat,lng);
    return;
  }
'''

new = '''function goToSearchResult(lat,lng,name){
  closeModal('searchModal');
  document.getElementById('searchInput').value='';
  document.getElementById('searchResults').innerHTML='';

  if(searchThenPinMode){
    searchThenPinMode=false;
    startCenterPinRefine(lat,lng);
    return;
  }

  map.flyTo({center:[lng,lat],zoom:16});
'''

count = content.count(old)
if count == 0:
    print("❌ לא נמצא עוגן מדויק")
elif count > 1:
    print(f"⚠️ {count} מופעים")
else:
    shutil.copy(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.replace(old, new))
    print("✅ הוסרה כפילות ה-flyTo")

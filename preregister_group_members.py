import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "snap.forEach(d=>{allUsersData[d.id]=d.data();currentIds.add(d.id);});"
new = "snap.forEach(d=>{allUsersData[d.id]=d.data();currentIds.add(d.id);if(d.id!==myUID&&window.AndroidBridge&&AndroidBridge.registerDmPeer){try{AndroidBridge.registerDmPeer(d.id);}catch(e){}}});"

count = content.count(old)
if count == 0:
    print("❌ לא נמצא עוגן מדויק")
elif count > 1:
    print(f"⚠️ {count} מופעים")
else:
    shutil.copy(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.replace(old, new))
    print("✅ כל חברי הקבוצה נרשמים אוטומטית כ-DM peers ברגע שרואים אותם ברשימה")

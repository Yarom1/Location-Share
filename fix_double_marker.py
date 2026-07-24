import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = "if(currentUser)updateMarker(myUID,{...currentUser,lat,lng});\n};\n\nnavigator.geolocation.watchPosition"
new = "if(currentUser&&!trackingMode)updateMarker(myUID,{...currentUser,lat,lng});\n};\n\nnavigator.geolocation.watchPosition"

count = content.count(old)
if count == 0:
    print("❌ לא נמצא מופע מדויק - בדוק ידנית")
elif count > 1:
    print(f"⚠️ נמצאו {count} מופעים (צריך בדיוק 1) - לא בוצע שינוי")
else:
    shutil.copy(path, path + ".bak")
    new_content = content.replace(old, new)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✅ תוקן: onBackgroundLocation עכשיו בודק trackingMode לפני updateMarker")

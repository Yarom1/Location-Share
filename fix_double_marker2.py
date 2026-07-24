import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old_call = "if(currentUser)updateMarker(myUID,{...currentUser,lat,lng});"
new_call = "if(currentUser&&!trackingMode)updateMarker(myUID,{...currentUser,lat,lng});"

count = content.count(old_call)
if count == 0:
    print("❌ לא נמצא אפילו העוגן הקצר - בדוק ידנית (אולי הרווחים בין הפרמטרים שונים)")
elif count > 1:
    print(f"⚠️ נמצאו {count} מופעים של העוגן הקצר - לא בוצע שינוי, צריך לצמצם")
else:
    shutil.copy(path, path + ".bak")
    new_content = content.replace(old_call, new_call)
    with open(path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("✅ תוקן: onBackgroundLocation עכשיו בודק trackingMode לפני updateMarker")

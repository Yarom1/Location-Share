import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def report(ok, label, extra=""):
    print(("✅ " if ok else "❌ ")+label+" "+extra)

old1 = "if(el)el.textContent='📍 '+addPointCoords.lat.toFixed(6)+', '+addPointCoords.lng.toFixed(6)+' — הזז את המפה לדיוק';"
new1 = "if(el)el.textContent='📍 \\u202A'+addPointCoords.lat.toFixed(6)+', '+addPointCoords.lng.toFixed(6)+'\\u202C — הזז את המפה לדיוק';"
if content.count(old1) == 0:
    report(False, "פאנל דיוק נקודה", "- לא נמצא עוגן מדויק")
elif content.count(old1) > 1:
    report(False, "פאנל דיוק נקודה", f"- {content.count(old1)} מופעים")
else:
    shutil.copy(path, path + ".bak")
    content = content.replace(old1, new1)
    report(True, "פאנל דיוק נקודה", "- מספרים נעולים ב-LTR")

old2 = "const text=lat.toFixed(6)+','+lng.toFixed(6);\n  const done=()=>showToast('נ.צ. הועתק: '+text,'success');"
new2 = "const text=lat.toFixed(6)+','+lng.toFixed(6);\n  const done=()=>showToast('נ.צ. הועתק: \\u202A'+text+'\\u202C','success');"
count2 = content.count(old2)
if count2 == 0:
    report(False, "טוסט העתקת מיקום עצמי", "- לא נמצא עוגן מדויק")
elif count2 > 1:
    report(False, "טוסט העתקת מיקום עצמי", f"- {count2} מופעים")
else:
    content = content.replace(old2, new2)
    report(True, "טוסט העתקת מיקום עצמי", "- מספרים נעולים ב-LTR")

old3 = "const text=u.lat.toFixed(6)+','+u.lng.toFixed(6);\n  const done=()=>showToast('נ.צ. הועתק: '+text,'success');"
new3 = "const text=u.lat.toFixed(6)+','+u.lng.toFixed(6);\n  const done=()=>showToast('נ.צ. הועתק: \\u202A'+text+'\\u202C','success');"
count3 = content.count(old3)
if count3 == 0:
    report(False, "טוסט העתקת נ.צ. חבר קבוצה", "- לא נמצא עוגן מדויק")
elif count3 > 1:
    report(False, "טוסט העתקת נ.צ. חבר קבוצה", f"- {count3} מופעים")
else:
    content = content.replace(old3, new3)
    report(True, "טוסט העתקת נ.צ. חבר קבוצה", "- מספרים נעולים ב-LTR")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

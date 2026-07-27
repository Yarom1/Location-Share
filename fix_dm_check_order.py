import shutil

path = "app/src/main/java/com/locationshare/LocationService.kt"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = '''                val groupId = prefs.getString("active_group_id", null)
                if (groupId.isNullOrEmpty()) return@Thread
                val idToken = getFreshIdToken() ?: return@Thread
                checkForNewDmMessages(uid, idToken, prefs)
'''
new = '''                val dmToken = getFreshIdToken()
                if (dmToken != null) checkForNewDmMessages(uid, dmToken, prefs)

                val groupId = prefs.getString("active_group_id", null)
                if (groupId.isNullOrEmpty()) return@Thread
                val idToken = getFreshIdToken() ?: return@Thread
'''

count = content.count(old)
if count == 0:
    print("❌ לא נמצא עוגן מדויק - בדוק ידנית")
elif count > 1:
    print(f"⚠️ {count} מופעים")
else:
    shutil.copy(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.replace(old, new))
    print("✅ תוקן: בדיקת DM עכשיו רצה גם בלי קבוצה פעילה, לפני ה-return@Thread")

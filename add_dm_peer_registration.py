import shutil

def report(ok, label, extra=""):
    print(("✅ " if ok else "❌ ")+label+" "+extra)

kpath = "app/src/main/java/com/locationshare/MainActivity.kt"
with open(kpath, "r", encoding="utf-8") as f:
    kc = f.read()

if "fun registerDmPeer(" in kc:
    report(False, "Kotlin registerDmPeer", "- כבר קיים, מדלג")
else:
    anchor = "fun reportJsAlive"
    idx_report = kc.find(anchor)
    if idx_report == -1:
        report(False, "Kotlin registerDmPeer", "- לא נמצא עוגן")
    else:
        idx_jsiface = kc.rfind("@JavascriptInterface", 0, idx_report)
        if idx_jsiface == -1:
            report(False, "Kotlin registerDmPeer", "- לא נמצא @JavascriptInterface")
        else:
            line_start = kc.rfind("\n", 0, idx_jsiface) + 1
            indent = kc[line_start:idx_jsiface]
            new_func = (
                f"{indent}@JavascriptInterface\n"
                f"{indent}fun registerDmPeer(uid: String) {{\n"
                f"{indent}    try {{\n"
                f"{indent}        val prefs = getSharedPreferences(\"location_share_prefs\", MODE_PRIVATE)\n"
                f"{indent}        val current = prefs.getStringSet(\"dm_peer_uids\", emptySet()) ?: emptySet()\n"
                f"{indent}        if (!current.contains(uid)) {{\n"
                f"{indent}            val updated = HashSet(current)\n"
                f"{indent}            updated.add(uid)\n"
                f"{indent}            prefs.edit().putStringSet(\"dm_peer_uids\", updated).apply()\n"
                f"{indent}        }}\n"
                f"{indent}    }} catch (e: Exception) {{ e.printStackTrace() }}\n"
                f"{indent}}}\n\n"
            )
            shutil.copy(kpath, kpath + ".bak")
            new_kc = kc[:line_start] + new_func + kc[line_start:]
            with open(kpath, "w", encoding="utf-8") as f:
                f.write(new_kc)
            report(True, "Kotlin registerDmPeer", "- נוסף")

jpath = "web/index.html"
with open(jpath, "r", encoding="utf-8") as f:
    jc = f.read()

old_js = '''function openDM(uid,name,avatar){
  activeDMUser={uid,name,avatar};
  document.getElementById('tabDM').textContent=`💌 ${name}`;
  openPanel('chat');switchChatTab('dm');
  if(currentUserPopup){currentUserPopup.remove();currentUserPopup=null;}
}'''
new_js = '''function openDM(uid,name,avatar){
  activeDMUser={uid,name,avatar};
  document.getElementById('tabDM').textContent=`💌 ${name}`;
  openPanel('chat');switchChatTab('dm');
  if(currentUserPopup){currentUserPopup.remove();currentUserPopup=null;}
  if(window.AndroidBridge&&AndroidBridge.registerDmPeer){
    try{AndroidBridge.registerDmPeer(uid);}catch(e){}
  }
}'''
count_js = jc.count(old_js)
if "AndroidBridge.registerDmPeer(uid)" in jc:
    report(False, "JS openDM עדכון", "- כבר קיים, מדלג")
elif count_js == 0:
    report(False, "JS openDM עדכון", "- לא נמצא עוגן מדויק")
elif count_js > 1:
    report(False, "JS openDM עדכון", f"- {count_js} מופעים")
else:
    shutil.copy(jpath, jpath + ".bak2")
    jc = jc.replace(old_js, new_js)
    with open(jpath, "w", encoding="utf-8") as f:
        f.write(jc)
    report(True, "JS openDM עדכון", "- נוסף")

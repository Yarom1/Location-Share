import shutil

def report(ok, label, extra=""):
    mark = "✅" if ok else "❌"
    print(f"{mark} {label} {extra}")

kpath = "app/src/main/java/com/locationshare/MainActivity.kt"
with open(kpath, "r", encoding="utf-8") as f:
    kc = f.read()

if "fun shutdownApp(" in kc:
    report(False, "Kotlin", "- shutdownApp כבר קיים (לא בוצע שינוי כפול)")
else:
    anchor = "fun reportJsAlive"
    idx_report = kc.find(anchor)
    if idx_report == -1:
        report(False, "Kotlin", "- לא נמצא עוגן 'fun reportJsAlive'")
    else:
        idx_jsiface = kc.rfind("@JavascriptInterface", 0, idx_report)
        if idx_jsiface == -1:
            report(False, "Kotlin", "- לא נמצא @JavascriptInterface לפני reportJsAlive")
        else:
            line_start = kc.rfind("\n", 0, idx_jsiface) + 1
            indent = kc[line_start:idx_jsiface]

            new_func = (
                f"{indent}@JavascriptInterface\n"
                f"{indent}fun shutdownApp() {{\n"
                f"{indent}    runOnUiThread {{\n"
                f"{indent}        try {{\n"
                f"{indent}            stopService(Intent(this@MainActivity, LocationService::class.java))\n"
                f"{indent}        }} catch (e: Exception) {{ e.printStackTrace() }}\n"
                f"{indent}        try {{\n"
                f"{indent}            val prefs = getSharedPreferences(\"location_share_prefs\", MODE_PRIVATE)\n"
                f"{indent}            prefs.edit().clear().apply()\n"
                f"{indent}        }} catch (e: Exception) {{ e.printStackTrace() }}\n"
                f"{indent}        finishAffinity()\n"
                f"{indent}        android.os.Process.killProcess(android.os.Process.myPid())\n"
                f"{indent}    }}\n"
                f"{indent}}}\n\n"
            )

            shutil.copy(kpath, kpath + ".bak")
            new_kc = kc[:line_start] + new_func + kc[line_start:]
            with open(kpath, "w", encoding="utf-8") as f:
                f.write(new_kc)
            report(True, "Kotlin", "- shutdownApp נוסף לפני reportJsAlive")

jpath = "web/index.html"
with open(jpath, "r", encoding="utf-8") as f:
    jc = f.read()

if "function shutdownApp(" in jc:
    report(False, "JS function", "- כבר קיים (לא בוצע שינוי כפול)")
else:
    anchor = "function updateMyUI(){"
    idx_anchor = jc.find(anchor)
    if idx_anchor == -1:
        report(False, "JS function", "- לא נמצא עוגן 'function updateMyUI(){'")
    else:
        line_start = jc.rfind("\n", 0, idx_anchor) + 1
        indent = jc[line_start:idx_anchor]

        new_func = (
            f"{indent}function shutdownApp(){{\n"
            f"{indent}if(!confirm('לסגור את האפליקציה ולעצור שיתוף מיקום ברקע?'))return;\n"
            f"{indent}try{{\n"
            f"{indent}setDoc(doc(db,'users',myUID),{{online:false,lastSeen:serverTimestamp()}},{{merge:true}});\n"
            f"{indent}if(activeGroupId)setDoc(gDoc('locations',myUID),{{online:false,lastSeen:serverTimestamp()}},{{merge:true}});\n"
            f"{indent}}}catch(e){{}}\n"
            f"{indent}if(window.AndroidBridge&&AndroidBridge.shutdownApp){{\n"
            f"{indent}AndroidBridge.shutdownApp();\n"
            f"{indent}}}\n"
            f"{indent}}}\n"
            f"{indent}window.shutdownApp=shutdownApp;\n\n"
        )

        shutil.copy(jpath, jpath + ".bak")
        new_jc = jc[:line_start] + new_func + jc[line_start:]
        with open(jpath, "w", encoding="utf-8") as f:
            f.write(new_jc)
        report(True, "JS function", "- shutdownApp נוסף לפני updateMyUI")

with open(jpath, "r", encoding="utf-8") as f:
    jc = f.read()

if 'onclick="shutdownApp()"' in jc:
    report(False, "HTML button", "- כבר קיים (לא בוצע שינוי כפול)")
else:
    version_anchor = '<div style="font-size:10px;color:var(--text2);text-align:center;margin-top:6px">Location Share v1.0</div>'
    idx_version = jc.find(version_anchor)
    if idx_version == -1:
        report(False, "HTML button", "- לא נמצא עוגן שורת הגרסה")
    else:
        button_html = (
            '<button onclick="shutdownApp()" style="background:var(--surface2);'
            'color:#ff453a;border:1px solid #ff453a55;border-radius:8px;padding:8px 14px;'
            'font-size:12px;font-weight:600;cursor:pointer;font-family:inherit;width:100%;'
            'display:flex;align-items:center;justify-content:flex-start;gap:10px;margin-top:4px">'
            '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M18.36 6.64a9 9 0 1 1-12.73 0"/><line x1="12" y1="2" x2="12" y2="12"/></svg>'
            'כיבוי אפליקציה</button>'
        )
        shutil.copy(jpath, jpath + ".bak2")
        new_jc = jc[:idx_version] + button_html + jc[idx_version:]
        with open(jpath, "w", encoding="utf-8") as f:
            f.write(new_jc)
        report(True, "HTML button", "- כפתור 'כיבוי אפליקציה' נוסף לפני שורת הגרסה")

print("\nגיבויים: .bak / .bak2 באותה תיקייה")

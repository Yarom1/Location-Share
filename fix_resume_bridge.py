import shutil

def report(ok, label, extra=""):
    print(("✅ " if ok else "❌ ")+label+" "+extra)

jpath = "web/index.html"
with open(jpath, "r", encoding="utf-8") as f:
    jc = f.read()

if "function resetLocationSmoothing" in jc:
    report(False, "JS resetLocationSmoothing", "- כבר קיים, מדלג")
else:
    anchor = "document.addEventListener('visibilitychange',()=>{"
    if jc.count(anchor) != 1:
        report(False, "JS resetLocationSmoothing", f"- עוגן נמצא {jc.count(anchor)} פעמים")
    else:
        func = '''function resetLocationSmoothing(){
  smoothLat=null;smoothLng=null;
}
window.resetLocationSmoothing=resetLocationSmoothing;
'''
        jc = jc.replace(anchor, func + anchor)
        shutil.copy(jpath, jpath + ".bak")
        with open(jpath, "w", encoding="utf-8") as f:
            f.write(jc)
        report(True, "JS resetLocationSmoothing", "- נוסף וחשוף ל-window")

kpath = "app/src/main/java/com/locationshare/MainActivity.kt"
with open(kpath, "r", encoding="utf-8") as f:
    kc = f.read()

old_k = '''        super.onResume()
        webView.onResume()'''
new_k = '''        super.onResume()
        webView.onResume()
        webView.evaluateJavascript("if(window.resetLocationSmoothing)window.resetLocationSmoothing();", null)'''

if "resetLocationSmoothing" in kc:
    report(False, "Kotlin קריאה מ-onResume", "- כבר קיים, מדלג")
elif kc.count(old_k) != 1:
    report(False, "Kotlin קריאה מ-onResume", f"- עוגן נמצא {kc.count(old_k)} פעמים")
else:
    shutil.copy(kpath, kpath + ".bak")
    kc = kc.replace(old_k, new_k)
    with open(kpath, "w", encoding="utf-8") as f:
        f.write(kc)
    report(True, "Kotlin קריאה מ-onResume", "- נוסף")

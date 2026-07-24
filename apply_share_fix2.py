import shutil

def report(ok, label, extra=""):
    mark = "✅" if ok else "❌"
    print(f"{mark} {label} {extra}")

# ===== 1. Kotlin: הוספת shareText לגשר =====
kpath = "app/src/main/java/com/locationshare/MainActivity.kt"
with open(kpath, "r", encoding="utf-8") as f:
    kc = f.read()

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
            f"{indent}fun shareText(text: String) {{\n"
            f"{indent}    runOnUiThread {{\n"
            f"{indent}        val sendIntent = Intent(Intent.ACTION_SEND).apply {{\n"
            f"{indent}            type = \"text/plain\"\n"
            f"{indent}            putExtra(Intent.EXTRA_TEXT, text)\n"
            f"{indent}        }}\n"
            f"{indent}        val chooser = Intent.createChooser(sendIntent, null).apply {{\n"
            f"{indent}            flags = Intent.FLAG_ACTIVITY_NEW_TASK\n"
            f"{indent}        }}\n"
            f"{indent}        startActivity(chooser)\n"
            f"{indent}    }}\n"
            f"{indent}}}\n\n"
        )

        if "fun shareText(" in kc:
            report(False, "Kotlin", "- shareText כבר קיים בקובץ (לא בוצע שינוי כפול)")
        else:
            shutil.copy(kpath, kpath + ".bak")
            new_kc = kc[:line_start] + new_func + kc[line_start:]
            with open(kpath, "w", encoding="utf-8") as f:
                f.write(new_kc)
            report(True, "Kotlin", "- shareText נוסף לפני reportJsAlive")

# ===== 2. JS: עדכון shareGroupInvite =====
jpath = "web/index.html"
with open(jpath, "r", encoding="utf-8") as f:
    jc = f.read()

start_anchor = "function shareGroupInvite(name,code){"
end_anchor = "window.shareGroupInvite=shareGroupInvite;"

idx_start = jc.find(start_anchor)
idx_end = jc.find(end_anchor)

if idx_start == -1 or idx_end == -1 or idx_end < idx_start:
    report(False, "JS", "- לא נמצאו עוגני התחלה/סוף כמצופה")
else:
    inner_check = "if(navigator.share){"
    idx_if = jc.find(inner_check, idx_start, idx_end)
    if idx_if == -1:
        report(False, "JS", "- לא נמצא 'if(navigator.share){' בתוך הפונקציה")
    elif "AndroidBridge.shareText" in jc[idx_start:idx_end]:
        report(False, "JS", "- השינוי כבר קיים (לא בוצע שינוי כפול)")
    else:
        line_start = jc.rfind("\n", 0, idx_if) + 1
        indent = jc[line_start:idx_if]

        insertion = (
            f"if(window.AndroidBridge&&AndroidBridge.shareText){{\n"
            f"{indent}AndroidBridge.shareText(code);\n"
            f"{indent}}}else "
        )

        shutil.copy(jpath, jpath + ".bak")
        new_jc = jc[:idx_if] + insertion + jc[idx_if:]
        with open(jpath, "w", encoding="utf-8") as f:
            f.write(new_jc)
        report(True, "JS", "- shareGroupInvite עודכן לנסות AndroidBridge.shareText קודם")

print("\nגיבויים נוצרו: .bak באותה תיקייה (אם בוצע שינוי בפועל)")

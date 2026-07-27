import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def report(ok, label, extra=""):
    print(("✅ " if ok else "❌ ")+label+" "+extra)

old1 = '<div style="font-size:10px;color:var(--text2);text-align:center;margin-top:6px">Location Share v1.0</div>'
if "copyrightYear" in content:
    report(False, "שורת קופירייט", "- כבר קיימת, מדלג")
elif content.count(old1) != 1:
    report(False, "שורת קופירייט", f"- עוגן נמצא {content.count(old1)} פעמים")
else:
    new1 = old1 + '<div style="font-size:9px;color:var(--text2);text-align:center;margin-top:2px;opacity:0.7">© <span id="copyrightYear"></span> Location Share. כל הזכויות שמורות.</div>'
    content = content.replace(old1, new1)
    report(True, "שורת קופירייט", "- נוספה מתחת לגרסה")

if "copyrightYear').textContent" in content:
    report(False, "מילוי שנה", "- כבר קיים, מדלג")
else:
    anchor2 = "function openModal(id){document.getElementById(id).classList.add('open');}"
    if content.count(anchor2) != 1:
        report(False, "מילוי שנה", f"- עוגן נמצא {content.count(anchor2)} פעמים")
    else:
        year_script = '''document.addEventListener('DOMContentLoaded',()=>{
  const cy=document.getElementById('copyrightYear');
  if(cy)cy.textContent=new Date().getFullYear();
});
'''
        content = content.replace(anchor2, year_script + anchor2)
        report(True, "מילוי שנה", "- נוסף (מתעדכן אוטומטית כל שנה)")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

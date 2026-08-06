import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def report(ok, label, extra=""):
    print(("✅ " if ok else "❌ ")+label+" "+extra)

anchor1 = "function navigateToUser(uid){"
if "function copyUserCoordinates(" in content:
    report(False, "copyUserCoordinates", "- כבר קיים, מדלג")
elif content.count(anchor1) != 1:
    report(False, "copyUserCoordinates", f"- עוגן נמצא {content.count(anchor1)} פעמים")
else:
    new_func = '''function copyUserCoordinates(uid){
  const u=allUsersData[uid];
  if(!u||!u.lat||!u.lng){showToast('אין מיקום זמין','error');return;}
  const text=u.lat.toFixed(6)+','+u.lng.toFixed(6);
  const done=()=>showToast('נ.צ. הועתק: '+text,'success');
  if(navigator.clipboard&&navigator.clipboard.writeText){
    navigator.clipboard.writeText(text).then(done).catch(()=>{
      const el=document.createElement('textarea');
      el.value=text;document.body.appendChild(el);el.select();
      document.execCommand('copy');document.body.removeChild(el);
      done();
    });
  }else{
    const el=document.createElement('textarea');
    el.value=text;document.body.appendChild(el);el.select();
    document.execCommand('copy');document.body.removeChild(el);
    done();
  }
}
window.copyUserCoordinates=copyUserCoordinates;

'''
    shutil.copy(path, path + ".bak")
    content = content.replace(anchor1, new_func + anchor1)
    report(True, "copyUserCoordinates", "- נוספה")

anchor2 = '''${d.id!==myUID?`<div class="user-act-btn" onclick="navigateToUser('${d.id}')"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg></div>`:''}'''
if anchor2 not in content:
    report(False, "כפתור ברשימה", "- לא נמצא עוגן")
elif 'onclick="copyUserCoordinates(\'${d.id}\')"' in content:
    report(False, "כפתור ברשימה", "- כבר קיים, מדלג")
else:
    copy_btn = '''
          ${d.id!==myUID?`<div class="user-act-btn" onclick="copyUserCoordinates('${d.id}')"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg></div>`:''}'''
    content = content.replace(anchor2, anchor2 + copy_btn)
    report(True, "כפתור ברשימה", "- נוסף")

anchor3 = '''<button onclick="navigateToUser('${uid}')" style="flex:1;background:var(--surface2);color:#fff;border:1px solid rgba(255,255,255,0.2);border-radius:8px;padding:7px 4px;font-size:12px;font-weight:600;cursor:pointer;font-family:inherit">🧭 ניווט</button>'''
if anchor3 not in content:
    report(False, "כפתור בפופאפ", "- לא נמצא עוגן")
elif "copyUserCoordinates('${uid}')" in content:
    report(False, "כפתור בפופאפ", "- כבר קיים, מדלג")
else:
    copy_btn3 = '''
        <button onclick="copyUserCoordinates('${uid}')" style="flex:1;background:var(--surface2);color:#fff;border:1px solid rgba(255,255,255,0.2);border-radius:8px;padding:7px 4px;font-size:12px;font-weight:600;cursor:pointer;font-family:inherit">📋 העתק נ.צ.</button>'''
    content = content.replace(anchor3, anchor3 + copy_btn3)
    report(True, "כפתור בפופאפ", "- נוסף")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

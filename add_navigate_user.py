import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

anchor1 = "function navigateToPoint(id){"
idx1 = content.find(anchor1)
if idx1 == -1:
    print("❌ שלב 1: לא נמצא עוגן navigateToPoint")
elif "function navigateToUser(" in content:
    print("⏭️ שלב 1: navigateToUser כבר קיים, מדלג")
else:
    new_func = """function navigateToUser(uid){
  const u=allUsersData[uid];
  if(!u||!u.lat||!u.lng){showToast('אין מיקום זמין','error');return;}
  window.location.href='geo:'+u.lat+','+u.lng+'?q='+u.lat+','+u.lng;
}
window.navigateToUser=navigateToUser;

"""
    content = content[:idx1] + new_func + content[idx1:]
    print("✅ שלב 1: navigateToUser נוסף")

anchor2 = '''<div class="user-act-btn" onclick="flyToUser('${d.id}')"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg></div>`:''}'''
if anchor2 not in content:
    print("❌ שלב 2: לא נמצא עוגן כפתור flyToUser ברשימה")
elif 'onclick="navigateToUser(\'${d.id}\')"' in content:
    print("⏭️ שלב 2: כפתור הניווט ברשימה כבר קיים, מדלג")
else:
    nav_btn = '''
          ${d.id!==myUID?`<div class="user-act-btn" onclick="navigateToUser('${d.id}')"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="3 11 22 2 13 21 11 13 3 11"/></svg></div>`:''}'''
    content = content.replace(anchor2, anchor2 + nav_btn)
    print("✅ שלב 2: כפתור ניווט נוסף לרשימת חברי הקבוצה")

anchor3 = '''<button onclick="openDM('${uid}','${escHtml(data.name)}','${data.avatar||'👤'}')" style="flex:1;background:#00d4aa;color:#000;border:none;border-radius:8px;padding:7px 4px;font-size:12px;font-weight:600;cursor:pointer;font-family:inherit">💌 הודעה</button>'''
if anchor3 not in content:
    print("❌ שלב 3: לא נמצא עוגן כפתור הודעה בפופאפ")
elif "🧭 ניווט" in content:
    print("⏭️ שלב 3: כפתור הניווט בפופאפ כבר קיים, מדלג")
else:
    nav_btn3 = '''
        <button onclick="navigateToUser('${uid}')" style="flex:1;background:var(--surface2);color:#fff;border:1px solid rgba(255,255,255,0.2);border-radius:8px;padding:7px 4px;font-size:12px;font-weight:600;cursor:pointer;font-family:inherit">🧭 ניווט</button>'''
    content = content.replace(anchor3, anchor3 + nav_btn3)
    print("✅ שלב 3: כפתור ניווט נוסף לפופאפ במפה")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

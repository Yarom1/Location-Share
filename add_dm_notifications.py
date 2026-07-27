import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def report(ok, label, extra=""):
    print(("✅ " if ok else "❌ ")+label+" "+extra)

start_anchor = "function listenDM(uid){"
end_anchor = "async function sendMessage()"
idx_start = content.find(start_anchor)
idx_end = content.find(end_anchor)

if idx_start == -1 or idx_end == -1 or idx_end < idx_start:
    report(False, "listenDM + notifyDMMessage", "- לא נמצאו עוגנים")
elif "function notifyDMMessage(" in content:
    report(False, "listenDM + notifyDMMessage", "- כבר קיים, מדלג")
else:
    new_block = '''function notifyDMMessage(m,otherUid){
  if(window.AndroidBridge&&window.AndroidBridge.showAlertNotification){
    try{
      window.AndroidBridge.showAlertNotification('dm_chat','הודעות פרטיות',`${m.name||'מישהו'} · הודעה פרטית`,m.text||'','dm:'+encodeURIComponent(otherUid)+':'+encodeURIComponent(m.name||'')+':'+encodeURIComponent(m.avatar||'👤'));
    }catch(e){console.error(e);}
  }
}

function listenDM(uid){
  if(unsubDM)unsubDM();
  let isFirstLoad=true;
  const dmId=[myUID,uid].sort().join('_');
  const q=query(collection(db,'dms',dmId,'messages'),orderBy('ts','asc'),limit(100));
  unsubDM=onSnapshot(q,snap=>{
    const chatOpenOnThisDM=document.getElementById('chatPanel').classList.contains('open')&&activeChatTab==='dm'&&activeDMUser&&activeDMUser.uid===uid;
    if(!isFirstLoad){
      snap.docChanges().forEach(change=>{
        if(change.type==='added'){
          const m=change.doc.data();
          if(m.uid!==myUID&&!chatOpenOnThisDM){
            notifyDMMessage(m,uid);
          }
        }
      });
    }
    isFirstLoad=false;
    const msgs=document.getElementById('chatMessages');msgs.innerHTML='';
    snap.forEach(d=>appendMsg(d.data()));msgs.scrollTop=msgs.scrollHeight;
  });
}

'''
    content = content[:idx_start] + new_block + content[idx_end:]
    report(True, "listenDM + notifyDMMessage", "- הוחלף/נוסף")

old2 = '''window.handleDeepLink=function(link){
  if(link==='groups'){
    openPanel('groups');
  } else if(link==='chat'){
    openPanel('chat');
    switchChatTab('group');
  }
};'''
new2 = '''window.handleDeepLink=function(link){
  if(link==='groups'){
    openPanel('groups');
  } else if(link==='chat'){
    openPanel('chat');
    switchChatTab('group');
  } else if(link.indexOf('dm:')===0){
    const parts=link.slice(3).split(':');
    const uid=decodeURIComponent(parts[0]||'');
    const name=decodeURIComponent(parts[1]||'');
    const avatar=decodeURIComponent(parts[2]||'👤');
    if(uid)openDM(uid,name,avatar);
  }
};'''
if content.count(old2) == 0:
    report(False, "עדכון handleDeepLink", "- לא נמצא עוגן מדויק")
elif content.count(old2) > 1:
    report(False, "עדכון handleDeepLink", f"- {content.count(old2)} מופעים")
else:
    content = content.replace(old2, new2)
    report(True, "עדכון handleDeepLink", "- נוסף טיפול בקישור dm:")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

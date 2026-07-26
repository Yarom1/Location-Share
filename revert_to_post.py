import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

old = """    const encodedQ=encodeURIComponent(query);
    const serverUrls=[
      'https://overpass-api.de/api/interpreter?data='+encodedQ,
      'https://overpass.kumi.systems/api/interpreter?data='+encodedQ
    ];
    const attemptFetch=(url)=>new Promise((resolve,reject)=>{
      const controller=new AbortController();
      const timer=setTimeout(()=>controller.abort(),12000);
      fetch(url,{method:'GET',signal:controller.signal})
        .then(res=>{
          clearTimeout(timer);
          if(!res.ok){reject(new Error('HTTP '+res.status));return;}
          return res.json();
        })
        .then(json=>{if(json)resolve(json);})
        .catch(err=>{clearTimeout(timer);reject(err);});
    });
    const data=await Promise.any(serverUrls.map(attemptFetch));"""

new = """    const serverUrls=[
      'https://overpass-api.de/api/interpreter',
      'https://overpass.kumi.systems/api/interpreter'
    ];
    const attemptFetch=(url)=>new Promise((resolve,reject)=>{
      const controller=new AbortController();
      const timer=setTimeout(()=>controller.abort(),12000);
      fetch(url,{method:'POST',body:query,signal:controller.signal})
        .then(res=>{
          clearTimeout(timer);
          if(!res.ok){reject(new Error('HTTP '+res.status));return;}
          return res.json();
        })
        .then(json=>{if(json)resolve(json);})
        .catch(err=>{clearTimeout(timer);reject(err);});
    });
    const data=await Promise.any(serverUrls.map(attemptFetch));"""

count = content.count(old)
if count == 0:
    print("❌ לא נמצא")
elif count > 1:
    print(f"⚠️ {count} מופעים")
else:
    shutil.copy(path, path + ".bak")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.replace(old, new))
    print("✅ הוחזר ל-POST, נשמרה המקביליות והטיימאאוט המקוצר")

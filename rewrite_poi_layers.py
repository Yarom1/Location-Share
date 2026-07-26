import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

start_anchor = "// ===== POI LAYERS"
end_anchor = "window.togglePOI=togglePOI;"

idx_start = content.find(start_anchor)
idx_end = content.find(end_anchor)

if idx_start == -1 or idx_end == -1:
    print("❌ לא נמצאו עוגני התחלה/סוף - בדוק ידנית")
    raise SystemExit

idx_end_full = idx_end + len(end_anchor)
old_block = content[idx_start:idx_end_full]

new_block = '''// ===== POI LAYERS (Overpass API) =====
const poiLayers={};
const poiConfig={
  fuel:{tag:'amenity=fuel',color:'#ff9800',icon:'⛽'},
  transit:{tag:'highway=bus_stop',color:'#2196f3',icon:'🚌'},
  rail:{tag:'railway=station',color:'#9c27b0',icon:'🚆'},
  food:{tag:'amenity=restaurant|amenity=cafe',color:'#f44336',icon:'🍽️'},
  parking:{tag:'amenity=parking',color:'#4caf50',icon:'🅿️'},
  ev:{tag:'amenity=charging_station',color:'#00bcd4',icon:'🔌'},
  pharmacy:{tag:'amenity=pharmacy',color:'#8bc34a',icon:'💊'},
  hospital:{tag:'amenity=hospital|amenity=clinic',color:'#e91e63',icon:'🏥'},
  bank:{tag:'amenity=bank|amenity=atm',color:'#3f51b5',icon:'🏧'},
  hotel:{tag:'tourism=hotel',color:'#795548',icon:'🏨'},
  school:{tag:'amenity=school',color:'#607d8b',icon:'🏫'},
  park:{tag:'leisure=park',color:'#4caf50',icon:'🌳'}
};

// ----- IndexedDB cache לנקודות POI -----
let poiDB=null;
function openPoiDB(){
  return new Promise((resolve)=>{
    if(poiDB){resolve(poiDB);return;}
    try{
      const req=indexedDB.open('locshare_poi_cache',1);
      req.onupgradeneeded=e=>{
        const db=e.target.result;
        if(!db.objectStoreNames.contains('points')){
          const store=db.createObjectStore('points',{keyPath:'key'});
          store.createIndex('type','type',{unique:false});
        }
      };
      req.onsuccess=e=>{poiDB=e.target.result;resolve(poiDB);};
      req.onerror=()=>resolve(null);
    }catch(e){resolve(null);}
  });
}
async function poiCacheGetByType(type){
  const db=await openPoiDB();
  if(!db)return [];
  return new Promise(resolve=>{
    try{
      const tx=db.transaction('points','readonly');
      const idx=tx.objectStore('points').index('type');
      const req=idx.getAll(IDBKeyRange.only(type));
      req.onsuccess=()=>resolve(req.result||[]);
      req.onerror=()=>resolve([]);
    }catch(e){resolve([]);}
  });
}
async function poiCachePut(type,el){
  const db=await openPoiDB();
  if(!db)return;
  try{
    const tx=db.transaction('points','readwrite');
    tx.objectStore('points').put({key:type+':'+el.id,type,id:el.id,lat:el.lat,lon:el.lon,tags:el.tags||{}});
  }catch(e){}
}

function togglePOILayers(e){
  const panel=document.getElementById('poiLayersPanel');
  const wasOpen=panel.classList.contains('open');
  document.getElementById('layersPanel').classList.remove('open');
  panel.classList.toggle('open',!wasOpen);
  if(!wasOpen&&e&&e.currentTarget){
    const r=e.currentTarget.getBoundingClientRect();
    panel.style.top=(r.bottom+8)+'px';
    panel.style.left='auto';
    panel.style.right=(window.innerWidth-r.right)+'px';
  }
}

async function togglePOI(type){
  const checked=document.getElementById('poi'+type.charAt(0).toUpperCase()+type.slice(1)).checked;
  if(!checked){
    if(poiLayers[type]){
      Object.values(poiLayers[type]).forEach(p=>p.marker.remove());
      delete poiLayers[type];
    }
    return;
  }
  await loadPOILayer(type);
}

function poiMarkerHTML(type,el){
  const cfg=poiConfig[type];
  const brand=el.tags&&(el.tags.brand||el.tags.operator||'');
  let icon=cfg.icon, bg=cfg.color;
  if(type==='fuel'&&brand){
    const b=brand.toLowerCase();
    if(b.includes('sonol')||b.includes('סונול')){icon='⛽';bg='#0066b3';}
    else if(b.includes('paz')||b.includes('פז')){icon='⛽';bg='#e30613';}
    else if(b.includes('delek')||b.includes('דלק')){icon='⛽';bg='#ffcc00';}
    else if(b.includes('dor')||b.includes('דור אלון')||b.includes('alon')){icon='⛽';bg='#00a651';}
    else if(b.includes('ten')||b.includes('טן')){icon='⛽';bg='#f7941d';}
  }
  const label=brand?brand:'';
  return '<div style="display:flex;flex-direction:column;align-items:center">'+
    (label?'<div style="background:rgba(13,17,23,0.8);color:#fff;font-size:9px;font-weight:600;padding:1px 5px;border-radius:6px;margin-bottom:2px;white-space:nowrap">'+escHtml(label)+'</div>':'')+
    '<div style="font-size:16px;background:'+bg+';border-radius:50%;width:24px;height:24px;display:flex;align-items:center;justify-content:center;box-shadow:0 2px 4px rgba(0,0,0,.4);border:2px solid white">'+icon+'</div></div>';
}

function renderPoiMarker(type,el){
  poiLayers[type]=poiLayers[type]||{};
  const key=String(el.id);
  const existing=poiLayers[type][key];
  if(existing){
    existing.marker.setLngLat([el.lon,el.lat]);
    existing.marker.getElement().innerHTML=poiMarkerHTML(type,el);
    existing.lat=el.lat;existing.lon=el.lon;existing.tags=el.tags||{};
    return;
  }
  const markerEl=document.createElement('div');
  markerEl.innerHTML=poiMarkerHTML(type,el);
  const marker=new maplibregl.Marker({element:markerEl}).setLngLat([el.lon,el.lat]).addTo(map);
  const displayName=el.tags&&(el.tags.name||(el.tags.brand||el.tags.operator));
  if(displayName){
    markerEl.addEventListener('click',()=>{
      new maplibregl.Popup({closeButton:true}).setLngLat([el.lon,el.lat]).setHTML('<div style="padding:4px;font-size:13px;font-weight:600">'+escHtml(displayName)+'</div>').addTo(map);
    });
  }
  poiLayers[type][key]={marker,lat:el.lat,lon:el.lon,tags:el.tags||{}};
}

async function loadPOILayer(type){
  const cfg=poiConfig[type];
  const bounds=map.getBounds();
  const south=bounds.getSouth(),west=bounds.getWest(),north=bounds.getNorth(),east=bounds.getEast();

  const cached=await poiCacheGetByType(type);
  const inView=cached.filter(p=>p.lat>=south&&p.lat<=north&&p.lon>=west&&p.lon<=east);
  inView.forEach(p=>renderPoiMarker(type,p));

  const bbox=south+','+west+','+north+','+east;
  const tags=cfg.tag.split('|').map(t=>{
    const[k,v]=t.split('=');
    return 'node['+k+'='+JSON.stringify(v)+'](' +bbox+');';
  }).join('');
  const query='[out:json][timeout:30];('+tags+');out body 500;';
  try{
    const servers=['https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter'];
    let data=null;
    for(const server of servers){
      try{
        const controller=new AbortController();
        const timer=setTimeout(()=>controller.abort(),30000);
        const res=await fetch(server,{method:'POST',body:query,signal:controller.signal});
        clearTimeout(timer);
        data=await res.json();
        break;
      }catch(e){
        if(server===servers[servers.length-1])throw e;
      }
    }
    data.elements.forEach(el=>{
      if(!el.lat||!el.lon)return;
      const key=String(el.id);
      const existing=poiLayers[type]&&poiLayers[type][key];
      const changed=!existing||existing.lat!==el.lat||existing.lon!==el.lon||JSON.stringify(existing.tags||{})!==JSON.stringify(el.tags||{});
      if(changed){
        renderPoiMarker(type,el);
        poiCachePut(type,el);
      }
    });
    if(inView.length===0){
      showToast(cfg.icon+' '+data.elements.length+' נמצאו','success');
    }
  }catch(e){
    if(inView.length===0){
      showToast('לא ניתן לטעון '+cfg.icon+' כרגע','error');
      document.getElementById('poi'+type.charAt(0).toUpperCase()+type.slice(1)).checked=false;
    }
  }
}

window.togglePOILayers=togglePOILayers;
window.togglePOI=togglePOI;'''

shutil.copy(path, path + ".bak")
new_content = content[:idx_start] + new_block + content[idx_end_full:]
with open(path, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"✅ הוחלף בהצלחה: {len(old_block)} תווים -> {len(new_block)} תווים")

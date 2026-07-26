import shutil

path = "web/index.html"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def report(ok, label, extra=""):
    print(("✅ " if ok else "❌ ")+label+" "+extra)

anchor_html = '<div class="toast-wrap" id="toastWrap"></div>'
if 'id="cropModal"' in content:
    report(False, "HTML מודאל", "- כבר קיים, מדלג")
else:
    idx = content.find(anchor_html)
    if idx == -1:
        report(False, "HTML מודאל", "- לא נמצא עוגן toastWrap")
    else:
        insert_after = idx + len(anchor_html)
        crop_modal_html = '''
<div class="modal" id="cropModal">
  <div class="modal-box">
    <h3>✂️ חיתוך תמונה</h3>
    <div id="cropViewport" style="width:260px;height:260px;margin:12px auto;position:relative;overflow:hidden;border-radius:50%;background:#000;touch-action:none;cursor:grab">
      <img id="cropImg" draggable="false" style="position:absolute;left:0;top:0;transform-origin:0 0;user-select:none;-webkit-user-drag:none">
    </div>
    <input type="range" id="cropZoom" min="1" max="3" step="0.01" value="1" style="width:100%" oninput="onCropZoomChange()">
    <div style="display:flex;gap:8px;margin-top:14px">
      <button class="btn secondary" style="flex:1" onclick="closeModal('cropModal')">ביטול</button>
      <button class="btn" style="flex:1" onclick="confirmCrop()">אישור</button>
    </div>
  </div>
</div>
'''
        content = content[:insert_after] + crop_modal_html + content[insert_after:]
        report(True, "HTML מודאל", "- נוסף")

anchor_js = "function openModal(id){document.getElementById(id).classList.add('open');}"
if "function openCropModal(" in content:
    report(False, "JS פונקציות חיתוך", "- כבר קיים, מדלג")
else:
    idx2 = content.find(anchor_js)
    if idx2 == -1:
        report(False, "JS פונקציות חיתוך", "- לא נמצא עוגן openModal")
    else:
        crop_js = '''let cropImgEl=null,cropNaturalW=0,cropNaturalH=0,cropBaseScale=1,cropZoomVal=1,cropOffX=0,cropOffY=0,cropDragging=false,cropDragStartX=0,cropDragStartY=0,cropStartOffX=0,cropStartOffY=0;
const CROP_SIZE=260;

function applyCropTransform(){
  const scale=cropBaseScale*cropZoomVal;
  cropImgEl.style.width=(cropNaturalW*scale)+'px';
  cropImgEl.style.height=(cropNaturalH*scale)+'px';
  cropImgEl.style.transform='translate('+cropOffX+'px,'+cropOffY+'px)';
}
function clampCropOffset(){
  const scale=cropBaseScale*cropZoomVal;
  const dispW=cropNaturalW*scale,dispH=cropNaturalH*scale;
  cropOffX=Math.min(0,Math.max(CROP_SIZE-dispW,cropOffX));
  cropOffY=Math.min(0,Math.max(CROP_SIZE-dispH,cropOffY));
}
function openCropModal(dataUrl){
  const img=document.getElementById('cropImg');
  cropImgEl=img;
  img.onload=()=>{
    cropNaturalW=img.naturalWidth;
    cropNaturalH=img.naturalHeight;
    cropBaseScale=CROP_SIZE/Math.min(cropNaturalW,cropNaturalH);
    cropZoomVal=1;
    document.getElementById('cropZoom').value=1;
    const dispW=cropNaturalW*cropBaseScale,dispH=cropNaturalH*cropBaseScale;
    cropOffX=(CROP_SIZE-dispW)/2;
    cropOffY=(CROP_SIZE-dispH)/2;
    applyCropTransform();
  };
  img.src=dataUrl;
  openModal('cropModal');
}
function onCropZoomChange(){
  const newZoom=parseFloat(document.getElementById('cropZoom').value);
  const scaleBefore=cropBaseScale*cropZoomVal;
  const scaleAfter=cropBaseScale*newZoom;
  const cx=CROP_SIZE/2,cy=CROP_SIZE/2;
  const imgCx=(cx-cropOffX)/scaleBefore;
  const imgCy=(cy-cropOffY)/scaleBefore;
  cropZoomVal=newZoom;
  cropOffX=cx-imgCx*scaleAfter;
  cropOffY=cy-imgCy*scaleAfter;
  clampCropOffset();
  applyCropTransform();
}
function confirmCrop(){
  const scale=cropBaseScale*cropZoomVal;
  const srcX=(0-cropOffX)/scale;
  const srcY=(0-cropOffY)/scale;
  const srcSize=CROP_SIZE/scale;
  const OUT=400;
  const canvas=document.createElement('canvas');
  canvas.width=OUT;canvas.height=OUT;
  canvas.getContext('2d').drawImage(cropImgEl,srcX,srcY,srcSize,srcSize,0,0,OUT,OUT);
  profileImageData=canvas.toDataURL('image/jpeg',0.85);
  updateEditPinPreview();
  closeModal('cropModal');
  const fi=document.getElementById('profileImageInput');
  if(fi)fi.value='';
}
document.addEventListener('DOMContentLoaded',()=>{
  const vp=document.getElementById('cropViewport');
  if(!vp)return;
  vp.addEventListener('pointerdown',e=>{
    cropDragging=true;
    cropDragStartX=e.clientX;cropDragStartY=e.clientY;
    cropStartOffX=cropOffX;cropStartOffY=cropOffY;
    vp.setPointerCapture(e.pointerId);
  });
  vp.addEventListener('pointermove',e=>{
    if(!cropDragging)return;
    cropOffX=cropStartOffX+(e.clientX-cropDragStartX);
    cropOffY=cropStartOffY+(e.clientY-cropDragStartY);
    clampCropOffset();
    applyCropTransform();
  });
  const endDrag=()=>{cropDragging=false;};
  vp.addEventListener('pointerup',endDrag);
  vp.addEventListener('pointercancel',endDrag);
});
window.onCropZoomChange=onCropZoomChange;
window.confirmCrop=confirmCrop;

'''
        content = content[:idx2] + crop_js + content[idx2:]
        report(True, "JS פונקציות חיתוך", "- נוספו")

start_anchor = "function handleProfileImage(e){"
end_anchor = "\n\nasync function saveE"
idx_start = content.find(start_anchor)
idx_end = content.find(end_anchor)
if idx_start == -1 or idx_end == -1 or idx_end < idx_start:
    report(False, "עדכון handleProfileImage", "- לא נמצאו עוגנים")
elif "openCropModal(ev.target.result)" in content[idx_start:idx_end]:
    report(False, "עדכון handleProfileImage", "- כבר עודכן, מדלג")
else:
    new_handler = '''function handleProfileImage(e){
  const file=e.target.files[0];
  if(!file)return;
  const reader=new FileReader();
  reader.onload=ev=>{
    openCropModal(ev.target.result);
  };
  reader.readAsDataURL(file);
}'''
    content = content[:idx_start] + new_handler + content[idx_end:]
    report(True, "עדכון handleProfileImage", "- מעכשיו פותח את מודאל החיתוך")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

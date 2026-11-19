from PIL import Image,ImageOps
from pathlib import Path
import json
root=Path(__file__).parent.parent;mapping={}
for f in (root/'dist/assets').iterdir():
 if f.stem.endswith(('-700','-1400')):continue
 try:
  im=ImageOps.exif_transpose(Image.open(f));w,h=im.size
  variants=[]
  for size in [700,1400]:
   if w<=size:continue
   out=f.with_name(f.stem+f'-{size}.webp')
   if not out.exists():
    cp=im.copy();cp.thumbnail((size,round(h*size/w)),Image.Resampling.LANCZOS);cp.save(out,'WEBP',quality=86,method=4)
   variants.append({'src':'/assets/'+out.name,'width':size})
  mapping['/assets/'+f.name]={'width':w,'height':h,'variants':variants}
 except Exception as ex:print('Skip',f.name,str(ex)[:80])
(root/'research/responsive-images.json').write_text(json.dumps(mapping,indent=2))
print('Responsive images',len(mapping))

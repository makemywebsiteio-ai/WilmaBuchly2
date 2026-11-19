from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse,unquote
import json
root=Path(__file__).parent/'dist';errors=[];external_images=set();blank=[]
for f in root.rglob('*.html'):
 s=BeautifulSoup(f.read_text(),'html.parser');path='/'+str(f.relative_to(root))
 if len(s.select('h1'))!=1:errors.append((path,'h1 count',len(s.select('h1'))))
 if not s.select_one('meta[name=robots][content="noindex,nofollow"]'):errors.append((path,'no robots'))
 for a in s.select('a[href],img[src],script[src],link[href]'):
  u=a.get('href') or a.get('src');p=urlparse(u)
  if u.startswith('/'):
   dest=root/p.path.lstrip('/')
   if p.path.endswith('/'):dest=dest/'index.html'
   if not dest.exists():errors.append((path,'missing',u))
  elif a.name=='img':external_images.add(u)
 if not s.select_one('main').get_text(strip=True):blank.append(path)
 if s.select('form,input[name],iframe,script:not([src])'):errors.append((path,'unsafe preview element'))
print(json.dumps({'pages':len(list(root.rglob('index.html'))),'errors':errors[:50],'external_images':len(external_images),'blank':blank},indent=2))
(root.parent/'research/validation.json').write_text(json.dumps({'pages':len(list(root.rglob('index.html'))),'errors':errors,'external_images':sorted(external_images),'blank':blank},indent=2))

from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse,urljoin,unquote
import concurrent.futures,subprocess,json,hashlib,re
ROOT=Path(__file__).parent; ASSETS=ROOT.parent/'dist/assets'; BASE='https://www.wilmabuchly.com'
routes=json.loads((ROOT/'routes.json').read_text())
def fetch(url):
 name=urlparse(url).path.strip('/').replace('/','__') or 'home';out=ROOT/(name+'.html')
 if not out.exists():
  r=subprocess.run(['curl','-L','--fail','--silent','--max-time','40',url,'-o',str(out)])
  if r.returncode:return url,'FAILED'
 return url,name+'.html'
# Follow observed blog, catalogue and pagination links; never cart mutation links.
extra=set()
for url,file in list(routes.items()):
 s=BeautifulSoup((ROOT/file).read_text(),'html.parser')
 if '/blog/' in url:
  extra.update(a['href'] for a in s.select('h2 a[href],h3 a[href],a.page-numbers') if a['href'].startswith(BASE))
 if '/product-categorie/' in url or '/winkel/' in url:
  extra.update(a['href'] for a in s.select('li.product a[href]') if '/product/' in a['href'] and '?' not in a['href'])
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex: routes.update(dict(ex.map(fetch,sorted(extra))))
(ROOT/'routes.json').write_text(json.dumps(routes,indent=2))
assets={}
for url,file in routes.items():
 if file=='FAILED':continue
 s=BeautifulSoup((ROOT/file).read_text(),'html.parser')
 for el in s.select('img[src]'):
  src=el['src']
  if not ('/wp-content/uploads/' in src):continue
  # Prefer largest explicitly declared image source, not guessed file names.
  ss=el.get('srcset',''); candidates=[]
  for item in ss.split(', '):
   m=re.match(r'(.+) (\d+)w$',item)
   if m:candidates.append((int(m[2]),m[1]))
  if candidates:src=max(candidates)[1]
  original=src
  if 'i0.wp.com/' in src:src='https://'+src.split('i0.wp.com/')[1].split('?')[0]
  ext=Path(urlparse(src).path).suffix or '.jpg'
  fname=hashlib.sha1(src.encode()).hexdigest()[:10]+ext
  assets[el['src']]={'url':src,'file':'/assets/'+fname,'alt':el.get('alt',''),'width':el.get('width'),'height':el.get('height')}
def asset(item):
 src,data=item;out=ASSETS/Path(data['file']).name
 if out.exists():return
 r=subprocess.run(['curl','-L','--fail','--silent','--max-time','40',data['url'],'-o',str(out)])
 if r.returncode:print('ASSET FAIL',data['url'])
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:list(ex.map(asset,assets.items()))
(ROOT/'assets.json').write_text(json.dumps(assets,indent=2,ensure_ascii=False))
print('Pages',len(routes),'Assets',len(assets))

from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import concurrent.futures, subprocess, json
ROOT=Path(__file__).parent
s=BeautifulSoup((ROOT/'home.html').read_text(),'html.parser')
urls=list(dict.fromkeys(a['href'] for a in s.select('a[href]') if a['href'].startswith('https://www.wilmabuchly.com/') and not any(x in a['href'] for x in ['/mijn-account/','/winkelwagen/','/afrekenen/'])))
def fetch(url):
 name=urlparse(url).path.strip('/').replace('/','__') or 'home'
 out=ROOT/(name+'.html')
 if not out.exists():
  r=subprocess.run(['curl','-L','--fail','--silent','--max-time','45',url,'-o',str(out)])
  if r.returncode:return (url,'FAILED')
 return (url,name+'.html')
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex: results=list(ex.map(fetch,urls))
(ROOT/'routes.json').write_text(json.dumps(dict(results),indent=2))
print(results)

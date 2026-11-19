from pathlib import Path
import json,subprocess,concurrent.futures,time
root=Path(__file__).parent
routes=json.loads((root/'routes.json').read_text())
jobs=[]
for url,file in routes.items():
 if file=='FAILED':jobs.append((url,root/(url.split('.com/')[1].strip('/').replace('/','__')+'.html')))
a=json.loads((root/'assets.json').read_text())
for v in a.values():
 out=root.parent/'dist'/v['file'].lstrip('/')
 if not out.exists():jobs.append((v['url'],out))
def work(job):
 url,out=job
 time.sleep(1)
 r=subprocess.run(['curl','-L','--fail','--silent','--show-error','--retry','2','--max-time','25',url,'-o',str(out)],capture_output=True)
 return url,str(out),r.returncode,r.stderr.decode()[:100]
with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:result=list(ex.map(work,jobs))
for url,out,code,err in result:
 if not code and url in routes:routes[url]=Path(out).name
(root/'routes.json').write_text(json.dumps(routes,indent=2))
print('Successful',sum(x[2]==0 for x in result),'failed',[(x[0],x[2],x[3]) for x in result if x[2]][:8])

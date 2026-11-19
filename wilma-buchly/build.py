"""Generate a static, no-tracking design preview from archived source content."""
from pathlib import Path
from bs4 import BeautifulSoup, NavigableString, Tag
from urllib.parse import urlparse
import json,re,html,shutil
ROOT=Path(__file__).parent; DIST=ROOT/'dist'; RESEARCH=ROOT/'research'; BASE='https://www.wilmabuchly.com'
ROUTES=json.loads((RESEARCH/'routes.json').read_text()); ASSETS=json.loads((RESEARCH/'assets.json').read_text())
PAGES={urlparse(u).path:BeautifulSoup((RESEARCH/f).read_text(),'html.parser') for u,f in ROUTES.items() if f!='FAILED'}
RESPONSIVE=json.loads((RESEARCH/'responsive-images.json').read_text())
e=lambda x:html.escape(str(x),quote=True)
def text(x):return x.get_text(' ',strip=True) if x else ''
def title(x):return re.sub(r'[.\u2026]+','',text(x)).strip()
def href(u):
 p=urlparse(u)
 if p.netloc in ['www.wilmabuchly.com','wilmabuchly.com'] and p.path in PAGES and not p.query:return p.path+(('#'+p.fragment) if p.fragment else '')
 return u

def img(el,cls='',eager=False):
 if isinstance(el,str):el=next((i for s in ([PAGES['/energetische-praktijk-hellevoetsluis/']]+list(PAGES.values())) for i in s.select('img[src]') if el in i['src']),None)
 if el is None:return ''
 a=ASSETS.get(el.get('src'))
 if not a:return ''
 src=a['file'] if (DIST/a['file'].lstrip('/')).exists() else a['url']
 dimensions=RESPONSIVE.get(a['file'],{});variants=dimensions.get('variants',[])
 srcset=', '.join(v['src']+' '+str(v['width'])+'w' for v in variants)+(', '+src+' '+str(dimensions['width'])+'w' if variants else '')
 extra=f' srcset="{e(srcset)}" sizes="(max-width: 650px) 90vw, (max-width: 950px) 45vw, 600px"' if variants else ''
 return f'<img class="{cls}" src="{e(src)}"{extra} alt="{e(el.get("alt") or "Beeld van Wilma Buchly")}" width="{e(dimensions.get("width") or a.get("width") or 1200)}" height="{e(dimensions.get("height") or a.get("height") or 900)}" loading="{"eager" if eager else "lazy"}" decoding="async">'
def inline(el):
 if isinstance(el,NavigableString):return e(str(el))
 if el.name in ['script','style','iframe','form','input','button','svg','noscript']:return ''
 body=''.join(inline(c) for c in el.children)
 if el.name=='h3':return '<h3>'+e(title(el))+'</h3>'
 if el.name=='ol' and 'steps' in el.get('class',[]):return '<ol class="steps">'+body+'</ol>'
 if el.name=='a':
  u=href(el.get('href',''))
  if not u or u.startswith('javascript:') or '?add-to-cart' in u:return body
  attrs=' class="outbound"' if u.startswith('http') else ''
  return f'<a href="{e(u)}"{attrs}>{body}</a>'
 if el.name in ['strong','em','b','i','br','ul','ol','li','p','blockquote','table','thead','tbody','tr','th','td']:
  return f'<{el.name}>{body}</{el.name}>' if el.name!='br' else '<br>'
 return body

def atoms(el,images=False):
 """Retain semantic source content in order, stripping execution and presentation."""
 result=[]
 for node in el.descendants:
  if not isinstance(node,Tag):continue
  if node.find_parent(['nav','header','footer','form','script','style','noscript']):continue
  if node.name not in ['h1','h2','h3','h4','h5','h6','p','ul','ol','table','blockquote','img','a','iframe','audio']:continue
  if node.find_parent(['p','ul','ol','table','blockquote']):continue
  if node.name=='iframe':
   if 'player.vimeo.com/' in node.get('src',''):
    result.append('<div class="video-block"><button class="video-load button" type="button" data-video="'+e(node['src'])+'">Video bekijken</button><p>De bestaande Vimeo-video wordt pas na je klik geladen.</p><a href="https://vimeo.com/984964723">Bekijk de video op Vimeo</a></div>')
  elif node.name=='audio':
   result.append('<audio controls preload="none" aria-label="Audiofragment Versterk je intuïtie"><source src="/assets/versterk-je-intuitie.mp3" type="audio/mpeg"></audio>')
  elif node.name=='img':
   if images:result.append(img(node))
  elif node.name.startswith('h') and node.name[1:].isdigit():
   if title(node):result.append(f'<h{2 if node.name in ["h1","h2"] else 3}>{e(title(node))}</h{2 if node.name in ["h1","h2"] else 3}>')
  elif node.name=='a':
   if node.find_parent(['h1','h2','h3','h4','h5','h6']) or not text(node) or node.find('img'):continue
   result.append('<p class="source-action">'+inline(node)+'</p>')
  elif text(node):result.append(inline(node))
 return ''.join(result)

def source_sections(path):
 s=PAGES[path];root=s.select_one('.wp-site-blocks') or s.body
 if '/product/' in path:return [s.select_one('.product') or root]
 if s.select_one('.wp-block-post-content,.guten-post-content'):return [s.select_one('.wp-block-post-content,.guten-post-content')]
 children=[x for x in root.children if isinstance(x,Tag)]
 return [x for x in children if x.name not in ['footer','header','script'] and not x.select_one('nav') and text(x) and 'guten-spacer' not in x.get('class',[])]

def photos(el):
 return [i for i in el.select('img[src]') if i['src'] in ASSETS and not any(t in i['src'] for t in ['lotus','Therapeut-5','website_banner','facebook','gravatar','google','logo-energetisch','je-bent-al-heel'])]
NAV=[('/','Home'),('/over-mij/','Over mij'),('/energetische-praktijk-hellevoetsluis/','Praktijkruimte'),('/boek-een-sessie/','Boek een sessie'),('/persoonlijke-begeleiding/','Trajecten'),('/blog/','Blog'),('/winkel/','Shop'),('/contact/','Contact')]
LOGO=img('Energetisch-Therapeut-5','brand-image',True)
SHAPES='<div class="petal-field" aria-hidden="true"><i class="petal petal-one"></i><i class="petal petal-two"></i><i class="petal petal-three"></i><i class="petal petal-four"></i><i class="petal petal-five"></i><i class="petal-outline"></i><i class="petal-outline outline-two"></i></div>'
def header(path):
 links=''.join(f'<a href="{p}" {"aria-current=page" if path==p else ""}>{t}</a>' for p,t in NAV)
 return f'''<a class="skip" href="#inhoud">Direct naar inhoud</a><div class="preview-bar">Ontwerpvoorstel door MakeMyWebsite <span>Onofficiële preview</span></div><header class="site-header"><div class="header-inner"><a class="brand" href="/" aria-label="Wilma Buchly - Home">{LOGO}</a><button class="menu-toggle" aria-expanded="false" aria-controls="navigation" hidden><span class="menu-lines" aria-hidden="true"></span><span class="menu-label">Menu</span></button><nav id="navigation" aria-label="Hoofdnavigatie">{links}</nav></div></header>'''
def footer():
 links=''.join(f'<a href="{p}">{t}</a>' for p,t in NAV[1:])
 legal=''.join(f'<a href="/{p}/">{t}</a>' for p,t in [('algemene-voorwaarden','Algemene voorwaarden'),('privacyverklaring','Privacyverklaring'),('disclaimer','Disclaimer'),('terugbetaal-retourneringen','Retouren'),('bach-bloesemtherapie','Bach bloesem')])
 return f'''<footer class="site-footer"><div class="wrap footer-grid"><div><a class="brand" href="/" aria-label="Wilma Buchly - Home">{LOGO}</a><p>Luisteren voorbij je denken</p><a href="https://www.instagram.com/wilmabuchly/">Instagram</a> <a href="https://www.facebook.com/profile.php?id=61576313136534">Facebook</a></div><div class="footer-links"><h2>Ontdek de praktijk</h2>{links}</div><div class="footer-links"><h2>Goed om te weten</h2>{legal}<a href="{e(next((a['href'] for a in PAGES['/'].select('a[href]') if 'forms.office.com' in a['href']),BASE))}">Anamneseformulier (externe website)</a></div><div><h2>Je bent welkom</h2><p>Staringhof 3<br>3221 VR Hellevoetsluis</p><p><a href="tel:+31647117186">06 47 11 71 86</a><br><a href="mailto:contact@wilmabuchly.com">contact@wilmabuchly.com</a></p><button class="motion-toggle" aria-pressed="false" hidden>Animaties pauzeren</button></div></div><div class="wrap rights"><p>Onofficieel ontwerpvoorstel door MakeMyWebsite. Teksten, logo en beeldmateriaal: Wilma Buchly en betrokken rechthebbenden. Geen officiële publicatie.</p><a href="https://www.wilmabuchly.com/">Oorspronkelijke website</a></div></footer>'''
def shell(path,t,body):
 content=BeautifulSoup(body,'html.parser')
 for index,section in enumerate(content.select('section.wrap,.treatments-section,.home-reflection')):
  if index%2==0:
   section['class']=section.get('class',[])+['has-ornament']
   ornament=BeautifulSoup(SHAPES,'html.parser').div
   ornament['class']=['petal-field','section-ornament',f'ornament-{index%3}']
   section.insert(0,ornament)
 body=str(content)
 return f'''<!doctype html><html lang="nl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow"><meta name="description" content="{e(t)} - onofficieel ontwerpvoorstel voor Wilma Buchly"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; img-src 'self' https: data:; style-src 'self'; script-src 'self'; connect-src 'none'; form-action 'none'; frame-src https://player.vimeo.com; media-src 'self'; base-uri 'self'"><title>{e(t)} | Wilma Buchly - Preview</title><link rel="stylesheet" href="/styles.css"><script src="/app.js" defer></script></head><body>{header(path)}<main id="inhoud">{body}</main>{footer()}<dialog class="lightbox" aria-label="Foto vergroten"><button class="lightbox-close" autofocus>Sluiten</button><img alt=""><p></p></dialog></body></html>'''
def write(path,t,body):
 dest=DIST/path.strip('/')/'index.html';dest.parent.mkdir(parents=True,exist_ok=True);dest.write_text(shell(path,t,body))
def intro(t,kicker='Praktijk Wilma Buchly',sub=''):
 return f'<section class="page-intro">{SHAPES}<div class="wrap"><p class="eyebrow">{e(kicker)}</p><h1>{e(t)}</h1>{f"<p class=lead>{e(sub)}</p>" if sub else ""}</div></section>'
def chapter(el,index=0):
 if el.select_one('.ti-review-item'):
  reviews=''.join('<details class="review"><summary>'+e(text(r.select_one('.ti-name')))+'</summary><blockquote>'+e(text(r.select_one('.ti-review-content')))+'</blockquote></details>' for r in el.select('.ti-review-item'))
  return '<section class="wrap reviews"><p class="eyebrow">Ervaringen uit de oorspronkelijke website</p><h2>Mijn recensies</h2><p>Deze recensies zijn overgenomen uit de Google-widget op de oorspronkelijke contactpagina.</p>'+reviews+'<a class="text-link" href="https://www.wilmabuchly.com/contact/">Bekijk de oorspronkelijke recensies</a></section>'
 # Preserve the source's six-step order while expressing it as a real ordered list.
 if 'Je komt tot rust' in text(el) and 'stap voor stap' in text(el):
  el=BeautifulSoup(str(el),'html.parser')
  target=next((p for p in el.select('p') if len(p.select('strong'))==6),None)
  if target:
   fragments=re.split(r'<strong>(.*?)</strong>',str(target),flags=re.S)
   steps=[]
   for n in range(1,len(fragments),2):
    head=BeautifulSoup(fragments[n],'html.parser').get_text().rstrip('.')
    desc=BeautifulSoup(fragments[n+1],'html.parser').get_text(' ',strip=True)
    steps.append('<li><h3>'+e(head)+'</h3><p>'+e(desc)+'</p></li>')
   target.replace_with(BeautifulSoup('<ol class="steps">'+''.join(steps)+'</ol>','html.parser'))
 pp=photos(el);visual=''
 if pp:
  visual='<div class="chapter-photos">'+''.join(f'<button class="photo-expand" type="button" aria-label="Foto vergroten: {e(p.get("alt") or "praktijkbeeld")}">{img(p)}</button>' for p in pp[:4])+'</div>'
  if len(pp)>4:visual+='<div class="photo-strip">'+''.join(f'<button class="photo-expand" type="button" aria-label="Foto vergroten: {e(p.get("alt") or "praktijkbeeld")}">{img(p)}</button>' for p in pp[4:])+'</div>'
 return f'<section class="wrap chapter {"with-images" if pp else "text-only"} {"reverse" if index%2 else ""}"><div class="prose" data-reveal>{atoms(el)}</div>{visual}</section>'

def blog_entries():
 entries=[]
 for p,s in PAGES.items():
  if p=='/blog/' or p.startswith('/blog/page/'):
   for li in s.select('.wp-block-post,article.guten-post'):
    a=li.select_one('h2 a,h3 a');im=li.select_one('img');ex=li.select_one('.wp-block-post-excerpt__excerpt,.guten-post-excerpt');cat=li.select_one('.taxonomy-category,.guten-post-category')
    if a:entries.append({'href':href(a['href']),'title':text(a),'img':im,'excerpt':text(ex),'category':text(cat) or 'Inzichten & inspiratie'})
 return list({x['href']:x for x in entries}.values())
def blog_cards(entries):
 return ''.join(f'<article class="blog-card" data-search="{e((x["title"]+" "+x["category"]).lower())}"><a href="{e(x["href"])}">{img(x["img"])}<p class="eyebrow">{e(x["category"])}</p><h2>{e(x["title"].replace(".",""))}</h2><p>{e(x["excerpt"])}</p><span class="text-link">Lees het artikel</span></a></article>' for x in entries)

def home():
 ss=source_sections('/');welcome=ss[0];treat=ss[1];middle=ss[2];about=ss[3];shop=ss[4]
 treatments=[]
 for h in treat.select('h3'):
  box=h.parent
  while box.parent and len(box.select('h3'))==1 and len(box.parent.select('h3'))==1:box=box.parent
  treatments.append(box)
 treatmenthtml=''
 for i,b in enumerate(treatments):
  t=text(b.select_one('h3'));content=BeautifulSoup(str(b),'html.parser');head=content.select_one('h3');head.decompose()
  icon=next(iter(b.select('img')),None)
  treatmenthtml+=f'<details class="treatment" {"open" if i==0 else ""}><summary>{img(icon)}<span>{e(t)}</span><span class="plus" aria-hidden="true"></span></summary><div class="detail-body prose">{atoms(content)}</div></details>'
 return f'''<section class="hero">{SHAPES}<div class="wrap hero-grid"><div class="hero-copy"><p class="eyebrow">Energetisch therapeut in Hellevoetsluis</p><h1>Luisteren voorbij<br>je <em>denken</em></h1><p class="hero-description">In mijn praktijk help ik je om te vertragen, los te laten en weer thuis te komen bij jezelf.</p><div class="actions"><a class="button" href="/boek-een-sessie/">Ontdek jouw sessie</a><a class="text-link" href="/over-mij/">Maak kennis met Wilma</a></div><div class="hero-note"><span></span><p>Reiki, Mahatma energie<br>en persoonlijke begeleiding</p></div></div><div class="hero-visual"><div class="portrait">{img('Wilma-Buchly-1','',True)}</div><div class="portrait-caption"><span>Wilma Buchly</span><small>Ruimte om jezelf te zijn</small></div><a class="room-inset" href="/energetische-praktijk-hellevoetsluis/">{img('IMG_4477','',True)}<span>Een plek om te landen</span></a></div></div><div class="hero-bottom wrap"><span>Rust</span><span>Balans</span><span>Verbinding met jezelf</span></div></section>
 <section class="wrap welcome" data-reveal><p class="eyebrow">Welkom, precies zoals je bent</p><div class="welcome-grid"><h2>De antwoorden die je zoekt,<br><span>draag je al in je</span></h2><div class="prose">{atoms(welcome).replace('<h2>Welkom</h2>','')}</div></div></section>
 <section class="treatments-section" id="behandelingen"><div class="wrap treatments-grid"><div class="section-side"><p class="eyebrow">Mijn energetische behandelingen</p><h2>Wat past <br>bij jou?</h2><p>Een sessie die wordt afgestemd op jouw behoeften van dat moment.</p><a class="text-link" href="/boek-een-sessie/">Bekijk alle sessies</a><div class="calm-ambient" aria-hidden="true"><div class="calm-halo halo-back"></div><div class="calm-halo halo-front"></div><div class="lotus-bloom"><i class="bloom-leaf leaf-a"></i><i class="bloom-leaf leaf-b"></i><i class="bloom-leaf leaf-c"></i><i class="bloom-leaf leaf-d"></i><i class="bloom-leaf leaf-e"></i><i class="bloom-contour contour-a"></i><i class="bloom-contour contour-b"></i></div><div class="calm-signature">{img('lotus-1024')}</div></div></div><div class="treatment-list">{treatmenthtml}</div></div></section>
 <section class="wrap home-about"><div class="home-about-photo">{img('IMG_4475')}<span class="photo-label">Met aandacht, rust en afstemming</span></div><div class="prose" data-reveal><p class="eyebrow">De mens achter de praktijk</p>{atoms(about)}<a class="button outline" href="/over-mij/">Meer over Wilma</a></div></section>
 <section class="home-reflection"><div class="wrap prose reflection-copy">{atoms(middle)}</div></section>
 <section class="wrap shop-feature"><div class="prose" data-reveal><p class="eyebrow">Met zorg geselecteerd</p>{atoms(shop)}</div><div class="shop-mosaic">{''.join(img(p) for p in photos(shop)[:4])}</div></section>
 <section class="wrap journal"><div class="section-heading"><div><p class="eyebrow">Inzichten & inspiratie</p><h2>Even stilstaan</h2></div><a class="text-link" href="/blog/">Alle artikelen</a></div><div class="blog-grid">{blog_cards(blog_entries()[:3])}</div></section>
 <section class="closing">{SHAPES}<div class="wrap"><p class="eyebrow">Je hoeft het niet alleen te doen</p><h2>Jouw moment van rust<br>begint hier</h2><a class="button" href="/contact/">Neem contact op</a></div></section>'''

def contact():
 ss=source_sections('/contact/');details=ss[0];rest=ss[1:]
 return intro('Er is ruimte voor jouw verhaal','Contact','Stel gerust je vraag of maak kennis met de praktijk')+f'''<section class="wrap contact-grid"><div class="contact-info"><p class="eyebrow">Praktijk in Hellevoetsluis</p><h2>Je bent welkom</h2><address>Staringhof 3<br>3221 VR Hellevoetsluis</address><a class="contact-link" href="mailto:contact@wilmabuchly.com">contact@wilmabuchly.com</a><a class="contact-link" href="tel:+31647117186">06 47 11 71 86</a>{img('IMG_4477')}<details class="business-details"><summary>Bedrijfsgegevens en aandachtspunten</summary><div class="prose">{atoms(details)}</div></details></div><div class="form-panel"><h2>Een bericht aan Wilma</h2><p id="preview-note" class="form-notice">Dit is een formulierpreview. Je kunt de velden testen; er wordt niets verzonden of opgeslagen.</p><div role="group" aria-labelledby="preview-note" id="preview-form"><label for="first-name">Voornaam</label><input id="first-name" autocomplete="off" type="text"><label for="email">E-mailadres <span>(verplicht)</span></label><input id="email" type="email" required autocomplete="off" aria-describedby="email-error"><p id="email-error" class="field-error" hidden></p><label for="phone">Telefoonnummer</label><input id="phone" type="tel" autocomplete="off"><label for="message">Bericht</label><textarea id="message" rows="5" maxlength="180" aria-describedby="message-count"></textarea><p class="character-count" id="message-count">0 / 180 tekens</p><button class="button" id="test-form" type="button" disabled>Test formulier</button><noscript><p>Schakel JavaScript in om de lokale validatie te testen. Er kan niets worden verzonden.</p></noscript><p id="form-status" role="status"></p></div></div></section>'''+''.join(chapter(x,i) for i,x in enumerate(rest))

def catalog(path):
 s=PAGES[path];products=s.select('li.product,.wc-block-product');items=[]
 for p in products:
  a=p.select_one('a[href*="/product/"]');im=p.select_one('img');h=p.select_one('h2,h3');price=p.select_one('.price,.wc-block-components-product-price');
  if not a or not h:continue
  val=re.search(r'(\d+[,.]\d+)',text(price));num=float(val[1].replace(',','.')) if val else 0
  items.append(f'<article class="product-card" data-search="{e(text(h).lower())}" data-price="{num}"><a href="{e(href(a["href"]))}"><div class="product-image">{img(im)}</div><h2>{e(title(h))}</h2><p class="price">{e(text(price))}</p><span class="text-link">Bekijk product</span></a></article>')
 cats=''.join(f'<a href="{e(p)}" {"aria-current=page" if p==path else ""}>{e(text(PAGES[p].select_one("h1")))}</a>' for p in PAGES if p.startswith('/product-categorie/'))
 t='Met aandacht voor jezelf' if path=='/winkel/' else text(s.select_one('h1'))
 pagination=''.join(f'<a href="{e(href(a["href"]))}">{e(text(a))}</a>' for a in s.select('a.page-numbers'))
 return intro(t,'De webshop','Edelstenen, koper, yoga en kleine momenten van aandacht')+f'<section class="wrap catalog"><p class="catalog-note">Webshoppreview - prijzen en beschikbaarheid komen uit de oorspronkelijke website. Bestellen gebeurt op de oorspronkelijke webshop.</p><div class="shop-utilities"><a href="https://www.wilmabuchly.com/mijn-account/">Mijn account (oorspronkelijke webshop)</a><a href="https://www.wilmabuchly.com/winkelwagen/">Winkelwagen (oorspronkelijke webshop)</a></div><div class="catalog-categories"><a href="/winkel/">Alles bekijken</a>{cats}</div><div class="filterbar"><label>Zoek een product<input type="search" id="filter" placeholder="Bijvoorbeeld koperen waterfles"></label><label>Sorteren<select id="sort"><option value="default">Oorspronkelijke volgorde</option><option value="asc">Prijs: laag naar hoog</option><option value="desc">Prijs: hoog naar laag</option><option value="name">Naam: A tot Z</option></select></label><p id="result-count" role="status">{len(items)} producten</p></div><div class="product-grid filter-grid">{"".join(items)}</div><p class="no-results" hidden>Geen producten gevonden. Probeer een andere zoekterm.</p><nav class="pagination" aria-label="Meer producten">{pagination}</nav><a class="text-link" href="{BASE+path}">Volledig aanbod op de oorspronkelijke webshop</a></section>'

def product(path):
 s=PAGES[path];root=s.select_one('div.product');name=text(s.select_one('h1'));images=s.select('.woocommerce-product-gallery img,.wp-block-woocommerce-product-image-gallery img')
 summary=s.select_one('.summary,.woocommerce-product-details__short-description,.wp-block-post-excerpt');price=s.select_one('.wp-block-woocommerce-product-price,.summary .price');desc=s.select_one('#tab-description');additional=s.select_one('#tab-additional_information')
 audio='<audio controls preload="none" aria-label="Audiofragment Versterk je intuïtie"><source src="/assets/versterk-je-intuitie.mp3" type="audio/mpeg"></audio>' if s.select_one('audio') else ''
 gallery=''.join('<button class="photo-expand" type="button" aria-label="Productfoto vergroten">'+img(i)+'</button>' for i in images)
 return intro(name,'Webshop')+f'<section class="wrap product-detail"><div class="product-gallery">{gallery}</div><div class="prose"><p class="eyebrow">Productinformatie uit de oorspronkelijke webshop</p>{f"<p class=price>{e(text(price))}</p>" if price else ""}{atoms(summary) if summary else ""}<p class="form-notice">Dit is een webshoppreview. Actuele voorraad, bestellen en afrekenen vind je op de oorspronkelijke website.</p><a class="button" href="{BASE+path}">Bekijk in de oorspronkelijke webshop</a></div></section><section class="wrap product-description prose">{atoms(desc) if desc else ""}{atoms(additional) if additional else ""}{audio if not (desc and desc.select_one("audio")) else ""}</section>'


for path,s in PAGES.items():
 name=text(s.select_one('h1')) or next((n for p,n in NAV if p==path),'Wilma Buchly')
 if path=='/':body=home();name='Luisteren voorbij je denken'
 elif path=='/contact/':body=contact()
 elif path=='/blog/' or path.startswith('/blog/page/'):
  body=intro('Inzichten om bij stil te staan','Het blog','Over energie, persoonlijke groei en de verbinding met jezelf')+'<section class="wrap journal"><div class="filterbar"><label>Zoek een artikel<input type="search" id="filter" placeholder="Zoek op onderwerp"></label><p id="result-count" role="status"></p></div><div class="blog-grid filter-grid">'+blog_cards(blog_entries())+'</div><p class="no-results" hidden>Geen artikelen gevonden. Probeer een andere zoekterm.</p></section>'
 elif path=='/winkel/' or path.startswith('/product-categorie/'):body=catalog(path)
 elif path.startswith('/product/'):body=product(path)
 else:
  kicker='Wilma Buchly';h2=s.select_one('h2');sub=text(h2) if h2 else ''
  body=intro(name,kicker,sub)+''.join(chapter(x,i) for i,x in enumerate(source_sections(path)))
 write(path,name.replace('.','').replace('…',''),body)
for name in ['styles.css','app.js']:shutil.copy(ROOT/'src'/name,DIST/name)
(DIST/'robots.txt').write_text('User-agent: *\nDisallow: /\n')
(DIST/'404.html').write_text(shell('/404/','Pagina niet gevonden',intro('Deze pagina is er niet')+'<div class="wrap missing"><a class="button" href="/">Terug naar de homepage</a></div>'))
print(f'Built {len(PAGES)} pages')

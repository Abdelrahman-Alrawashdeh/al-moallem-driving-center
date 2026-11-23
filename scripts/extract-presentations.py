"""Read only OOXML slide content, image relationships and notes from user decks."""
import json,re,zipfile,hashlib
from pathlib import Path
from xml.etree import ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main'}
out=ROOT/'content/presentations';out.mkdir(exist_ok=True)
decks=[]
for index,path in enumerate(sorted(ROOT.glob('*.pptx')),1):
 with zipfile.ZipFile(path) as z:
  slides=[]
  names=sorted([n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)],key=lambda s:int(re.search(r'slide(\d+)',s)[1]))
  for name in names:
   xml=E.fromstring(z.read(name));number=int(re.search(r'slide(\d+)',name)[1]);shapes=[]
   for sp in xml.findall('.//p:sp',NS):
    paragraphs=[]
    for para in sp.findall('.//a:p',NS):
     text=''.join(t.text or '' for t in para.findall('.//a:t',NS)).strip()
     if text:paragraphs.append(text)
    if paragraphs:
     shapes.append({'text':'\n'.join(paragraphs),'colors':list(dict.fromkeys(c.get('val') for c in sp.findall('.//a:srgbClr',NS))),'xml':E.tostring(sp,encoding='unicode')})
   note=f'ppt/notesSlides/notesSlide{number}.xml'
   notes=' '.join(t.text or '' for t in E.fromstring(z.read(note)).findall('.//a:t',NS)) if note in z.namelist() else ''
   slides.append({'number':number,'text':'\n'.join(s['text'] for s in shapes),'shapes':shapes,'notes':notes,'images':len(xml.findall('.//p:pic',NS))})
  deck={'id':f'material-{index:02}','title':path.stem.replace('ـ',''),'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'slides':slides}
  decks.append(deck)
(out/'extracted.json').write_text(json.dumps(decks,ensure_ascii=False,indent=2),encoding='utf8')
(out/'text-review.txt').write_text('\n\n'.join(f"=== {d['id']} {d['title']} | SLIDE {s['number']} ===\n{s['text']}\nNOTES: {s['notes']}" for d in decks for s in d['slides']),encoding='utf8')
print([(d['id'],d['title'],len(d['slides'])) for d in decks])

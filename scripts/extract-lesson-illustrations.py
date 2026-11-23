"""Extract original embedded pictures; no redraws and no answer text from slides."""
import json,zipfile,posixpath,hashlib
from pathlib import Path
from xml.etree import ElementTree as E
ROOT=Path(__file__).resolve().parents[1]
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main','p':'http://schemas.openxmlformats.org/presentationml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
decks=json.loads((ROOT/'content/presentations/extracted.json').read_text(encoding='utf8'))
out=ROOT/'public/assets/materials/illustrations';out.mkdir(parents=True,exist_ok=True)
selected={}
for line in (ROOT/'content/presentations/new-questions.txt').read_text(encoding='utf8').splitlines():
 if not line or line.startswith('#'):continue
 fields=line.split('|')
 if fields[-1]:selected.setdefault('material-'+fields[0],set()).add(int(fields[-1]))
manifest=[]
for d in decks:
 if d['id'] not in selected:continue
 with zipfile.ZipFile(ROOT/d['file']) as z:
  for n in sorted(selected[d['id']]):
   x=E.fromstring(z.read(f'ppt/slides/slide{n}.xml'))
   rels={r.get('Id'):r.get('Target') for r in E.fromstring(z.read(f'ppt/slides/_rels/slide{n}.xml.rels'))}
   pics=[]
   for pic in x.findall('.//p:pic',NS):
    blip=pic.find('.//a:blip',NS);extent=pic.find('.//a:xfrm/a:ext',NS)
    if blip is None or extent is None:continue
    rid=blip.get('{'+NS['r']+'}embed');target=posixpath.normpath('ppt/slides/'+rels[rid]);area=int(extent.get('cx'))*int(extent.get('cy'))
    pics.append((area,target))
   if not pics:continue
   target=max(pics)[1];payload=z.read(target);suffix=Path(target).suffix.lower();name=f'{d["id"]}-{n:03}{suffix}'
   (out/name).write_bytes(payload)
   manifest.append({'material':d['id'],'slide':n,'image':'/assets/materials/illustrations/'+name,'sha256':hashlib.sha256(payload).hexdigest()})
(ROOT/'content/presentations/illustrations.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print('Extracted',len(manifest),'original illustrations:',{Path(q['image']).suffix for q in manifest})

import json,re,hashlib
from pathlib import Path
from xml.etree import ElementTree as E
from difflib import SequenceMatcher
ROOT=Path(__file__).resolve().parents[1]
def norm(s):
 s=s.replace('ـ','').replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ة','ه').replace('ى','ي')
 return re.sub(r'[^\u0621-\u064a0-9]','',s)
decks=json.loads((ROOT/'content/presentations/extracted.json').read_text(encoding='utf8'))
bank=json.loads((ROOT/'public/data/question-bank.json').read_text(encoding='utf8'))['questions']
NS={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
questions=[]
for slide in decks[3]['slides']:
 if slide['number']>29:continue
 for shape in slide['shapes']:
  current=None
  for p in E.fromstring(shape['xml']).findall('.//a:p',NS):
   text=''.join(t.text or '' for t in p.findall('.//a:t',NS)).strip()
   if not text:continue
   match=re.match(r'^(\d+)\s*[-–]\s*(.+)',text)
   if match:
    current={'number':int(match[1]),'slide':slide['number'],'text':match[2],'options':[],'unbulleted':[]};questions.append(current)
   elif current:
    if len(current['options'])<6:
     current['options'].append(text)
     if p.find('a:pPr/a:buChar',NS) is None:current['unbulleted'].append(len(current['options'])-1)
for q in questions:
 sig=norm(q['text'])
 ranked=sorted(((SequenceMatcher(None,sig,norm(b['text']),autojunk=False).ratio(),b) for b in bank if not b.get('image')),key=lambda r:r[0],reverse=True)
 q['closest']=[{'score':round(score,3),'id':b['id'],'text':b['text']} for score,b in ranked[:2]]
 q['candidateAnswer']=q['unbulleted'][0] if len(q['unbulleted'])==1 else None
(ROOT/'content/presentations/question-candidates.json').write_text(json.dumps(questions,ensure_ascii=False,indent=2),encoding='utf8')
(ROOT/'content/presentations/question-audit.txt').write_text('\n\n'.join(f"Q{q['number']} slide{q['slide']} match {q['closest'][0]}\n{q['text']}\n"+'\n'.join(f"{i}. {x}" for i,x in enumerate(q['options']))+f"\nCandidate only: {q['candidateAnswer']}" for q in questions),encoding='utf8')
print('Numbered question candidates:',len(questions),'Likely existing (>= .82):',sum(q['closest'][0]['score']>=.82 for q in questions))
# Existing bank: identical normalized wording, answer and image must not be published twice.
groups={}
for q in bank:
 image=q.get('image','')
 if image:image=hashlib.sha256((ROOT/('public'+image)).read_bytes()).hexdigest()
 key=(norm(q['text']),image)
 groups.setdefault(key,[]).append(q['id'])
print('Exact duplicate groups:',[ids for ids in groups.values() if len(ids)>1])

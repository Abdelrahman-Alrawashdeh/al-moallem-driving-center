import json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def normalized(s):
 s=s.replace('ـ','').replace('أ','ا').replace('إ','ا').replace('آ','ا').replace('ة','ه').replace('ى','ي')
 return re.sub(r'[^\u0621-\u064a0-9]','',s)
def integrate_presentations(questions):
 decks=json.loads((ROOT/'content/presentations/extracted.json').read_text(encoding='utf8'))
 illustrations=json.loads((ROOT/'content/presentations/illustrations.json').read_text(encoding='utf8'))
 images={(q['material'],q['slide']):q['image'] for q in illustrations}
 for q in questions:
  materials=[]
  if q['topic']=='signals' or q['id'] in ['general-052','general-309','general-312']:materials.append('material-01')
  if 'مسافة' in q['text'] and ('cars' in q['categories'] or 'heavy' in q['categories']):materials.append('material-02')
  if q['id'] in ['general-333','general-334','general-337','general-338','general-341','general-343','general-344','general-347','general-348','general-354','general-355','general-361']:materials.append('material-03')
  if 'cars' in q['categories']:materials.append('material-04')
  if 'signs' in q['categories']:materials.append('material-05')
  if q['topic']=='heavy-rules' and 'رخص' in q['text']:materials.append('material-06')
  if q['topic']=='priority':materials.append('material-07')
  if q['id'] in ['general-000','general-001','general-002','general-003','general-004','general-005','general-006','general-007','general-053','general-467']:materials.append('material-08')
  q['materials']=materials
 for i,line in enumerate((ROOT/'content/presentations/new-questions.txt').read_text(encoding='utf8').splitlines()):
  if not line or line.startswith('#'):continue
  material,slide,topic,categories,text,correct,wrong1,wrong2,explanation,picture=line.split('|')
  material='material-'+material;slide=int(slide);deck=next(d for d in decks if d['id']==material)
  options=[correct,wrong1,wrong2];shift=i%3;options=options[shift:]+options[:shift]
  source={'title':deck['title'],'kind':'provided-pptx','page':slide,'slide':slide,'material':material,'localUrl':f'/materials.html?material={material}&slide={slide}'}
  if material=='material-06':source['verificationUrl']='https://www.dvld.gov.jo/Ar/Modules/Faq'
  if material=='material-08':source['verificationUrl']='https://www.fda.gov/consumers/consumer-updates/some-medicines-and-driving-dont-mix' if slide==9 else 'https://www.nhtsa.gov/risky-driving/drowsy-driving'
  q={'id':f'ppt-{i:03}','text':text,'options':options,'answer':options.index(correct),'categories':categories.split(','),'topic':topic,'source':source,'explanation':explanation,'materials':[material]}
  if picture:q['image']=images[(material,int(picture))]
  questions.append(q)
 # A single canonical record can belong to several categories and lessons.
 groups=json.loads((ROOT/'content/presentations/duplicate-groups.json').read_text(encoding='utf8'))
 indexed={q['id']:q for q in questions};removed=set();report=[]
 for keep,duplicates in groups.items():
  canonical=indexed[keep]
  for duplicate in duplicates:
   other=indexed[duplicate];removed.add(duplicate)
   canonical['categories']=list(dict.fromkeys(canonical['categories']+other['categories']))
   canonical['materials']=list(dict.fromkeys(canonical['materials']+other['materials']))
   canonical.setdefault('additionalSources',[]).append(other['source'])
   canonical.setdefault('equivalentIds',[]).append(duplicate)
   report.append({'removed':duplicate,'canonical':keep,'reason':'نفس السؤال أو إعادة صياغة/نفي للمعلومة نفسها، بعد مراجعة بشرية للمحتوى.'})
 questions[:]=[q for q in questions if q['id'] not in removed]
 # Combine the two complementary versions rather than repeating their stems.
 indexed['general-027']['options']=['حمولة المركبة وحالة الطريق والإطارات','حالة الفرامل وزمن استجابة السائق','تصميم المركبة','جميع ما ذكر']
 indexed['general-040']['options']=['حمل الأوزان وامتصاص الصدمات','نقل قوى الدفع والفرملة إلى الطريق','تغيير اتجاه الحركة والمحافظة عليه','جميع ما ذكر']
 for qid in ['general-027','general-040']:indexed[qid]['source']['kind']='adapted'
 for q in questions:
  replacements=[('الرتكاب','لارتكاب'),('باختالف','باختلاف'),('للداللة','للدلالة'),('خالل','خلال'),('مالبس','ملابس'),('أم ال','أم لا'),('ال تفترض','لا تفترض'),('المرك:بات','المركبات'),('من :الاجهزة','من الأجهزة'),('اح د','أحد'),('احد ى','إحدى')]
  def clean(t):
   for a,b in replacements:t=t.replace(a,b)
   return t
  q['text']=clean(q['text']);q['options']=[clean(o) for o in q['options']]
  if q['explanation'].startswith('الإجابة المعتمدة في الكتاب:'):q['explanation']='الإجابة: '+q['options'][q['answer']]+'.'
 seen={}
 for q in questions:
  image=q.get('image','')
  if image:image=hashlib.sha256((ROOT/('public'+image)).read_bytes()).hexdigest()
  key=(normalized(q['text']),image)
  assert key not in seen,('Duplicate question',seen.get(key),q['id'])
  seen[key]=q['id']
 (ROOT/'content/presentations/merged-duplicates.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
 return questions

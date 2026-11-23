"""Document corrections separately from source captures; never invent source keys."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
REFERENCES={
 'energy':('NASA Glenn — Conservation of energy','https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/conservation-of-energy/'),
 'registration':('بوابة البيانات الحكومية — نظام تسجيل وترخيص المركبات','https://opendata.gov.jo/dataset/MIGRATED-759-2020/resource/80f44b85-323e-41b3-a175-362fcbaadcba/download/-104-2008.pdf'),
 'psd-traffic':('مديرية الأمن العام — منهاج السير التأسيسية','https://psd.gov.jo/media/3rzj2s1k/السير-التأسيسية.pdf'),
 'psd-heavy':('مديرية الأمن العام — مدربي آليات الفئة الخامسة','https://psd.gov.jo/media/zmedfwje/مدربي-اليات-الفئة-الخامسة.pdf'),
 'equipment':('الجريدة الرسمية — تعليمات تجهيز المركبات لسنة 2020','https://opendata.gov.jo/dataset/MIGRATED-759-2020/resource/66de58ff-d986-4d19-963f-e1ca616877bc/download/-2020.pdf'),
 'breakdown':('The Highway Code — breakdowns and incidents','https://www.gov.uk/guidance/the-highway-code/breakdowns-and-incidents-274-to-287'),
 'michelin':('Michelin — Truck Tire Service Manual','https://www.michelinb2b.com/wps/b2bcontent/ZIP/PLNA/Michelin_Truck_Tire_Service_Manual.pdf'),
 'toyota':('Toyota — التعامل مع التسارع غير المقصود','https://pressroom.toyota.com/toyota-prius-vehicle-throttle-and-brake-systems-myth-vs-fact/'),
 'ford-snow':('Ford — القيادة في الثلج والجليد','https://www.fordservicecontent.com/Ford_Content/vdirsnet/OwnerManual/Home/Content?ProcUid=G2136989&Uid=G2136982&buildtype=web&countryCode=USA&div=f&languageCode=en&moidRef=G2126344&userMarket=USA&vFilteringEnabled=False&variantid=7430'),
 'toyota-manual':('Toyota — دليل المالك: توقف المحرك أثناء القيادة','https://techinfo.toyota.com/t3Portal/document/om-s/OM04041U/pdf/OM04041U.pdf'),
}
MERGED={'form-3-q49':'heavy-010','form-3-q53':'heavy-064','form-3-q54':'heavy-064'}

def correct_source_records(records):
 indexed={q['id']:q for q in records}
 # Qualify legal scope and make choices mutually exclusive without changing source images.
 changes={
 'form-3-q30':{'text':'أي مما يلي عيب ظاهر في إطار المركبة الثقيلة؟','options':['وجود نقشة مداس سليمة','سطح مطاطي سليم دون تشققات','وجود أسلاك بارزة من جدران الإطار','مطابقة المقاس لتوصية المصنع']},
 'form-4-q39':{'text':'وفق تعليمات تجهيز المركبات الأردنية لسنة 2020، تجهز سيارات الركوب المتوسطة التي يزيد عدد ركابها على 20 بمن فيهم السائق، والحافلات ومركبات الشحن التي يزيد وزنها الإجمالي على 8 أطنان، بفرملة محرك أو مخفض سرعة أو نظام يفي بالغرض.'},
 'form-4-q41':{'text':'وفق المادة 5 من تعليمات تجهيز المركبات الأردنية لسنة 2020، ما الحد الأعلى لكثافة دخان عادم محرك الديزل؟'},
 }
 for qid,change in changes.items():
  q=indexed[qid];q['originalText']=q['text'];q['originalOptions']=q['options'][:];q.update(change);q['revisionNote']='توضيح نطاق السؤال وإزالة الخيارات الملتبسة؛ الصورة الأصلية محفوظة في سجل المراجعة.'

def additional_answers():
 return (ROOT/'content/heavy-completion-answers.txt').read_text(encoding='utf8').splitlines()

def merge_completed_questions(questions):
 indexed={q['id']:q for q in questions}
 audit=json.loads((ROOT/'content/heavy-original-review.json').read_text(encoding='utf8'))
 for record in audit:
  if record['id'] in MERGED:
   q=indexed[MERGED[record['id']]]
   q.setdefault('equivalentIds',[]).append('heavy-'+record['id'])
   q.setdefault('additionalSources',[]).append({'title':'النموذج الأصلي للثقيلة — موضع '+record['id'],'kind':'provided-google-form','capture':record['image']})
 groups={'heavy-016':['heavy-form-3-q30'],'heavy-form-3-q03':['heavy-form-4-q29'],'heavy-form-4-q05':['heavy-047']}
 removed=set()
 for keep,duplicates in groups.items():
  q=indexed[keep]
  for other in duplicates:
   q.setdefault('equivalentIds',[]).append(other);q.setdefault('additionalSources',[]).append(indexed[other]['source']);removed.add(other)
 questions[:]=[q for q in questions if q['id'] not in removed]
 for r in audit:
  published='heavy-'+r['id']
  for q in questions:
   if published==q['id'] or published in q.get('equivalentIds',[]):r['publishedId']=q['id'];break
  if r.get('duplicateOf'):
   canonical=next(a for a in audit if a['id']==r['duplicateOf']);r['publishedId']=canonical.get('publishedId','heavy-'+r['duplicateOf'])
 (ROOT/'content/heavy-original-review.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')

def revised_questions(indexed,base):
 result={}
 for line in (ROOT/'content/heavy-revised-questions.txt').read_text(encoding='utf8').splitlines():
  if not line or line.startswith('#'):continue
  short,ref,section,topic,text,correct,wrong1,wrong2,explanation=line.split('|')
  form,number=short.split('-');qid=f'form-{form}-q{number}';original=indexed[qid]
  options=[correct,wrong1,wrong2];shift=int(number)%3;options=options[shift:]+options[:shift]
  source={k:v for k,v in base[ref].items() if k in ['title','url']};source.update(section=section,checkedAt='2026-09-25',kind='adapted-web')
  result[qid]={'id':'heavy-'+qid,'text':text,'options':options,'answer':options.index(correct),'categories':['heavy'],'topic':topic,'explanation':explanation,'source':source,'origin':{'kind':'provided-google-form','form':int(form),'question':int(number),'capture':original['image'],'answerBasis':'revised-independent-reference-review','revisionNote':'سؤال مصحح من موضوع الأصل؛ تغيّرت الصياغة أو الخيارات لإزالة الالتباس. لا يمثل مفتاح النموذج الأصلي.'}}
 return result

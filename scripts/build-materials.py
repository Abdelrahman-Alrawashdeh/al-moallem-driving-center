"""Publish reviewed learning sections; archive all source slides privately."""
import json,re
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
decks=json.loads((ROOT/'content/presentations/extracted.json').read_text(encoding='utf8'))
bank=json.loads((ROOT/'public/data/question-bank.json').read_text(encoding='utf8'))
selected={
 '01':[2,3,7,8,9,10,11,12,13,14,15,17,18,19,20,21,22],
 '02':[2,3,7,9,10,12,14,15,16,17,18,19],
 '03':[n for n in range(3,24) if n!=6],
 '04':[1,2,5,6,7,8,10,11,12],
 '05':list(range(2,38)),
 '06':list(range(4,13)),
 '07':list(range(2,19))+[20,21,22,23,25,28,29,30,31,32,33,34],
 '08':list(range(2,11)),
}
descriptions=[
 'اقرأ إشارات المركبة والضوء وشرطي المرور، واتخذ القرار المناسب.',
 'افهم مسافة التوقف والتتابع، واضبط سرعتك حسب ظروف الطريق.',
 'تعرّف إلى المسارب الأساسية والإضافية، وخطوات الانتقال والاندماج.',
 'راجع الأسئلة الأساسية، ثم اختبر فهمك داخل بنك التدريب دون تكرار نسخها.',
 'دليل بصري للمنع والإلزام والتحذير والإرشاد وأشكال الشواخص.',
 'ملخص لتصنيف الرخص، مع تحديث المعلومات المتعارضة مع مرجع الترخيص.',
 'افهم قواعد التقاطعات وتدرّب على مواقف مصوّرة خطوة بخطوة.',
 'استعد للقيادة بانتباه، وتعرّف إلى أثر التعب والتشتت والأدوية.',
]
icons=['signals','speed','lanes','questions','signs','license','priority','health']

# Covers, section dividers and author contact slides are retained in the source archive.
archive_only={'01':{1,16,23,24,30},'02':{1,20},'03':{1,2,24},'04':{73},'05':{1,38},'06':{1,3,13},'07':{1,19,45},'08':{1,12}}
for d in decks:selected[d['id'][-2:]]=[s['number'] for s in d['slides'] if s['number'] not in archive_only[d['id'][-2:]]]
overrides={
 ('01',18):('الضوء الأصفر','استعد للتوقف عند ظهور الأصفر بعد الأخضر، وتوقف إذا أمكن ذلك بأمان قبل خط التوقف. لا تعتمد على مدة ثابتة للضوء الأصفر ولا تسرع للحاق بالإشارة.'),
 ('02',2):('السرعة التصميمية','تؤخذ سرعة تصميمية في الحسبان عند تصميم الطريق ومنحنياته. لكنها ليست ضمانًا للسلامة في كل الظروف ولا بديلًا عن السرعة المحددة بالشواخص. خفف السرعة أكثر إذا تطلبت الرؤية أو الطقس أو حالة الطريق ذلك.'),
 ('02',16):('متى تزيد مسافة الأمان؟','زد الفاصل عن المركبة الأمامية في المطر وضعف الرؤية. أما النعاس والمرض الذي يؤثر في القيادة أو الفرامل والإطارات غير السليمة، فلا تعالجها بزيادة الفاصل فقط: توقف بأمان، واسترح أو أصلح العطل قبل استئناف القيادة.'),
 ('03',11):('المسرب الأيسر','يُستخدم للتجاوز أو الاتجاه المسموح به وفق الشواخص والعلامات. القيادة بالسرعة القصوى لا تمنح حق احتلاله أو تجاوز الحد المسموح. اختر المسرب وفق تنظيم الطريق وانتقل إليه بعد التأكد من الأمان.'),
 ('06',4):('الفئة الأولى (1)','تخص قيادة الدراجة الآلية بحسب تصنيف إدارة الترخيص.'),
 ('06',5):('الفئة الأولى (2)','تخص قيادة الدراجة الآلية من نوع سكوتر بحسب تصنيف إدارة الترخيص.'),
 ('06',6):('الفئة الثانية','تتضمن فرعين: قيادة المركبة الإنشائية، وقيادة المركبة الزراعية.'),
 ('06',7):('الفئة الثالثة','تتضمن فرعين للمبدل اليدوي والأوتوماتيكي، وتشمل مركبات الركوب الخصوصية والتأجير والمركبات الخصوصية حتى خمسة أطنان وفق التصنيف الرسمي.'),
 ('06',8):('الفئة الرابعة','تخص سيارة الركوب العمومية أو مركبة لا يتجاوز وزنها الإجمالي 7.5 طن. شروط منح الرخصة منفصلة عن تعريف الفئة.'),
 ('06',9):('الفئة الخامسة','تخص الحافلة المتوسطة أو المركبة التي يزيد وزنها الإجمالي على 7.5 طن. استُبدل التعريف القديم في العرض بهذا الملخص من إدارة الترخيص.'),
 ('06',10):('الفئة السادسة (2)','تخص قيادة الحافلة. راجع إدارة الترخيص لشروط الحصول عليها.'),
 ('06',11):('الفئة السادسة (1)','تخص قيادة قاطرة ومقطورة أو رأس قاطر ونصف مقطورة.'),
 ('06',12):('الفئة السابعة','تخص قيادة مركبة ذوي الإعاقة بحسب التصنيف الرسمي.'),
 ('08',5):('استعد للرحلة قبل أن تتعب','احصل على نوم كافٍ قبل الرحلة. خطط للاستراحات وتوقف في مكان آمن إذا شعرت بالنعاس. القهوة وفتح النوافذ لا يعوضان نقص النوم.'),
 ('08',7):('تأثير الكحول في القيادة','الكحول يضعف التركيز وتقدير السرعة والمسافات وسرعة الاستجابة. قد يمنح ثقة زائفة ويزيد المخاطرة والنعاس؛ تجنب القيادة تحت تأثيره.'),
 ('08',9):('اقرأ تحذير الدواء','بعض الأدوية قد تسبب النعاس أو ضعف الانتباه. اتبع التحذيرات واسأل الطبيب أو الصيدلي عن تأثير دوائك في القيادة. لا تغيّر علاجًا موصوفًا من تلقاء نفسك.'),
}
links={
 '06':{'title':'إدارة ترخيص السواقين والمركبات — تصنيف الرخص','url':'https://www.dvld.gov.jo/Ar/Modules/Faq'},
 '08':{'title':'FDA — الأدوية والقيادة','url':'https://www.fda.gov/consumers/consumer-updates/some-medicines-and-driving-dont-mix'},
}
for line in (ROOT/'content/presentations/completed-sections.txt').read_text(encoding='utf8').splitlines():
 if not line or line.startswith('#'):continue
 short,n,title,body=line.split('|');overrides[(short,int(n))]=(title,body)
traffic_ref={'title':'مديرية الأمن العام — منهاج السير','url':'https://psd.gov.jo/media/3rzj2s1k/السير-التأسيسية.pdf'}
output=[];audit=[]
for i,d in enumerate(decks):
 short=d['id'][-2:];sections=[]
 for slide in d['slides']:
  n=slide['number'];included=n in selected[short]
  audit.append({'material':d['id'],'slide':n,'status':'updated-text' if (short,n) in overrides else 'published' if included else 'archived-structural','reason':'نص تعليمي مصحح يحل محل الصياغة القديمة، وليس اعتمادًا لمفتاحها.' if (short,n) in overrides else '' if included else 'غلاف أو فاصل أو صورة تقديمية أو بيانات المؤلف؛ محفوظ في الأصل ومعلومات النسب معروضة في المادة.'})
  if not included:continue
  lines=[re.sub(r'\s+',' ',line).strip() for line in slide['text'].splitlines() if line.strip()]
  title=next((x for x in lines if len(x)>4 and len(x)<85),d['title'])
  item={'number':n,'title':title,'paragraphs':lines,'sourceSlide':n}
  if (short,n) in overrides:
   item['title'],body=overrides[(short,n)];item['paragraphs']=[body];item['reviewNote']='ملخص مراجع؛ حُذفت الصياغة القديمة أو غير الدقيقة من العرض التعليمي.'
   if short in links:item['reference']=links[short]
   if short=='06' and n==2:item['reference']=traffic_ref
   if short in ['01','02','03','07']:item['reference']=traffic_ref
   if short=='04' and n in [13,14,15,16,17,18,19,52,53,57,58,70]:item['reference']=traffic_ref
   if short=='08' and n==5:item['reference']={'title':'NHTSA — القيادة والنعاس','url':'https://www.nhtsa.gov/risky-driving/drowsy-driving'}
   if short=='08' and n==11:item['reference']={'title':'NHTSA — تشتت الانتباه','url':'https://www.nhtsa.gov/risky-driving/distracted-driving'}
  else:
   folder=ROOT/'public/assets/materials'/d['id'];folder.mkdir(parents=True,exist_ok=True)
   original=ROOT/f'content/presentations/rendered/{d["id"]}/slide-{n:03}.png'
   target=folder/f'slide-{n:03}.webp'
   if not target.exists() or original.stat().st_mtime>target.stat().st_mtime:
    image=Image.open(original).convert('RGB');image.save(target,quality=88,method=6)
   item['image']=f'/assets/materials/{d["id"]}/slide-{n:03}.webp'
  if short=='02':item.setdefault('note','المسافات تتغير مع الظروف. قاعدة الثانيتين تخص الظروف الجيدة؛ لا تعوّض إصلاح العيوب أو الراحة عند النعاس.')
  if short=='07':item.setdefault('note','تُقرأ القاعدة ضمن الموقف وشواخصه وإشاراته. تعليمات شرطي المرور والتنظيم القائم مقدمة على القواعد العامة، وتجنب التصادم واجب حتى عند امتلاك الأولوية.')
  sections.append(item)
 related=[q['id'] for q in bank['questions'] if d['id'] in q.get('materials',[])]
 output.append({'id':d['id'],'title':d['title'],'description':descriptions[i],'icon':icons[i],'sourceFile':d['file'],'originalSlides':len(d['slides']),'sections':sections,'questionIds':related,'author':'المادة الأصلية من إعداد المدرب نضال عدنان أبو العافية، مقدمة ضمن ملفات المركز.'})
used={s['image'] for m in output for s in m['sections'] if s.get('image')}
asset_root=(ROOT/'public/assets/materials').resolve()
for stale in asset_root.glob('material-*/slide-*.webp'):
 if '/'+stale.relative_to(ROOT/'public').as_posix() not in used:
  assert stale.resolve().is_relative_to(asset_root)
  stale.unlink()
(ROOT/'public/data/materials.json').write_text(json.dumps({'version':bank['version'],'materials':output},ensure_ascii=False,indent=2),encoding='utf8')
(ROOT/'content/presentations/slide-review.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf8')
print('Materials:',len(output),'Reviewed sections:',sum(len(d['sections']) for d in output),'Archived source slides:',len(audit))

import pathlib,json,re,hashlib
from heavy_bank import build_heavy_questions
from heavy_original_bank import build_original_heavy_questions
from presentation_bank import integrate_presentations
root=pathlib.Path('.')
raw=json.loads((root/'content/sources/extracted-bank.json').read_text(encoding='utf8'))
corrections=json.loads((root/'scripts/general-corrections.json').read_text(encoding='utf8'))
def tidy(s):
 s=re.sub(r'([\u0621-\u064a])\.([\u0621-\u064a])',r'\1\2',s)
 for a,b in [('ال شيء','لا شيء'),('الشيء','لا شيء'),('الشئ','لا شيء'),('ال يوجد','لا يوجد'),('ال يسمح','لا يسمح'),('ال تحاول','لا تحاول'),('ال يت','لا يت'),('ن عم','نعم'),('أ ثناء','أثناء'),('ال.خمول','الخمول'),('السالمة','السلامة'),('الحافالت','الحافلات'),('سالمة','سلامة'),('عالمة','علامة'),('عالمات','علامات'),('إرتكاب','ارتكاب'),('ت قاطع','تقاطع'),('الاحضر','الأخضر'),('ت جنب','تجنب'),('عب ور','عبور'),('التح ديد','التحديد'),('الرئي سي','الرئيسي')]:s=s.replace(a,b)
 return re.sub(r'\s+',' ',s).strip(' .:')
selected=[0,1,2,3,4,5,6,7,8,19,20,21,23,25,26,27,28,29,30,31,32,34,36,37,38,40,41,44,46,50,52,53,108,253,254,255,256,257,258,260,261,291,292,293,295,298,301,302,304,305,306,307,308,309,312,316,317,318,319]
signs=[i for i,q in enumerate(raw) if q['valid'] and q.get('image') and 61<=q['page']<=123 and i not in [191,193]]
signs=[56,59,63,70,71,74,75,80,84,86,88,102,103,109,116]+signs
selected += [333,334,337,338,341,343,344,347,348,354,355,361,403,404,405,457,459,460,461,463,464,466,467,469,470,471,472,473,474,475,478,480,482,484,489,492,493,494,495,496,498,500,503,504,506,522,525,527,528,530,533,534,556,562,565,568]
questions=[]
for i in sorted(set(selected+signs)):
 q=raw[i]
 assert q['valid'],i
 text=tidy(q['text']);options=[tidy(x) for x in q['options']];answer=q['answer']
 if len(options)==3 and options[-2:]==['نعم','لا']:
  text+=' '+options[0];options=options[1:];answer-=1
 if i in signs and 61<=q['page']<=117:text='ما معنى الشاخصة الظاهرة في الصورة؟'
 if i==2:text='أي تصرف يساعد على تقليل شرود الذهن وخطر الحوادث أثناء القيادة؟'
 if i==21:text='هل يساعد استخدام حزام الأمان على تقليل شدة الإصابة مقارنة بعدم استخدامه؟'
 if i==23:text='يجب إعطاء راكبي الدراجات الهوائية مسافة أمان كافية عند الاقتراب منهم.'
 if i==25:text='عند تجاوز شاحنة أو حافلة، يجب تذكّر أنها أطول من السيارة وقد يستغرق تجاوزها وقتًا أطول.'
 if i==26:text='لتقليل خطر التصادم مع المركبات الثقيلة، لا تنافسها على المساحة نفسها واترك لها فراغًا كافيًا.'
 if i==29:text='تساعد قاعدة الثانيتين على ترك مسافة أمان في الظروف الجوية الجيدة وعلى السطح الجاف.'
 if i==30:text='يجب زيادة الفاصل الزمني ومسافة الأمان خلف المركبة الأمامية في الظروف الجوية السيئة.'
 if i==31:text='هل تكون مسافة التوقف أقل عندما يكون الطريق مبتلًا أو رطبًا؟'
 if i==32:text='هل تكون مسافة التوقف على الطريق الجاف أكبر منها على الطريق المبتل في الظروف المتشابهة؟'
 if i==34:text='هل تكون مسافة توقف الشاحنات والحافلات أقل من مسافة توقف المركبات الصغيرة؟'
 if i==50:text='استخدام حزام الأمان داخل المركبة';options=['خاص بالأردن فقط','خاص بالقيادة داخل المدن فقط','خاص بالطرق الخارجية فقط','منتشر في أنحاء العالم بما فيها الأردن']
 if i==53:text='هل تناول السوائل أثناء القيادة قد يشتت الانتباه ويزيد احتمال الاشتراك في حادث؟'
 if i==108:text='أين يمكن أن توضع إشارات المرور الضوئية؟'
 if i==305:text='هل ينبغي الإصرار على أخذ الأولوية إذا كانت هناك مركبات تعيق الطريق داخل التقاطع؟'
 if i==308:text='عند الاقتراب من تقاطع طرق، على السائق أن:'
 if i==312:text='عند ظهور الضوء الأحمر، يتوقف السائق قبل خط التوقف المخصص لذلك إن وجد.'
 if i==506:options=['للقطار','للمركبة'];text='عند معبر السكك الحديدية في الصورة، لمن تكون الأولوية؟'
 if i==471:text='هل يجوز فتح غطاء الرديتر عندما يكون المحرك ساخنًا؟'
 if i==472:text='يجب التأكد من إغلاق غطاء المحرك بإحكام قبل القيادة.'
 if i==474:text='يحوّل محرك الاحتراق الداخلي الطاقة الحرارية الناتجة عن احتراق الوقود إلى طاقة ميكانيكية.'
 if i==492:text='في ناقل الحركة الأوتوماتيكي، يرمز الحرف P إلى وضع الوقوف.'
 if i==493:text='في ناقل الحركة الأوتوماتيكي، يرمز الحرف R إلى الرجوع للخلف.'
 if i==494:text='في ناقل الحركة الأوتوماتيكي، يرمز الحرف D إلى القيادة للأمام.'
 if i==503:text='في الصورة، شخص كفيف يعبر الطريق. ما التصرف الصحيح للسائق؟'
 if i==504:text='في الصورة، شخص يستخدم كرسيًا متحركًا يعبر الطريق. ما التصرف الصحيح للسائق؟';options[2]='التوقف التام حتى ينتهي الشخص من العبور'
 if i in signs and 'تعن' in text and 'ما معنى' not in text:text=tidy(text)
 correction=corrections.get(str(i),{})
 text=correction.get('text',text);options=correction.get('options',options)
 item={'id':f'general-{i:03}','text':text,'options':options,'answer':answer,'categories':['signs','cars'] if i in signs else ['cars'],'source':q['source'],'explanation':f'الإجابة المعتمدة في الكتاب: {options[answer]}.'}
 if q.get('image'):item['image']=q['image']
 questions.append(item)
for n,line in enumerate((root/'scripts/bike-questions.txt').read_text(encoding='utf8').splitlines()):
 if not line.strip():continue
 page,text,correct,*wrong=line.split('|');options=[correct]+wrong;shift=n%len(options);options=options[shift:]+options[:shift];answer=options.index(correct)
 questions.append({'id':f'bike-{n+1:03}','text':text,'options':options,'answer':answer,'categories':['bike'],'source':{'title':'كتاب الدراجة النظري — المنهاج الخاص بسائقي الدراجات الآلية','page':int(page),'kind':'adapted'},'explanation':correct+'.'})
categories=[{'id':'signs','name':'الشواخص والإشارات','available':True,'description':'أسئلة مصوّرة من كتاب الأسئلة، بإجابات موثّقة من المصدر.'},{'id':'cars','name':'الثالثة والرابعة','available':True,'description':'تدريب على قواعد القيادة والسلامة والشواخص، مستند إلى كتاب الأسئلة المرفق.'},{'id':'bike','name':'الدراجات النارية','available':True,'description':'أسئلة مُعدّة من شرح كتاب الدراجة: التجهيزات، الفحص، الرؤية والقيادة الآمنة.'},{'id':'heavy','name':'الخامسة والسادسة','available':True,'description':'تدريب تخصصي: 45 سؤالًا عن الشاحنات والحافلات والحمولات والوصل، و15 سؤال شواخص وإشارات. مبادئ فنية موثقة؛ ليس نسخة من بنك الترخيص الرسمي.'}]
for q in questions:
 if 'signs' in q['categories']:q['categories'].append('heavy')
categories[-1]['description']='45 سؤالًا تخصصيًا من نماذج المركز والمراجع، و15 شواخص وإشارات، تشمل القيادة والحمولات والأبعاد والرخص. ليس نسخة من بنك الترخيص الرسمي.'
questions.extend(q for q in build_heavy_questions() if q['id'] not in ['heavy-073','heavy-074'])
questions.extend(build_original_heavy_questions())
topics=[{'id':key,'name':name} for key,name in [('signs','الشواخص المرورية'),('signals','الإشارات الضوئية'),('markings','الخطوط والعلامات الأرضية'),('priority','الأولويات والمواقف المصوّرة'),('behavior','السلوك والقيادة الآمنة'),('mechanics','الميكانيك وفحص المركبة'),('bike','قيادة الدراجات النارية'),('heavy-inspection','فحص المركبات الثقيلة'),('heavy-loading','توزيع الحمولة وتثبيتها'),('heavy-coupling','وصل المقطورات وفصلها'),('heavy-passengers','سلامة ركاب الحافلات')]]
topics.extend([{'id':'heavy-driving','name':'قيادة الثقيلة والظروف الجوية'},{'id':'heavy-rules','name':'فئات الرخص والأبعاد والأوزان'}])
for q in questions:
 if q['id'].startswith('heavy-'):continue
 i=int(q['id'].split('-')[1]);page=q['source']['page']
 if q['id'].startswith('bike-'):topic='bike'
 elif i>=501 and i<550:topic='priority'
 elif 469<=i<=500:topic='mechanics'
 elif 291<=i<=319:topic='priority'
 elif 118<=page<=123:topic='markings'
 elif 50<=page<=54 or i==108:topic='signals'
 elif 'signs' in q['categories'] or i>=550:topic='signs'
 else:topic='behavior'
 q['topic']=topic
integrate_presentations(questions)
from heavy_completion import merge_completed_questions
merge_completed_questions(questions)
for t in topics:t['count']=sum(q['topic']==t['id'] for q in questions)
for c in categories:
 c['poolSize']=sum(c['id'] in q['categories'] for q in questions)
 if c['available']:assert c['poolSize']>=60,(c['id'],c['poolSize'])
seen=set()
for q in questions:
 assert q['id'] not in seen;seen.add(q['id'])
 assert 2<=len(q['options'])<=4 and len(set(q['options']))==len(q['options']) and 0<=q['answer']<len(q['options']),q
payload=json.dumps({'categories':categories,'topics':topics,'questions':questions},ensure_ascii=False,sort_keys=True)
bank={'version':'2026-09-25-'+hashlib.sha256(payload.encode()).hexdigest()[:10],'categories':categories,'topics':topics,'questions':questions}
(root/'public/data').mkdir(exist_ok=True)
(root/'public/data/question-bank.json').write_text(json.dumps(bank,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'questions':len(questions),'categories':[(c['id'],c['poolSize']) for c in categories]},ensure_ascii=False))

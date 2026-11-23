"""Extract only questions with one explicitly coloured answer in the supplied PDF."""
import sys, pathlib, json, re, hashlib
sys.path.insert(0, str(pathlib.Path('.tools/pymupdf').resolve()))
import pymupdf
source=next(pathlib.Path('content/originals').glob('204*.pdf'))
doc=pymupdf.open(source)
out=pathlib.Path('content/sources');out.mkdir(parents=True,exist_ok=True)
images=pathlib.Path('public/assets/questions');images.mkdir(parents=True,exist_ok=True)
questions=[]; current=None
def clean(text):
    text=re.sub(r'\s+',' ',text).strip(' .:،-\u200f')
    for a,b in [('اإل','الإ'),('األ','الأ'),('اال','الا'),('إستخدام','استخدام'),('االرهاق','الإرهاق')]:text=text.replace(a,b)
    return text
def flush():
    global current
    if not current:return
    q=current;current=None
    q['text']=clean(' '.join(q.pop('parts')))
    for o in q['options']:o['text']=clean(' '.join(o.pop('parts')))
    marked=[i for i,o in enumerate(q['options']) if o.pop('marked')]
    q['valid']=len(marked)==1 and 2<=len(q['options'])<=4 and len(q['text'])>6 and all(o['text'] for o in q['options'])
    q['answer']=marked[0] if len(marked)==1 else None
    q['options']=[o['text'] for o in q['options']]
    questions.append(q)
for pageindex,page in enumerate(doc):
    blocks=page.get_text('dict')['blocks']
    for block in blocks:
        if block['type']!=0:continue
        spans=[s for l in block['lines'] for s in l['spans'] if s['text'].strip()]
        if not spans or block['bbox'][1]>770:continue
        texts=[s['text'].strip() for s in spans]
        if len(texts)>1 and re.fullmatch(r'\d{1,3}',texts[0]) and texts[1]=='.':
            flush();current={'id':f'book-p{pageindex+1}-q{texts[0]}','number':texts[0],'page':pageindex+1,'parts':texts[2:],'options':[],'start':block['bbox'][1],'firstOption':None,'endPage':pageindex+1}
        elif current and texts[0]=='-':
            if current['firstOption'] is None:current['firstOption']=[pageindex+1,block['bbox'][1]]
            current['options'].append({'parts':texts[1:],'marked':any(s['color'] in (16737792,16711680) for s in spans)})
            current['endPage']=pageindex+1
        elif current and not any('الجزء' in t for t in texts):
            if current['options']:
                current['options'][-1]['parts'].extend(texts)
                current['options'][-1]['marked']|=any(s['color'] in (16737792,16711680) for s in spans)
            else:current['parts'].extend(texts)
flush()
for q in questions:
    if not q['valid'] or not q['firstOption']:continue
    # Questions spanning pages are held for manual review, never auto-published.
    if q['page']!=q['endPage'] or q['firstOption'][0]!=q['page']:q['valid']=False;continue
    page=doc[q['page']-1]
    figures=[b for b in page.get_text('dict')['blocks'] if b['type']==1 and b['bbox'][1]>=q['start'] and b['bbox'][3]<=q['firstOption'][1]+2]
    if figures:
        rect=pymupdf.Rect(figures[0]['bbox'])
        for b in figures[1:]:rect|=pymupdf.Rect(b['bbox'])
        path=images/(q['id']+'.png')
        page.get_pixmap(matrix=pymupdf.Matrix(1.8,1.8),clip=rect).save(str(path))
        q['image']='/assets/questions/'+path.name
    elif any(w in q['text'] for w in ['شاخص','الصورة','بالشكل','المبين','الموضح','الإشارة','الاشارة']):
        q['valid']=False
    q['source']={'title':'أسئلة الفحص النظري للسواقة مع الإجابات','page':q['page'],'kind':'provided-pdf'}
(out/'extracted-bank.json').write_text(json.dumps(questions,ensure_ascii=False,indent=2),encoding='utf8')
valid=[q for q in questions if q['valid']]
print(json.dumps({'total':len(questions),'valid':len(valid),'withImage':sum('image' in q for q in valid)},ensure_ascii=False))
print(json.dumps([{k:q[k] for k in ['id','text','options','answer']} for q in valid[:15]],ensure_ascii=False,indent=2))

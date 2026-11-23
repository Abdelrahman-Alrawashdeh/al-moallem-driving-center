"""Only publish individually reviewed user-form questions; keep pending items private."""
import json, re, shutil
from heavy_completion import REFERENCES, MERGED, correct_source_records, additional_answers, revised_questions
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def build_original_heavy_questions():
    base=json.loads((ROOT/'content/heavy-sources.json').read_text(encoding='utf8'))
    extra={
      'weather': ('The Highway Code — adverse weather', 'https://www.gov.uk/guidance/the-highway-code/driving-in-adverse-weather-conditions-226-to-237'),
      'road': ('The Highway Code — using the road', 'https://www.gov.uk/guidance/the-highway-code/using-the-road-159-to-203'),
      'lighting': ('The Highway Code — lighting and vehicle control', 'https://www.gov.uk/guidance/the-highway-code/general-rules-techniques-and-advice-for-all-drivers-and-riders-103-to-158'),
      'dimensions': ('وزارة الأشغال العامة والإسكان — نظام الأبعاد والأوزان وقوة المحرك', 'https://www.mpwh.gov.jo/AR/ListDetails/الانظمة/65/4'),
      'tyres': ('NHTSA — TireWise', 'https://www.nhtsa.gov/vehicle-safety/tires'),
      'tanks': ('New York DMV — Tank Vehicles', 'https://dmv.ny.gov/brochure/cdl10sec08.pdf'),
      'lorries': ('DVSA — National standard for driving lorries', 'https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/377668/national-standard-for-driving-lorries.pdf'),
      'cdl': ('AAMVA — CDL manual, hosted by FMCSA', 'https://www.fmcsa.dot.gov/sites/fmcsa.dot.gov/files/docs/2005%20CDL%20Driver%20Manual%20-July%202014%20-%20FINAL.pdf'),
      'tipping': ('HSE — Tipping', 'https://www.hse.gov.uk/workplacetransport/information/tipping.htm'),
      'tachograph': ('GOV.UK — Tachographs', 'https://www.gov.uk/tachographs'),
      'limiter': ('GOV.UK — Speed limiters', 'https://www.gov.uk/speed-limits'),
    }
    for key,(title,url) in extra.items():
        base[key]={'title':title,'url':url}
    for key,(title,url) in REFERENCES.items():base[key]={'title':title,'url':url}
    records=json.loads((ROOT/'content/sources/heavy-originals/matched.json').read_text(encoding='utf8'))
    correct_source_records(records)
    # The supplied screenshot itself truncates the last distractor; complete its sentence,
    # keeping the answer and meaning unchanged, and retain the original capture in the audit.
    for item in records:
        if item['id']=='form-4-q28':
            item['options'][3]='تكرار الوميض (فلاش) للأنوار الأمامية عند المسير خلف مركبة أخرى.'
            item['transcriptionNote']='استكمال نهاية الخيار الرابع المبتورة في الصورة الأصلية؛ لا يغير الإجابة.'
    indexed={q['id']:q for q in records}
    reviewed={}
    for line in (ROOT/'content/heavy-original-answers.txt').read_text(encoding='utf8').splitlines()+additional_answers():
        if not line.strip() or line.startswith('#'):continue
        short,number,ref,section,topic,explanation=line.split('|')
        form,n=short.split('-');qid=f'form-{form}-q{n}'
        assert qid not in reviewed,qid
        original=indexed[qid]
        answer=int(number)-1
        assert 0<=answer<len(original['options'])
        evidence={k:v for k,v in base[ref].items() if k in ['title','url']}
        evidence.update(section=section,checkedAt='2026-09-25',kind='answer-reference')
        q={'id':'heavy-'+qid,'text':original['text'],'options':original['options'],'answer':answer,'categories':['heavy'],'topic':topic,'explanation':explanation,'source':evidence,'origin':{'kind':'provided-google-form','form':int(form),'question':int(n),'capture':original['image'],'answerBasis':'independent-reference-review'}}
        if original.get('revisionNote'):
            q['origin']['revisionNote']=original['revisionNote']
            q['source']['kind']='adapted-web'
        if qid=='form-4-q06':
            q['image']='/assets/questions/heavy/original-form-4-q06.png'
            q['imagePresentation']='original-question'
            shutil.copyfile(ROOT/original['image'],ROOT/('public'+q['image']))
        reviewed[qid]=q
    revised=revised_questions(indexed,base)
    assert not set(revised).intersection(reviewed)
    reviewed.update(revised)
    for qid in ['form-4-q03','form-4-q04','form-4-q05']:
        q=reviewed[qid];q['image']='/assets/questions/heavy/original-'+qid+'.png';q['imagePresentation']='loading-'+qid[-2:]
        shutil.copyfile(ROOT/indexed[qid]['image'],ROOT/('public'+q['image']))
    # Preserve all 120 source positions, including duplicates, without inflating the published bank.
    duplicate_of={}
    seen={}
    for q in records:
        signature=(q['text'],tuple(q['options']))
        if q['id'] not in ['form-4-q03','form-4-q04','form-4-q05']:
            if signature in seen:duplicate_of[q['id']]=seen[signature]
            else:seen[signature]=q['id']
    audit=[]
    for q in records:
        item={**q,'status':'needs-answer-review','answer':None,'reviewNote':'يلزم مفتاح المدرب أو مرجع يحدد الجواب دون التباس.'}
        if q['id'] in ['form-3-q05','form-3-q06','form-3-q17','form-4-q07','form-4-q31']:
            item['reviewNote']='الصياغة أو الخيارات تحتمل التباسًا. يلزم شرح المدرب أو تعديل السؤال قبل إدخاله في التصحيح.'
        if q['id'] in ['form-4-q03','form-4-q04','form-4-q05']:
            item['reviewNote']='صور تحميل مختلفة لها النص نفسه؛ يلزم تقييم تثبيت الحمولة في كل صورة على حدة.'
        canonical=duplicate_of.get(q['id'],q['id'])
        if canonical in reviewed:
            item.update(status='reference-reviewed',answer=reviewed[canonical]['answer'],evidence=reviewed[canonical]['source'],reviewNote=reviewed[canonical]['explanation'])
            if reviewed[canonical]['origin'].get('revisionNote'):
                revised_q=reviewed[canonical]
                item.update(status='revised',answer=None,revisionNote=revised_q['origin']['revisionNote'],revisedQuestion={k:revised_q[k] for k in ['text','options','answer']})
        if q['id'] in duplicate_of:item['duplicateOf']=canonical
        if q['id'] in MERGED:item.update(status='merged',answer=None,canonicalId=MERGED[q['id']],reviewNote='دُمج موضوع الوقاية أو فحص المقابض في سؤال قائم، دون اعتماد الخيارات القديمة الملتبسة.')
        audit.append(item)
    (ROOT/'content/heavy-original-review.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    visually_checked={'form-3-q15','form-3-q16','form-4-q46'}
    assert all(q['matchScore']>=.8 or q['id'] in visually_checked for q in records if q['id'] in reviewed)
    return list(reviewed.values())

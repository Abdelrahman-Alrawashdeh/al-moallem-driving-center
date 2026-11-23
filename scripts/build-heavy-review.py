"""Build an offline trainer review packet. It is deliberately outside public/ and dist/."""
import json, hashlib
from pathlib import Path
root=Path(__file__).resolve().parents[1]
records=json.loads((root/'content/heavy-original-review.json').read_text(encoding='utf8'))
for q in records:
 if q.get('originalText'):q['text']=q['originalText'];q['options']=q['originalOptions']
 if q['status']=='revised':
  revised=q['revisedQuestion'];q['reviewNote']='نُشر سؤال مصحح بدل الصياغة الأصلية. هذا ليس مفتاح الأصل. الصياغة المنشورة: '+revised['text']+' — الإجابة: '+revised['options'][revised['answer']]
 if q['status']=='merged':q['reviewNote']='موضوع مكرر؛ دُمج بالسؤال '+q.get('publishedId','')+' دون افتراض مفتاح للأصل.'
 q['fingerprint']=hashlib.sha256((root/q['image']).read_bytes()).hexdigest()
 q['image']=q['image'].removeprefix('content/')
template=(root/'scripts/heavy-review-template.html').read_text(encoding='utf8')
data=json.dumps(records,ensure_ascii=False).replace('<','\\u003c')
(root/'content/review-heavy.html').write_text(template.replace('/*REVIEW_DATA*/[]',data),encoding='utf8')
print(f'Offline review packet: {len(records)} original questions; content/review-heavy.html')

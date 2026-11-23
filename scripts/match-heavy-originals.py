"""Match user-supplied form screenshots to clean text; never infer answer keys."""
import json, re, html
from pathlib import Path
from difflib import SequenceMatcher

ROOT = Path(__file__).resolve().parents[1]
DIR = ROOT / 'content/sources/heavy-originals'
source = (ROOT / 'content/sources/heavy-reference.html').read_text(encoding='utf8')

def plain(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', s))).strip()

def norm(s):
    s = re.sub('[أإآ]', 'ا', s).replace('ى', 'ي').replace('ة', 'ه')
    return re.sub(r'[^\u0621-\u064a0-9 ]', '', s)

def signature(s):
    return ' '.join(sorted(norm(s).split()))

reference = {}
for block in re.split(r"<div class='step[^']*' data-question-id='", source)[1:]:
    qid = block.split("'", 1)[0]
    prompt = re.search(r"<div class='ays_quiz_question'>(.*?)</div>", block, re.S)
    options = re.findall(r"<label\b[^>]*class=['\"][^'\"]*ays-quiz-keyboard-label[^'\"]*['\"][^>]*>(.*?)</label>", block, re.S)
    if prompt and options:
        reference[qid] = {'referenceId': qid, 'text': plain(prompt[1]), 'options': [plain(x) for x in options]}

reference = {k:q for k,q in reference.items() if 2 <= len(q['options']) <= 4}
for q in reference.values():
    q['_signature'] = signature(q['text']+' '+' '.join(q['options']))
ocr = json.loads((DIR / 'ocr.json').read_text(encoding='utf8'))
matches = []
for item in ocr:
    sig = signature(item['text'])
    words = set(sig.split())
    shortlist = sorted(reference.values(), key=lambda q: len(words & set(q['_signature'].split())) / max(1,len(words | set(q['_signature'].split()))), reverse=True)[:8]
    ranked = sorted(((SequenceMatcher(None, sig, q['_signature'], autojunk=False).ratio(), q) for q in shortlist), key=lambda x: x[0], reverse=True)
    score, q = ranked[0]
    matches.append({'id': item['id'], 'image': 'content/sources/heavy-originals/'+item['id']+'.png', 'matchScore': round(score, 3), **{k:v for k,v in q.items() if not k.startswith('_')}, 'answer': None, 'status': 'awaiting-review', 'alternativeReferenceId': ranked[1][1]['referenceId']})
(DIR / 'matched.json').write_text(json.dumps(matches, ensure_ascii=False, indent=2)+'\n', encoding='utf8')
(DIR / 'transcription-review.txt').write_text('\n\n'.join(f"{q['id']} | match={q['matchScore']} | ref={q['referenceId']}\n{q['text']}\n"+'\n'.join(f'{i+1}. {o}' for i,o in enumerate(q['options'])) for q in matches), encoding='utf8')
print(f'{len(reference)} reference questions; {len(matches)} image matches; {sum(q["matchScore"] >= .8 for q in matches)} scores >= .8. All answers remain unset.')
print('Lowest matches:', [(q['id'], q['matchScore']) for q in sorted(matches, key=lambda q:q['matchScore'])[:12]])

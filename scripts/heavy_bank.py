import json
from pathlib import Path
def build_heavy_questions():
 sources=json.loads(Path('content/heavy-sources.json').read_text(encoding='utf8'))
 questions=[]
 for n,line in enumerate(Path('scripts/heavy-questions.txt').read_text(encoding='utf8').splitlines(),1):
  if not line.strip():continue
  source,section,topic,text,correct,wrong1,wrong2,explanation,diagram=line.split('|')
  options=[correct,wrong1,wrong2];shift=(n*7)%3;options=options[shift:]+options[:shift]
  q={'id':f'heavy-{n:03}','text':text,'options':options,'answer':options.index(correct),'categories':['heavy'],'topic':topic,'source':{**sources[source],'section':section,'checkedAt':'2026-09-24'},'explanation':explanation}
  if diagram:
   q['image']=f'/assets/questions/heavy/{diagram}.svg'
   assert Path('public'+q['image']).is_file(),q['image']
  questions.append(q)
 assert len(questions)>=60
 assert len(set(q['text'] for q in questions))==len(questions)
 return questions

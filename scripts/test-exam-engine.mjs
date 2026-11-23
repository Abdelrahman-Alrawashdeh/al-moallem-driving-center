import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,access} from 'node:fs/promises';
import {createAttempt,selectQuestions,remaining,finish,grade,validAttempt,DURATION} from '../public/exam-engine.js';
import {sourceReference} from '../public/source-reference.js';
const bank=JSON.parse(await readFile('public/data/question-bank.json','utf8'));
test('mixed car exams cover every available topic and illustrated situations',()=>{
 const topics=new Set(bank.questions.filter(q=>q.categories.includes('cars')).map(q=>q.topic));
 for(const model of [1,2,3]){const selected=selectQuestions(bank,'cars',model);assert.deepEqual(new Set(selected.map(q=>q.topic)),topics);assert(selected.some(q=>q.image));}
 for(const topic of bank.topics)assert.equal(topic.count,bank.questions.filter(q=>q.topic===topic.id).length);
});
test('bank integrity, source references, images, and unique IDs',async()=>{
 assert.equal(new Set(bank.questions.map(q=>q.id)).size,bank.questions.length);
 for(const q of bank.questions){assert(q.text.length>5);assert(q.source.page>0||q.source.url?.startsWith('https://'));assert(q.source.title);assert.equal(new Set(q.options).size,q.options.length);assert(q.answer>=0&&q.answer<q.options.length);assert(q.explanation);if(q.image)await access('public'+q.image);}
});
test('all published models have exactly 60 unique questions and different selections',()=>{
 for(const category of bank.categories.filter(c=>c.available)){
 const models=[1,2,3].map(model=>selectQuestions(bank,category.id,model).map(q=>q.id));
 for(const ids of models){assert.equal(ids.length,60);assert.equal(new Set(ids).size,60);}
 assert.notDeepEqual(models[0],models[1]);assert.notDeepEqual(models[1],models[2]);
 }
 assert.throws(()=>selectQuestions(bank,'unknown',1));
});
test('heavy models include 45 specialized and 15 common illustrated questions',()=>{
 for(const model of [1,2,3]){
  const selected=selectQuestions(bank,'heavy',model),specialized=selected.filter(q=>!q.categories.includes('signs'));
  assert.equal(specialized.length,45);assert.equal(selected.length-specialized.length,15);
  const topics=new Set(bank.questions.filter(q=>q.categories.includes('heavy')&&!q.categories.includes('signs')).map(q=>q.topic));
  assert.deepEqual(new Set(specialized.map(q=>q.topic)),topics);assert(specialized.some(q=>q.image));
  assert(specialized.some(q=>q.origin?.kind==='provided-google-form'));
  const attempt=createAttempt(bank,'heavy',model);for(const q of selected)attempt.answers[q.id]=q.answer;
  assert.equal(grade(attempt,selected).correct,60);assert(validAttempt(attempt,bank));
 }
});
test('unreviewed originals and repeated source positions never enter scored exams',async()=>{
 const audit=JSON.parse(await readFile('content/heavy-original-review.json','utf8'));
 assert.equal(audit.length,120);
 for(const q of audit){const published=bank.questions.find(item=>item.id==='heavy-'+q.id);
  assert(['reference-reviewed','revised','merged'].includes(q.status),q.id);
  assert(bank.questions.some(item=>item.id===q.publishedId),q.id+' has a published equivalent');
  if(q.status==='merged'||q.duplicateOf)assert(!published,q.id);
  if(published){const key=q.status==='revised'?q.revisedQuestion:q;assert.equal(published.answer,key.answer);assert.deepEqual(published.options,key.options);assert(published.source.url);}
 }
});
test('web source references show sections and credits without undefined page numbers',()=>{
 for(const q of bank.questions.filter(q=>q.id.startsWith('heavy-'))){const html=sourceReference(q.source);assert(html.includes(q.source.url.replaceAll('&','&amp;')));assert(!html.includes('undefined'));if(q.source.license)assert(html.includes('OGL v3.0'));}
 assert(!sourceReference({title:'<script>',url:'javascript:alert(1)'}).includes('href='));
});
test('deadline persists and is not reset by serialization; expiry clamps to zero',()=>{
 const a=createAttempt(bank,'cars',1,100000);
 assert.equal(a.deadline-a.startedAt,DURATION);
 assert.equal(remaining(JSON.parse(JSON.stringify(a)),100000+120000),3480);
 assert.equal(remaining(a,a.deadline),0);assert.equal(remaining(a,a.deadline+10000),0);
});
test('grading separates correct, incorrect and unanswered; finishing is idempotent',()=>{
 const a=createAttempt(bank,'signs',1);const qs=a.questionIds.map(id=>bank.questions.find(q=>q.id===id));
 a.answers[qs[0].id]=qs[0].answer;a.answers[qs[1].id]=(qs[1].answer+1)%qs[1].options.length;
 const result=grade(a,qs);assert.equal(result.correct,1);assert.equal(result.wrong,1);assert.equal(result.unanswered,58);
 const done=finish(a,'manual',a.startedAt+60000);assert.equal(done.reason,'manual');assert.equal(finish(done,'timeout',a.deadline),done);
 a.answers[qs[0].id]=99;assert.notEqual(done.answers[qs[0].id],99);
});
test('expired attempts record the deadline rather than late return time',()=>{
 const a=createAttempt(bank,'bike',2,1000);const done=finish(a,'manual',a.deadline+900000);assert.equal(done.reason,'timeout');assert.equal(done.finishedAt,a.deadline);
});
test('saved state validation rejects malformed, stale, duplicate and unknown answers',()=>{
 const a=createAttempt(bank,'cars',3);assert(validAttempt(a,bank));
 assert(!validAttempt({...a,deadline:a.deadline+1},bank));
 assert(!validAttempt({...a,questionIds:Array(60).fill(a.questionIds[0])},bank));
 assert(!validAttempt({...a,bankVersion:'old'},bank));
 assert(!validAttempt({...a,answers:{unknown:0}},bank));
 assert(!validAttempt({...a,answers:{[a.questionIds[0]]:99}},bank));
 assert(!validAttempt({...a,flags:['unknown']},bank));
});

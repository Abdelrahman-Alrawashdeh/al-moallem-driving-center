export const DURATION = 60 * 60 * 1000;
export const QUESTION_COUNT = 60;
export const STORAGE_KEY = 'moallem-exam-v1';
export function shuffle(items, seed) {
  const list = [...items]; let state = seed >>> 0;
  const random = () => { state = (Math.imul(1664525, state) + 1013904223) >>> 0; return state / 4294967296; };
  for(let i=list.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[list[i],list[j]]=[list[j],list[i]];}
  return list;
}
export function selectQuestions(bank, category, model) {
  const pool=bank.questions.filter(q=>q.categories.includes(category));
  const unique=[...new Map(pool.map(q=>[q.id,q])).values()];
  if(unique.length<QUESTION_COUNT)throw new Error('لا توجد أسئلة موثقة كافية لهذه الفئة.');
  const seed=2417 + model*9811 + category.charCodeAt(0)*123;
  const shuffled=shuffle(unique,seed);
  if(category==='heavy'){
    const specialized=shuffled.filter(q=>!q.categories.includes('signs'));
    const common=shuffled.filter(q=>q.categories.includes('signs'));
    if(specialized.length<45||common.length<15)throw new Error('بنك الثقيلة لا يحقق توزيع النموذج.');
    const groups=[...new Set(specialized.map(q=>q.topic))].map(topic=>specialized.filter(q=>q.topic===topic));
    const selected=[];
    while(selected.length<45)for(const group of groups){if(group.length&&selected.length<45)selected.push(group.shift());}
    return shuffle([...selected,...common.slice(0,15)],seed+73);
  }
  if(category!=='cars')return shuffled.slice(0,QUESTION_COUNT);
  // Draw across topics so a mixed model cannot be dominated by sign questions.
  const groups=[...new Set(shuffled.map(q=>q.topic))].map(topic=>shuffled.filter(q=>q.topic===topic));
  const selected=[];
  while(selected.length<QUESTION_COUNT)for(const group of groups){if(group.length&&selected.length<QUESTION_COUNT)selected.push(group.shift());}
  return shuffle(selected,seed+73);
}
export function createAttempt(bank, category, model, now=Date.now()) {
  const questions=selectQuestions(bank,category,model);
  return {version:1,bankVersion:bank.version,id:globalThis.crypto.randomUUID(),category,model,startedAt:now,deadline:now+DURATION,finishedAt:null,reason:null,answers:{},flags:[],questionIds:questions.map(q=>q.id)};
}
export function remaining(attempt,now=Date.now()){return Math.max(0,Math.ceil((attempt.deadline-now)/1000));}
export function finish(attempt,reason='manual',now=Date.now()) {
  if(attempt.finishedAt!==null)return attempt;
  return {...attempt,finishedAt:Math.min(now,attempt.deadline),reason:now>=attempt.deadline?'timeout':reason,answers:{...attempt.answers},flags:[...attempt.flags]};
}
export function grade(attempt,questions) {
  let correct=0,wrong=0,unanswered=0;
  const rows=questions.map(q=>{const answer=attempt.answers[q.id];const status=answer===undefined?'unanswered':answer===q.answer?'correct':'wrong';if(status==='correct')correct++;else if(status==='wrong')wrong++;else unanswered++;return {...q,selected:answer,status};});
  return {correct,wrong,unanswered,total:questions.length,percent:Math.round(correct/questions.length*100),rows};
}
export function validAttempt(value,bank) {
  if(!value||value.version!==1||value.bankVersion!==bank.version||typeof value.id!=='string'||!Array.isArray(value.questionIds)||value.questionIds.length!==QUESTION_COUNT||new Set(value.questionIds).size!==QUESTION_COUNT)return false;
  if(!bank.categories.some(c=>c.id===value.category&&c.available)||![1,2,3].includes(value.model))return false;
  if(!Number.isFinite(value.startedAt)||value.deadline!==value.startedAt+DURATION||value.startedAt>Date.now()+60000)return false;
  if(value.finishedAt!==null&&(!Number.isFinite(value.finishedAt)||value.finishedAt<value.startedAt||value.finishedAt>value.deadline))return false;
  if(!value.answers||typeof value.answers!=='object'||Array.isArray(value.answers)||!Array.isArray(value.flags)||value.flags.some(id=>!value.questionIds.includes(id)))return false;
  const questions=new Map(bank.questions.map(q=>[q.id,q]));
  if(value.questionIds.some(id=>!questions.has(id)||!questions.get(id).categories.includes(value.category)))return false;
  return Object.entries(value.answers).every(([id,a])=>value.questionIds.includes(id)&&Number.isInteger(a)&&a>=0&&a<questions.get(id).options.length);
}

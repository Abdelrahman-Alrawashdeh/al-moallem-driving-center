import {STORAGE_KEY,validAttempt,remaining,finish} from './exam-engine.js';
const card=document.getElementById('return-attempt');
let bank,loading;
const clock=s=>`${Math.floor(s/60).toString().padStart(2,'0')}:${(s%60).toString().padStart(2,'0')}`;
function mirror(){
 document.getElementById('return-exams').hidden=card.hidden;
 for(const part of ['title','detail','link'])document.getElementById('return-exams-'+part).textContent=document.getElementById('return-'+part).textContent;
 document.getElementById('return-exams-link').href=document.getElementById('return-link').href;
}
async function refresh(){
 let saved;
 try{saved=JSON.parse(localStorage.getItem(STORAGE_KEY));}catch{card.hidden=true;mirror();return;}
 if(!saved){card.hidden=true;mirror();return;}
 try{
  if(!bank){loading??=fetch('/data/question-bank.json').then(r=>{if(!r.ok)throw Error();return r.json();});bank=await loading;return refresh();}
  const title=document.getElementById('return-title'),detail=document.getElementById('return-detail'),link=document.getElementById('return-link');
  card.hidden=false;
  if(!validAttempt(saved,bank)){
   title.textContent='المحاولة السابقة غير متاحة للاستكمال';
   detail.textContent='بياناتها لا تتوافق مع بنك الأسئلة الحالي. يمكنك تجهيز محاولة جديدة.';
   link.textContent='إلى قاعة الامتحانات';link.href='/exam.html';return;
  }
  const seconds=remaining(saved);
  if(saved.finishedAt===null&&!seconds){saved=finish(saved,'timeout');try{localStorage.setItem(STORAGE_KEY,JSON.stringify(saved));}catch{/* The exam page can finalize the same deadline on return. */}}
  const category=bank.categories.find(c=>c.id===saved.category).name;
  title.textContent=`${saved.finishedAt===null?'أكمل اختبارك':'نتيجة اختبارك جاهزة'} · ${category} · النموذج ${saved.model}`;
  detail.textContent=saved.finishedAt===null?`أجبت عن ${Object.keys(saved.answers).length} من 60 سؤالًا · المتبقي ${clock(seconds)}. الوقت يستمر أثناء مغادرتك، والحفظ في هذا المتصفح.`:saved.reason==='timeout'?'انتهى الوقت. يمكنك الآن مراجعة النتيجة وإجاباتك المحفوظة.':'محاولتك مكتملة. ارجع لنتيجتك ومراجعة الإجابات في أي وقت من هذا المتصفح.';
  link.textContent=saved.finishedAt===null?'استكمال الاختبار ←':'عرض النتيجة والمراجعة ←';link.href='/exam.html?resume=1';
 }catch{loading=null;card.hidden=false;document.getElementById('return-title').textContent='لديك محاولة محفوظة';document.getElementById('return-detail').textContent='افتح قاعة الامتحانات للتحقق من حالتها واستكمالها.';document.getElementById('return-link').href='/exam.html';}finally{mirror();}
}
refresh();setInterval(()=>{if(!document.hidden)refresh();},1000);
window.addEventListener('pageshow',refresh);
window.addEventListener('storage',e=>{if(e.key===STORAGE_KEY||e.key===null)refresh();});
document.addEventListener('visibilitychange',()=>{if(!document.hidden)refresh();});

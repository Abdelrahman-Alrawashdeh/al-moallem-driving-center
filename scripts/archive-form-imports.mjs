import {readFile,writeFile,mkdir} from 'node:fs/promises';
await mkdir('content',{recursive:true});
const files=[];
for(let i=0;i<5;i++){
 const raw=JSON.parse(await readFile(`content/sources/form-${i}.json`,'utf8'));
 const html=await readFile(`content/sources/form-${i}.html`,'utf8');
 const images=[...html.matchAll(/<img[^>]+src="([^"]+)"[^>]*>/g)].map(m=>m[1].replaceAll('&amp;','&'));
 let imageIndex=0;
 const questions=raw[1][1].filter(q=>q[3]===2).map((q,n)=>({id:`form-${i+1}-q${n+1}`,sourceItemId:q[0],text:q[1]||`السؤال ${n+1}`,options:q[4][0][1].filter(o=>o[0]).map(o=>o[0]),image:q[9]?.length?images[imageIndex++]:null,answer:null,status:'awaiting-answer-key'}));
 files.push({id:`form-${i+1}`,title:raw[1][0],questions});
}
await writeFile('content/imported-google-forms.json',JSON.stringify(files,null,2));
await writeFile('content/answer-key-template.json',JSON.stringify(files.map(f=>({id:f.id,title:f.title,questions:f.questions.map(q=>({id:q.id,correctOptionNumber:null,optionCount:q.options.length}))})),null,2));
console.log(files.map(f=>`${f.id}: ${f.questions.length} questions awaiting verified answer keys`).join('\n'));

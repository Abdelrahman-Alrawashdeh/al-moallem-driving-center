import {chromium,expect} from '@playwright/test';
import {spawn} from 'node:child_process';
import {readFile,mkdir} from 'node:fs/promises';
import assert from 'node:assert/strict';
const bank=JSON.parse(await readFile('public/data/question-bank.json','utf8'));
const server=spawn(process.execPath,['scripts/serve.mjs'],{stdio:'pipe',env:{...process.env,PORT:'4178'}});
await new Promise((resolve,reject)=>{server.stdout.once('data',resolve);server.once('error',reject);});
let browser;
try{
 browser=await chromium.launch({channel:process.env.BROWSER_CHANNEL||'msedge'});
 await mkdir('artifacts/exams',{recursive:true});
 const context=await browser.newContext({viewport:{width:1440,height:1000},reducedMotion:'reduce'});
 const page=await context.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:4178/exam.html?category=signs');
 await expect(page.locator('#setup')).toBeVisible();
 await page.screenshot({path:'artifacts/exams/setup-desktop.png',fullPage:true});
 await page.locator('#start').click();
 await expect(page.locator('.question-card')).toHaveCount(60);
 let attempt=await page.evaluate(()=>JSON.parse(localStorage.getItem('moallem-exam-v1')));
 assert.equal(attempt.deadline-attempt.startedAt,3600000);
 const first=bank.questions.find(q=>q.id===attempt.questionIds[0]);
 await page.locator(`input[name="${first.id}"][value="${first.answer}"]`).check();
 await page.locator('.flag-button').first().click();
 await expect(page.locator('#answered-count')).toHaveText('1 من 60');
 await page.reload();await page.locator('#resume').click();
 await expect(page.locator(`input[name="${first.id}"][value="${first.answer}"]`)).toBeChecked();
 const restored=await page.evaluate(()=>JSON.parse(localStorage.getItem('moallem-exam-v1')));
 assert.equal(restored.deadline,attempt.deadline);assert.deepEqual(restored.flags,[first.id]);
 await page.locator('.question-card').first().screenshot({path:'artifacts/exams/question.png'});
 await page.locator('#submit-exam').click();await expect(page.locator('#dialog-message')).toContainText('59');
 await page.locator('#cancel-submit').click();await expect(page.locator('#active-exam')).toBeVisible();
 const second=bank.questions.find(q=>q.id===attempt.questionIds[1]);
 await page.locator(`input[name="${second.id}"][value="${(second.answer+1)%second.options.length}"]`).check();
 await page.locator('#submit-exam').click();await page.locator('#confirm-submit').click();
 await expect(page.locator('#correct-count')).toHaveText('1');await expect(page.locator('#wrong-count')).toHaveText('1');await expect(page.locator('#unanswered-count')).toHaveText('58');
 await expect(page.locator('.review-card')).toHaveCount(60);
 await page.locator('[data-review=wrong]').click();await expect(page.locator('.review-card:visible')).toHaveCount(1);
 await expect(page.locator('.review-card:visible .selected-wrong')).toHaveCount(1);await expect(page.locator('.review-card:visible .review-option.correct')).toHaveCount(1);
 await page.locator('[data-review=all]').click();
 await page.screenshot({path:'artifacts/exams/result-desktop.png'});
 await page.reload();await page.locator('#resume').click();await expect(page.locator('#correct-count')).toHaveText('1');
 assert.deepEqual(errors,[]);console.log('PASS manual grading, review filters, unanswered confirmation, flags, reload and result persistence');
 // Two tabs share one deadline and finalized result.
 await page.locator('#retry').click();await page.locator('#start').click();await page.locator('#confirm-submit').click();
 const other=await context.newPage();await other.goto('http://127.0.0.1:4178/exam.html');await other.locator('#resume').click();
 await page.locator('#submit-exam').click();await page.locator('#confirm-submit').click();await expect(other.locator('#results')).toBeVisible();
 console.log('PASS cross-tab submission locks both views');
 await context.close();
 // Absolute-clock expiry after browser suspension, with a pending confirmation dialog.
 const timed=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
 await timed.clock.install({time:new Date()});
 await timed.goto('http://127.0.0.1:4178/exam.html?category=bike');await timed.locator('#start').click();
 await timed.locator('#questions input').first().check();
 await timed.evaluate(()=>document.getElementById('submit-bottom').click());
 await timed.clock.fastForward(3601000);
 await expect(timed.locator('#results')).toBeVisible();await expect(timed.locator('#result-reason')).toContainText('تلقائيًا');
 await expect(timed.locator('#time-used')).toHaveText('60:00');await expect(timed.locator('#confirm-dialog')).not.toBeVisible();
 await timed.reload();await timed.locator('#resume').click();await expect(timed.locator('#results')).toBeVisible();
 await timed.screenshot({path:'artifacts/exams/result-mobile.png'});await timed.close();
 console.log('PASS 60-minute automatic submission, closed dialog, locked answers and expired reload');
 for(const width of [320,390,768,1440]){
  const p=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce',hasTouch:width<700});
  await p.goto('http://127.0.0.1:4178/exam.html?category=cars');await expect(p.locator('#setup')).toBeVisible();
  assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`Setup overflow ${width}`);
  await p.locator('[data-category=heavy]').click();await expect(p.locator('#start')).toBeEnabled();
  await p.locator('[data-category=cars]').click();await p.locator('#start').click();
  assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`Exam overflow ${width}`);
  if(width<700){await p.locator('#map-toggle').click();await p.locator('[data-map]').nth(59).click();await expect(p.locator('#question-map')).not.toHaveClass(/open/);await expect(p.locator('#question-60 input').first()).toBeFocused();}
  await p.evaluate(()=>scrollTo(0,0));await p.screenshot({path:`artifacts/exams/active-${width}.png`});
  // Decode every source image, including lazy images below the fold.
  const broken=await p.locator('.question-image').evaluateAll(async imgs=>{imgs.forEach(i=>i.loading='eager');await Promise.all(imgs.map(i=>i.decode().catch(()=>{})));return imgs.filter(i=>!i.naturalWidth).map(i=>i.src);});assert.deepEqual(broken,[]);
  await p.close();console.log(`PASS ${width}px: layout, question map, 60 questions, source images and available heavy category`);
 }
 const heavy=await browser.newPage({viewport:{width:390,height:844},reducedMotion:'reduce'});
 await heavy.goto('http://127.0.0.1:4178/exam.html?category=heavy&model=2');await heavy.locator('#start').click();await expect(heavy.locator('.question-card')).toHaveCount(60);
 const h=await heavy.evaluate(()=>JSON.parse(localStorage.getItem('moallem-exam-v1')));assert.equal(h.questionIds.filter(id=>!bank.questions.find(q=>q.id===id).categories.includes('signs')).length,45);
 const specialized=h.questionIds.find(id=>id.startsWith('heavy-')),hq=bank.questions.find(q=>q.id===specialized);await heavy.locator(`input[name="${specialized}"][value="${hq.answer}"]`).check();
 await heavy.locator('#submit-bottom').click();await heavy.locator('#confirm-submit').click();await expect(heavy.locator('#correct-count')).toHaveText('1');await expect(heavy.locator('#unanswered-count')).toHaveText('59');
 assert(!await heavy.locator('#review-list').innerText().then(t=>t.includes('undefined')));await expect(heavy.locator('.source-line a[href^="https://"]').first()).toBeVisible();
 assert(await heavy.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await heavy.screenshot({path:'artifacts/exams/heavy-result-mobile.png',fullPage:true});await heavy.close();
 console.log('PASS specialized heavy exam: 45+15 distribution, mobile grading and web source links');
}finally{await browser?.close();server.kill();}

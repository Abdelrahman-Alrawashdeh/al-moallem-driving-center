import {chromium,expect} from '@playwright/test';
import {spawn} from 'node:child_process';
import {readFile,mkdir} from 'node:fs/promises';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
import assert from 'node:assert/strict';
const bank=JSON.parse(await readFile('public/data/question-bank.json','utf8'));
const server=spawn(process.execPath,['scripts/serve.mjs'],{stdio:'pipe',env:{...process.env,PORT:'4181'}});
await new Promise((ok,no)=>{server.stdout.once('data',ok);server.once('error',no);});
let browser;
try{
 browser=await chromium.launch({channel:'msedge'});await mkdir('artifacts/heavy-originals',{recursive:true});
 for(const width of [320,390,1440]){
  const page=await browser.newPage({viewport:{width,height:900}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:4181/practice.html?topic=heavy-loading');await page.locator('#search').fill('إن وجود المركبة بهذه الطريقة');
  await expect(page.locator('.question-card')).toHaveCount(1);await expect(page.locator('.original-diagram')).toBeVisible();
  assert(await page.locator('.original-diagram img').evaluate(async img=>{await img.decode();return img.naturalWidth>0;}));
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await expect(page.locator('.practice-choice')).toHaveCount(4);
  assert(await page.locator('.question-card').evaluate(card=>{const box=card.getBoundingClientRect();return [...card.querySelectorAll('.practice-choice')].every(b=>b.getBoundingClientRect().bottom<=box.bottom+1);}));
  await page.locator('.practice-choice').last().scrollIntoViewIfNeeded();
  await page.locator('.question-card').screenshot({path:`artifacts/heavy-originals/question-${width}.png`});
  await page.locator('[data-answer="0"]').click();await expect(page.locator('.feedback')).toContainText('مرجع التحقق من الإجابة');
  await page.locator('.image-zoom').click();await expect(page.locator('#large-image')).toBeVisible();await page.locator('#close-image').click();
  for(const suffix of ['03','04','05']){
   const q=bank.questions.find(q=>q.id==='heavy-form-4-q'+suffix);
   await page.locator('#search').fill(q.text);
   await expect(page.locator('.question-card')).toHaveCount(1);
   await expect(page.locator('.loading-'+suffix)).toBeVisible();
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
   await page.locator('.question-card').screenshot({path:`artifacts/heavy-originals/loading-${suffix}-${width}.png`});
   await page.locator('.image-zoom').click();await expect(page.locator('#image-frame')).toHaveClass('loading-diagram loading-'+suffix);
   assert(await page.locator('#image-frame').evaluate(e=>{const [w,h]=getComputedStyle(e).aspectRatio.split('/').map(Number);return e.clientWidth>200&&Math.abs(e.clientHeight-e.clientWidth*h/w)<2;}));
   await page.screenshot({path:`artifacts/heavy-originals/zoom-${suffix}-${width}.png`});
   await page.locator('#close-image').click();
  }
  assert.deepEqual(errors,[]);await page.close();
 }
 const review=await browser.newPage({viewport:{width:390,height:844}});
 await review.goto(pathToFileURL(resolve('content/review-heavy.html')).href);await expect(review.locator('#grid button')).toHaveCount(60);
 await review.locator('#form').selectOption('4');await expect(review.locator('#grid button')).toHaveCount(60);
 await review.locator('#filter').selectOption('pending');await expect(review.locator('#confirm')).toBeVisible();
 await review.locator('#reviewer').fill('اختبار آلي للواجهة');await review.locator('[name=answer]').first().check();
 await review.locator('#confirm').click();await expect(review.locator('#message')).toContainText('أضف مرجعًا');
 await review.locator('#note').fill('اختبار واجهة فقط؛ ليس مفتاح إجابة معتمدًا.');await review.locator('#confirm').click();await expect(review.locator('#status')).toContainText('1 راجعها');
 await review.reload();await expect(review.locator('#status')).toContainText('1 راجعها');
 const download=review.waitForEvent('download');await review.locator('#export').click();const file=await download;
 const payload=JSON.parse(await readFile(await file.path(),'utf8'));assert.equal(payload.answers.length,1);assert.equal(payload.answers[0].correctOptionNumber,1);assert.match(payload.answers[0].sourceFingerprint,/^[a-f0-9]{64}$/);
 assert(await review.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await review.screenshot({path:'artifacts/heavy-originals/review-mobile.png',fullPage:true});
 console.log('PASS original illustration: 320/390/1440, feedback and zoom; offline trainer review, required notes, persistence and export');
}finally{await browser?.close();server.kill();}

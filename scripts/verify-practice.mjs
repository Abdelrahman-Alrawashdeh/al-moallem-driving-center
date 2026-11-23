import {chromium,expect} from '@playwright/test';
import {spawn} from 'node:child_process';
import {readFile,mkdir} from 'node:fs/promises';
import assert from 'node:assert/strict';
const bank=JSON.parse(await readFile('public/data/question-bank.json','utf8'));
const server=spawn(process.execPath,['scripts/serve.mjs'],{stdio:'pipe',env:{...process.env,PORT:'4179'}});
await new Promise((resolve,reject)=>{server.stdout.once('data',resolve);server.once('error',reject);});
let browser;
try{
 browser=await chromium.launch({channel:'msedge'});await mkdir('artifacts/practice',{recursive:true});
 for(const width of [320,390,768,1440]){
  const page=await browser.newPage({viewport:{width,height:900},reducedMotion:'reduce'});const errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto('http://127.0.0.1:4179/practice.html');await expect(page.locator('#bank-total')).toHaveText(String(bank.questions.length));await expect(page.locator('[data-topic]')).toHaveCount(bank.topics.length+1);await expect(page.locator('.question-card')).toHaveCount(12);
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`overflow ${width}`);
  await page.locator('[data-topic=mechanics]').click();await expect(page.locator('#library-title')).toHaveText('الميكانيك وفحص المركبة');
  const first=bank.questions.find(q=>q.topic==='mechanics');await page.locator(`[data-id="${first.id}"] [data-answer="${first.answer}"]`).click();await expect(page.locator(`[data-id="${first.id}"] .feedback`)).toContainText('إجابة صحيحة');await expect(page.locator('#session-score')).toContainText('1 صحيحة من 1');
  await page.locator('#next').click();await expect(page.locator('#page-label')).toHaveText('2 / 2');await page.locator('#previous').click();await expect(page.locator(`[data-id="${first.id}"] .correct`)).toBeDisabled();
  await page.locator('[data-topic=priority]').click();await page.locator('#images-only').check();await page.locator('.image-zoom').first().click();await expect(page.locator('#image-dialog')).toBeVisible();await expect(page.locator('#large-image')).toBeVisible();await page.locator('#close-image').click();
  await page.locator('#search').fill('zzzz-nonexistent');await expect(page.locator('.practice-empty')).toBeVisible();await expect(page.locator('#next')).toBeDisabled();
  await page.locator('#search').fill('');await page.locator('#images-only').uncheck();await page.locator('[data-topic=all]').click();await page.locator('#category').selectOption('bike');await expect(page.locator('#match-count')).toContainText('66 سؤالًا');
  await page.locator('#category').selectOption('all');await page.locator('[data-topic=signs]').click();await page.evaluate(async()=>{const imgs=[...document.images];imgs.forEach(i=>i.loading='eager');await Promise.all(imgs.map(i=>i.decode()));});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));assert.equal(errors.length,0,errors.join('\n'));await page.screenshot({path:`artifacts/practice/library-${width}.png`,fullPage:true});
  await page.locator('[data-topic=all]').click();await page.locator('#category').selectOption('heavy');await expect(page.locator('#match-count')).toContainText(`${bank.questions.filter(q=>q.categories.includes('heavy')).length} سؤالًا`);
  await page.locator('[data-topic=heavy-loading]').click();await page.locator('#images-only').check();await expect(page.locator('.image-zoom').first()).toBeVisible();
  await page.locator('.practice-choice').first().click();await expect(page.locator('.source-line').first()).toContainText('DVSA');await expect(page.locator('.source-line').first()).not.toContainText('undefined');
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));await page.screenshot({path:`artifacts/practice/heavy-${width}.png`,fullPage:true});await page.close();
 }
 const page=await browser.newPage();await page.goto('http://127.0.0.1:4179/practice.html?topic=mechanics');await expect(page.locator('[data-topic=mechanics]')).toHaveAttribute('aria-pressed','true');
 // Check every published image, not just the first page of lazy images.
 for(const q of bank.questions.filter(q=>q.image)){const response=await page.request.get('http://127.0.0.1:4179'+q.image);assert.equal(response.status(),200,q.image);}
 await page.evaluate(async images=>{await Promise.all(images.map(src=>new Promise((resolve,reject)=>{const img=new Image();img.onload=resolve;img.onerror=()=>reject(Error(src));img.src=src;})));},bank.questions.filter(q=>q.id.startsWith('heavy-')&&q.image).map(q=>q.image));
 console.log('PASS: topic/search/category/image filters, feedback, pagination, image zoom, all published images, 4 responsive sizes');
}finally{await browser?.close();server.kill();}

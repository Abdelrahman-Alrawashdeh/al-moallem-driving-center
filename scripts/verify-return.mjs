import {chromium,expect} from '@playwright/test';
import {spawn} from 'node:child_process';
import {mkdir} from 'node:fs/promises';
import assert from 'node:assert/strict';
const server=spawn(process.execPath,['scripts/serve.mjs'],{stdio:'pipe',env:{...process.env,PORT:'4185'}});
await new Promise((ok,no)=>{server.stdout.once('data',ok);server.once('error',no);});
let browser;
const origin='http://127.0.0.1:4185',key='moallem-exam-v1';
const stored=p=>p.evaluate(k=>JSON.parse(localStorage.getItem(k)),key);
try{
 browser=await chromium.launch({channel:'msedge'});await mkdir('artifacts/return',{recursive:true});
 for(const width of [320,390,768,1440]){
  const context=await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce'}),errors=[];
  context.on('page',p=>p.on('pageerror',e=>errors.push(e.message)));
  let page=await context.newPage();await page.goto(origin);await expect(page.locator('#return-attempt')).toBeHidden();
  await page.goto(origin+'/exam.html?category=heavy&model=2');await page.locator('#start').click();
  await page.locator('#questions input').first().check();await page.locator('.flag-button').first().click();
  const initial=await stored(page);await page.locator('.home-link').click();
  await expect(page.locator('#return-attempt')).toBeVisible();await expect(page.locator('#return-detail')).toContainText('1 من 60');
  await expect(page.locator('#return-exams')).toBeVisible();await expect(page.locator('#return-exams-link')).toHaveAttribute('href','http://127.0.0.1:4185/exam.html?resume=1');
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.locator('#return-attempt').scrollIntoViewIfNeeded();await page.screenshot({path:`artifacts/return/landing-${width}.png`});
  await page.locator('#return-link').click();await expect(page.locator('#active-exam')).toBeVisible();
  await expect(page.locator('#questions input').first()).toBeChecked();assert.deepEqual((await stored(page)).flags,initial.flags);assert.equal((await stored(page)).deadline,initial.deadline);
  await page.goBack();await expect(page.locator('#return-exams')).toBeVisible();await page.goForward();
  if(await page.locator('#setup').isVisible())await page.locator('#resume').click();
  await expect(page.locator('#active-exam')).toBeVisible();await expect(page.locator('#questions input').first()).toBeChecked();
  // Close the tab entirely; a new tab on the same browser must find the same attempt.
  await page.close();page=await context.newPage();await page.goto(origin+'/exam.html');await expect(page.locator('#saved-attempt')).toBeVisible();
  await expect(page.locator('#saved-description')).toContainText('1');await page.locator('#resume').click();await expect(page.locator('#questions input').first()).toBeChecked();
  assert.equal((await stored(page)).id,initial.id);
  const home=await context.newPage();await home.goto(origin);await expect(home.locator('#return-link')).toContainText('استكمال');
  // Simulate time passing while away, preserving the original duration.
  await home.evaluate(k=>{const a=JSON.parse(localStorage.getItem(k));a.startedAt=Date.now()-3601000;a.deadline=a.startedAt+3600000;localStorage.setItem(k,JSON.stringify(a));},key);
  await expect(home.locator('#return-link')).toContainText('عرض النتيجة');await expect(page.locator('#results')).toBeVisible();
  await home.locator('#return-link').click();await expect(home.locator('#results')).toBeVisible();await expect(home.locator('#time-used')).toHaveText('60:00');
  const done=await stored(home);assert.equal(done.finishedAt,done.deadline);assert.equal(Object.keys(done.answers).length,1);
  await home.goto(origin+'/exam.html');await home.locator('#start').click();await home.locator('#cancel-submit').click();assert.equal((await stored(home)).id,initial.id);
  // Storage removal in another tab must not leave an editable stale attempt or stale card.
  await home.locator('#start').click();await home.locator('#confirm-submit').click();await expect(home.locator('#active-exam')).toBeVisible();
  await page.goto(origin);await expect(page.locator('#return-attempt')).toBeVisible();await page.evaluate(k=>localStorage.removeItem(k),key);
  await expect(home.locator('#setup')).toBeVisible();await expect(home.locator('#saved-attempt')).toBeHidden();await expect(page.locator('#return-attempt')).toBeHidden();
  assert.deepEqual(errors,[]);await context.close();console.log('PASS leave, landing, resume, closed tab, expiry, cross-tab reset, responsive',width);
 }
 // Deadline updates on the setup screen without reloading; stale data never becomes a scored attempt.
 const p=await browser.newPage();await p.goto(origin+'/exam.html');await p.locator('#start').click();
 await p.goto(origin+'/exam.html');await p.clock.install({time:new Date()});await p.clock.fastForward(3601000);
 await expect(p.locator('#resume')).toContainText('عرض النتيجة');await p.locator('#resume').click();await expect(p.locator('#results')).toBeVisible();
 await p.evaluate(k=>localStorage.setItem(k,JSON.stringify({version:1,bankVersion:'old'})),key);await p.goto(origin);await expect(p.locator('#return-title')).toContainText('غير متاحة');
 await p.evaluate(k=>localStorage.setItem(k,'invalid-json'),key);await p.reload();await expect(p.locator('#return-attempt')).toBeHidden();
 await p.close();console.log('PASS setup clock, incompatible data and corrupt storage');
}finally{await browser?.close();server.kill();}

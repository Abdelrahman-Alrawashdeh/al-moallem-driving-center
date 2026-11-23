import { chromium } from '@playwright/test';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
import { spawn } from 'node:child_process';
const server=spawn(process.execPath,['scripts/serve.mjs'],{stdio:'pipe',env:{...process.env,PORT:'4174'}});
await new Promise((resolve,reject)=>{server.stdout.once('data',resolve);server.once('error',reject);server.once('exit',code=>{if(code)reject(new Error('Preview server failed'));});});
let browser;
try {
 browser=await chromium.launch({channel:process.env.BROWSER_CHANNEL||'msedge',headless:true});
 await mkdir('artifacts',{recursive:true});
 for(const [width,height] of [[1440,1000],[768,1024],[320,568],[360,800],[375,667],[390,844],[414,896],[430,932],[600,900],[667,375],[844,390]]) {
  const mobile=width<=600||height<500;
  const page=await browser.newPage({viewport:{width,height},isMobile:mobile,hasTouch:mobile,deviceScaleFactor:mobile?2:1,reducedMotion:'reduce'});
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  await page.goto('http://127.0.0.1:4174',{waitUntil:'networkidle'});
  assert.equal(await page.locator('html').getAttribute('dir'),'rtl');
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`Horizontal overflow at ${width}`);
  const overflowing=await page.locator('h1,h2,h3,p,.filters,.contact-actions,.instructor,.nav-wrap').evaluateAll(elements=>elements.filter(el=>el.scrollWidth>el.clientWidth+1).map(el=>el.className||el.tagName));
  assert.deepEqual(overflowing,[],`Content clipping at ${width}x${height}`);
  if(width<=800){
   const undersized=await page.locator('.menu-toggle,.nav-cta,.filters button,.faq-list summary').evaluateAll(elements=>elements.filter(el=>el.getBoundingClientRect().height<44).map(el=>el.className||el.tagName));
   assert.deepEqual(undersized,[],`Small touch targets at ${width}`);
  }
  assert.equal(await page.locator('[data-category]:visible').count(),5);
  await page.locator('[data-filter="heavy"]').click();
  assert.equal(await page.locator('[data-category]:visible').count(),3);
  await page.locator('[data-filter="bike"]').click();
  assert.equal(await page.locator('[data-category]:visible').count(),2);
  await page.locator('[data-filter="all"]').click();
  if(width<=800){await page.locator('.menu-toggle').click();assert.equal(await page.locator('.menu-toggle').getAttribute('aria-expanded'),'true');await page.locator('#navigation a[href="#contact"]').click();assert.equal(await page.locator('.menu-toggle').getAttribute('aria-expanded'),'false');assert.equal(await page.locator('.menu-toggle').getAttribute('aria-label'),'فتح القائمة');}
  await page.locator('summary').first().click();assert.equal(await page.locator('details[open]').count(),1);
  assert(await page.locator('[data-map-link]').getAttribute('href').then(h=>h.includes('0xf61615a7363f793e')));
  const badImages=await page.locator('img').evaluateAll(async imgs=>{await Promise.all(imgs.map(img=>img.decode().catch(()=>{})));return imgs.filter(img=>!img.naturalWidth).map(img=>img.src);});assert.deepEqual(badImages,[]);
  assert.deepEqual(errors,[]);
  if(width<=600){
   await page.evaluate(()=>scrollTo(0,document.body.scrollHeight));
   const footerClear=await page.evaluate(()=>document.querySelector('.footer-bottom').lastElementChild.getBoundingClientRect().bottom<document.querySelector('.mobile-call').getBoundingClientRect().top);
   assert(footerClear,`Sticky call obscures footer at ${width}`);
  }
  await page.evaluate(()=>scrollTo(0,0));
  await page.screenshot({path:`artifacts/site-${width}x${height}.png`,fullPage:true});
  if(width===390||width===320){await page.screenshot({path:`artifacts/mobile-top-${width}.png`});await page.locator('#exams').scrollIntoViewIfNeeded();await page.screenshot({path:`artifacts/mobile-exams-${width}.png`});}
  console.log(`PASS ${width}x${height}: layout, touch targets, images, filters, navigation, FAQ, map and JavaScript`);
  await page.close();
 }
 const motionPage=await browser.newPage({viewport:{width:1440,height:1000}});
 await motionPage.goto('http://127.0.0.1:4174');
 await motionPage.locator('#journey').scrollIntoViewIfNeeded();
 await motionPage.waitForTimeout(1000);
 assert(await motionPage.locator('.road-car').evaluate(el=>parseFloat(el.style.right)>5));
 assert(await motionPage.locator('#journey .reveal').first().evaluate(el=>el.classList.contains('visible')));
 console.log('PASS scroll animation and reveal behavior');
} finally {await browser?.close();server.kill();}

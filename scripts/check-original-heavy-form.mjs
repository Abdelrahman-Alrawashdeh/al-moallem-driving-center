// Read-only verification of whether the user-supplied form images load in a browser.
import {chromium} from '@playwright/test';
import {mkdir,writeFile} from 'node:fs/promises';
const browser=await chromium.launch({channel:'msedge'});
try{
 const sources=[['form-3','1FAIpQLSd9t6zgNvkb3m79yV9d6biiNQUimm-6Drka8jOefnJbE0fDtA'],['form-4','1FAIpQLSe_8B0zWwUGGUygHd_jQsRXjrnBuQ3q6OXlsRc4Auors2iWjw']];
 await mkdir('content/sources/heavy-originals',{recursive:true});
 for(const [id,key] of sources){
  const page=await browser.newPage({viewport:{width:1100,height:900},deviceScaleFactor:1});
  const captured=new Map();
  page.on('response',response=>{if(response.url().includes('forms-images')&&response.ok())captured.set(response.url(),response.body().catch(()=>null));});
  await page.goto(`https://docs.google.com/forms/d/e/${key}/viewform`,{waitUntil:'domcontentloaded',timeout:60000});
  const images=page.locator('img[src*="forms-images"]');const count=await images.count();const manifest=[];
  for(let i=0;i<count;i++){
   const img=images.nth(i);await img.scrollIntoViewIfNeeded();await img.evaluate(el=>el.decode());
   const info=await img.evaluate(el=>({url:el.src,width:el.naturalWidth,height:el.naturalHeight}));
   const path=`content/sources/heavy-originals/${id}-q${String(i+1).padStart(2,'0')}.png`;
   const bytes=await captured.get(info.url);
   if(bytes)await writeFile(path,bytes);else await img.screenshot({path});
   manifest.push({id:`${id}-q${i+1}`,image:path,width:info.width,height:info.height});
   if((i+1)%15===0)console.log(`${id}: saved ${i+1}/${count}`);
  }
  await writeFile(`content/sources/heavy-originals/${id}.json`,JSON.stringify(manifest,null,2));await page.close();
 }
}finally{await browser.close();}

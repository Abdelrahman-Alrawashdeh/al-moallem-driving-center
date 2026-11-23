import { chromium } from '@playwright/test';
import { readFile, writeFile } from 'node:fs/promises';
const svg=await readFile('public/assets/favicon-v4.svg');
const browser=await chromium.launch({channel:process.env.BROWSER_CHANNEL||'msedge'});
const frames=[];
try {
  for(const size of [16,32,48,180]) {
    const page=await browser.newPage({viewport:{width:size,height:size},deviceScaleFactor:1});
    await page.setContent(`<style>html,body{margin:0;background:transparent}img{display:block;width:${size}px;height:${size}px}</style><img src="data:image/svg+xml;base64,${svg.toString('base64')}" alt="">`);
    await page.locator('img').evaluate(img=>img.decode());
    const png=await page.screenshot({omitBackground:true});
    if(size===180||size===32)await writeFile(size===180?'public/apple-touch-icon.png':`public/assets/favicon-${size}-v4.png`,png);
    if(size!==180)frames.push({size,png});
    await page.close();
  }
}finally{await browser.close();}
// ICO directory with lossless PNG images at three native tab-icon sizes.
const header=Buffer.alloc(6+frames.length*16);
header.writeUInt16LE(1,2);header.writeUInt16LE(frames.length,4);
let offset=header.length;
frames.forEach(({size,png},i)=>{const p=6+i*16;header[p]=size;header[p+1]=size;header.writeUInt16LE(1,p+4);header.writeUInt16LE(32,p+6);header.writeUInt32LE(png.length,p+8);header.writeUInt32LE(offset,p+12);offset+=png.length;});
await writeFile('public/favicon.ico',Buffer.concat([header,...frames.map(f=>f.png)]));
await writeFile('public/assets/favicon-v4.svg',svg);
console.log('Generated SVG, multi-resolution ICO, PNG and Apple touch icons.');

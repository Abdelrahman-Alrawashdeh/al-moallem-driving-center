// Read-only source capture. This never submits answers or sends a form response.
import {mkdir,writeFile} from 'node:fs/promises';
const sources=[
 ['form-3','https://docs.google.com/forms/d/e/1FAIpQLSd9t6zgNvkb3m79yV9d6biiNQUimm-6Drka8jOefnJbE0fDtA/viewform'],
 ['form-4','https://docs.google.com/forms/d/e/1FAIpQLSe_8B0zWwUGGUygHd_jQsRXjrnBuQ3q6OXlsRc4Auors2iWjw/viewform']
];
await mkdir('content/sources/heavy-review',{recursive:true});
for(const [id,url] of sources){
 const response=await fetch(`${url}?review=${Date.now()}`);if(!response.ok)throw Error(`Form ${id}: ${response.status}`);
 const html=await response.text();
 await writeFile(`content/sources/heavy-review/${id}.html`,html);
 const images=[...html.matchAll(/<img\b[^>]*\bsrc="([^"]+)"/g)].map(m=>m[1].replaceAll('&amp;','&')).filter(src=>src.includes('forms-images'));
 await writeFile(`content/sources/heavy-review/${id}-images.json`,JSON.stringify(images,null,2));
 console.log(`${id}: ${images.length} question images`);
 for(let offset=0;offset<images.length;offset+=4){
  await Promise.all(images.slice(offset,offset+4).map(async(src,i)=>{
   const result=await fetch(src);if(!result.ok)throw Error(`${id} image ${offset+i+1}: ${result.status}`);
   await writeFile(`content/sources/heavy-review/${id}-q${offset+i+1}.png`,Buffer.from(await result.arrayBuffer()));
  }));
 }
}

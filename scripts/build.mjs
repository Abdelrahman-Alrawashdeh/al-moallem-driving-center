import { cp, mkdir, readdir, rm } from 'node:fs/promises';
import { basename, resolve, dirname } from 'node:path';
const root=resolve('.'),destination=resolve(root,'dist');
if(dirname(destination)!==root||basename(destination)!=='dist')throw new Error('Unsafe build destination');
await rm(destination,{recursive:true,force:true});
await mkdir('dist', { recursive: true });
await cp('public', 'dist', { recursive: true, filter: source => !['desktop.ini','thumbs.db','.ds_store'].includes(basename(source).toLowerCase()) });
console.log(`Built static website in dist (${(await readdir('dist')).length} entries).`);

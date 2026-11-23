const escape=value=>String(value??'').replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
export function sourceReference(source){
 const safeUrl=typeof source.localUrl==='string'&&/^\/materials\.html\?/.test(source.localUrl)?source.localUrl:typeof source.url==='string'&&/^https:\/\//.test(source.url)?source.url:null;
 const title=safeUrl?`<a href="${escape(safeUrl)}" target="_blank" rel="noopener noreferrer">${escape(source.title)} ↗</a>`:escape(source.title);
 return `${source.kind==='answer-reference'?'مرجع التحقق من الإجابة':'المصدر'}: ${title}${source.slide?` · شريحة ${source.slide}`:source.page?` · صفحة ${source.page}`:''}${source.section?` · ${escape(source.section)}`:''}${source.kind==='adapted'?' · سؤال مُعدّ من الشرح':source.kind==='adapted-web'?' · صياغة تدريبية من المرجع':''}${source.license==='OGL-3.0'?' · <a href="/sources.html">© Crown copyright · OGL v3.0</a>':''}${/^https:\/\//.test(source.verificationUrl||'')?` · <a href="${escape(source.verificationUrl)}" target="_blank" rel="noopener noreferrer">مرجع التدقيق ↗</a>`:''}`;
}

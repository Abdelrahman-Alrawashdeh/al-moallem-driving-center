const escape=value=>String(value).replace(/[&<>"']/g,ch=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
export function questionImage(q,alt){
 const img=`<img class="question-image" src="${escape(q.image)}" alt="${escape(alt)}" loading="lazy">`;
 // Keep the supplied screenshot intact; frame its illustration in the student interface.
 if(/^loading-0[345]$/.test(q.imagePresentation||''))return `<span class="loading-diagram ${q.imagePresentation}">${img}</span>`;
 return q.imagePresentation==='original-question'?`<span class="original-diagram">${img}</span>`:img;
}

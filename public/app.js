const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const menu = document.querySelector('.menu-toggle');
const navigation = document.querySelector('#navigation');
function closeMenu() { menu.setAttribute('aria-expanded','false'); menu.setAttribute('aria-label','فتح القائمة'); navigation.classList.remove('open'); }
menu.addEventListener('click', () => { const open = menu.getAttribute('aria-expanded') !== 'true'; menu.setAttribute('aria-expanded',String(open)); navigation.classList.toggle('open',open); menu.setAttribute('aria-label',open ? 'إغلاق القائمة' : 'فتح القائمة'); });
navigation.addEventListener('click', event => { if (event.target.closest('a')) closeMenu(); });
document.addEventListener('keydown', event => { if(event.key === 'Escape') { closeMenu(); if (navigation.contains(document.activeElement)) menu.focus(); } });
document.addEventListener('click', event => { if(!event.target.closest('.header')) closeMenu(); });
window.matchMedia('(min-width: 801px)').addEventListener('change', closeMenu);
document.querySelector('#year').textContent = new Date().getFullYear();
const mapUrl = 'https://www.google.com/maps/place/مركز+المعلم+للتدريب+قيادة+السيارة،+اربد.....+الكوره/data=!4m2!3m1!1s0x151c65850e5e3fcb:0xf61615a7363f793e';
document.querySelectorAll('[data-map-link]').forEach(link => { link.href=mapUrl; });
const cards = [...document.querySelectorAll('[data-category]')];
document.querySelectorAll('[data-filter]').forEach(button => {
  button.addEventListener('click', () => {
    document.querySelector('.exam-grid').classList.toggle('is-filtered',button.dataset.filter!=='all');
    document.querySelectorAll('[data-filter]').forEach(item => { const selected=item===button; item.classList.toggle('selected',selected); item.setAttribute('aria-pressed',String(selected)); });
    let count=0;
    cards.forEach(card => { const visible=button.dataset.filter==='all'||card.dataset.category==='all'||card.dataset.category===button.dataset.filter; card.hidden=!visible; if(visible){count++;card.classList.add('visible');} });
    document.querySelector('.exam-count').textContent=`${count} اختبارات متاحة`;
  });
});
if('IntersectionObserver' in window){
  if(!reducedMotion.matches) document.documentElement.classList.add('js-motion');
  const observer = new IntersectionObserver(entries => { entries.forEach(entry => { if(entry.isIntersecting){entry.target.classList.add('visible');observer.unobserve(entry.target);} }); },{threshold:0.08});
  document.querySelectorAll('.reveal').forEach(el=>observer.observe(el));
  const activeObserver = new IntersectionObserver(entries=> { entries.forEach(entry=> {if(entry.isIntersecting){navigation.querySelectorAll('a').forEach(link=>link.classList.toggle('active',link.hash===`#${entry.target.id}`));}}); },{rootMargin:'-15% 0px -65% 0px'});
  document.querySelectorAll('main section[id]').forEach(section=>activeObserver.observe(section));
}
const visual=document.querySelector('.hero-visual');
const finePointer=window.matchMedia('(hover:hover) and (pointer:fine)');
visual.addEventListener('pointermove',event=>{if(reducedMotion.matches||!finePointer.matches)return;const rect=visual.getBoundingClientRect();const x=(event.clientX-rect.left)/rect.width-.5;const y=(event.clientY-rect.top)/rect.height-.5;visual.style.transform=`perspective(1100px) rotateY(${x*5}deg) rotateX(${-y*5}deg)`;});
visual.addEventListener('pointerleave',()=>{visual.style.transform='';});
const journey=document.querySelector('.journey-section');
const car=document.querySelector('.road-car');
let scheduled=false;
function updateScroll(){scheduled=false;if(reducedMotion.matches)return;const rect=journey.getBoundingClientRect();const progress=Math.min(1,Math.max(0,(innerHeight-rect.top)/(innerHeight+rect.height)));car.style.right=`${5+progress*80}%`;const heroRect=visual.getBoundingClientRect();if(heroRect.bottom>0&&heroRect.top<innerHeight){document.querySelector('.hero-image').style.transform=`scale(1.08) translateY(${Math.min(16,Math.max(-16,-heroRect.top*.025))}px)`;}}
window.addEventListener('scroll',()=>{if(!scheduled){scheduled=true;requestAnimationFrame(updateScroll);}},{passive:true});
reducedMotion.addEventListener('change',()=>{if(reducedMotion.matches){document.documentElement.classList.remove('js-motion');visual.style.transform='';document.querySelector('.hero-image').style.transform='';car.style.right='5%';}});
updateScroll();

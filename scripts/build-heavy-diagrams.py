"""Original schematic SVGs. Not photographs or copied third-party illustrations."""
from pathlib import Path
from html import escape
out=Path('public/assets/questions/heavy');out.mkdir(parents=True,exist_ok=True)
def rect(x,y,w,h,fill='#d5e5fc',stroke='#1b355d',r=6):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>'
def line(x1,y1,x2,y2,color='#1b355d',width=5):return f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linecap="round"/>'
def circle(x,y,r,fill='#1b355d'):return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>'
def label(x,y,text):return f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Arial,sans-serif" font-size="25" font-weight="bold" fill="#1b355d">{escape(text)}</text>'
def platform():return rect(70,235,450,18,'#6c809d')+circle(130,267,24)+circle(420,267,24)+circle(475,267,24)
scenes={
 'pedals':('جسم متحرك قرب دواسات المركبة',rect(100,45,440,240,'#e8eef6')+line(200,55,200,180)+line(340,55,340,180)+rect(170,175,70,55,'#667e9f')+rect(305,175,70,55,'#667e9f')+rect(240,225,105,36,'#f5b938',r=18)),
 'twin-wheels':('حجر عالق بين إطارين متجاورين',rect(130,45,150,225,'#29394f',r=40)+rect(310,45,150,225,'#29394f',r=40)+rect(185,60,40,195,'#667080',r=20)+rect(365,60,40,195,'#667080',r=20)+'<path d="M275 130 309 120 329 151 313 181 275 171 260 151Z" fill="#ecb847" stroke="#8b6420" stroke-width="3"/>'),
 'unsecured-load':('صندوق على منصة شاحنة دون أربطة',platform()+rect(185,110,180,120,'#d6ab6b')+line(200,122,350,218,'#b18343',3)),
 'low-center':('مقارنة ترتيب A بوزن أثقل أسفل وB بوزن أثقل أعلى',label(160,42,'A')+label(465,42,'B')+rect(65,250,190,14,'#667e9f')+rect(370,250,190,14,'#667e9f')+rect(95,167,130,80,'#16375e')+label(160,215,'')+rect(95,84,130,80,'#b8cce8')+rect(400,167,130,80,'#b8cce8')+rect(400,84,130,80,'#16375e')+label(160,302,'80 kg ↓  /  20 kg ↑')+label(465,302,'20 kg ↓  /  80 kg ↑')),
 'centered-load':('حمولة موزعة حول الخط الوسطي لمنصة الشاحنة',rect(90,45,420,240,'#e3eaf3')+'<path d="M300 30V295" stroke="#175cdb" stroke-width="3" stroke-dasharray="9 7"/>'+rect(165,105,110,110,'#d5ab6c')+rect(325,105,110,110,'#d5ab6c')),
 'damaged-anchor':('نقطة ربط فيها تشقق',rect(100,220,440,25,'#7286a3')+'<path d="M250 219V115Q300 55 350 115V219" fill="none" stroke="#1b355d" stroke-width="25"/>'+'<path d="m261 112-22 9 20 14-23 13" fill="none" stroke="#f25547" stroke-width="7"/>'),
 'edge-protection':('حزام يمر فوق زاوية صندوق حادة',platform()+rect(160,100,260,133,'#d5ab6c')+'<path d="M135 235V93H440V235" fill="none" stroke="#175cdb" stroke-width="12"/>'+circle(137,96,28,'none')+'<circle cx="137" cy="96" r="28" fill="none" stroke="#f5b938" stroke-width="5"/>'),
 'damaged-strap':('نسيج حزام تثبيت به قطع ظاهر',rect(95,115,430,80,'#175cdb',r=2)+'<path d="m280 111 30 25-34 23 30 18-20 23" fill="none" stroke="#fff" stroke-width="12"/>'+line(275,110,260,92,'#175cdb',3)+line(291,115,310,85,'#175cdb',3)),
 'roll-chocks':('مصدات على جانبي حمولة أسطوانية فوق منصة',platform()+circle(295,157,77,'#c5d6ec')+circle(295,157,40,'#f4f7fb')+'<path d="M180 235 225 189 237 235Z M355 235 367 189 412 235Z" fill="#e8b43e" stroke="#8b6420" stroke-width="3"/>'),
 'leaning-load':('صناديق مائلة خارج جانب سطح التحميل',rect(175,240,285,17,'#667e9f')+circle(220,278,24)+circle(410,278,24)+'<g transform="rotate(20 450 240)">'+rect(315,140,145,95,'#d6ab6b')+rect(315,44,145,95,'#d6ab6b')+'</g>'),
 'blocked-exit':('حقائب أمام باب خروج الحافلة',rect(235,30,175,230,'#d4e7ec')+rect(253,48,139,145,'#edf8fc')+line(326,30,326,260,'#667e9f',3)+rect(205,206,110,75,'#d6ab6b')+rect(320,221,120,60,'#175cdb')+rect(240,196,40,12,'#d6ab6b')+line(110,284,520,284)),
 'landing-legs':('أرجل إسناد نصف مقطورة على أرض مستوية',rect(105,55,405,110,'#d5e5fc')+rect(105,164,405,15,'#667e9f')+line(185,180,185,269,'#1b355d',13)+line(245,180,245,269,'#1b355d',13)+rect(160,267,50,12,'#1b355d')+rect(220,267,50,12,'#1b355d')+circle(425,241,34)+circle(490,241,34)+line(75,281,550,281,'#7a8b6c',8))
}
for name,(title,body) in scenes.items():
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 330" width="620" height="330" role="img" aria-labelledby="title"><title id="title">{escape(title)}</title><rect width="620" height="330" rx="16" fill="#f7faff"/>{body}</svg>'
 (out/(name+'.svg')).write_text(svg,encoding='utf8')
print(f'Built {len(scenes)} original heavy-vehicle diagrams')

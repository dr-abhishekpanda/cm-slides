// Exercise every widget on every page and report script errors, NaN/undefined output and text overflow.
// Usage: node tools/qa.js decks/*.html
const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1600,height:956}});
let errs=[];p.on('pageerror',e=>errs.push('pageerror: '+e.message));p.on('console',m=>{if(m.type()==='error')errs.push('console: '+m.text());});
let flagged=0;
for(const f of process.argv.slice(2)){errs=[];
 await p.goto('file://'+path.resolve(f));await p.waitForTimeout(500);
 const n=await p.$$eval('.slide',s=>s.length);const out=[];
 for(let i=0;i<n;i++){
  const r=await p.evaluate(async i=>{window.Deck.show(i);const s=document.querySelector('.slide.active');const res=[];
   s.querySelectorAll('.frag').forEach(x=>x.classList.add('on'));
   s.querySelectorAll('.reveal,.hot').forEach(x=>{x.click();if(!x.classList.contains('open'))res.push('reveal did not open');});
   s.querySelectorAll('.mcq').forEach(q=>{const o=q.querySelectorAll('.opt');const a=+q.dataset.ans;
     if(!(a>=0&&a<o.length)){res.push('mcq data-ans out of range');return;}
     o[a].click();const fb=q.querySelector('.fb');if(fb&&!fb.textContent.trim())res.push('mcq feedback empty');
     if(!o[a].classList.contains('right'))res.push('mcq correct option not marked');});
   const fire=(el,t)=>el.dispatchEvent(new Event(t,{bubbles:true}));
   for(const r of s.querySelectorAll('input[type=range]')){for(const v of [r.min,r.max,(+r.min+ +r.max)/2,r.defaultValue]){r.value=v;fire(r,'input');fire(r,'change');
     const tx=s.innerText;if(/\bNaN\b|undefined|Infinity/.test(tx))res.push('NaN/undefined at '+r.id+'='+v);}}
   for(const sel of s.querySelectorAll('select')){for(let k=0;k<sel.options.length;k++){sel.selectedIndex=k;fire(sel,'change');
     if(/\bNaN\b|undefined/.test(s.innerText))res.push('NaN/undefined at select');}sel.selectedIndex=0;fire(sel,'change');}
   s.querySelectorAll('button.btn').forEach(x=>{x.click();if(/\bNaN\b|undefined/.test(s.innerText))res.push('NaN/undefined after button');});
   await new Promise(r=>setTimeout(r,30));
   s.querySelectorAll('.reveal,.panel,.stat,.opt,.hot,.clip,td,th,li,p,h2,label,.big-num').forEach(e=>{
     if(e.closest('aside,.foot,.run,.tab'))return;
     if(e.scrollWidth>e.clientWidth+3&&getComputedStyle(e).display!=='inline'){res.push('h-overflow '+e.tagName+'.'+e.className+' "'+(e.innerText||'').trim().slice(0,40)+'"');}});
   return [...new Set(res)];},i);
  if(r.length)out.push('p'+String(i+1).padStart(2,'0')+': '+r.join(' | '));}
 if(out.length||errs.length){flagged++;console.log('## '+path.basename(f));out.forEach(x=>console.log('  '+x));[...new Set(errs)].forEach(x=>console.log('  '+x));}}
console.log('decks flagged:',flagged);await b.close();})();

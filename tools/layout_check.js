// Flag content that runs into the footer band or past the right edge, on every page with all steps shown.
// Usage: node tools/layout_check.js decks/*.html
const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1600,height:956}});let total=0;
for(const f of process.argv.slice(2)){await p.goto('file://'+path.resolve(f));await p.waitForTimeout(600);
 const n=await p.$$eval('.slide',s=>s.length);
 for(let i=0;i<n;i++){await p.evaluate(i=>{location.hash='#s'+(i+1)},i);await p.waitForTimeout(60);
  const r=await p.evaluate(()=>{const s=document.querySelector('.slide.active');s.querySelectorAll('.frag').forEach(x=>x.classList.add('on'));
   s.querySelectorAll('.reveal,.hot').forEach(x=>x.classList.add('open'));
   const st=document.getElementById('stage').getBoundingClientRect(),k=st.width/1600;const foot=s.querySelector('.foot');
   const fTop=foot?(foot.getBoundingClientRect().top-st.top)/k:900;const out=[];
   s.querySelectorAll('*').forEach(e=>{if(e.closest('.run,.foot,.tab,.art,aside,.big-n,.poll,svg text')||e.tagName=='svg'&&e.classList.contains('art'))return;
    if(['TEXT','TSPAN'].includes(e.tagName.toUpperCase()))return;const q=e.getBoundingClientRect();if(!q.width||!q.height)return;
    const bot=(q.bottom-st.top)/k,right=(q.right-st.left)/k;
    if(bot>fTop-4||right>1560){const t=(e.innerText||e.tagName).trim().slice(0,40);out.push(`${Math.round(bot)}/${Math.round(right)} ${e.tagName} ${t}`);}});
   return out.slice(0,3);});
  if(r.length){total++;console.log(path.basename(f),'p'+(i+1),r.join(' | '));}}}
 console.log('pages flagged:',total);await b.close();})();

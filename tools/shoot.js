// Screenshot every slide of a built deck (all steps shown) into a contact sheet folder.
// Usage: node tools/shoot.js decks/<file>.html <outdir>
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{const [file,out]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch();const p=await b.newPage({viewport:{width:1600,height:956}});
const errs=[];p.on('pageerror',e=>errs.push(e.message));p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
await p.goto('file://'+path.resolve(file));await p.waitForTimeout(1500);
const n=await p.$$eval('.slide',s=>s.length);
for(let i=0;i<n;i++){await p.evaluate(i=>{location.hash='#s'+(i+1)},i);await p.waitForTimeout(120);
 await p.evaluate(()=>{document.querySelectorAll('.slide.active .frag').forEach(f=>f.classList.add('on'));document.querySelectorAll('.slide.active .reveal').forEach((r,j)=>{if(j%2==0)r.classList.add('open')});});
 await p.waitForTimeout(450);await p.screenshot({path:path.join(out,'s'+String(i+1).padStart(2,'0')+'.png'),clip:{x:0,y:0,width:1600,height:900}});}
// contact sheets of 4
console.log(n,'slides',errs.length?errs:'no errors');await b.close();})();

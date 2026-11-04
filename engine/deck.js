/* CM Slides engine: navigation, steps, notes, contents, timer, and the shared widgets
   (reveal cards, hotspots, MCQs, optional live-poll QR). Deck-specific widgets live in each deck. */
(function(){
  const stage=document.getElementById('stage'), vp=document.getElementById('viewport');
  const slides=[...document.querySelectorAll('.slide')];
  const N=slides.length; let cur=0;
  slides.forEach((s,i)=>{const pn=s.querySelector('.pn'); if(pn) pn.textContent='Page '+String(i+1).padStart(2,'0');});

  function fit(){const k=Math.min(vp.clientWidth/1600,vp.clientHeight/900);stage.style.transform='scale('+k+')';}
  addEventListener('resize',fit); fit();

  const frags=s=>[...s.querySelectorAll('.frag')];
  function show(i,fromBack){
    i=Math.max(0,Math.min(N-1,i));
    slides[cur].classList.remove('active'); cur=i; const s=slides[cur]; s.classList.add('active');
    frags(s).forEach(f=>f.classList.toggle('on',!!fromBack));
    document.getElementById('count').textContent=(cur+1)+' / '+N;
    document.getElementById('prog').style.width=((cur+1)/N*100)+'%';
    const n=s.querySelector('aside.notes');
    document.getElementById('notes').innerHTML='<h4>Page '+(cur+1)+' · '+(s.dataset.title||'')+'</h4>'+(n?n.innerHTML:'<p>No notes.</p>');
    try{history.replaceState(null,'','#s'+(cur+1));}catch(e){}
    s.dispatchEvent(new CustomEvent('slideshown'));
  }
  function next(){const h=frags(slides[cur]).find(f=>!f.classList.contains('on')); if(h){h.classList.add('on');return;} if(cur<N-1) show(cur+1);}
  function prev(){const on=frags(slides[cur]).filter(f=>f.classList.contains('on')); if(on.length){on[on.length-1].classList.remove('on');return;} if(cur>0) show(cur-1,true);}
  const fromHash=()=>{const m=/^#s(\d+)$/.exec(location.hash);return m?+m[1]-1:0;};
  addEventListener('hashchange',()=>{const i=fromHash(); if(i!==cur) show(i,false);});

  const black=document.createElement('div');black.style.cssText='position:fixed;inset:0;background:#000;z-index:9';black.hidden=true;document.body.appendChild(black);
  black.addEventListener('click',()=>black.hidden=true);
  addEventListener('keydown',e=>{
    if(e.target.matches('input,textarea,select')) return;
    const k=e.key;
    if(['ArrowRight','PageDown',' '].includes(k)){e.preventDefault();next();}
    else if(['ArrowLeft','PageUp'].includes(k)){e.preventDefault();prev();}
    else if(k==='Home') show(0); else if(k==='End') show(N-1);
    else if(k==='n'||k==='N') toggle('notes');
    else if(k==='o'||k==='O') toggle('toc');
    else if(k==='f'||k==='F') fs();
    else if(k==='b'||k==='B'||k==='.') black.hidden=!black.hidden;
    else if(k==='Escape'){document.getElementById('toc').hidden=true;black.hidden=true;}
  });
  document.getElementById('bNext').onclick=next; document.getElementById('bPrev').onclick=prev;
  let sx=null; vp.addEventListener('touchstart',e=>{sx=e.touches[0].clientX},{passive:true});
  vp.addEventListener('touchend',e=>{if(sx==null)return;const dx=e.changedTouches[0].clientX-sx;if(Math.abs(dx)>60)(dx<0?next:prev)();sx=null;});
  function toggle(id){const n=document.getElementById(id);n.hidden=!n.hidden;}
  document.getElementById('bNotes').onclick=()=>toggle('notes'); document.getElementById('bToc').onclick=()=>toggle('toc');
  const tl=document.getElementById('tocList');
  slides.forEach((s,i)=>{const li=document.createElement('li');const b=document.createElement('button');b.textContent=(i+1)+'. '+(s.dataset.title||'');b.onclick=()=>{show(i);toggle('toc');};li.appendChild(b);tl.appendChild(li);});
  function fs(){try{if(!document.fullscreenElement)document.documentElement.requestFullscreen().catch(()=>{});else document.exitFullscreen();}catch(e){}}
  document.getElementById('bFs').onclick=fs;

  let t0=null,acc=0,tick=null;const ck=document.getElementById('clock');
  const fmt=s=>String(Math.floor(s/60)).padStart(2,'0')+':'+String(Math.floor(s%60)).padStart(2,'0');
  ck.onclick=()=>{if(tick){acc+=(Date.now()-t0)/1000;clearInterval(tick);tick=null;}else{t0=Date.now();tick=setInterval(()=>{const s=acc+(Date.now()-t0)/1000;ck.textContent=fmt(s)+' / 60';ck.style.color=s>3600?'#E9B98D':'';},500);}};

  /* shared widgets */
  document.querySelectorAll('.reveal,.hot').forEach(b=>b.addEventListener('click',()=>b.classList.toggle('open')));
  document.querySelectorAll('.mcq').forEach(q=>{
    const ans=+q.dataset.ans, fb=q.querySelector('.fb');
    q.querySelectorAll('.opt').forEach((o,i)=>o.addEventListener('click',()=>{
      if(q.querySelector('.right')) return;
      if(i===ans){o.classList.add('right'); if(fb) fb.textContent=fb.dataset.fb||'';}
      else o.classList.add('wrong');
    }));
  });

  /* optional live poll: set window.POLL_URL in the deck */
  const POLL=window.POLL_URL||'';
  if(POLL){document.querySelectorAll('[data-poll]').forEach(p=>p.classList.add('on'));
    const s=document.createElement('script');s.src='https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js';
    s.onload=()=>document.querySelectorAll('[data-poll] .qr').forEach(q=>new QRCode(q,{text:POLL,width:120,height:120}));
    s.onerror=()=>document.querySelectorAll('[data-poll] .qr').forEach(q=>{q.textContent=POLL;q.style.fontSize='11px';q.style.wordBreak='break-all';});
    document.head.appendChild(s);}

  window.Deck={show,next,prev,slides};
  show(fromHash());
})();

const $=s=>document.querySelector(s);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const LS={get(k,d){try{const v=localStorage.getItem(k);return v==null?d:JSON.parse(v)}catch(e){return d}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};

// ---------------------------------------------------------------- state (stored values are untrusted)
let prog=LS.get('ro.cards',{}); if(!prog||typeof prog!=='object'||Array.isArray(prog)) prog={};
const known=id=>{const p=prog[id];return !!(p&&typeof p==='object'&&p.s)};
const markSeen=id=>{prog[id]={s:1,t:new Date().toISOString()};LS.set('ro.cards',prog); if(typeof refreshProgress==='function') refreshProgress();};
let reads=LS.get('ro.read',{}); if(!reads||typeof reads!=='object'||Array.isArray(reads)) reads={};      // the furthest point reached in each chapter, 0 to 1
const readOf=id=>{const v=reads[id]; return typeof v==='number'&&v>0?Math.min(1,v):0;};
let readTimer=0, readDirty=false; const flushReads=()=>{clearTimeout(readTimer); if(readDirty){readDirty=false; LS.set('ro.read',reads);}};
let qs=LS.get('ro.q',{}); if(!qs||typeof qs!=='object'||Array.isArray(qs)) qs={};
const saveQ=()=>{LS.set('ro.q',qs); if(typeof refreshProgress==='function') refreshProgress();};
let _sig=null; const sigOf=id=>{if(!_sig){_sig={}; DATA.cards.forEach(c=>{if(c.sig)_sig[c.id]=c.sig;});} return _sig[id];};
const qSel=id=>{const v=qs[id];return v&&typeof v==='object'&&v.sig&&v.sig===sigOf(id)&&Array.isArray(v.sel)&&v.sel.length&&v.sel.every(x=>typeof x==='string')?v.sel:null;};
const savedTheme=LS.get('ro.theme',null);
if(savedTheme==='light'||savedTheme==='dark') document.documentElement.dataset.theme=savedTheme;

// ---------------------------------------------------------------- usage events
// ANALYTICS is null unless a release build turned usage counts on. track() sends only the events and properties in DATA.aschema, which is also the
// source of the privacy text on the About page. It sets no cookie and stores nothing in the browser.
const AS_BY={}; (DATA.aschema||[]).forEach(e=>{AS_BY[e.name]=e;});
const asOk=(c,v)=>c.kind==='bool'?typeof v==='boolean':c.kind==='enum'?(typeof v!=='boolean'&&c.values.includes(v)):c.kind==='pattern'?(typeof v==='string'&&new RegExp(c.re).test(v)):false;
const asTok=(p,v)=>typeof v==='boolean'?p.tokens[v?0:1]:String(v).replace(/[^A-Za-z0-9._,:+\/-]/g,'_');
function track(ev,props){
  if(!ANALYTICS) return;
  try{
    const e=AS_BY[ev]; if(!e) return; const out={};
    for(const p of e.props){const v=props&&props[p.name]; if(v===undefined||!asOk(p.check,v)) return; out[p.name]=v;}      // a property that is not listed is left out; an event missing a listed one is not sent
    if(ANALYTICS.backend==='endpoint') fetch(ANALYTICS.url,{method:'POST',mode:'no-cors',credentials:'omit',referrerPolicy:'no-referrer',keepalive:true,headers:{'Content-Type':'text/plain;charset=UTF-8'},body:JSON.stringify({event:ev,props:out})}).catch(()=>{});
    else{const img=new Image(); img.referrerPolicy='no-referrer'; img.src=ANALYTICS.url+'?p='+encodeURIComponent(['ev',ev,...e.props.map(p=>asTok(p,out[p.name]))].join('/'))+'&e=true&rnd='+Math.random().toString(36).slice(2,8);}
  }catch(_){}
}
const secsBin=s=>s<5?'lt5':s<15?'5-15':s<30?'15-30':s<60?'30-60':'gt60';
// A question is timed while at least half of it is in view (or half of the screen, for a tall question) and the tab is shown, from when it is drawn or last reset until it is answered.
let qIO=null; const qWatched=new Set();
const qNow=()=>performance.now();
function qSet(el,on){if(on&&!document.hidden){if(el._since==null) el._since=qNow();} else if(el._since!=null){el._vis+=qNow()-el._since; el._since=null;}}
function qWatch(el){
  if(!ANALYTICS||!('IntersectionObserver' in window)) return;
  el._vis=0; el._since=null; el._seen=false; qWatched.add(el);
  if(!qIO) qIO=new IntersectionObserver(es=>es.forEach(en=>{const on=en.isIntersecting&&en.intersectionRect.height>=.5*Math.min(en.boundingClientRect.height,window.innerHeight); en.target._seen=on; qSet(en.target,on);}),{threshold:[0,.1,.2,.3,.4,.5,.6,.7,.8,.9,1]});
  qIO.observe(el);
}
function qReset(el){if(!ANALYTICS||el._vis===undefined) return; el._vis=0; el._since=null; qSet(el,el._seen);}
function qSecs(el){return el._vis===undefined?0:(el._vis+(el._since!=null?qNow()-el._since:0))/1000;}
document.addEventListener('visibilitychange',()=>{qWatched.forEach(el=>{if(el.isConnected) qSet(el,el._seen&&!document.hidden);});});
// the identifier of a question: topic, its number among the topic's questions, and the first six characters of the question's hash
function itemOf(el){const id=el.dataset.id, i=id.lastIndexOf(':'), tid=id.slice(0,i); return tid+':'+(+id.slice(i+1)-flashOf(tid).length)+':'+String(el.dataset.sig).slice(0,6);}
// answers given so far to a question, from the stored state (an untrusted value: a whole number of 1 or more, or none)
const attemptsOf=el=>{const v=qs[el.dataset.id]; return v&&typeof v==='object'&&v.sig===el.dataset.sig&&Number.isInteger(v.n)&&v.n>0&&v.n<1000?v.n:0;};
// store an answer the learner has just given, count it, and send the usage event
function ansRec(el,rec,kind,ok,choice){
  const n=attemptsOf(el)+1; rec.n=n; qs[el.dataset.id]=rec; saveQ();
  if(ANALYTICS){const help=!!el._help; el._help=false; track('ans',{item:itemOf(el),kind,ok:!!ok,attempt:Math.min(n,3),choice:String(choice),secs:secsBin(qSecs(el)),help});}
}
// Try again: the answer is cleared, and the count of answers so far is kept
function ansClear(el){const n=attemptsOf(el); if(n) qs[el.dataset.id]={sig:el.dataset.sig,n}; else delete qs[el.dataset.id]; saveQ(); qReset(el);}

// ---------------------------------------------------------------- data
const dom=n=>DATA.domains.find(d=>d.n===n);
const topic=id=>DATA.topics.find(t=>t.id===id);
const cardsOf=id=>DATA.cards.filter(c=>c.topic===id);
const topicsOfDom=n=>DATA.topics.filter(t=>t.dom===n);
const cardsOfDom=n=>DATA.cards.filter(c=>c.dom===n);
const flashOf=id=>DATA.cards.filter(c=>c.topic===id&&!c.opts);
const quizOf=id=>DATA.cards.filter(c=>c.topic===id&&c.opts);
const allFlash=()=>DATA.cards.filter(c=>!c.opts);
const activeDoms=()=>DATA.domains.filter(d=>topicsOfDom(d.n).length);
const seenCount=cs=>cs.filter(c=>known(c.id)).length;
const idx=s=>{const n=parseInt(s,10);return Number.isFinite(n)&&n>=1?n-1:0};
function mixCards(){
  const lists=DATA.topics.map(t=>flashOf(t.id)); const out=[]; const max=Math.max(0,...lists.map(l=>l.length));
  for(let i=0;i<max;i++) for(const l of lists) if(l[i]) out.push(l[i]);
  return out;
}
function deck(kind,key){
  if(kind==='t'){const t=topic(key); return t?{kind,key,cards:flashOf(key),title:t.num+' '+t.title,back:'#t/'+key,backLabel:'Read the chapter',base:'#t/'+key+'/c'}:null;}
  if(kind==='mix') return {kind,key:'',cards:mixCards(),title:'All topics',back:'',backLabel:'',base:'#mix'};
  return null;
}
const slideHref=(base,i)=>base+(i>0?'/'+(i+1):'');

// ---------------------------------------------------------------- linac dial
function catAngles(){const A0=-90,A1=270,gap=3,span=(A1-A0)/DATA.domains.length;return DATA.domains.map((c,i)=>[A0+i*span+gap/2,A0+(i+1)*span-gap/2]);}
const rad=d=>d*Math.PI/180;
const lim=a=>{a=((a%360)+360)%360;return a>180?a-360:a;};
function arcPath(cx,cy,r,a0,a1){const x0=cx+r*Math.cos(rad(a0)),y0=cy+r*Math.sin(rad(a0)),x1=cx+r*Math.cos(rad(a1)),y1=cy+r*Math.sin(rad(a1));return `M${x0.toFixed(1)},${y0.toFixed(1)} A${r},${r} 0 ${a1-a0>180?1:0} 1 ${x1.toFixed(1)},${y1.toFixed(1)}`;}
function linacGroup(cx,cy,size,angle){const s=size,x=cx-0.494*s,y=cy-0.47*s;return `<image href="${LINAC.base}" x="${x}" y="${y}" width="${s}" height="${s}"/><g class="gantry" style="transform:rotate(${lim(angle)}deg)"><image href="${LINAC.gantry}" x="${x}" y="${y}" width="${s}" height="${s}"/></g><image href="${LINAC.couch}" x="${x}" y="${y}" width="${s}" height="${s}"/>`;}
function dialSVG(mobile){
  const angs=catAngles();
  const G=mobile?{vw:860,vh:780,cx:430,cy:390,R:200,S:360,fn:26,fs:22,fnum:22,lo:26}:{vw:1120,vh:740,cx:560,cy:370,R:245,S:500,fn:24,fs:17,fnum:24,lo:30};
  const {cx,cy,R,S}=G; const out=[`<circle class="ring" cx="${cx}" cy="${cy}" r="${R-26}"/>`];
  DATA.domains.forEach((c,ci)=>{
    const [a0,a1]=angs[ci], am=(a0+a1)/2, cs=DATA.cards.filter(x=>x.dom===c.n&&x.opts), k=cs.filter(x=>qSel(x.id)).length, on=topicsOfDom(c.n).length>0, nt=topicsOfDom(c.n).length;
    const co=Math.cos(rad(am)), sn=Math.sin(rad(am));
    const anchor=co>0.3?'start':(co<-0.3?'end':'middle');
    const lx=cx+(R+G.lo)*co, ly=cy+(R+G.lo)*sn, nx=cx+(R-62)*co, ny=cy+(R-62)*sn;
    const lines=mobile?c.linesM:c.lines;
    const lh=G.fn*1.05, side=Math.abs(sn)<=0.3;
    let nameY=sn<-0.3?ly-6-(lines.length-1)*lh:ly+16-(side?(lines.length-1)*lh/2:0);
    let smY=sn<-0.3?nameY-lh:(side?nameY-lh-6:ly-10);
    const name=lines.map((t,i)=>`<tspan x="${lx.toFixed(1)}" dy="${i?lh:0}">${esc(t)}</tspan>`).join('');
    const smParts=on?[`${nt} topic${nt===1?'':'s'}`].concat(cs.length?[`${cs.length} questions`]:[]):['no topics yet'], lhS=G.fs*1.15, two=mobile&&smParts.length>1;
    if(sn>0.3){smY=ly+12; nameY=smY+(two?lhS:0)+lh+2;}
    const smTop=sn>0.3?smY:smY-(two?lhS:0), smHTML=two?smParts.map((t,i)=>`<tspan x="${lx.toFixed(1)}" dy="${i?lhS.toFixed(1):0}">${t}</tspan>`).join(''):smParts.join(' · ');
    const inner=`<path d="${arcPath(cx,cy,R,a0,a1)}"/>
      <text class="num" style="font-size:${G.fnum}px" x="${nx.toFixed(1)}" y="${(ny+8).toFixed(1)}" text-anchor="middle">${c.roman}</text>
      <text class="sm" style="font-size:${G.fs}px" x="${lx.toFixed(1)}" y="${smTop.toFixed(1)}" text-anchor="${anchor}">${smHTML}</text>
      <text class="name" style="font-size:${G.fn}px" x="${lx.toFixed(1)}" y="${nameY.toFixed(1)}" text-anchor="${anchor}">${name}</text>`;
    out.push(on?`<a href="#t/${(topicsOfDom(c.n)[0]||{}).id}" class="seg" data-dom="${c.n}" data-ang="${am.toFixed(1)}">${inner}</a>`:`<g class="seg off">${inner}</g>`);
  });
  return `<svg viewBox="0 0 ${G.vw} ${G.vh}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Domains">${linacGroup(cx,cy,S,0)}${out.join('')}</svg>`;
}
function ringSVG(frac){const r=46,c=2*Math.PI*r;return `<svg class="ring" viewBox="0 0 120 120" aria-hidden="true"><circle class="track" cx="60" cy="60" r="${r}"/><circle class="fill" cx="60" cy="60" r="${r}" stroke-dasharray="${c.toFixed(1)}" stroke-dashoffset="${(c*(1-frac)).toFixed(1)}"/>${linacGroup(60,60,84,frac*180)}</svg>`;}
let dialTimer=null, progMode=null, progFn=null, progRaf=0, sideManual=false, sideHold=0;
// the sidebar is an accordion: one domain open at a time. On Home the machine opens the domain it points at.
function openDom(n){document.querySelectorAll('#side .blk[data-dom]').forEach(b=>{const o=+b.dataset.dom===n; b.classList.toggle('open',o); const bt=b.querySelector('.nm'); if(bt) bt.setAttribute('aria-expanded',String(o));});}
// the linac as a progress indicator: the ring fills and the gantry turns as the page is read, the deck is stepped through, or the questions are answered
const lpHTML=()=>`<div class="lp" role="progressbar" aria-label="Progress on this page" aria-valuemin="0" aria-valuemax="100" aria-valuenow="0"><div class="lpr">${ringSVG(0)}</div><div class="lpt"><b>0%</b><span></span></div></div>`;
function setProgress(frac,big,small,tip){frac=Math.max(0,Math.min(1,frac)); const C=2*Math.PI*46, pct=Math.round(100*frac);
  document.querySelectorAll('.lp').forEach(el=>{const f=el.querySelector('circle.fill'), g=el.querySelector('.gantry'); if(f) f.setAttribute('stroke-dashoffset',(C*(1-frac)).toFixed(1)); if(g) g.style.transform=`rotate(${lim(frac*180)}deg)`;
    el.setAttribute('aria-valuenow',String(pct)); el.setAttribute('aria-valuetext',big+' '+small+(tip?'. '+tip:'')); el.title=tip||''; el.querySelector('b').textContent=big; el.querySelector('span').textContent=small;});}
// the total: chapters read (weighted by length), flash cards seen, and questions answered, a third each
function courseStats(){
  const W=DATA.topics.reduce((a,t)=>a+t.words,0)||1, read=DATA.topics.reduce((a,t)=>a+t.words*readOf(t.id),0)/W;
  const fl=allFlash(), cards=fl.length?seenCount(fl)/fl.length:0, qz=DATA.cards.filter(c=>c.opts), nq=qz.length+MUC().length, q=nq?(qz.filter(c=>qSel(c.id)).length+MUC().filter(c=>muDone(c.id)).length)/nq:0;      // MU cases count with the questions
  return {read,cards,q,total:(read+cards+q)/3};
}
function showCourse(){const s=courseStats(), p=100*s.total, pc=x=>Math.round(100*x)+'%';
  setProgress(s.total,(p<10?p.toFixed(1):String(Math.round(p)))+'%','of the course',`Chapters read ${pc(s.read)}, flash cards seen ${pc(s.cards)}, questions answered ${pc(s.q)}`);}
// reading a chapter moves the linac: the furthest point reached counts toward the chapters read
const chapterProg=id=>()=>{const mx=document.documentElement.scrollHeight-innerHeight, f=mx>0?Math.min(1,Math.max(0,scrollY/mx)):1, cur=readOf(id), nv=f>=0.995?1:Math.round(f*1000)/1000;
  if(nv>cur){reads[id]=nv; readDirty=true; clearTimeout(readTimer); readTimer=setTimeout(flushReads,600);} showCourse();};
function refreshProgress(){ if(progFn) progFn(); spySide(); }
function gantryAngle(g){const t=getComputedStyle(g).transform; if(!t||t==='none') return 0; const v=t.match(/matrix\(([^)]+)\)/)[1].split(',').map(Number); let a=Math.atan2(v[1],v[0])*180/Math.PI; if(Math.abs(a)>179.9){const an=g.getAnimations()[0]; a=an&&(an.currentTime%220000)>=110000?-180:180;} return Math.round(a*100)/100;}
function bindDial(){
  if(dialTimer){clearInterval(dialTimer); dialTimer=null;}
  const side=[...document.querySelectorAll('.side .blk[data-dom]')], N=DATA.domains.length, span=360/N, still=matchMedia('(prefers-reduced-motion:reduce)').matches;
  const mark=n=>{side.forEach(b=>b.classList.toggle('pt',+b.dataset.dom===n)); openDom(n);};   // the domain the machine points at is lit and opened in the list
  const domAt=a=>Math.floor((((a%360)+360)%360)/span)%N+1;                        // a segment's centre is at (angle + 90) degrees on the gantry
  // pointing at a segment turns the machine and opens that domain in the list at once, not as the machine passes each domain on the way
  document.querySelectorAll('.dial').forEach(dial=>{const g=dial.querySelector('.gantry'); if(!g) return;
    dial.querySelectorAll('a.seg').forEach(s=>{const turn=()=>{const from=gantryAngle(g), to=lim((+s.dataset.ang)+90); dial.classList.remove('spin'); g.style.transition='none'; g.style.transform=`rotate(${from}deg)`; void g.getBoundingClientRect(); g.style.transition=''; g.style.transform=`rotate(${to}deg)`; sideManual=false; sideHold=Date.now()+1400; mark(domAt(to));}; s.addEventListener('mouseenter',turn); s.addEventListener('focus',turn); s.addEventListener('touchstart',turn,{passive:true});});});
  const vis=[...document.querySelectorAll('.dial')].find(d=>d.getClientRects().length&&d.querySelector('.gantry'));
  if(!side.length||!vis||still) return;
  const g=vis.querySelector('.gantry'); let last=-1;
  dialTimer=setInterval(()=>{ if(!g.isConnected){clearInterval(dialTimer); dialTimer=null; return;} const n=domAt(gantryAngle(g)); if(Date.now()<sideHold){last=n; return;} if(n!==last){last=n; if(!sideManual) mark(n);} },100);
}

// ---------------------------------------------------------------- views
const figHTML=x=>x.fig&&FIG[x.fig]?`<div class="figs"><div>${FIG[x.fig]}</div></div>`:'';
function homeView(){
  return `<h1 class="sr">Home</h1>
  <h2>Exam domains</h2>
  <p class="small">Select a domain to open its first topic.</p>
  <div class="dial big spin">${dialSVG(false)}</div><div class="dial m spin">${dialSVG(true)}</div>`;
}
function topicQuestions(id){
  const t=topic(id), qc=quizOf(id), n=qc.length, k=qc.filter(c=>qSel(c.id)).length, i=DATA.topics.findIndex(x=>x.id===id), nx=DATA.topics[i+1], pv=DATA.topics[i-1], nf=flashOf(id).length;
  const d=document.createElement('div'); d.innerHTML=t.html; const by={}; d.querySelectorAll('.pq').forEach(e=>{by[e.dataset.id]=e.outerHTML;});     // the question cards, taken from the chapter page
  const ordered=['Easy','Moderate','Challenging'].flatMap(l=>qc.filter(c=>c.lvl===l));      // the order they were written in, from recall toward multi-step; not shown
  const body=`<div class="checks">${ordered.map(c=>by[c.id]||'').join('')}</div>`;
  return `<p class="crumb">Questions › ${esc(t.num)} ${esc(t.title)}</p>
  <h1><span class="sn">${esc(t.num)}</span>${esc(t.title)}</h1>
  <p class="lead">${n} question${n===1?'':'s'}${k?`, ${k} answered`:''}.</p>
  <p class="tocx"><a href="#t/${id}">Read the chapter</a>${nf?` · <a href="#t/${id}/c">Flash cards (${nf})</a>`:''}</p>
  <div class="guide qpage">${body}</div>
  <div class="endrow">${pv?`<a class="btn" href="#t/${pv.id}/q">Previous topic</a>`:''}${nx?`<a class="btn primary" href="#t/${nx.id}/q">Next topic</a>`:''}<a class="btn" href="#t/${id}">Read the chapter</a></div>`;
}
function topicView(id){
  const t=topic(id), d=dom(t.dom), nq=quizOf(id).length, nf=flashOf(id).length;
  const i=DATA.topics.findIndex(x=>x.id===id), nx=DATA.topics[i+1], pv=DATA.topics[i-1];
  const toc=(t.secs||[]).map(s=>`<li><a href="#t/${id}" data-go="${esc(s.id)}"><span class="sn">${esc(s.n)}</span>${s.t}</a></li>`).join('')+(nq?`<li><a href="#t/${id}" data-go="${id}-q">Practice questions <span class="muted">(${nq})</span></a></li>`:'');
  return `<p class="crumb"><a href="#home">Home</a> › ${esc(d.roman)}. ${esc(d.name)}</p>
  <h1><span class="sn">${esc(t.num)}</span>${esc(t.title)}</h1>
  <nav class="toc" aria-label="On this page"><div class="hd">On this page</div><ol>${toc}</ol>${nf||nq?`<p class="tocx">${nf?`<a href="#t/${id}/c">Flash cards for this topic (${nf})</a>`:''}${nf&&nq?' · ':''}${nq?`<a href="#t/${id}/q">Questions for this topic (${nq})</a>`:''}</p>`:''}</nav>
  <div class="guide">${t.html}</div>
  <div class="endrow">${pv?`<a class="btn" href="#t/${pv.id}">Previous topic</a>`:''}${nx?`<a class="btn primary" href="#t/${nx.id}">Next topic</a>`:''}${nf?`<a class="btn" href="#t/${id}/c">Flash cards (${nf})</a>`:''}${nq?`<a class="btn" href="#t/${id}/q">Questions (${nq})</a>`:''}</div>`;
}
// ---------------------------------------------------------------- Work it out: a calculator that carries units
const ALIAS={Hz:{s:-1},Bq:{s:-1},N:{J:1,m:-1}};
const DIMS={J:[1,2,-2,0],eV:[1,2,-2,0],keV:[1,2,-2,0],MeV:[1,2,-2,0],m:[0,1,0,0],cm:[0,1,0,0],mm:[0,1,0,0],'µm':[0,1,0,0],nm:[0,1,0,0],'Å':[0,1,0,0],pm:[0,1,0,0],fm:[0,1,0,0],
  s:[0,0,1,0],min:[0,0,1,0],h:[0,0,1,0],d:[0,0,1,0],y:[0,0,1,0],kHz:[0,0,-1,0],MHz:[0,0,-1,0],GHz:[0,0,-1,0],kBq:[0,0,-1,0],MBq:[0,0,-1,0],GBq:[0,0,-1,0],TBq:[0,0,-1,0],mCi:[0,0,-1,0],Ci:[0,0,-1,0],
  kg:[1,0,0,0],g:[1,0,0,0],mg:[1,0,0,0],ng:[1,0,0,0],u:[1,0,0,0],C:[0,0,0,1]};
const DIMNAME={'0,0,0,0':'a pure number','0,1,0,0':'a length','0,0,1,0':'a time','1,0,0,0':'a mass','1,2,-2,0':'an energy','0,0,-1,0':'a rate (1/time)','0,0,0,1':'a charge','1,1,-2,0':'a force'};
const SUPD='⁰¹²³⁴⁵⁶⁷⁸⁹', SUPV={'⁰':0,'¹':1,'²':2,'³':3,'⁴':4,'⁵':5,'⁶':6,'⁷':7,'⁸':8,'⁹':9};
const supStr=n=>String(n).replace(/-/g,'⁻').replace(/\d/g,d=>SUPD[d]);
function unitTok(tok){const m=tok.match(/^(.*?)(⁻?[⁰¹²³⁴⁵⁶⁷⁸⁹]+)?$/); let e=1; if(m[2]){const neg=m[2][0]==='⁻'; e=(neg?-1:1)*parseInt([...m[2]].filter(c=>c!=='⁻').map(c=>SUPV[c]).join(''),10);} return [m[1],e];}
function uput(m,s,e){ if(ALIAS[s]){for(const [s2,e2] of Object.entries(ALIAS[s])) uput(m,s2,e*e2); return;} m[s]=(m[s]||0)+e; if(!m[s]) delete m[s]; }
function uparse(str){const m={}; if(!str) return m; const p=str.split('/'); const add=(x,sg)=>{ if(x) x.split('·').forEach(t=>{t=t.trim(); if(t){const [s,e]=unitTok(t); uput(m,s,sg*e);}}); }; add(p[0],1); if(p[1]) add(p[1],-1); return m;}
const umul=(a,b,sg)=>{const m={...a}; for(const [s,e] of Object.entries(b)) uput(m,s,(sg||1)*e); return m;};
const ueq=(a,b)=>{const ka=Object.keys(a); return ka.length===Object.keys(b).length&&ka.every(k=>a[k]===b[k]);};
const unone=a=>Object.keys(a).length===0;
function ustr(m){const n=[],d=[]; Object.keys(m).sort().forEach(s=>{const e=m[s]; (e>0?n:d).push(s+(Math.abs(e)>1?supStr(Math.abs(e)):''));}); return (n.join('·')||(d.length?'1':''))+(d.length?'/'+(d.length>1?'('+d.join('·')+')':d[0]):'');}
function udims(m){const v=[0,0,0,0]; for(const [s,e] of Object.entries(m)){const d=DIMS[s]; if(!d) return null; for(let i=0;i<4;i++) v[i]+=e*d[i];} return v;}
const dimName=m=>{const d=udims(m); return d?(DIMNAME[d.join(',')]||ustr(m)):ustr(m);};
function fmtNum(x){
  if(!isFinite(x)) return String(x); if(x===0) return '0'; const a=Math.abs(x);
  if(a>=1e5||a<1e-3){let e=Math.floor(Math.log10(a)), s=(a/Math.pow(10,e)).toPrecision(3); if(parseFloat(s)>=10){e+=1; s=(a/Math.pow(10,e)).toPrecision(3);} return (x<0?'−':'')+parseFloat(s)+' × 10'+supStr(e);}
  return String(parseFloat(x.toPrecision(3))).replace('-','−');
}
class CErr extends Error{constructor(m,soft){super(m); this.soft=!!soft;}}
const needPure=(a,name)=>{ if(!unone(a.u)) throw new CErr(name+' needs a number without units. This has units of '+ustr(a.u)+'; cancel or convert them first.'); return a.v; };
const FUN={
  '√(':a=>{ if(Object.values(a.u).some(e=>e%2!==0)) throw new CErr('A square root needs every unit to have an even power; this has '+ustr(a.u)+'.'); if(a.v<0) throw new CErr('Square root of a negative number.'); const u={}; for(const [s,e] of Object.entries(a.u)) u[s]=e/2; return {v:Math.sqrt(a.v),u}; },
  'ln(':a=>{const x=needPure(a,'ln'); if(x<=0) throw new CErr('Logarithm of a number that is not positive.'); return {v:Math.log(x),u:{}};},
  'log₂(':a=>{const x=needPure(a,'log₂'); if(x<=0) throw new CErr('Logarithm of a number that is not positive.'); return {v:Math.log2(x),u:{}};},
  'log₁₀(':a=>{const x=needPure(a,'log₁₀'); if(x<=0) throw new CErr('Logarithm of a number that is not positive.'); return {v:Math.log10(x),u:{}};},
  '2^(':a=>({v:Math.pow(2,needPure(a,'2^')),u:{}}), '10^(':a=>({v:Math.pow(10,needPure(a,'10^')),u:{}}), 'e^(':a=>({v:Math.exp(needPure(a,'e^')),u:{}})
};
function evalToks(toks){
  let i=0; const isOp=o=>toks[i]&&toks[i].k==='op'&&toks[i].o===o;
  function expr(){ let a=term(); while(isOp('+')||isOp('−')){ const op=toks[i++].o, b=term();
      if(!ueq(a.u,b.u)) throw new CErr('Cannot '+(op==='+'?'add':'subtract')+' '+(ustr(a.u)||'a pure number')+' and '+(ustr(b.u)||'a pure number')+'. Convert to the same unit first.');
      a={v:op==='+'?a.v+b.v:a.v-b.v,u:a.u}; } return a; }
  function term(){ let a=unary(); while(isOp('×')||isOp('÷')){ const op=toks[i++].o, b=unary();
      if(op==='÷'&&b.v===0) throw new CErr('Division by zero.');
      a=op==='×'?{v:a.v*b.v,u:umul(a.u,b.u)}:{v:a.v/b.v,u:umul(a.u,b.u,-1)}; } return a; }
  function unary(){ if(isOp('−')){ i++; const a=unary(); return {v:-a.v,u:a.u}; } return postfix(); }
  function postfix(){ let a=primary(); while(isOp('²')){ i++; const u={}; for(const [s,e] of Object.entries(a.u)) u[s]=2*e; a={v:a.v*a.v,u}; } return a; }
  function primary(){ const t=toks[i]; if(!t) throw new CErr('The expression is incomplete.',true);
    if(t.k==='v'){ i++; return {v:t.v,u:t.u}; }
    if(t.k==='fn'){ i++; const a=expr(); if(!isOp(')')) throw new CErr('A closing bracket is missing.',true); i++; return FUN[t.o](a); }
    if(t.k==='op'&&t.o==='('){ i++; const a=expr(); if(!isOp(')')) throw new CErr('A closing bracket is missing.',true); i++; return a; }
    throw new CErr('An operator needs a value after it.',true); }
  const r=expr(); if(i<toks.length) throw new CErr('Two values need an operator between them, or there is an extra symbol.',true); return r;
}
function initCalc(el){
  const box=el.querySelector('details.calc'); if(!box||!el.dataset.calc) return;
  let spec,vals; try{spec=JSON.parse(el.dataset.calc); vals=JSON.parse(el.dataset.vals||'[]');}catch(e){box.remove(); return;}
  const target=uparse(spec.unit), body=box.querySelector('.cb'); let toks=[];
  const tile=t=>`<button type="button" class="tile" data-id="${esc(t.id)}">${esc(t.t)}</button>`;
  body.innerHTML=`<div class="cg"><div class="hd">Givens and constants</div><div class="tiles">${spec.tiles.map(tile).join('')}</div></div>
    <div class="cg"><div class="hd">Operators</div><div class="tiles">${spec.ops.map(o=>`<button type="button" class="tile op" data-op="${esc(o)}">${esc(o)}</button>`).join('')}</div></div>
    <div class="cg"><div class="hd">Your calculation</div><div class="expr" aria-live="polite"></div><p class="cres" aria-live="polite"></p>
    <div class="acts"><button type="button" class="btn sm" data-act="undo">Remove last</button><button type="button" class="btn sm" data-act="clear">Clear</button><button type="button" class="btn sm primary" data-act="use" hidden></button></div></div>`;
  const exprEl=body.querySelector('.expr'), resEl=body.querySelector('.cres'), useBtn=body.querySelector('[data-act="use"]');
  function redraw(){
    exprEl.innerHTML=toks.length?toks.map(t=>`<span>${esc(t.s)}</span>`).join(' '):'<span class="muted">Tap values and operators to build the calculation.</span>';
    body.querySelectorAll('[data-act="undo"],[data-act="clear"]').forEach(x=>x.hidden=!toks.length);
    useBtn.hidden=true; resEl.className='cres'; resEl.textContent=''; if(!toks.length) return;
    try{
      const r=evalToks(toks), same=ueq(r.u,target); let msg='= '+fmtNum(r.v)+' '+(same?spec.unit:ustr(r.u));
      if(same){ let k=-1,kd=1e9; vals.forEach((v,i)=>{const dd=Math.abs(r.v-v)/Math.abs(v); if(dd<=0.015&&dd<kd){kd=dd; k=i;}});
        if(k>=0){msg+='. Matches option '+'ABCDEFG'[k]+'.'; useBtn.textContent='Select '+'ABCDEFG'[k]; useBtn.dataset.k=k; useBtn.hidden=false;} else msg+='. No option matches this result.'; }
      else{ const dr=udims(r.u), dt=udims(target);
        if(dr&&dt&&dr.join()===dt.join()) msg+='. The answer is in '+spec.unit+'; convert with a conversion factor.';
        else{ resEl.classList.add('bad'); msg+='. The answer must be '+dimName(target)+' in '+spec.unit+'; this is '+dimName(r.u)+'.'; } }
      resEl.textContent=msg.trim();
    }catch(err){ if(!(err instanceof CErr)) throw err; resEl.textContent=err.message; resEl.classList.add(err.soft?'soft':'bad'); }
  }
  body.addEventListener('click',e=>{
    const b=e.target.closest('button'); if(!b||!body.contains(b)) return;
    if(b.dataset.id!==undefined){const t=spec.tiles.find(x=>x.id===b.dataset.id); if(t) toks.push({k:'v',v:t.v,u:uparse(t.u),s:t.s});}
    else if(b.dataset.op){const o=b.dataset.op; toks.push({k:FUN[o]?'fn':'op',o,s:o});}
    else if(b.dataset.act==='undo') toks.pop();
    else if(b.dataset.act==='clear') toks=[];
    else if(b.dataset.act==='use'){const o=el.querySelectorAll('.opt')[+b.dataset.k]; if(o&&!el.classList.contains('done')) o.click(); return;}
    redraw();
  });
  redraw();
}
// ---------------------------------------------------------------- animated diagrams in the take-aways
const NS='http://www.w3.org/2000/svg', REDUCE=matchMedia('(prefers-reduced-motion:reduce)').matches, AV={};
function sv(tag,at,parent){const e=document.createElementNS(NS,tag); for(const k in at){ if(k==='stroke'||k==='fill') e.style[k]=at[k]; else e.setAttribute(k,at[k]); } if(parent) parent.appendChild(e); return e;}
function stext(p,x,y,str,at){const e=sv('text',Object.assign({x,y,'font-size':15,fill:'var(--fg)'},at||{}),p);
  if(typeof str==='string'&&/_[A-Za-z0-9]/.test(str)){const fs=parseFloat((at&&at['font-size'])||15); let after=false; str.split(/(_[A-Za-z0-9]+)/).forEach(t=>{if(!t) return; if(t[0]==='_'&&t.length>1){const u=sv('tspan',{'font-size':Math.round(fs*0.75),dy:fs*0.2},e); u.textContent=t.slice(1); after=true;} else{const u=sv('tspan',after?{dy:-fs*0.2}:{},e); u.textContent=t; after=false;}});}
  else e.textContent=str; return e;}
const fmt3=x=>String(parseFloat(x.toPrecision(3)));
const ease=u=>u<.5?2*u*u:1-Math.pow(-2*u+2,2)/2;
function wavePath(x0,x1,yc,amp,lam,ph){let d=''; const st=Math.max(1,Math.min(3,lam/8)); for(let x=x0;x<=x1+.01;x+=st){const y=yc-amp*Math.sin(2*Math.PI*(x-x0)/lam-ph); d+=(d?'L':'M')+x.toFixed(1)+' '+y.toFixed(1);} return d;}
function packetPath(len,amp,lam){let d=''; for(let x=0;x<=len;x+=1){const y=-amp*Math.sin(Math.PI*x/len)*Math.sin(2*Math.PI*x/lam); d+=(d?'L':'M')+x+' '+y.toFixed(1);} return d;}
function avLoop(step,maxMs){let id=0,t0=null,on=false,el=0;
  const frame=ts=>{ if(!on) return; if(t0===null) t0=ts-el; el=ts-t0; step(Math.min(el,maxMs)); if(el>=maxMs){on=false; return;} id=requestAnimationFrame(frame); };
  return {play(reset){ if(reset){el=0;t0=null;} if(on) return; on=true; id=requestAnimationFrame(frame); }, stop(){on=false; cancelAnimationFrame(id);}, get on(){return on;}};}
function runOnce(ms,step,done){ if(REDUCE){step(1); if(done) done(); return {stop(){}};} let id=0,t0=null,stop=false;
  const f=ts=>{ if(stop) return; if(t0===null) t0=ts; const u=Math.min(1,(ts-t0)/ms); step(u); if(u<1) id=requestAnimationFrame(f); else if(done) done(); }; id=requestAnimationFrame(f); return {stop(){stop=true; cancelAnimationFrame(id);}};}
function avShell(root,w,h,label,cap){root.innerHTML=''; const s=sv('svg',{viewBox:`0 0 ${w} ${h}`,role:'img','aria-label':label},root);
  const c=document.createElement('div'); c.className='avc'; root.appendChild(c); const f=document.createElement('figcaption'); f.className='cap'; f.innerHTML=String(cap).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/_([A-Za-z0-9]+)/g,'<sub>$1</sub>'); root.appendChild(f); return {s,c};}
function replayBtn(c,fn){const b=document.createElement('button'); b.type='button'; b.className='btn sm'; b.textContent='Replay'; b.addEventListener('click',fn); b.hidden=REDUCE; c.appendChild(b); return b;}
function tick(s,x,y1,y2,w){return sv('line',{x1:x,y1,x2:x,y2,stroke:'var(--fg)','stroke-width':w||1.5},s);}
function stream(s,o){const g=sv('g',{},s), n=Math.ceil((o.x1-o.x0)/o.sp), span=n*o.sp, ps=[];
  for(let k=0;k<n;k++) ps.push(sv('path',{d:packetPath(o.len,o.amp,o.lam),fill:'none',stroke:o.color,'stroke-width':2,'stroke-linejoin':'round'},g));
  return t=>ps.forEach((p,k)=>{const x=o.x0+((t*0.09+k*o.sp)%span); p.setAttribute('transform',`translate(${x.toFixed(1)} ${o.y})`); p.style.display=x>o.x1-o.len?'none':'';});}

AV['wave-energy']=root=>{
  const W=420,H=190,{s,c}=avShell(root,W,H,'A travelling wave whose wavelength shrinks as photon energy rises','The bar is 1 nm: double the energy and the wavelength halves.');
  const PX=150,X0=14,X1=406,YC=120,AMP=34;
  sv('line',{x1:X0,y1:YC,x2:X1,y2:YC,stroke:'var(--gr)','stroke-width':1},s);
  sv('line',{x1:X0,y1:32,x2:X0+PX,y2:32,stroke:'var(--fg)','stroke-width':2},s); tick(s,X0,26,38,2); tick(s,X0+PX,26,38,2); stext(s,X0+PX/2,20,'1 nm',{'text-anchor':'middle'});
  const wave=sv('path',{fill:'none',stroke:'var(--c1)','stroke-width':2.2,'stroke-linejoin':'round'},s);
  c.innerHTML='<label>Photon energy<input type="range" min="0" max="100" value="100" step="1"></label><output class="avo" aria-live="polite"></output>';
  const rng=c.querySelector('input'), out=c.querySelector('output');
  let pos=100, ph=0, sweeping=false, started=false;
  const E=p=>Math.pow(25,p/100);
  const draw=()=>{const e=E(pos), lam=1.23984/e; wave.setAttribute('d',wavePath(X0,X1,YC,AMP,lam*PX,ph));
    out.innerHTML=`E = <span class="v">${fmt3(e)} keV</span>, λ = 1240 / ${Math.round(e*1000)} = <span class="f">${fmt3(lam)} nm = ${fmt3(lam*10)} Å</span>`;};
  const loop=avLoop(t=>{ if(sweeping){const u=Math.min(1,t/3200); pos=100*ease(u); rng.value=pos; if(u>=1) sweeping=false;} ph=2*Math.PI*(55*t/1000)/(1.23984/E(pos)*PX); draw(); },14000);
  rng.addEventListener('input',()=>{sweeping=false; pos=+rng.value; draw(); if(!REDUCE) loop.play(true);});
  draw();
  return {enter(){ if(REDUCE||started){ if(!REDUCE) loop.play(false); return;} started=true; pos=0; rng.value=0; sweeping=true; loop.play(true); }, leave(){loop.stop();}, finish(){loop.stop(); sweeping=false; pos=100; rng.value=100; ph=0; draw();}};
};

AV['photon-origin']=root=>{
  const W=420,H=212,{s,c}=avShell(root,W,H,'A gamma ray from a nucleus and an x-ray from electrons, drawn as identical waves','A γ-ray and an x-ray of the same energy are the same wave. Only the source differs.');
  const upd=[];
  [{y:68,t:'γ-ray: emitted by the nucleus',nuc:1},{y:162,t:'x-ray: emitted by electrons',nuc:0}].forEach(L=>{
    stext(s,14,L.y-40,L.t,{'font-weight':600});
    if(L.nuc) [[-5,-4],[5,-4],[0,5],[-10,4],[10,4],[0,-11],[0,0]].forEach((p,i)=>sv('circle',{cx:34+p[0],cy:L.y+p[1],r:5,fill:i%2?'var(--c2)':'var(--paper)',stroke:'var(--fg)','stroke-width':1.4},s));
    else{sv('ellipse',{cx:34,cy:L.y,rx:19,ry:8,fill:'none',stroke:'var(--mu)','stroke-width':1.4},s); sv('circle',{cx:34,cy:L.y,r:3.5,fill:'var(--fg)'},s); sv('circle',{cx:53,cy:L.y,r:3.5,fill:'var(--c1)'},s);}
    upd.push(stream(s,{y:L.y,x0:78,x1:406,len:50,amp:13,lam:10,sp:110,color:'var(--c1)'}));
    stext(s,406,L.y+36,'E = 100 keV',{'text-anchor':'end',fill:'var(--mu)','font-size':14.5});
  });
  const loop=avLoop(t=>upd.forEach(u=>u(t)),6000); upd.forEach(u=>u(0)); replayBtn(c,()=>loop.play(true));
  return {enter(){ if(!REDUCE) loop.play(false);}, leave(){loop.stop();}, finish(){loop.stop(); upd.forEach(u=>u(0));}};
};

AV['intensity-energy']=root=>{
  const W=420,H=266,{s,c}=avShell(root,W,H,'Three photon beams: a baseline, one with twice the photons, and one with twice the photon energy','Doubling the intensity doubles the photons. Doubling each photon\'s energy halves its wavelength.');
  const upd=[];
  [{y:66,t:'N photons per second',sp:140,lam:11,col:'var(--c1)'},{y:144,t:'2N photons per second: twice the intensity',sp:70,lam:11,col:'var(--c1)'},{y:222,t:'N photons per second, each with twice the energy',sp:140,lam:5.5,col:'var(--c2)'}].forEach(R=>{
    stext(s,14,R.y-30,R.t,{'font-weight':600,'font-size':14.5}); sv('line',{x1:14,y1:R.y,x2:406,y2:R.y,stroke:'var(--gr)','stroke-width':1},s);
    upd.push(stream(s,{y:R.y,x0:14,x1:406,len:44,amp:11,lam:R.lam,sp:R.sp,color:R.col}));
  });
  const loop=avLoop(t=>upd.forEach(u=>u(t)),6000); upd.forEach(u=>u(0)); replayBtn(c,()=>loop.play(true));
  return {enter(){ if(!REDUCE) loop.play(false);}, leave(){loop.stop();}, finish(){loop.stop(); upd.forEach(u=>u(0));}};
};

AV['ev-gain']=root=>{
  const W=420,H=214,{s,c}=avShell(root,W,H,'An electron crossing a potential difference gains kinetic energy measured in electron-volts','An electron crossing 1 V gains 1 eV. A thousand times the voltage gives a thousand times the energy.');
  const LV=[{v:'1 V',e:'1 eV',j:'1.602 × 10⁻¹⁹ J'},{v:'1 kV',e:'1 keV',j:'1.602 × 10⁻¹⁶ J'},{v:'1 MV',e:'1 MeV',j:'1.602 × 10⁻¹³ J'}];
  const XL=96,XR=324,YT=46,YB=138;
  sv('line',{x1:XL,y1:YT,x2:XL,y2:YB,stroke:'var(--fg)','stroke-width':3},s); sv('line',{x1:XR,y1:YT,x2:XR,y2:YB,stroke:'var(--fg)','stroke-width':3},s);
  stext(s,XL,36,'−',{'text-anchor':'middle','font-size':20,'font-weight':700}); stext(s,XR,36,'+',{'text-anchor':'middle','font-size':20,'font-weight':700});
  [64,92,120].forEach(y=>sv('line',{x1:XL+34,y1:y,x2:XR-34,y2:y,stroke:'var(--gr)','stroke-width':1.5,'stroke-dasharray':'4 4'},s));
  const vt=stext(s,210,32,'',{'text-anchor':'middle','font-weight':700,fill:'var(--given)'});
  const trail=sv('line',{x1:XL+14,y1:92,x2:XL+14,y2:92,stroke:'var(--c1)','stroke-width':2.5,'stroke-opacity':.45},s), el=sv('circle',{cx:XL+14,cy:92,r:9,fill:'var(--c1)'},s);
  const k1=stext(s,210,170,'',{'text-anchor':'middle','font-size':16,'font-weight':700}), k2=stext(s,210,194,'',{'text-anchor':'middle','font-size':16,'font-weight':700,fill:'var(--find)'});
  c.innerHTML='<span class="muted" style="flex:1 1 100%">Potential difference</span>'; const btns=LV.map((L,i)=>{const b=document.createElement('button'); b.type='button'; b.className='btn sm'; b.textContent=L.v; b.setAttribute('aria-pressed','false'); c.appendChild(b); return b;});
  let cur=null, timer=0;
  const place=x=>{el.setAttribute('cx',x); trail.setAttribute('x2',x);};
  const show=i=>{btns.forEach((b,j)=>b.setAttribute('aria-pressed',j===i?'true':'false')); vt.textContent='ΔV = '+LV[i].v; k1.textContent='gains '+LV[i].e; k2.textContent='= '+LV[i].j; place(XR-14);};
  function run(i,done){ if(cur) cur.stop(); btns.forEach((b,j)=>b.setAttribute('aria-pressed',j===i?'true':'false')); vt.textContent='ΔV = '+LV[i].v; k1.textContent=''; k2.textContent=''; place(XL+14);
    cur=runOnce(1300,u=>place(XL+14+(XR-XL-28)*u*u),()=>{show(i); if(done) done();}); }
  const stop=()=>{clearTimeout(timer); if(cur) cur.stop();};
  btns.forEach((b,i)=>b.addEventListener('click',()=>{stop(); run(i);}));
  show(2); let started=false;
  return {enter(){ if(REDUCE||started) return; started=true; run(0,()=>{timer=setTimeout(()=>run(1,()=>{timer=setTimeout(()=>run(2),500);}),500);}); }, leave(){stop();}, finish(){stop(); show(2);}};
};

AV['length-units']=root=>{
  const W=420,H=186,{s,c}=avShell(root,W,H,'Three rulers of equal length marked in nanometres, ångströms, and picometres','The three rulers are the same length: 1 nm = 10 Å = 1000 pm.');
  const X0=20,X1=400,N=10,seg=(X1-X0)/N, ys=[46,98,150], items=[];
  [X0,X1].forEach(x=>sv('line',{x1:x,y1:38,x2:x,y2:158,stroke:'var(--gr)','stroke-width':1.2,'stroke-dasharray':'3 3'},s));
  const r1=sv('line',{x1:X0,y1:ys[0],x2:X1,y2:ys[0],stroke:'var(--fg)','stroke-width':2},s); const e1=[tick(s,X0,ys[0]-7,ys[0]+7,2),tick(s,X1,ys[0]-7,ys[0]+7,2)], l1=stext(s,210,ys[0]-14,'1 nm',{'text-anchor':'middle','font-weight':700});
  const mk=(y,lab,sub,col)=>{const ln=sv('line',{x1:X0,y1:y,x2:X1,y2:y,stroke:col,'stroke-width':2},s), ts=[]; for(let i=0;i<=N;i++) ts.push(tick(s,X0+i*seg,y-(i%N?5:8),y+(i%N?5:8),i%N?1.4:2));
    const L=stext(s,210,y-14,lab,{'text-anchor':'middle','font-weight':700,fill:col}), sb=stext(s,X0+seg/2,y+24,sub,{'text-anchor':'middle','font-size':14.5,fill:col}); return {ln,ts,L,sb};};
  const R2=mk(ys[1],'10 Å','1 Å','var(--c1)'), R3=mk(ys[2],'1000 pm','100 pm','var(--c2)');
  const setStep=u=>{ r1.setAttribute('x2',X0+(X1-X0)*Math.min(1,u/.22)); e1.forEach(e=>e.style.display=u>0?'':'none'); l1.style.display=u>.22?'':'none';
    [R2,R3].forEach((R,k)=>{const a=k?.66:.3; R.ln.style.display=u>a?'':'none'; R.ts.forEach((t,i)=>t.style.display=u>a+.025*i?'':'none'); R.L.style.display=u>a+.3?'':'none'; R.sb.style.display=u>a+.3?'':'none';});};
  setStep(1); let cur=null;
  const play=()=>{ if(cur) cur.stop(); if(REDUCE){setStep(1); return;} setStep(0); cur=runOnce(3600,setStep); };
  replayBtn(c,play); let started=false;
  return {enter(){ if(REDUCE||started) return; started=true; play(); }, leave(){ if(cur) cur.stop(); }, finish(){ if(cur) cur.stop(); setStep(1); }};
};

AV['matter-wave']=root=>{
  const W=420,H=222,{s,c}=avShell(root,W,H,'A 100 keV electron wave and a 100 keV photon wave drawn against the width of an atom','A 100 keV electron has a shorter wavelength than a 100 keV photon, and both are much shorter than an atom.');
  const PX=1.5,X0=18,X1=402,AW=100*PX;
  sv('line',{x1:X0,y1:40,x2:X0+AW,y2:40,stroke:'var(--fg)','stroke-width':2},s); tick(s,X0,34,46,2); tick(s,X0+AW,34,46,2); stext(s,X0+AW/2,28,'atom ≈ 100 pm',{'text-anchor':'middle','font-weight':700});
  [X0,X0+AW].forEach(x=>sv('line',{x1:x,y1:50,x2:x,y2:204,stroke:'var(--gr)','stroke-width':1.2,'stroke-dasharray':'3 3'},s));
  sv('rect',{x:X0,y:50,width:AW,height:154,fill:'var(--gr)','fill-opacity':.6},s);
  const rows=[{y:98,t:'100 keV electron: λ = 3.7 pm',n:'27 wavelengths per atom',lam:3.7*PX,col:'var(--c1)'},{y:176,t:'100 keV photon: λ = 12.4 pm',n:'8 wavelengths per atom',lam:12.4*PX,col:'var(--c2)'}];
  const paths=rows.map(R=>{stext(s,X0,R.y-30,R.t,{'font-weight':600,'font-size':14.5,fill:R.col}); stext(s,X1,R.y+38,R.n,{'text-anchor':'end','font-size':14.5,fill:'var(--mu)'}); return sv('path',{fill:'none',stroke:R.col,'stroke-width':2,'stroke-linejoin':'round'},s);});
  const draw=t=>rows.forEach((R,k)=>paths[k].setAttribute('d',wavePath(X0,X1,R.y,14,R.lam,2*Math.PI*(45*t/1000)/R.lam)));
  const loop=avLoop(draw,6000); draw(0); replayBtn(c,()=>loop.play(true));
  return {enter(){ if(!REDUCE) loop.play(false);}, leave(){loop.stop();}, finish(){loop.stop(); draw(0);}};
};


// ---------------------------------------------------------------- toolkit: charts, bars, timelines
let avN=0;
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v)), seg=(u,a,b)=>clamp((u-a)/(b-a),0,1), lerp=(a,b,u)=>a+(b-a)*u;
function avArrowDef(s){const id='ava'+(++avN), d=sv('defs',{},s), m=sv('marker',{id,viewBox:'0 0 10 10',refX:8,refY:5,markerWidth:6,markerHeight:6,orient:'auto'},d); sv('path',{d:'M2 1L8 5L2 9',fill:'none',stroke:'context-stroke','stroke-width':1.5,'stroke-linecap':'round','stroke-linejoin':'round'},m); return id;}
function avLine(s,mk,x1,y1,x2,y2,col,w,dash){const l=sv('line',{x1,y1,x2,y2,stroke:col,'stroke-width':w||2,'marker-end':'url(#'+mk+')'},s); if(dash) l.setAttribute('stroke-dasharray',dash); return l;}
function avPlay(c,dur,step){let cur=null,started=false;
  const play=()=>{ if(cur) cur.stop(); if(REDUCE){step(1); return;} step(0); cur=runOnce(dur,step); };
  replayBtn(c,play); step(1);
  return {enter(){ if(REDUCE||started) return; started=true; play(); }, leave(){ if(cur){cur.stop(); cur=null; step(1);} }, finish(){ started=true; if(cur){cur.stop(); cur=null;} step(1); }};}
function avTimeline(root,cfg){const {s,c}=avShell(root,420,cfg.h,cfg.label,cfg.cap); const step=cfg.build(s,c); return avPlay(c,cfg.dur||3600,step);}
function avBars(root,cfg){
  const W=420,rowH=cfg.rowH||38,m=Object.assign({l:84,r:50,t:34,b:44},cfg.m||{}),H=m.t+cfg.rows.length*rowH+m.b,ax=cfg.x,pw=W-m.l-m.r;
  const {s,c}=avShell(root,W,H,cfg.label,cfg.cap), fr=v=>ax.log?Math.log10(v/ax.min)/Math.log10(ax.max/ax.min):(v-ax.min)/(ax.max-ax.min), X=v=>m.l+pw*fr(v), by=m.t+cfg.rows.length*rowH;
  (ax.ticks||[]).forEach(v=>{sv('line',{x1:X(v),x2:X(v),y1:m.t,y2:by,stroke:'var(--gr)','stroke-width':1},s); stext(s,X(v),by+18,(ax.fmt||fmt3)(v),{'text-anchor':'middle','font-size':14,fill:'var(--mu)'});});
  sv('line',{x1:m.l,y1:m.t,x2:m.l,y2:by,stroke:'var(--fg)','stroke-width':1.5},s);
  if(ax.label) stext(s,m.l+pw/2,H-8,ax.label,{'text-anchor':'middle','font-size':14.5});
  (cfg.vlines||[]).forEach(l=>{sv('line',{x1:X(l.x),x2:X(l.x),y1:m.t-8,y2:by,stroke:'var(--mu)','stroke-width':1.4,'stroke-dasharray':'5 4'},s); stext(s,X(l.x)+(l.anchor==='end'?-4:4),m.t-14,l.label,{'text-anchor':l.anchor||'start','font-size':14,fill:'var(--mu)'});});
  const bars=cfg.rows.map((r,i)=>{const y=m.t+i*rowH+7; stext(s,m.l-8,y+(rowH-14)/2,r.t,{'text-anchor':'end','dominant-baseline':'central','font-weight':600}); const b=sv('rect',{x:m.l,y,height:rowH-14,width:0,fill:r.col,rx:2},s); const v=stext(s,0,y+(rowH-14)/2,r.val,{'dominant-baseline':'central','font-size':14.5,'font-weight':600}); return {b,v,e:X(r.v)};});
  const dl=.4/Math.max(1,cfg.rows.length-1); return avPlay(c,cfg.dur||2600,u=>bars.forEach((o,i)=>{const p=ease(seg(u,i*dl,i*dl+.6)); o.b.setAttribute('width',Math.max(0,(o.e-m.l)*p)); o.v.setAttribute('x',m.l+(o.e-m.l)*p+6); o.v.style.display=p>.98?'':'none';}));
}
function avChart(root,cfg){
  const W=420,H=cfg.h||240,m=Object.assign({l:52,r:16,t:28,b:44},cfg.m||{}),id='avc'+(++avN),ax=cfg.x,ay=cfg.y;
  const {s,c}=avShell(root,W,H,cfg.label,cfg.cap), pw=W-m.l-m.r, ph=H-m.t-m.b, mk=avArrowDef(s);
  const fr=(a,v)=>a.log?Math.log10(v/a.min)/Math.log10(a.max/a.min):(v-a.min)/(a.max-a.min), X=v=>m.l+pw*fr(ax,v), Y=v=>m.t+ph*(1-fr(ay,v));
  (ay.ticks||[]).forEach(v=>{sv('line',{x1:m.l,x2:m.l+pw,y1:Y(v),y2:Y(v),stroke:'var(--gr)','stroke-width':1},s); stext(s,m.l-6,Y(v),(ay.fmt||fmt3)(v),{'text-anchor':'end','dominant-baseline':'central','font-size':14,fill:'var(--mu)'});});
  (ax.ticks||[]).forEach(v=>{sv('line',{x1:X(v),x2:X(v),y1:m.t,y2:m.t+ph,stroke:'var(--gr)','stroke-width':1},s); stext(s,X(v),m.t+ph+18,(ax.fmt||fmt3)(v),{'text-anchor':'middle','font-size':14,fill:'var(--mu)'});});
  sv('line',{x1:m.l,y1:m.t+ph,x2:m.l+pw,y2:m.t+ph,stroke:'var(--fg)','stroke-width':1.5},s); sv('line',{x1:m.l,y1:m.t,x2:m.l,y2:m.t+ph,stroke:'var(--fg)','stroke-width':1.5},s);
  if(ax.label) stext(s,m.l+pw/2,H-8,ax.label,{'text-anchor':'middle','font-size':14.5}); if(ay.label) stext(s,m.l,16,ay.label,{'font-size':14.5});
  const defs=sv('defs',{},s), cr=sv('rect',{x:m.l,y:m.t,width:pw,height:ph},sv('clipPath',{id},defs)), g=sv('g',{'clip-path':'url(#'+id+')'},s), top=sv('g',{},s);
  const samp=f=>{const o=[],N=170; for(let i=0;i<=N;i++){const x=ax.log?ax.min*Math.pow(ax.max/ax.min,i/N):ax.min+(ax.max-ax.min)*i/N, y=f(x); if(isFinite(y)) o.push([x,y]);} return o;};
  let slider=cfg.slider, rng=null, out=null;
  if(!slider&&cfg.fixed){c.innerHTML='<output class="avo" aria-live="polite"></output>'; out=c.querySelector('output');}
  const fixedD=()=>{const n=cfg.fixed.length, L='ABCDEFG', r={out:''}, K=['marks','series','vlines','hlines','labels','bands','arrows'], outs=[]; K.forEach(k=>r[k]=[]);
    cfg.fixed.forEach((v,i)=>{const e=cfg.dyn(v); K.forEach(k=>{ if(e[k]) r[k]=r[k].concat(k==='marks'&&n>1?e[k].map((m,j)=>Object.assign({},m,{label:m.label||(e[k].length===1?L[i]:L[i]+(j+1))})):e[k]);}); outs.push((n>1?'<b>'+L[i]+'</b> ':'')+(e.out||''));}); r.out=outs.join('<br>'); return r;};
  if(slider){const p0=slider.log?100*Math.log(slider.value/slider.min)/Math.log(slider.max/slider.min):100*(slider.value-slider.min)/(slider.max-slider.min);
    c.innerHTML='<label>'+slider.label+'<input type="range" min="0" max="100" step="0.01" value="'+p0+'"></label><output class="avo" aria-live="polite"></output>'; rng=c.querySelector('input'); out=c.querySelector('output');}
  const val=()=>slider.log?slider.min*Math.pow(slider.max/slider.min,+rng.value/100):slider.min+(slider.max-slider.min)*(+rng.value/100);
  const cat=(a,b,k)=>(a[k]||[]).concat((b&&b[k])||[]);
  function draw(){
    const d=slider&&cfg.dyn?cfg.dyn(val()):(cfg.fixed&&cfg.dyn?fixedD():{}); g.innerHTML=''; top.innerHTML='';
    cat(cfg,d,'bands').forEach(b=>sv('rect',{x:X(b.x0),y:m.t,width:X(b.x1)-X(b.x0),height:ph,fill:b.fill||'var(--gr)','fill-opacity':b.op||.55},g));
    cat(cfg,d,'series').forEach(S=>{let d2='',pen=false; const P=S.pts||samp(S.fn); P.forEach(p=>{if(p[1]>=ay.min&&p[1]<=ay.max){d2+=(pen?'L':'M')+X(p[0]).toFixed(1)+' '+Y(p[1]).toFixed(1); pen=true;} else{ if(pen) d2+='L'+X(p[0]).toFixed(1)+' '+Y(clamp(p[1],ay.min,ay.max)).toFixed(1); pen=false; }}); if(S.area&&d2) sv('path',{d:d2+'L'+X(P[P.length-1][0]).toFixed(1)+' '+Y(ay.min).toFixed(1)+'L'+X(P[0][0]).toFixed(1)+' '+Y(ay.min).toFixed(1)+'Z',fill:S.area,'fill-opacity':.22,stroke:'none'},g); sv('path',{d:d2,fill:'none',stroke:S.color||'var(--c1)','stroke-width':S.w||2.4,'stroke-dasharray':S.dash||'none','stroke-linejoin':'round'},g);});
    cat(cfg,d,'vlines').forEach(v=>{sv('line',{x1:X(v.x),x2:X(v.x),y1:m.t,y2:m.t+ph,stroke:v.color||'var(--mu)','stroke-width':1.4,'stroke-dasharray':'5 4'},g); if(v.label) stext(top,X(v.x)+(v.dx===undefined?5:v.dx),m.t+(v.dy||15),v.label,{'text-anchor':v.anchor||'start','font-size':14.5,fill:v.color||'var(--mu)'});});
    cat(cfg,d,'hlines').forEach(h=>{sv('line',{x1:m.l,x2:m.l+pw,y1:Y(h.y),y2:Y(h.y),stroke:h.color||'var(--mu)','stroke-width':1.4,'stroke-dasharray':'5 4'},g); if(h.label) stext(top,m.l+pw-4,Y(h.y)-6,h.label,{'text-anchor':'end','font-size':14.5,fill:h.color||'var(--mu)'});});
    cat(cfg,d,'arrows').forEach(a=>avLine(top,mk,X(a.x1),Y(a.y1),X(a.x2),Y(a.y2),a.color||'var(--fg)',2));
    cat(cfg,d,'marks').forEach(k=>{sv('circle',{cx:X(k.x),cy:Y(k.y),r:k.r||4.8,fill:k.color||'var(--c2)'},top); if(k.label) stext(top,X(k.x)+(k.dx===undefined?8:k.dx),Y(k.y)+(k.dy===undefined?-8:k.dy),k.label,{'text-anchor':k.anchor||'start','font-size':14.5,'font-weight':600});});
    cat(cfg,d,'labels').forEach(l=>stext(top,X(l.x),Y(l.y),l.t,{'text-anchor':l.anchor||'start','font-size':14.5,'font-weight':l.b?600:400,fill:l.color||'var(--fg)'}));
    if(out) out.innerHTML=d.out||'';
  }
  const reveal=u=>{cr.setAttribute('width',pw*u); top.style.display=u>=.92?'':'none';};
  if(rng) rng.addEventListener('input',draw);
  draw(); reveal(1); return {enter(){},leave(){},finish(){}};          // a chart is drawn at once: replaying the line being drawn teaches nothing
}
const AVME=0.511, AVMP=938.272, bRel=(k,m)=>{const g=1+k/m; return Math.sqrt(1-1/(g*g));}, bCl=(k,m)=>Math.sqrt(2*k/m), pcKE=k=>Math.sqrt(k*k+2*k*AVME);

AV['rest-energy']=root=>avBars(root,{label:'Rest energies of the electron, proton, neutron, and alpha particle on a log scale',cap:'A proton is 1836 times heavier than an electron. 1 u is 931.5 MeV.',
  m:{l:76,r:48},x:{min:0.1,max:10000,log:true,ticks:[0.1,1,10,100,1000,10000],fmt:v=>String(v),label:'Rest energy (MeV), log scale'},
  rows:[{t:'electron',v:0.511,col:'var(--c1)',val:'0.511'},{t:'proton',v:938.3,col:'var(--c2)',val:'938'},{t:'neutron',v:939.6,col:'var(--c2)',val:'940'},{t:'alpha',v:3727.4,col:'var(--c2)',val:'3727'}],
  vlines:[{x:931.5,label:'1 u = 931.5 MeV',anchor:'end'}]});

AV['ke-classical']=root=>avChart(root,{h:252,label:'Speed of an electron against kinetic energy by the classical and relativistic formulas',cap:'Above about 50 keV the classical formula fails; beyond 0.26 MeV it gives speeds faster than light.',
  x:{min:0.01,max:100,log:true,ticks:[0.01,0.1,1,10,100],fmt:v=>String(v),label:'Kinetic energy (MeV)'},y:{min:0,max:1.5,ticks:[0,0.5,1,1.5],label:'Speed (fraction of c)'},
  series:[{fn:k=>bRel(k,AVME),color:'var(--c1)'},{fn:k=>bCl(k,AVME),color:'var(--c2)',dash:'6 4'}],hlines:[{y:1,label:'c'}],vlines:[{x:0.05,label:'50 keV',dy:150,dx:5}],
  labels:[{x:0.012,y:0.62,t:'relativistic',color:'var(--c1)',b:1},{x:0.012,y:1.3,t:'classical',color:'var(--c2)',b:1}],
  fixed:[0.02,5,6],
  dyn:k=>({marks:[{x:k,y:bRel(k,AVME),color:'var(--c1)',label:''},{x:k,y:Math.min(1.5,bCl(k,AVME)),color:'var(--c2)',label:bCl(k,AVME)>1.5?fmt3(bCl(k,AVME))+'c':'',dx:-8,dy:18,anchor:'end'}],out:'KE = <span class="v">'+fmt3(k)+' MeV</span>: relativistic <span class="f">'+fmt3(bRel(k,AVME))+'c</span>, classical '+fmt3(bCl(k,AVME))+'c'+(bCl(k,AVME)>1?' (faster than light)':'')})});

AV['speed-ke']=root=>avChart(root,{h:252,label:'Speed against kinetic energy for electrons and protons',cap:'An electron is near the speed of light by a few MeV. A 150 MeV proton is at about half of it.',
  x:{min:0.01,max:1000,log:true,ticks:[0.01,0.1,1,10,100,1000],fmt:v=>String(v),label:'Kinetic energy (MeV)'},y:{min:0,max:1.05,ticks:[0,0.5,1],label:'Speed (fraction of c)'},
  series:[{fn:k=>bRel(k,AVME),color:'var(--c1)'},{fn:k=>bRel(k,AVMP),color:'var(--c2)'}],hlines:[{y:1,label:'c'}],
  labels:[{x:0.011,y:0.8,t:'electron',color:'var(--c1)',b:1},{x:1,y:0.2,t:'proton',color:'var(--c2)',b:1}],
  fixed:[2,100,150],
  dyn:k=>({marks:[{x:k,y:bRel(k,AVME),color:'var(--c1)',label:''},{x:k,y:bRel(k,AVMP),color:'var(--c2)',label:''}],out:'KE = <span class="v">'+fmt3(k)+' MeV</span>: electron <span class="f">'+fmt3(bRel(k,AVME))+'c</span>, proton <span class="f">'+fmt3(bRel(k,AVMP))+'c</span>'})});

AV['annihilation']=root=>avTimeline(root,{h:218,label:'A positron and an electron annihilate into two photons moving in opposite directions',cap:'Two 511 keV photons leave back to back, so their momentum adds to zero, as it did before.',dur:3800,build:s=>{
  const C=[210,100], D=130, ang=[210,30], axis=sv('line',{x1:C[0]-Math.cos(Math.PI/6)*184,y1:C[1]-Math.sin(Math.PI/6)*184,x2:C[0]+Math.cos(Math.PI/6)*184,y2:C[1]+Math.sin(Math.PI/6)*184,stroke:'var(--gr)','stroke-width':1.8,'stroke-dasharray':'4 4'},s), ph=ang.map(()=>sv('path',{d:packetPath(54,9,10),fill:'none',stroke:'var(--c3)','stroke-width':2.2,'stroke-linejoin':'round'},s));
  const ring=sv('circle',{cx:C[0],cy:C[1],r:0,fill:'none',stroke:'var(--mu)','stroke-width':1.6},s);
  const pos=sv('circle',{r:11,fill:'var(--c2)'},s), neg=sv('circle',{r:11,fill:'var(--c1)'},s), ps=stext(s,0,0,'+',{'text-anchor':'middle','dominant-baseline':'central','font-weight':700,'font-size':17,fill:'var(--paper)'}), ns=stext(s,0,0,'−',{'text-anchor':'middle','dominant-baseline':'central','font-weight':700,'font-size':17,fill:'var(--paper)'});
  const l1=stext(s,14,64,'511 keV',{'font-weight':600,fill:'var(--c3)'}), l2=stext(s,406,142,'511 keV',{'text-anchor':'end','font-weight':600,fill:'var(--c3)'}), note=stext(s,210,212,'two photons, 180° apart',{'text-anchor':'middle',fill:'var(--mu)'});
  return u=>{const a=ease(seg(u,0,.38)), gone=u>=.4;
    [[pos,ps,lerp(50,C[0],a)],[neg,ns,lerp(370,C[0],a)]].forEach(([d,t,x])=>{d.setAttribute('cx',x); d.setAttribute('cy',C[1]); t.setAttribute('x',x); t.setAttribute('y',C[1]); d.style.display=t.style.display=gone?'none':'';});
    ring.setAttribute('r',36*seg(u,.38,.55)); ring.style.strokeOpacity=u<.38?0:1-seg(u,.5,.6);
    const d=lerp(6,D,ease(seg(u,.42,.95))); ang.forEach((g,i)=>{const x=C[0]+Math.cos(g*Math.PI/180)*d, y=C[1]+Math.sin(g*Math.PI/180)*d; ph[i].setAttribute('transform','translate('+x.toFixed(1)+' '+y.toFixed(1)+') rotate('+g+')'); ph[i].style.display=u<.42?'none':'';});
    l1.style.display=l2.style.display=u>.9?'':'none'; note.style.display=u>.95?'':'none'; axis.style.display=u>.42?'':'none';};}});

AV['pair-production']=root=>avChart(root,{h:240,label:'Kinetic energy shared by an electron and a positron against photon energy',cap:'No pair forms below 1.022 MeV. Above it, the pair shares the excess.',
  x:{min:0,max:5,ticks:[0,1,2,3,4,5],label:'Photon energy hν (MeV)'},y:{min:0,max:4,ticks:[0,1,2,3,4],label:'Pair kinetic energy (MeV)'},
  series:[{pts:[[0,0],[1.022,0],[5,3.978]],color:'var(--c1)'}],vlines:[{x:1.022,label:'1.022 MeV',dy:40}],
  fixed:[1,3,5],
  dyn:e=>({marks:[{x:e,y:Math.max(0,e-1.022),color:'var(--c2)',label:''}],out:e<1.022?'hν = <span class="v">'+e.toFixed(2)+' MeV</span> is below the threshold: <span class="f">no pair</span>':'hν = <span class="v">'+e.toFixed(2)+' MeV</span>: the pair shares hν − 1.022 = <span class="f">'+(e-1.022).toFixed(3)+' MeV</span>'})});

AV['coulomb-inverse-square']=root=>avChart(root,{h:240,label:'Coulomb force against distance, falling as one over the distance squared',cap:'Double the distance and the force falls to one quarter; triple it and the force falls to one ninth.',
  x:{min:0.5,max:4,ticks:[1,2,3,4],label:'Distance r (in units of r₀)'},y:{min:0,max:4,ticks:[0,1,2,3,4],label:'Force (in units of F at r₀)'},
  series:[{fn:r=>1/(r*r),color:'var(--c1)'}],marks:[{x:1,y:1,label:'1',color:'var(--c1)'},{x:2,y:0.25,label:'1/4',color:'var(--c1)',dy:-10},{x:3,y:1/9,label:'1/9',color:'var(--c1)',dy:-10}],
  fixed:[2],
  dyn:r=>({marks:[{x:r,y:1/(r*r),color:'var(--c2)',r:6,label:''}],out:'r = <span class="v">'+fmt3(r)+' r₀</span>: F = <span class="f">'+fmt3(1/(r*r))+' F₀</span>'})});

AV['magnetic-circle']=root=>{
  const W=420,H=262,{s,c}=avShell(root,W,H,'A charged particle in a magnetic field moves in a circle at constant speed','The magnetic force points to the centre and is always perpendicular to the velocity: it turns the particle without speeding it up.');
  const mk=avArrowDef(s), CX=210, CY=118, K=100*pcKE(6)/299.792458, PXCM=5;
  for(let x=40;x<=380;x+=34) for(let y=24;y<=212;y+=34) sv('circle',{cx:x,cy:y,r:1.8,fill:'var(--mu)'},s);
  stext(s,14,16,'B out of the page',{'font-size':14,fill:'var(--mu)'});
  const orbit=sv('circle',{cx:CX,cy:CY,fill:'none',stroke:'var(--c1)','stroke-width':1.6,'stroke-dasharray':'3 4'},s), dot=sv('circle',{r:8,fill:'var(--c1)'},s);
  const vA=avLine(s,mk,0,0,0,0,'var(--c2)',2.4), fA=avLine(s,mk,0,0,0,0,'var(--c3)',2.4), vT=stext(s,0,0,'v',{'font-weight':700,fill:'var(--c2)'}), fT=stext(s,0,0,'F',{'font-weight':700,fill:'var(--c3)'});
  c.innerHTML='<label>Field B<input type="range" min="0" max="100" step="1" value="25"></label><output class="avo" aria-live="polite"></output>'; const rng=c.querySelector('input'), out=c.querySelector('output');
  let th=0, B=0.2, rpx=K/B*PXCM;
  const draw=()=>{const x=CX+rpx*Math.cos(th), y=CY-rpx*Math.sin(th), tx=-Math.sin(th), ty=-Math.cos(th), nx=-Math.cos(th), ny=Math.sin(th);
    dot.setAttribute('cx',x); dot.setAttribute('cy',y); orbit.setAttribute('r',rpx);
    vA.setAttribute('x1',x); vA.setAttribute('y1',y); vA.setAttribute('x2',x+tx*40); vA.setAttribute('y2',y+ty*40); vT.setAttribute('x',x+tx*40+(tx>0?6:-16)); vT.setAttribute('y',y+ty*40+(ty>0?14:-4));
    fA.setAttribute('x1',x); fA.setAttribute('y1',y); fA.setAttribute('x2',x+nx*Math.min(34,rpx-12)); fA.setAttribute('y2',y+ny*Math.min(34,rpx-12)); fT.setAttribute('x',x+nx*Math.min(34,rpx-12)*0.5+(nx>0?8:-14)); fT.setAttribute('y',y+ny*Math.min(34,rpx-12)*0.5+(ny>0?14:-6));};
  const text=()=>{out.innerHTML='B = <span class="v">'+B.toFixed(2)+' T</span>, r = pc / (299.8 B) = '+(pcKE(6)).toFixed(2)+' / (299.8 × '+B.toFixed(2)+') = <span class="f">'+fmt3(K/B)+' cm</span>. Speed and kinetic energy stay <span class="v">6.0 MeV</span>.';};
  const set=()=>{B=0.1+0.4*(+rng.value)/100; rpx=K/B*PXCM; text(); draw();};
  const loop=avLoop(t=>{th=t/1000*110/rpx; draw();},12000);
  rng.addEventListener('input',()=>{set(); if(!REDUCE) loop.play(true);}); set();
  return {enter(){ if(!REDUCE) loop.play(false); }, leave(){loop.stop();}, finish(){loop.stop(); th=0.6; set();}};
};

AV['bend-radius']=root=>avChart(root,{h:250,label:'Radius of an electron path in a magnetic field against kinetic energy',cap:'r (m) = pc (MeV) / (299.8 × B (T)). Higher momentum bends less; a stronger field bends more.',
  x:{min:0,max:20,ticks:[0,5,10,15,20],label:'Electron kinetic energy (MeV)'},y:{min:0,max:70,ticks:[0,20,40,60],label:'Radius (cm)'},
  slider:{min:0.1,max:0.5,value:0.2,label:'Field B'},
  dyn:B=>({series:[{fn:k=>100*pcKE(k)/(299.792458*B),color:'var(--c1)'}],marks:[{x:6,y:100*pcKE(6)/(299.792458*B),color:'var(--c2)',label:fmt3(100*pcKE(6)/(299.792458*B))+' cm',dx:-8,dy:-14,anchor:'end'}],out:'6 MeV electron, B = <span class="v">'+B.toFixed(2)+' T</span>: r = '+pcKE(6).toFixed(2)+' / (299.8 × '+B.toFixed(2)+') = <span class="f">'+fmt3(100*pcKE(6)/(299.792458*B))+' cm</span>'})});

AV['rutherford']=root=>avTimeline(root,{h:240,label:'Alpha particles fired at a thin foil: most pass straight through and a few turn back',cap:'Most α particles pass through the foil. A few are turned back, so the positive charge sits in a tiny nucleus.',dur:4200,build:s=>{
  const FX=210; sv('line',{x1:FX,y1:22,x2:FX,y2:214,stroke:'var(--gr)','stroke-width':14,'stroke-opacity':.8},s); [70,144].forEach(y=>sv('circle',{cx:FX,cy:y,r:6,fill:'var(--c2)'},s));
  stext(s,FX,14,'foil',{'text-anchor':'middle',fill:'var(--mu)'}); stext(s,14,18,'α particles',{'font-weight':600,fill:'var(--c1)'});
  const ds=['M14 98 L406 98','M14 52 L168 52 L204 44 L290 38 L406 30','M14 152 L176 152 Q198 152 194 170 L120 202 L44 226'];
  const P=ds.map(d=>{const p=sv('path',{d,fill:'none',stroke:'var(--c1)','stroke-width':2,'stroke-opacity':.8},s), L=p.getTotalLength(); p.style.strokeDasharray='0 '+L; return {p,L,dot:sv('circle',{r:6,fill:'var(--c1)'},s)};});
  const l1=stext(s,228,90,'most pass straight through',{fill:'var(--mu)'}), l2=stext(s,406,232,'a few turn back',{'text-anchor':'end',fill:'var(--mu)'});
  return u=>{P.forEach((o,i)=>{const p=ease(seg(u,i*.12,i*.12+.58)), pt=o.p.getPointAtLength(p*o.L); o.dot.setAttribute('cx',pt.x); o.dot.setAttribute('cy',pt.y); o.p.style.strokeDasharray=(p*o.L)+' '+o.L;}); l1.style.display=l2.style.display=u>.85?'':'none';};}});

AV['bohr-levels']=root=>{
  const W=420,H=262,{s,c}=avShell(root,W,H,'Hydrogen energy levels and the photon emitted when the electron drops between levels','A photon carries the energy difference between two levels. Higher levels crowd together toward 0 eV.');
  const LV={1:206,2:84,3:58}, E=n=>-13.6/(n*n), X0=124, X1=296;
  sv('line',{x1:X0,y1:30,x2:X1,y2:30,stroke:'var(--mu)','stroke-width':1.6,'stroke-dasharray':'6 4'},s); stext(s,X0-8,30,'0 eV',{'text-anchor':'end','dominant-baseline':'central',fill:'var(--mu)'});
  [1,2,3].forEach(n=>{sv('line',{x1:X0,y1:LV[n],x2:X1,y2:LV[n],stroke:'var(--fg)','stroke-width':2.4},s); stext(s,X0-8,LV[n],'n = '+n+'  '+E(n).toFixed(2).replace('-','−')+' eV',{'text-anchor':'end','dominant-baseline':'central','font-size':14});});
  const el=sv('circle',{cx:210,r:8,fill:'var(--c1)'},s), ph=sv('path',{d:packetPath(54,9,10),fill:'none',stroke:'var(--c2)','stroke-width':2.2,'stroke-linejoin':'round'},s);
  c.innerHTML='<span class="muted" style="flex:1 1 100%">Electron drops</span>'; const TR=[[3,2],[2,1],[3,1]], btns=TR.map(t=>{const b=document.createElement('button'); b.type='button'; b.className='btn sm'; b.textContent=t[0]+' → '+t[1]; b.setAttribute('aria-pressed','false'); c.appendChild(b); return b;});
  const out=document.createElement('output'); out.className='avo'; out.setAttribute('aria-live','polite'); c.appendChild(out); let cur=null,timer=0,started=false;
  const dE=(a,b)=>13.6*(1/(b*b)-1/(a*a)), txt=(a,b)=>{out.innerHTML='n = '+a+' → '+b+': ΔE = 13.6 (1/'+b+'² − 1/'+a+'²) = <span class="f">'+fmt3(dE(a,b))+' eV</span>';};
  const set=(i,u)=>{const [a,b]=TR[i], ym=(LV[a]+LV[b])/2; btns.forEach((x,k)=>x.setAttribute('aria-pressed',k===i?'true':'false'));
    const e=ease(seg(u,0,.45)); el.setAttribute('cy',lerp(LV[a]-12,LV[b]-12,e)); const p=seg(u,.45,1); ph.style.display=u<.45?'none':''; ph.setAttribute('transform','translate('+lerp(312,350,p)+' '+ym+')'); if(u>=.45) txt(a,b); else out.innerHTML='';};
  const run=i=>{ if(cur) cur.stop(); clearTimeout(timer); cur=runOnce(1900,u=>set(i,u)); };
  btns.forEach((b,i)=>b.addEventListener('click',()=>{started=true; run(i);})); set(0,1);
  return {enter(){ if(REDUCE||started) return; started=true; run(0); }, leave(){ if(cur){cur.stop(); cur=null;} }, finish(){ started=true; if(cur){cur.stop(); cur=null;} set(0,1); }};
};

AV['characteristic-xray']=root=>avTimeline(root,{h:244,label:'An electron falls into an inner-shell vacancy and a characteristic x-ray carries off the energy difference',cap:'The photon energy is the difference between two shell binding energies. For tungsten: 69.5 − 10.2 = 59.3 keV.',dur:5200,build:s=>{
  const CX=124, CY=120, R=[30,62,94], at=(r,a)=>[CX+r*Math.cos(a*Math.PI/180), CY-r*Math.sin(a*Math.PI/180)];
  R.forEach((r,i)=>{sv('circle',{cx:CX,cy:CY,r,fill:'none',stroke:'var(--gr)','stroke-width':2.2},s); const p=at(r,90); stext(s,p[0],p[1]-5,['K','L','M'][i],{'text-anchor':'middle','font-size':14,fill:'var(--mu)','font-weight':600});});
  sv('circle',{cx:CX,cy:CY,r:8,fill:'var(--c2)'},s);
  const k1=at(30,135), k2=at(30,315), l1=at(62,135); [k2,at(62,45),at(62,225),at(62,315)].forEach(p=>sv('circle',{cx:p[0],cy:p[1],r:5.5,fill:'var(--c1)'},s));
  const vac=sv('circle',{cx:k1[0],cy:k1[1],r:7,fill:'none',stroke:'var(--mu)','stroke-width':1.6,'stroke-dasharray':'3 3'},s), ke=sv('circle',{r:5.5,fill:'var(--c1)'},s), le=sv('circle',{r:5.5,fill:'var(--c1)'},s), pr=sv('circle',{r:7,fill:'var(--c2)'},s), ph=sv('path',{d:packetPath(54,9,10),fill:'none',stroke:'var(--c3)','stroke-width':2.2,'stroke-linejoin':'round'},s);
  const t1=stext(s,236,150,'K shell: 69.5 keV',{'font-size':14.5}), t2=stext(s,236,176,'L shell: 10.2 keV',{'font-size':14.5}), t3=stext(s,236,206,'x-ray: 59.3 keV',{'font-size':15,'font-weight':700,fill:'var(--c3)'});
  return u=>{const a=ease(seg(u,0,.25)); pr.setAttribute('cx',lerp(18,k1[0],a)); pr.setAttribute('cy',lerp(18,k1[1],a)); pr.style.display=u<.25?'':'none';
    const e=ease(seg(u,.25,.42)); ke.setAttribute('cx',lerp(k1[0],26,e)); ke.setAttribute('cy',lerp(k1[1],200,e)); ke.style.display=u<.25?'none':'';
    vac.style.display=u>=.25&&u<.65?'':'none'; const j=ease(seg(u,.45,.65)); le.setAttribute('cx',lerp(l1[0],k1[0],j)); le.setAttribute('cy',lerp(l1[1],k1[1],j));
    const p=ease(seg(u,.66,1)), d=lerp(0,236,p); ph.setAttribute('transform','translate('+(k1[0]+d*0.99).toFixed(1)+' '+(k1[1]-d*0.14).toFixed(1)+') rotate(-8)'); ph.style.display=u<.66?'none':'';
    t1.style.display=u>.3?'':'none'; t2.style.display=u>.5?'':'none'; t3.style.display=u>.85?'':'none';};}});

AV['nuclide-families']=root=>avTimeline(root,{h:254,label:'A chart of nuclides with a row of isotopes, a column of isotones, a diagonal of isobars, and an isomer',cap:'Neutron number runs across and proton number runs up. Each family holds one quantity fixed.',dur:6000,build:s=>{
  const n=8, cs=24, X0=22, Y0=28; stext(s,X0,16,'protons (Z)',{'font-size':14.5,fill:'var(--mu)'}); stext(s,X0+n*cs/2,Y0+n*cs+22,'neutrons (N)',{'text-anchor':'middle','font-size':14.5,fill:'var(--mu)'});
  const cell=(i,j,col,op)=>sv('rect',{x:X0+i*cs,y:Y0+(n-1-j)*cs,width:cs-2,height:cs-2,fill:col,'fill-opacity':op,rx:2},s);
  for(let i=0;i<n;i++) for(let j=0;j<n;j++) cell(i,j,'var(--gr)',.6);
  const G=[0,1,2,3].map(()=>sv('g',{},s)), put=(g,i,j,col)=>sv('rect',{x:X0+i*cs,y:Y0+(n-1-j)*cs,width:cs-2,height:cs-2,fill:col,rx:2},g);
  for(let i=0;i<n;i++){put(G[0],i,3,'var(--c1)'); put(G[1],4,i,'var(--c2)'); put(G[2],i,n-1-i,'var(--c3)');}
  put(G[3],2,5,'var(--c4)'); sv('rect',{x:X0+2*cs-3,y:Y0+(n-1-5)*cs-3,width:cs+4,height:cs+4,fill:'none',stroke:'var(--c4)','stroke-width':1.6,rx:3},G[3]); stext(G[3],X0+2*cs+cs/2-1,Y0+(n-1-5)*cs+cs/2,'m',{'text-anchor':'middle','dominant-baseline':'central','font-size':14,'font-weight':700,fill:'var(--paper)'});
  const rows=[['Isotopes: same Z','I-125, I-131','var(--c1)'],['Isotones: same N','C-14, N-15','var(--c2)'],['Isobars: same A','Mo-99, Tc-99, Ru-99','var(--c3)'],['Isomers: same Z and A','Tc-99m, Tc-99','var(--c4)']].map((r,i)=>{const y=52+i*46, g=sv('g',{},s); sv('rect',{x:228,y:y-12,width:14,height:14,fill:r[2],rx:2},g); stext(g,250,y-4,r[0],{'font-size':14.5,'font-weight':600,'dominant-baseline':'central'}); stext(g,250,y+16,r[1],{'font-size':13.5,fill:'var(--mu)','dominant-baseline':'central'}); return g;});
  return u=>{const cur=Math.max(0,Math.min(3,Math.floor((u-.02)/.25))); G.forEach((g,i)=>g.style.display=(u>=1||u>=i*.25+.02)?'':'none'); rows.forEach((g,i)=>g.style.opacity=u>=1?1:(i===cur?1:(i<cur?.55:.25)));};}});

AV['nuclear-forces']=root=>{const cl=r=>230.8/(r*r), st=r=>3000*Math.exp(-(r-1)/.55); return avChart(root,{h:256,label:'Strength of the Coulomb and strong forces between two protons against separation',cap:'Schematic. The strong force is attractive but fades within a few femtometres; the Coulomb repulsion falls off slowly.',
  x:{min:0.5,max:6,ticks:[1,2,3,4,5,6],label:'Separation (fm)'},y:{min:1,max:10000,log:true,ticks:[1,10,100,1000,10000],fmt:v=>String(v),label:'Force strength (N), log scale'},
  series:[{fn:cl,color:'var(--c2)'},{fn:r=>r>=0.8?st(r):NaN,color:'var(--c1)'}],vlines:[{x:3,label:'~3 fm',dy:150}],
  labels:[{x:0.78,y:7800,t:'strong: attractive',color:'var(--c1)',b:1},{x:5.95,y:55,t:'Coulomb: repulsive',color:'var(--c2)',b:1,anchor:'end'}]});};

AV['stability-line']=root=>{const stable=[]; for(let A=1;A<=240;A++){const Z=A/(1.98+0.0155*Math.pow(A,2/3)); if(Z<=90) stable.push([Z,A-Z]);}
  return avChart(root,{h:256,label:'Neutron number against proton number for stable nuclei, which curve above the line N = Z',cap:'Light stable nuclei have N ≈ Z. Heavier ones need extra neutrons: Pb-208 has N/Z = 1.5.',
  x:{min:0,max:90,ticks:[0,20,40,60,80],label:'Protons Z'},y:{min:0,max:140,ticks:[0,40,80,120],label:'Neutrons N'},
  series:[{pts:[[0,0],[90,90]],color:'var(--mu)',dash:'5 4'},{pts:stable,color:'var(--c1)'}],marks:[{x:2,y:2,label:'He-4',dx:10,dy:-14},{x:82,y:126,label:'Pb-208',dx:-8,dy:-10,anchor:'end'}],
  labels:[{x:58,y:44,t:'N = Z',color:'var(--mu)'},{x:30,y:100,t:'stable nuclei',color:'var(--c1)',b:1}]});};

AV['mass-defect']=root=>avTimeline(root,{h:262,label:'Separate nucleons weigh more than the bound helium-4 nucleus; the difference is the binding energy',cap:'Helium-4: Δm = 0.0304 u, and 0.0304 u × 931.5 MeV/u = 28.3 MeV. The mass axis starts at 4.000 u.',dur:4200,build:s=>{
  const Y=m=>220-(m-4.0)*4500; for(let t=4.0;t<=4.0401;t+=0.01){sv('line',{x1:78,x2:372,y1:Y(t),y2:Y(t),stroke:'var(--gr)','stroke-width':1},s); stext(s,72,Y(t),t.toFixed(3),{'text-anchor':'end','dominant-baseline':'central','font-size':13.5,fill:'var(--mu)'});}
  stext(s,78,14,'mass (u)',{'font-size':14.5,fill:'var(--mu)'});
  sv('rect',{x:92,y:Y(4.03298),width:96,height:220-Y(4.03298),fill:'var(--c1)',rx:2},s); sv('rect',{x:262,y:Y(4.00260),width:96,height:220-Y(4.00260),fill:'var(--c2)',rx:2},s);
  stext(s,140,Y(4.03298)-8,'4.03298 u',{'text-anchor':'middle','font-weight':600}); stext(s,310,Y(4.00260)-8,'4.00260 u',{'text-anchor':'middle','font-weight':600}); stext(s,140,242,'2 H + 2 n',{'text-anchor':'middle'}); stext(s,310,242,'He-4 atom',{'text-anchor':'middle'});
  const gap=sv('rect',{x:262,y:Y(4.03298),width:96,height:Y(4.00260)-Y(4.03298),fill:'var(--c2)','fill-opacity':.22,stroke:'var(--c2)','stroke-dasharray':'4 3','stroke-width':1.4,rx:2},s), g1=stext(s,310,Y(4.0164)-8,'Δm = 0.0304 u',{'text-anchor':'middle','font-weight':600}), g2=stext(s,310,Y(4.0164)+12,'= 28.3 MeV',{'text-anchor':'middle','font-weight':700,fill:'var(--find)'});
  return u=>{const p=ease(seg(u,.1,.55)), h=(Y(4.00260)-Y(4.03298))*p; gap.setAttribute('y',Y(4.00260)-h); gap.setAttribute('height',h); g1.style.display=u>.55?'':'none'; g2.style.display=u>.75?'':'none';};}});

AV['be-curve']=root=>avChart(root,{h:256,label:'Binding energy per nucleon against mass number, peaking near iron',cap:'Fusing light nuclei and splitting heavy nuclei both move toward the peak near Fe-56 at about 8.8 MeV.',
  x:{min:0,max:250,ticks:[0,50,100,150,200,250],label:'Mass number A'},y:{min:0,max:10.5,ticks:[0,2,4,6,8,10],label:'Binding energy per nucleon (MeV)'},
  series:[{pts:[[2,1.112],[4,7.074],[12,7.68],[16,7.976],[28,8.448],[40,8.551],[56,8.79],[62,8.795],[90,8.71],[120,8.505],[208,7.867],[238,7.57]],color:'var(--c1)'}],
  marks:[{x:4,y:7.074,label:'He-4',dx:6,dy:20},{x:56,y:8.79,label:'Fe-56',dx:0,dy:26,anchor:'middle'},{x:238,y:7.57,label:'U-238',dx:-4,dy:20,anchor:'end'}],
  arrows:[{x1:8,y1:9.8,x2:44,y2:9.8,color:'var(--c2)'},{x1:236,y1:9.8,x2:100,y2:9.8,color:'var(--c3)'}],labels:[{x:8,y:10.3,t:'fusion',color:'var(--c2)',b:1},{x:236,y:10.3,t:'fission',color:'var(--c3)',b:1,anchor:'end'}]});


// ---------------------------------------------------------------- 1.5 decay modes, 1.6 decay schemes, 1.7 decay law
const AVBAND='M52 204 L112 142 L200 94 L300 60 L392 40';
function avNZ(s,mk,lab){
  avLine(s,mk,34,226,398,226,'var(--mu)',1.6); avLine(s,mk,34,226,34,14,'var(--mu)',1.6);
  stext(s,398,246,'neutrons N',{'text-anchor':'end','font-size':14.5,fill:'var(--mu)'}); stext(s,44,22,'protons Z',{'font-size':14.5,fill:'var(--mu)'});
  sv('path',{d:AVBAND,fill:'none',stroke:'var(--gr)','stroke-width':28,'stroke-linecap':'round','stroke-linejoin':'round'},s);
  sv('path',{d:AVBAND,fill:'none',stroke:'var(--mu)','stroke-width':1.2,'stroke-dasharray':'4 4'},s);
  if(lab!==false) stext(s,236,120,'stable nuclei',{'font-size':14.5,fill:'var(--mu)'});
}
function avGrow(s,mk,x1,y1,x2,y2,col,w,dash){const l=avLine(s,mk,x1,y1,x1,y1,col,w||2.8,dash); return p=>{l.setAttribute('x2',lerp(x1,x2,p)); l.setAttribute('y2',lerp(y1,y2,p)); l.style.display=p>0?'':'none';};}
function avBtns(c,head,names){c.innerHTML='<span class="muted" style="flex:1 1 100%">'+head+'</span>'; const b=names.map(t=>{const e=document.createElement('button'); e.type='button'; e.className='btn sm'; e.textContent=t; e.setAttribute('aria-pressed','false'); c.appendChild(e); return e;}); const o=document.createElement('output'); o.className='avo'; o.setAttribute('aria-live','polite'); c.appendChild(o); return {b,o};}

AV['decay-map']=root=>avTimeline(root,{h:256,label:'A chart of nuclides: neutron-rich nuclei decay by beta minus, proton-rich nuclei by positron emission or electron capture, and heavy nuclei by alpha emission',cap:'Each decay moves a nucleus toward the stable band: β⁻ from the neutron-rich side, β⁺ or EC from the proton-rich side, and α from the heavy end.',dur:5200,build:s=>{
  const mk=avArrowDef(s); avNZ(s,mk);
  const items=[{x:182,y:152,ex:154,ey:124,col:'var(--c2)',tag:'β⁻',tx:190,ty:136,name:'neutron-rich',nx:182,ny:176,na:'middle'},{x:84,y:112,ex:112,ey:140,col:'var(--c1)',tag:'β⁺ or EC',tx:20,ty:142,name:'proton-rich',nx:76,ny:98,na:'middle'},{x:372,y:26,ex:328,ey:70,col:'var(--c3)',tag:'α',tx:362,ty:64,name:'heavy',nx:372,ny:14,na:'middle'}];
  const parts=items.map(it=>{const d=avGrow(s,mk,it.x,it.y,it.ex,it.ey,it.col); sv('circle',{cx:it.x,cy:it.y,r:6.5,fill:'var(--fg)'},s); stext(s,it.nx,it.ny,it.name,{'text-anchor':it.na,'font-size':14,fill:'var(--mu)'}); return {d,t:stext(s,it.tx,it.ty,it.tag,{'font-weight':700,fill:it.col}),e:sv('circle',{cx:it.ex,cy:it.ey,r:6.5,fill:'none',stroke:it.col,'stroke-width':2},s)};});
  return u=>parts.forEach((o,i)=>{const p=ease(seg(u,.08+i*.3,.32+i*.3)); o.d(p); o.t.style.display=p>.4?'':'none'; o.e.style.display=p>=1?'':'none';});}});

AV['decay-steps']=root=>{
  const W=420,H=276,{s,c}=avShell(root,W,H,'A grid of nuclides showing how each decay mode changes Z, N, and A','Z + N = A. β⁻, β⁺, and EC move one cell and keep A. α moves two cells down and two left and lowers A by 4.');
  const cs=22, X0=40, Y0=26, n=9, CX=i=>X0+i*cs+(cs-2)/2, CY=j=>Y0+(n-1-j)*cs+(cs-2)/2;
  for(let i=0;i<n;i++) for(let j=0;j<n;j++) sv('rect',{x:X0+i*cs,y:Y0+(n-1-j)*cs,width:cs-2,height:cs-2,fill:'var(--gr)','fill-opacity':.6,rx:2},s);
  stext(s,X0,16,'protons Z',{'font-size':14.5,fill:'var(--mu)'}); stext(s,X0+n*cs/2,Y0+n*cs+20,'neutrons N',{'text-anchor':'middle','font-size':14.5,fill:'var(--mu)'});
  const tr=sv('line',{stroke:'var(--mu)','stroke-width':1.6,'stroke-dasharray':'3 3'},s), gh=sv('circle',{r:8,fill:'none',stroke:'var(--mu)','stroke-width':1.6},s), tok=sv('circle',{r:8},s);
  const title=stext(s,282,54,'',{'font-weight':700}), rows=[0,1,2].map(i=>({k:stext(s,282,92+i*30,['Z','N','A'][i],{fill:'var(--mu)'}),v:stext(s,306,92+i*30,'',{'font-weight':600})}));
  const M=[{b:'β⁻',from:'Co-60',to:'Ni-60',Z:[27,28],N:[33,32],A:[60,60],di:-1,dj:1,col:'var(--c2)',txt:'a neutron becomes a proton. Z + 1, N − 1, A unchanged.'},{b:'β⁺ or EC',from:'F-18',to:'O-18',Z:[9,8],N:[9,10],A:[18,18],di:1,dj:-1,col:'var(--c1)',txt:'a proton becomes a neutron. Z − 1, N + 1, A unchanged.'},{b:'α',from:'Ra-226',to:'Rn-222',Z:[88,86],N:[138,136],A:[226,222],di:-2,dj:-2,col:'var(--c3)',txt:'the nucleus loses 2 protons and 2 neutrons. Z − 2, N − 2, A − 4.'}];
  const {b:btns,o:out}=avBtns(c,'Decay mode',M.map(m=>m.b)); let cur=null,started=false;
  const set=(i,u)=>{const m=M[i], p=ease(seg(u,0,.6)), x0=CX(4), y0=CY(4), x=lerp(x0,CX(4+m.di),p), y=lerp(y0,CY(4+m.dj),p);
    gh.setAttribute('cx',x0); gh.setAttribute('cy',y0); tok.setAttribute('cx',x); tok.setAttribute('cy',y); tok.style.fill=m.col; tr.setAttribute('x1',x0); tr.setAttribute('y1',y0); tr.setAttribute('x2',x); tr.setAttribute('y2',y);
    btns.forEach((b,k)=>b.setAttribute('aria-pressed',k===i?'true':'false')); const show=u>=.6; title.textContent=show?m.from+' → '+m.to:m.from;
    rows.forEach((r,k)=>{const a=m[['Z','N','A'][k]]; r.v.textContent=show?a[0]+' → '+a[1]:String(a[0]); r.v.style.fill=show&&a[0]!==a[1]?'var(--find)':'var(--fg)';}); out.innerHTML=show?m.b+': '+m.txt:'';};
  const run=i=>{ if(cur) cur.stop(); cur=runOnce(2000,u=>set(i,u)); };
  btns.forEach((b,i)=>b.addEventListener('click',()=>{started=true; run(i);})); set(0,1);
  return {enter(){ if(REDUCE||started) return; started=true; run(0); }, leave(){ if(cur){cur.stop(); cur=null;} }, finish(){ started=true; if(cur){cur.stop(); cur=null;} set(0,1); }};
};

AV['beta-plus-threshold']=root=>avTimeline(root,{h:224,label:'Available energy for four radionuclides against the 1.022 MeV threshold for positron emission',cap:'β⁺ decay needs more than 1.022 MeV (two electron masses) of available energy. Below that, electron capture is the only route.',dur:4600,build:s=>{
  const X=e=>40+e*140, YA=146, T=1.022;
  const z1=sv('rect',{x:X(0),y:100,width:X(T)-X(0),height:46,fill:'var(--gr)','fill-opacity':.8},s), z2=sv('rect',{x:X(T),y:100,width:X(2.5)-X(T),height:46,fill:'var(--c1)','fill-opacity':.16},s);
  const tz1=stext(s,(X(0)+X(T))/2,127,'EC only',{'text-anchor':'middle','font-weight':600}), tz2=stext(s,(X(T)+X(2.5))/2,127,'β⁺ possible, EC competes',{'text-anchor':'middle','font-weight':600,fill:'var(--c1)'});
  sv('line',{x1:40,y1:YA,x2:392,y2:YA,stroke:'var(--fg)','stroke-width':1.6},s); [0,0.5,1,1.5,2,2.5].forEach(e=>{sv('line',{x1:X(e),y1:YA,x2:X(e),y2:YA+6,stroke:'var(--fg)','stroke-width':1.4},s); stext(s,X(e),YA+22,String(e),{'text-anchor':'middle','font-size':14,fill:'var(--mu)'});});
  stext(s,216,200,'Available energy (MeV)',{'text-anchor':'middle','font-size':14.5});
  const th=sv('line',{x1:X(T),y1:44,x2:X(T),y2:YA,stroke:'var(--fg)','stroke-width':1.6,'stroke-dasharray':'5 4'},s), tt=stext(s,X(T)+6,52,'1.022 MeV',{'font-weight':600});
  const ds=[['I-125',0.186],['Pd-103',0.543],['F-18',1.656],['C-11',1.982]].map(([n,e])=>({c:sv('circle',{cx:X(e),r:6,fill:'var(--fg)'},s),t:stext(s,X(e),70,n,{'text-anchor':'middle','font-weight':700}),v:stext(s,X(e),86,e.toFixed(3),{'text-anchor':'middle','font-size':13.5,fill:'var(--mu)'})}));
  return u=>{const a=seg(u,0,.2); [z1,z2,tz1,tz2].forEach(z=>z.style.opacity=a); const b=seg(u,.2,.36); th.style.opacity=tt.style.opacity=b; th.style.display=tt.style.display=b>0?'':'none';
    ds.forEach((o,i)=>{const p=ease(seg(u,.4+i*.13,.6+i*.13)); o.c.setAttribute('cy',lerp(24,100,p)); o.c.style.display=p>0?'':'none'; o.t.style.display=o.v.style.display=p>.9?'':'none';});};}});

AV['pet-coincidence']=root=>avTimeline(root,{h:256,label:'A positron annihilates near its source and the two photons reach opposite detectors in a ring',cap:'A positron stops within a few millimetres and annihilates. The two 511 keV photons leave about 180° apart, so detectors on opposite sides record a coincidence on a line through the source.',dur:5400,build:s=>{
  const C=[210,118], R=90, S0=[194,104], A=[208,98], g=25*Math.PI/180, d=[Math.cos(g),Math.sin(g)], dets=[];
  for(let k=0;k<24;k++){const a=k*Math.PI/12; dets.push(sv('circle',{cx:C[0]+(R+10)*Math.cos(a),cy:C[1]+(R+10)*Math.sin(a),r:7,fill:'var(--gr)',stroke:'var(--line)','stroke-width':1},s));}
  const hit=sg=>{const dx=sg*d[0], dy=sg*d[1], ox=A[0]-C[0], oy=A[1]-C[1], b=dx*ox+dy*oy, c2=ox*ox+oy*oy-R*R, t=-b+Math.sqrt(b*b-c2); return {x:A[0]+dx*t,y:A[1]+dy*t,t};};
  const h=[hit(1),hit(-1)], near=q=>{let b=0,bd=1e9; dets.forEach((e,k)=>{const dd=Math.hypot(+e.getAttribute('cx')-q.x,+e.getAttribute('cy')-q.y); if(dd<bd){bd=dd;b=k;}}); return b;}, ks=h.map(near);
  const lor=sv('line',{x1:h[0].x,y1:h[0].y,x2:h[1].x,y2:h[1].y,stroke:'var(--c2)','stroke-width':1.8,'stroke-dasharray':'5 4'},s), lt=stext(s,210,250,'line of response',{'text-anchor':'middle','font-weight':600,fill:'var(--c2)'});
  sv('circle',{cx:S0[0],cy:S0[1],r:5,fill:'var(--c2)'},s); const pp=sv('line',{x1:S0[0],y1:S0[1],x2:S0[0],y2:S0[1],stroke:'var(--c2)','stroke-width':2.4,'stroke-linecap':'round'},s), fl=sv('circle',{cx:A[0],cy:A[1],r:0,fill:'none',stroke:'var(--mu)','stroke-width':1.6},s);
  const ph=[0,1].map(()=>sv('path',{d:packetPath(36,7,9),fill:'none',stroke:'var(--c3)','stroke-width':2.2,'stroke-linejoin':'round'},s));
  return u=>{const p1=ease(seg(u,0,.2)); pp.setAttribute('x2',lerp(S0[0],A[0],p1)); pp.setAttribute('y2',lerp(S0[1],A[1],p1)); fl.setAttribute('r',16*seg(u,.22,.34)); fl.style.strokeOpacity=u<.22?0:1-seg(u,.3,.4);
    const p=ease(seg(u,.3,.7)); ph.forEach((e,i)=>{const dd=lerp(0,h[i].t-40,p), sg=i?-1:1; e.setAttribute('transform','translate('+(A[0]+sg*d[0]*dd).toFixed(1)+' '+(A[1]+sg*d[1]*dd).toFixed(1)+') rotate('+(i?205:25)+')'); e.style.display=u<.3?'none':'';});
    ks.forEach(k=>dets[k].style.fill=u>.72?'var(--c2)':'var(--gr)'); const lp=seg(u,.78,.92); lor.style.display=lp>0?'':'none'; lor.style.opacity=lp; lt.style.display=u>.9?'':'none';};}});

AV['vacancy-fates']=root=>avTimeline(root,{h:262,label:'A shell vacancy is filled and the energy leaves either as a characteristic x-ray or as an Auger electron',cap:'EC and internal conversion leave a K-shell vacancy. An outer electron falls in, and the energy leaves as a photon or ejects another electron.',dur:5200,build:s=>{
  const atoms=[{cx:105,cy:146,x:1},{cx:315,cy:146,x:0}], at=(a,r,dg)=>[a.cx+r*Math.cos(dg*Math.PI/180),a.cy-r*Math.sin(dg*Math.PI/180)];
  const dots=(a,r,dgs)=>dgs.forEach(dg=>{const p=at(a,r,dg); sv('circle',{cx:p[0],cy:p[1],r:4.8,fill:'var(--c1)'},s);});
  const E=atoms.map(a=>{[16,38,60].forEach(r=>sv('circle',{cx:a.cx,cy:a.cy,r,fill:'none',stroke:'var(--gr)','stroke-width':2.2},s)); sv('circle',{cx:a.cx,cy:a.cy,r:5,fill:'var(--c2)'},s);
    dots(a,16,[200]); dots(a,38,[130,220,310]); dots(a,60,[250]); const vp=at(a,16,20), lp=at(a,38,40), mp=at(a,60,70);
    const vac=sv('circle',{cx:vp[0],cy:vp[1],r:6,fill:'none',stroke:'var(--mu)','stroke-width':1.6,'stroke-dasharray':'3 3'},s), le=sv('circle',{cx:lp[0],cy:lp[1],r:4.8,fill:'var(--c1)'},s);
    const o={a,vp,lp,mp,vac,le}; if(a.x) o.ph=sv('path',{d:packetPath(54,8,10),fill:'none',stroke:'var(--c3)','stroke-width':2.2,'stroke-linejoin':'round'},s); else o.me=sv('circle',{cx:mp[0],cy:mp[1],r:4.8,fill:'var(--c1)'},s);
    return o;});
  stext(s,105,246,'characteristic x-ray',{'text-anchor':'middle','font-weight':700,fill:'var(--c3)'}); stext(s,315,246,'Auger electron',{'text-anchor':'middle','font-weight':700,fill:'var(--c1)'});
  return u=>{const j=ease(seg(u,.25,.5)), q=ease(seg(u,.5,1));
    E.forEach(o=>{o.le.setAttribute('cx',lerp(o.lp[0],o.vp[0],j)); o.le.setAttribute('cy',lerp(o.lp[1],o.vp[1],j)); o.vac.style.display=j<1?'':'none';
      if(o.ph){const dd=lerp(0,104,q); o.ph.setAttribute('transform','translate('+(o.vp[0]+Math.cos(0.7)*dd).toFixed(1)+' '+(o.vp[1]-Math.sin(0.7)*dd).toFixed(1)+') rotate(-40)'); o.ph.style.display=u<.5?'none':'';}
      else{const dd=lerp(0,70,q); o.me.setAttribute('cx',o.mp[0]+0.342*dd); o.me.setAttribute('cy',o.mp[1]-0.94*dd);}});};}});

AV['source-half-lives']=root=>avBars(root,{label:'Half-lives of five sealed-source radionuclides on a log scale, coloured by decay mode',cap:'Blue bars: electron capture. Orange bars: β⁻. Half-lives run from 17 days to 30 years.',
  m:{l:112,r:54},x:{min:10,max:100000,log:true,ticks:[10,100,1000,10000,100000],fmt:v=>String(v),label:'Half-life (days), log scale'},
  rows:[{t:'Pd-103 · EC',v:17.0,col:'var(--c1)',val:'17.0 d'},{t:'I-125 · EC',v:59.4,col:'var(--c1)',val:'59.4 d'},{t:'Ir-192 · β⁻',v:73.8,col:'var(--c2)',val:'73.8 d'},{t:'Co-60 · β⁻',v:1925,col:'var(--c2)',val:'5.27 y'},{t:'Cs-137 · β⁻',v:10994,col:'var(--c2)',val:'30.1 y'}]});

AV['nuclide-bins']=root=>avTimeline(root,{h:246,label:'Five radionuclides sorted by decay mode into beta minus, alpha, and beta plus emitters',cap:'Y-90, Lu-177, and I-131 are β⁻ emitters. Ra-223 is an α emitter. F-18 is a β⁺ emitter.',dur:4600,build:s=>{
  const bins=[{x:12,w:170,t:'β⁻ emitters',col:'var(--c2)'},{x:194,w:92,t:'α emitter',col:'var(--c3)'},{x:298,w:110,t:'β⁺ emitter',col:'var(--c1)'}];
  bins.forEach(b=>{sv('rect',{x:b.x,y:88,width:b.w,height:140,rx:6,fill:'none',stroke:b.col,'stroke-width':1.8},s); stext(s,b.x+b.w/2,110,b.t,{'text-anchor':'middle','font-weight':700,fill:b.col});});
  const chips=[['Y-90',50,97,134,0],['F-18',130,353,160,2],['I-131',210,97,198,0],['Ra-223',290,240,160,1],['Lu-177',370,97,166,0]].map(([n,sx,tx,ty,b])=>{const g=sv('g',{},s), r=sv('rect',{width:76,height:26,rx:5,fill:'var(--paper)',stroke:'var(--fg)','stroke-width':1.6},g); stext(g,38,14,n,{'text-anchor':'middle','dominant-baseline':'central','font-size':14.5,'font-weight':600}); return {g,r,sx,tx,ty,col:bins[b].col};});
  return u=>chips.forEach((c,i)=>{const p=ease(seg(u,.08+i*.13,.4+i*.13)), x=lerp(c.sx,c.tx,p), y=lerp(28,c.ty,p); c.g.setAttribute('transform','translate('+(x-38).toFixed(1)+' '+(y-13).toFixed(1)+')'); c.r.style.stroke=p>=1?c.col:'var(--fg)';});}});

AV['scheme-arrows']=root=>avTimeline(root,{h:262,label:'A decay-scheme layout with an arrow for each process: beta minus, beta plus or electron capture, alpha, and gamma or internal conversion',cap:'Energy runs up and Z runs right. β⁻ goes down-right, β⁺ or EC short down-left, α steep down-left, and γ or IC straight down.',dur:5200,build:s=>{
  const mk=avArrowDef(s), lv=(x,y)=>sv('line',{x1:x,y1:y,x2:x+70,y2:y,stroke:'var(--fg)','stroke-width':2.6},s);
  lv(206,46); lv(311,112); lv(311,190); lv(117,62); lv(27,206);
  stext(s,241,34,'parent',{'text-anchor':'middle','font-weight':600}); [['Z − 2',62],['Z − 1',152],['Z',241],['Z + 1',346]].forEach(([t,x])=>stext(s,x,236,t,{'text-anchor':'middle','font-size':14,fill:'var(--mu)'}));
  avLine(s,mk,20,222,400,222,'var(--mu)',1.4);
  const P=[{d:avGrow(s,mk,276,46,311,112,'var(--c2)'),t:'β⁻',x:300,y:84,col:'var(--c2)'},{d:avGrow(s,mk,206,46,188,62,'var(--c1)'),t:'β⁺ or EC',x:184,y:44,col:'var(--c1)',a:'end'},{d:avGrow(s,mk,206,46,98,206,'var(--c3)'),t:'α',x:142,y:150,col:'var(--c3)'},{d:avGrow(s,mk,346,112,346,190,'var(--c4)'),t:'γ or IC',x:354,y:156,col:'var(--c4)'}].map(o=>(o.e=stext(s,o.x,o.y,o.t,{'font-weight':700,fill:o.col,'text-anchor':o.a||'start'}),o));
  return u=>P.forEach((o,i)=>{const p=ease(seg(u,.06+i*.22,.26+i*.22)); o.d(p); o.e.style.display=p>.4?'':'none';});}});

AV['scheme-cascades']=root=>avTimeline(root,{h:256,label:'Decay schemes of Co-60 and Cs-137 showing their beta minus decays and gamma emissions',cap:'Co-60 emits two photons per decay, 1.173 and 1.332 MeV. The 662 keV photon of Cs-137 comes from its daughter Ba-137m.',dur:5400,build:s=>{
  const mk=avArrowDef(s), Y=e=>220-e*60, lv=(x,e,w)=>sv('line',{x1:x,y1:Y(e),x2:x+(w||62),y2:Y(e),stroke:'var(--fg)','stroke-width':2.6},s);
  lv(20,2.824); lv(108,2.506,70); lv(108,1.333,70); lv(108,0,70); lv(232,1.176); lv(322,0.662,66); lv(322,0,66);
  stext(s,20,Y(2.824)-8,'Co-60',{'font-weight':700}); stext(s,143,238,'Ni-60',{'text-anchor':'middle',fill:'var(--mu)'}); stext(s,232,Y(1.176)-8,'Cs-137',{'font-weight':700}); stext(s,355,238,'Ba-137',{'text-anchor':'middle',fill:'var(--mu)'});
  stext(s,355,Y(0.662)-24,'Ba-137m',{'text-anchor':'middle','font-size':14,fill:'var(--mu)'}); stext(s,355,Y(0.662)-9,'2.55 min',{'text-anchor':'middle','font-size':13.5,fill:'var(--mu)'});
  const P=[{d:avGrow(s,mk,82,Y(2.824),106,Y(2.506),'var(--c2)'),t:'β⁻',x:92,y:90,col:'var(--c2)',a:.04},{d:avGrow(s,mk,130,Y(2.506),130,Y(1.333),'var(--c3)'),t:'1.173',x:138,y:112,col:'var(--c3)',a:.3},{d:avGrow(s,mk,160,Y(1.333),160,Y(0),'var(--c3)'),t:'1.332',x:168,y:186,col:'var(--c3)',a:.55},
    {d:avGrow(s,mk,294,Y(1.176),320,Y(0.662),'var(--c2)'),t:'β⁻',x:288,y:Y(0.662)+4,col:'var(--c2)',a:.04,an:'end'},{d:avGrow(s,mk,355,Y(0.662),355,Y(0),'var(--c3)'),t:'0.662',x:363,y:206,col:'var(--c3)',a:.3}].map(o=>(o.e=stext(s,o.x,o.y,o.t,{'font-weight':700,fill:o.col,'text-anchor':o.an||'start'}),o));
  return u=>P.forEach(o=>{const p=ease(seg(u,o.a,o.a+.22)); o.d(p); o.e.style.display=p>.4?'':'none';});}});

AV['beta-spectrum']=root=>{const g=E=>Math.sqrt(E)*(1-E)*(1-E)/0.286216; return avChart(root,{h:252,label:'A continuous beta energy spectrum with its mean near one third of the maximum, beside discrete lines from other radiations',cap:'β spectra are continuous because the energy is shared with a neutrino; the mean is about Emax/3. α, γ, conversion electrons, x-rays, and Auger electrons are discrete lines.',
  x:{min:0,max:1,ticks:[0,0.2,0.4,0.6,0.8,1],fmt:v=>String(v),label:'Energy as a fraction of Emax'},y:{min:0,max:1.2,ticks:[],label:'Relative number'},
  series:[{fn:g,color:'var(--c1)'},{pts:[[0.72,0],[0.72,0.55]],color:'var(--c3)',w:3.4},{pts:[[0.9,0],[0.9,0.85]],color:'var(--c3)',w:3.4}],
  vlines:[{x:1/3,label:'mean ≈ Emax/3',dy:170}],labels:[{x:0.37,y:1.1,t:'β: continuous',color:'var(--c1)',b:1},{x:1.0,y:1.1,t:'discrete lines',color:'var(--c3)',b:1,anchor:'end'}]});};

AV['production-routes']=root=>avTimeline(root,{h:256,label:'Reactor products gain neutrons and decay by beta minus; cyclotron products gain protons and decay by positron emission or electron capture',cap:'Reactor routes add neutrons, which leaves a nucleus neutron-rich (β⁻). Cyclotron routes add protons, which leaves it proton-rich (β⁺ or EC).',dur:5600,build:s=>{
  const mk=avArrowDef(s); avNZ(s,mk,false); stext(s,96,206,'stable nuclei',{'font-size':14.5,fill:'var(--mu)'});
  const sh=(x1,y1,x2,y2,off)=>{const dx=x2-x1, dy=y2-y1, L=Math.hypot(dx,dy), ux=dx/L, uy=dy/L, o=off||0; return [x1+ux*8-uy*o,y1+uy*8+ux*o,x2-ux*8-uy*o,y2-uy*8+ux*o];};
  const dot=(x,y)=>sv('circle',{cx:x,cy:y,r:6,fill:'var(--fg)'},s), hol=(x,y)=>sv('circle',{cx:x,cy:y,r:6,fill:'none',stroke:'var(--mu)','stroke-width':1.8},s);
  dot(196,108); dot(136,118); const H=[hol(232,108),hol(196,72),hol(100,82)];
  const A=[avGrow(s,mk,...sh(196,108,232,108),'var(--fg)',2.8),avGrow(s,mk,...sh(232,108,196,72),'var(--c2)',2.8),avGrow(s,mk,...sh(136,118,100,82,-5),'var(--fg)',2.8),avGrow(s,mk,...sh(100,82,136,118,-5),'var(--c1)',2.8)];
  const T=[stext(s,248,130,'reactor:',{'font-weight':700}),stext(s,248,148,'n capture, then β⁻',{}),stext(s,44,42,'cyclotron:',{'font-weight':700}),stext(s,44,60,'p in, n out, then β⁺ or EC',{})];
  return u=>{[[0,.04,.2],[1,.22,.4],[2,.52,.68],[3,.7,.88]].forEach(([i,a,b])=>A[i](ease(seg(u,a,b)))); H[0].style.display=u>.2?'':'none'; H[1].style.display=u>.4?'':'none'; H[2].style.display=u>.68?'':'none'; T[0].style.display=T[1].style.display=u>.04?'':'none'; T[2].style.display=T[3].style.display=u>.5?'':'none';};}});

AV['neutron-capture']=root=>avTimeline(root,{h:206,label:'A nucleus absorbs a reactor neutron and becomes the next heavier isotope, emitting a gamma ray',cap:'Neutron capture raises A by one: Co-59 becomes Co-60 and Ir-191 becomes Ir-192. Both are then β⁻ emitters.',dur:5200,build:s=>{
  const hex=[[0,0],[12,0],[-12,0],[6,10],[-6,10],[6,-10],[-6,-10]];
  const R=[{y:56,a:'Co-59',eq:'Co-59 + n → Co-60 + γ',t0:0},{y:150,a:'Ir-191',eq:'Ir-191 + n → Ir-192 + γ',t0:.5}].map(r=>{hex.forEach(p=>sv('circle',{cx:170+p[0],cy:r.y+p[1],r:6,fill:'var(--mu)','fill-opacity':.75},s));
    return Object.assign(r,{n:sv('circle',{cx:24,cy:r.y,r:6,fill:'var(--c1)'},s),nw:sv('circle',{cx:188,cy:r.y+10,r:6,fill:'var(--c1)'},s),g:sv('path',{d:packetPath(46,8,9),fill:'none',stroke:'var(--c3)','stroke-width':2.2,'stroke-linejoin':'round'},s),ta:stext(s,230,r.y-6,r.a,{'font-weight':600}),te:stext(s,230,r.y-6,r.eq,{'font-weight':600})});});
  return u=>R.forEach(r=>{const v=(u-r.t0)/.5, p=ease(seg(v,0,.4)), cap=v>=.4; r.n.setAttribute('cx',lerp(24,172,p)); r.n.style.display=cap?'none':''; r.nw.style.display=cap?'':'none';
    const q=ease(seg(v,.45,1)); r.g.setAttribute('transform','translate('+lerp(222,330,q).toFixed(1)+' '+(r.y+18)+')'); r.g.style.display=v<.45?'none':''; r.ta.style.display=cap?'none':''; r.te.style.display=cap?'':'none';});}});

AV['fission-yield']=root=>{const fy=A=>6.4*Math.exp(-0.5*Math.pow((A-97.5)/6.2,2))+6.6*Math.exp(-0.5*Math.pow((A-139)/5.5,2)); return avChart(root,{h:252,label:'Schematic fission product yield against mass number, with two peaks',cap:'Schematic. U-235 splits unevenly, so yields peak near A = 95 and A = 139. Mo-99 and Cs-137 each have a yield of about 6%.',
  x:{min:70,max:170,ticks:[70,90,110,130,150,170],fmt:v=>String(v),label:'Mass number A of the fission product'},y:{min:0.01,max:10,log:true,ticks:[0.01,0.1,1,10],fmt:v=>String(v),label:'Yield (% per fission), log scale'},
  series:[{fn:fy,color:'var(--c1)'}],marks:[{x:99,y:fy(99),label:'Mo-99',dx:-10,dy:-12,anchor:'end'},{x:137,y:fy(137),label:'Cs-137',dx:10,dy:-12}]});};

AV['decay-atoms']=root=>{
  const W=420,H=240,{s,c}=avShell(root,W,H,'One hundred radioactive atoms decaying over several half-lives, with the fraction remaining plotted beside them','Each atom decays at random, but the number left follows N = N₀e^(−λt), so the activity A = λN halves every half-life.');
  const order=(()=>{const a=[...Array(100).keys()]; let r=2024; for(let i=99;i>0;i--){r=(r*1103515245+12345)&0x7fffffff; const j=r%(i+1), t=a[i]; a[i]=a[j]; a[j]=t;} return a;})(), rank=[]; order.forEach((idx,k)=>{rank[idx]=k;});
  const at=[]; for(let k=0;k<100;k++) at.push(sv('circle',{cx:24+(k%10)*20,cy:24+Math.floor(k/10)*20,r:7},s));
  const L=272,Rr=404,T=24,B=196, X=t=>L+(Rr-L)*t/5, Y=f=>B-(B-T)*f;
  avLine(s,avArrowDef(s),L,B,Rr+2,B,'var(--fg)',1.5); sv('line',{x1:L,y1:B,x2:L,y2:T-4,stroke:'var(--fg)','stroke-width':1.5},s);
  [[1,'100%'],[0.5,'50%'],[0.25,'25%']].forEach(([f,t])=>{sv('line',{x1:L,y1:Y(f),x2:Rr,y2:Y(f),stroke:'var(--gr)','stroke-width':1},s); stext(s,L-5,Y(f),t,{'text-anchor':'end','dominant-baseline':'central','font-size':14,fill:'var(--mu)'});});
  for(let t=0;t<=5;t++) stext(s,X(t),B+18,String(t),{'text-anchor':'middle','font-size':14,fill:'var(--mu)'}); stext(s,(L+Rr)/2,B+38,'time (half-lives)',{'text-anchor':'middle','font-size':14.5});
  let d=''; for(let t=0;t<=5.001;t+=0.1) d+=(d?'L':'M')+X(t).toFixed(1)+' '+Y(Math.pow(2,-t)).toFixed(1); sv('path',{d,fill:'none',stroke:'var(--c1)','stroke-width':2.4},s); const mark=sv('circle',{r:5.5,fill:'var(--c2)'},s);
  c.innerHTML='<label>Time (half-lives)<input type="range" min="0" max="100" step="0.1" value="40"></label><output class="avo" aria-live="polite"></output>'; const rng=c.querySelector('input'), out=c.querySelector('output');
  const set=t=>{const n=Math.round(100*Math.pow(2,-t)); at.forEach((e,k)=>{const dead=rank[k]<100-n; e.style.fill=dead?'none':'var(--c1)'; e.style.stroke=dead?'var(--line)':'none'; e.style.strokeWidth=1.5;}); mark.setAttribute('cx',X(t)); mark.setAttribute('cy',Y(Math.pow(2,-t)));
    out.innerHTML='t = <span class="v">'+t.toFixed(2)+' T½</span>: <span class="f">'+n+'</span> of 100 atoms left, so A = <span class="f">'+fmt3(100*Math.pow(2,-t))+'%</span> of A₀';};
  rng.addEventListener('input',()=>set(+rng.value/20));
  return avPlay(c,3800,u=>{const t=2*ease(u); rng.value=t*20; set(t);});
};

AV['ci-bq']=root=>avTimeline(root,{h:214,label:'A curie ruler lined up with a becquerel ruler: one curie, one millicurie, and one microcurie',cap:'1 Ci = 3.7 × 10¹⁰ Bq, and each step down by a factor of 1000 divides both by 1000. So 1 mCi = 3.7 × 10⁷ Bq = 37 MBq.',dur:4600,build:s=>{
  const xs=[70,210,350]; sv('line',{x1:30,y1:70,x2:394,y2:70,stroke:'var(--fg)','stroke-width':1.6},s); sv('line',{x1:30,y1:150,x2:394,y2:150,stroke:'var(--fg)','stroke-width':1.6},s);
  stext(s,30,34,'curies',{'font-size':14,fill:'var(--mu)'}); stext(s,30,138,'becquerels',{'font-size':14,fill:'var(--mu)'}); stext(s,140,64,'÷ 1000',{'text-anchor':'middle','font-size':13.5,fill:'var(--mu)'}); stext(s,280,64,'÷ 1000',{'text-anchor':'middle','font-size':13.5,fill:'var(--mu)'});
  const C=[['1 Ci','3.7 × 10¹⁰ Bq','37 GBq'],['1 mCi','3.7 × 10⁷ Bq','37 MBq'],['1 µCi','3.7 × 10⁴ Bq','37 kBq']].map((t,i)=>{const x=xs[i], hot=i===1; return {x,top:stext(s,x,50,t[0],{'text-anchor':'middle','font-weight':700,fill:hot?'var(--find)':'var(--fg)'}),l:sv('line',{x1:x,y1:70,x2:x,y2:150,stroke:hot?'var(--find)':'var(--mu)','stroke-width':hot?2:1.2,'stroke-dasharray':'4 4'},s),d1:sv('circle',{cx:x,cy:70,r:5,fill:hot?'var(--find)':'var(--fg)'},s),d2:sv('circle',{cx:x,cy:150,r:5,fill:hot?'var(--find)':'var(--fg)'},s),b1:stext(s,x,172,t[1],{'text-anchor':'middle','font-size':14.5,fill:hot?'var(--find)':'var(--fg)','font-weight':hot?700:400}),b2:stext(s,x,194,t[2],{'text-anchor':'middle','font-weight':700,fill:hot?'var(--find)':'var(--fg)'})};});
  return u=>C.forEach((o,i)=>{const p=seg(u,.1+i*.25,.3+i*.25); [o.top,o.d1,o.d2,o.b1,o.b2].forEach(e=>e.style.display=p>0?'':'none'); o.l.style.display=p>.5?'':'none'; o.b1.style.opacity=o.b2.style.opacity=seg(p,.5,1);});}});

AV['half-life-mean-life']=root=>avChart(root,{h:252,label:'Fraction remaining against time in half-lives, with the half-life and mean life marked',cap:'The curve falls to 50% at T½ and to 36.8% at τ = 1.443 T½. The tangent at t = 0 reaches zero at τ.',
  x:{min:0,max:4,ticks:[0,1,2,3,4],label:'Time (half-lives)'},y:{min:0,max:1,ticks:[0,0.25,0.5,0.75,1],fmt:v=>Math.round(v*100)+'%',label:'Fraction remaining'},
  series:[{fn:t=>Math.pow(2,-t),color:'var(--c1)'},{pts:[[0,1],[1.4427,0]],color:'var(--c2)',dash:'6 4',w:1.8}],
  vlines:[{x:1,label:'T½',dy:30,dx:-6,anchor:'end'},{x:1.4427,label:'τ',dy:30}],marks:[{x:1,y:0.5,label:'50%',dx:8,dy:-8},{x:1.4427,y:0.3679,label:'36.8%',dx:8,dy:-8}],labels:[{x:2.0,y:0.84,t:'tangent at t = 0',color:'var(--c2)',b:1}],
  fixed:[0.5,3],dyn:t=>({marks:[{x:t,y:Math.pow(2,-t),color:'var(--find)',r:6,label:''}],out:'t = <span class="v">'+t.toFixed(2)+' T½</span> = '+(t*1.4427>0?(t/1.4427).toFixed(2):'0.00')+' τ: <span class="f">'+fmt3(100*Math.pow(2,-t))+'%</span> remains'})});

AV['half-life-steps']=root=>avBars(root,{label:'Fraction of a radionuclide remaining after zero to five half-lives',cap:'After n half-lives, (½)ⁿ remains. Express the elapsed time and the half-life in the same unit before dividing.',
  m:{l:62,r:56},x:{min:0,max:100,ticks:[0,25,50,75,100],fmt:v=>v+'%',label:'Fraction remaining'},rowH:34,
  rows:[0,1,2,3,4,5].map(n=>({t:'n = '+n,v:100*Math.pow(0.5,n),col:'var(--c1)',val:fmt3(100*Math.pow(0.5,n))+'%'}))});

AV['percent-per-time']=root=>avChart(root,{h:252,label:'Decay constant against the fraction lost per unit time, comparing minus natural log of one minus x with x itself',cap:'A loss of x per unit time means λ = −ln(1 − x). Using λ = x is only close for small x.',
  x:{min:0,max:0.8,ticks:[0,0.2,0.4,0.6,0.8],label:'Fraction lost per unit time, x'},y:{min:0,max:1.8,ticks:[0,0.5,1,1.5],label:'Decay constant λ (per unit time)'},
  series:[{fn:x=>-Math.log(1-x),color:'var(--c1)'},{pts:[[0,0],[0.8,0.8]],color:'var(--mu)',dash:'5 4',w:1.8}],labels:[{x:0.3,y:1.18,t:'λ = −ln(1 − x)',color:'var(--c1)',b:1},{x:0.62,y:0.44,t:'λ = x',color:'var(--mu)',b:1}],
  fixed:[0.1,0.5],dyn:x=>({marks:[{x,y:-Math.log(1-x),color:'var(--c2)',label:''},{x,y:x,color:'var(--mu)',label:''}],out:'x = <span class="v">'+Math.round(x*100)+'%</span>: λ = −ln(1 − '+x.toFixed(2)+') = <span class="f">'+fmt3(-Math.log(1-x))+'</span>, not '+x.toFixed(2)})});

AV['implant-dose']=root=>avChart(root,{h:252,label:'Dose rate falling exponentially, with the area under the curve equal to the initial rate times the mean life',cap:'The area under the curve equals a rectangle of height R₀ and width τ, so the total dose is R₀ × τ = R₀ × 1.443 T½.',
  x:{min:0,max:4,ticks:[0,1,2,3,4],label:'Time (in mean lives τ)'},y:{min:0,max:1.1,ticks:[0,0.5,1],label:'Dose rate (fraction of R₀)'},
  series:[{fn:t=>Math.exp(-t),color:'var(--c1)',area:'var(--c1)'},{pts:[[0,1],[1,1],[1,0]],color:'var(--c2)',dash:'6 4',w:2}],vlines:[{x:1,label:'τ = 1.443 T½',dy:16,dx:6}],labels:[{x:1.4,y:0.68,t:'dose = R₀ × τ',color:'var(--c2)',b:1}]});


// ---------------------------------------------------------------- 3.4 calibration conventions
AV['calibration-points']=root=>{
  const W=420,H=292,{s,c}=avShell(root,W,H,'Where 1 cGy per MU is defined under SSD calibration and under SAD calibration, and the inverse-square factors that follow','SSD calibration puts the surface at 100 cm, so the point is at 100 + d_max from the source. SAD calibration puts the point at 100 cm. Dose per MU follows (d_cal / d)². Not to scale.');
  const mk=avArrowDef(s), SX=132, SY=26, Y100=158, DM=22, X0=80, X1=184, YB=270, XD=240, DMX=1.5;
  const sb=(p,x,y,base,sub,at)=>{const t=stext(p,x,y,base,at); const u=sv('tspan',{'font-size':11,dy:3},t); u.textContent=sub; return t;};
  [-1,1].forEach(g=>sv('line',{x1:SX,y1:SY,x2:SX+g*58,y2:YB,stroke:'var(--gr)','stroke-width':1.8},s));
  const ph=sv('rect',{x:X0,width:X1-X0,fill:'var(--gr)','fill-opacity':.5},s);
  sv('line',{x1:X0-6,y1:Y100,x2:XD,y2:Y100,stroke:'var(--mu)','stroke-width':1.3,'stroke-dasharray':'5 4'},s);
  const top=sv('line',{x1:X0-6,x2:X1+6,stroke:'var(--c1)','stroke-width':2.6},s);
  sv('circle',{cx:SX,cy:SY,r:5.5,fill:'var(--fg)'},s); stext(s,SX+10,SY+5,'source',{'font-size':14,fill:'var(--mu)'});
  const lab1=stext(s,X0-10,0,'surface',{'text-anchor':'end','font-size':14,fill:'var(--c1)','font-weight':600}), dot=sv('circle',{cx:SX,r:6,fill:'var(--c2)'},s), lab2=stext(s,X0-10,0,'1 cGy/MU',{'text-anchor':'end','font-size':13.5,fill:'var(--c2)','font-weight':700});
  const br=sv('line',{x1:X1+10,x2:X1+10,stroke:'var(--fg)','stroke-width':1.6},s), t1=sv('line',{x1:X1+5,x2:X1+15,stroke:'var(--fg)','stroke-width':1.6},s), t2=sv('line',{x1:X1+5,x2:X1+15,stroke:'var(--fg)','stroke-width':1.6},s), dm=sb(s,X1+20,0,'d','max',{'font-size':14});
  const dl=avLine(s,mk,XD,SY,XD,0,'var(--c2)',2.2); sb(s,XD+6,92,'d','cal',{'font-weight':700,'font-size':15,fill:'var(--c2)'}); stext(s,XD+6,Y100+4,'100 cm',{'font-size':13.5,fill:'var(--mu)'});
  const PX=298, P=[stext(s,PX,48,'',{'font-weight':700,'font-size':15}),stext(s,PX,82,'calibration distance',{'font-size':13,fill:'var(--mu)'}),stext(s,PX,104,'',{'font-weight':700,'font-size':17}),
    stext(s,PX,150,'SSD technique',{'font-size':13,fill:'var(--mu)'}),stext(s,PX,172,'',{'font-weight':700,'font-size':17}),stext(s,PX,188,'at SSD 100 cm',{'font-size':13,fill:'var(--mu)'}),
    stext(s,PX,222,'SAD technique',{'font-size':13,fill:'var(--mu)'}),stext(s,PX,244,'',{'font-weight':700,'font-size':17})];
  const F=sad=>{const dc=sad?100:100+DMX; return {name:sad?'SAD calibration':'SSD calibration', dc:sad?'100 cm':'101.5 cm', a:Math.pow(dc/(100+DMX),2), b:Math.pow(dc/100,2)};};
  const set=t=>{const yT=Y100-DM*t, yP=yT+DM, sad=t>.5, f=F(sad);
    ph.setAttribute('y',yT); ph.setAttribute('height',YB-yT); top.setAttribute('y1',yT); top.setAttribute('y2',yT); lab1.setAttribute('y',yT+5); dot.setAttribute('cy',yP); lab2.setAttribute('y',yP+5);
    br.setAttribute('y1',yT); br.setAttribute('y2',yP); t1.setAttribute('y1',yT); t1.setAttribute('y2',yT); t2.setAttribute('y1',yP); t2.setAttribute('y2',yP); dm.setAttribute('y',(yT+yP)/2+5); dl.setAttribute('y2',yP-8);
    P[0].textContent=f.name; P[2].textContent=f.dc; P[4].textContent='× '+f.a.toFixed(3); P[7].textContent='× '+f.b.toFixed(3);};
  const {b:btns,o:out}=avBtns(c,'Calibration',['SSD calibration','SAD calibration']); let cur=null,started=false,tNow=0,target=0;
  const ui=to=>{const f=F(to===1); btns.forEach((x,k)=>x.setAttribute('aria-pressed',k===to?'true':'false')); out.innerHTML=f.name+': d<sub>cal</sub> = '+(to?'100 cm':'100 + d<sub>max</sub> = 101.5 cm')+'. SSD technique at SSD 100 cm: <span class="f">× '+f.a.toFixed(3)+'</span>. SAD technique: <span class="f">× '+f.b.toFixed(3)+'</span>.';};
  const go=(to,from)=>{ if(cur) cur.stop(); target=to; const a=from===undefined?tNow:from; cur=runOnce(1100,u=>{tNow=lerp(a,to,ease(u)); set(tNow); if(u>=1) ui(to);}); };
  btns.forEach((b,i)=>b.addEventListener('click',()=>{started=true; go(i);})); set(0); ui(0);
  return {enter(){ if(REDUCE||started) return; started=true; go(0,1); }, leave(){ if(cur){cur.stop(); cur=null; tNow=target; set(tNow); ui(target);} }, finish(){ started=true; if(cur){cur.stop(); cur=null;} tNow=0; target=0; set(0); ui(0); }};
};


// ---------------------------------------------------------------- 1.8 specific activity, 1.9 equilibrium, 1.10 photon interactions, 2.1 kerma and dose
const avSUP=n=>String(n).replace(/\d/g,d=>'⁰¹²³⁴⁵⁶⁷⁸⁹'[d]);
const avSci=v=>{const e=Math.floor(Math.log10(v)); return e>=3?(v/Math.pow(10,e)).toFixed(1)+' × 10'+avSUP(e):(v<10?v.toFixed(2):v.toFixed(0));};
const avLOGT={0.1:'0.1',1:'1',10:'10',100:'100',1000:'1000',1e4:'10⁴',1e5:'10⁵',1e6:'10⁶'};
const avSb=(p,x,y,base,sub,at)=>{const t=stext(p,x,y,base,at); const u=sv('tspan',{'font-size':11,dy:3},t); u.textContent=sub; return t;};
const avSaS=(td,M)=>Math.LN2*6.02214076e23/(td*86400*M)/3.7e10;
const avSAN=[['Pd-103',16.99,102.91],['I-125',59.4,124.90],['Ir-192',73.8,191.96],['Co-60',5.27*365.25,59.93],['Cs-137',30.1*365.25,136.91],['Ra-226',1600*365.25,226.03]];
const avSeed=()=>{const a=[...Array(100).keys()]; let r=2024; for(let i=99;i>0;i--){r=(r*1103515245+12345)&0x7fffffff; const j=r%(i+1), t=a[i]; a[i]=a[j]; a[j]=t;} const rk=[]; a.forEach((idx,k)=>{rk[idx]=k;}); return rk;};
const avPct=v=>Math.round(v*100)+'%';

AV['sa-formula']=root=>avChart(root,{h:272,label:'Specific activity of six nuclides against half-life on log axes, with a line for the molar mass set by the slider',cap:'S = ln 2 · N_A / (T½ · M). A shorter half-life or a lighter atom raises S. Dots are real nuclides; the line is S for the molar mass on the slider.',
  x:{min:10,max:1e6,log:true,ticks:[10,100,1000,1e4,1e5,1e6],fmt:v=>avLOGT[v],label:'Half-life (days), log scale'},y:{min:0.5,max:2e5,log:true,ticks:[1,10,100,1000,1e4,1e5],fmt:v=>avLOGT[v]||String(v),label:'Specific activity (Ci/g), log scale'},
  marks:avSAN.map(([n,td,M],i)=>({x:td,y:avSaS(td,M),label:n,dx:i===5?-8:8,dy:[-8,4,18,-8,-8,-10][i],anchor:i===5?'end':'start',color:'var(--c2)'})),
  slider:{min:50,max:250,value:100,label:'Molar mass M (g/mol)'},
  dyn:M=>({series:[{fn:td=>avSaS(td,M),color:'var(--c1)'}],out:'M = <span class="v">'+Math.round(M)+' g/mol</span>: S at a half-life of 100 d is <span class="f">'+fmt3(avSaS(100,M))+' Ci/g</span>. Doubling T<sub>½</sub> or M halves it.'})});

AV['sa-order']=root=>{const R=avSAN.map(([n,td,M])=>({n,S:avSaS(td,M)})).sort((a,b)=>b.S-a.S); return avBars(root,{rowH:36,label:'Specific activity of six brachytherapy and teletherapy nuclides, largest first, on a log scale',cap:'Pd-103 and I-125 are the most active per gram and Ra-226 the least. 1 g of Ra-226 is about 1 Ci, which is how the curie was defined.',
  m:{l:76,r:92},x:{min:0.1,max:1e6,log:true,ticks:[0.1,1,10,100,1000,1e4,1e5,1e6],fmt:v=>avLOGT[v],label:'Specific activity (Ci/g), log scale'},
  rows:R.map(r=>({t:r.n,v:r.S,col:r.n==='Ra-226'?'var(--c2)':'var(--c1)',val:avSci(r.S)})),vlines:[{x:1,label:'1 Ci/g'}]});};

AV['source-size']=root=>avTimeline(root,{h:218,label:'The mass of iridium, cobalt, and caesium that gives 10 curies, drawn as discs with area in proportion to mass',cap:'10 Ci (370 GBq) is about 1 mg of Ir-192 but over 100 mg of Cs-137, so high specific activity gives a small source. Disc area is proportional to mass.',dur:3600,build:s=>{
  const N=[['Ir-192',73.8,191.96,84],['Co-60',5.27*365.25,59.93,204],['Cs-137',30.1*365.25,136.91,330]], m=N.map(n=>3.7e11/(Math.LN2*6.02214076e23/(n[1]*86400*n[2]))*1e3), R=m.map(v=>5.5*Math.sqrt(v/m[0]));
  stext(s,210,18,'10 Ci of each nuclide',{'text-anchor':'middle',fill:'var(--mu)'});
  const D=N.map((n,i)=>({c:sv('circle',{cx:n[3],cy:100,r:0,fill:'var(--c2)','fill-opacity':.85},s),n:stext(s,n[3],178,n[0],{'text-anchor':'middle','font-weight':700}),m:stext(s,n[3],200,m[i]<10?m[i].toFixed(1)+' mg':Math.round(m[i])+' mg',{'text-anchor':'middle',fill:'var(--c2)','font-weight':600}),r:R[i]}));
  return u=>D.forEach((o,i)=>{const p=ease(seg(u,.1+i*.15,.55+i*.15)); o.c.setAttribute('r',o.r*p); o.n.style.display=o.m.style.display=p>.95?'':'none';});}});

AV['carrier-atoms']=root=>{
  const W=420,H=240,{s,c}=avShell(root,W,H,'A source in which only part of the atoms are radioactive, with the fraction of the theoretical specific activity shown beside it','Reactor-made sources keep stable atoms of the target element (carrier), so the specific activity falls short of the theoretical value in proportion to the radioactive fraction. The fraction shown is illustrative.');
  const rk=avSeed(), at=[]; for(let k=0;k<100;k++) at.push(sv('circle',{cx:24+(k%10)*20,cy:26+Math.floor(k/10)*20,r:7},s));
  const BX=318, B0=206, BT=30; stext(s,262,18,'S ÷ theoretical S',{'font-size':13.5,fill:'var(--mu)'}); sv('line',{x1:BX-14,y1:B0,x2:BX+74,y2:B0,stroke:'var(--fg)','stroke-width':1.5},s);
  const bar=sv('rect',{x:BX,width:46,fill:'var(--c2)','fill-opacity':.85,rx:2},s), pct=stext(s,BX+23,0,'',{'text-anchor':'middle','font-weight':700,fill:'var(--c2)'}); stext(s,BX-18,BT+4,'100%',{'text-anchor':'end','font-size':13.5,fill:'var(--mu)'}); stext(s,BX-18,B0+4,'0',{'text-anchor':'end','font-size':13.5,fill:'var(--mu)'});
  c.innerHTML='<label>Radioactive fraction of the atoms<input type="range" min="5" max="100" step="1" value="20"></label><output class="avo" aria-live="polite"></output>'; const rng=c.querySelector('input'), out=c.querySelector('output');
  const set=f=>{const n=Math.round(100*f); at.forEach((e,k)=>{const on=rk[k]<n; e.style.fill=on?'var(--c2)':'none'; e.style.stroke=on?'none':'var(--mu)'; e.style.strokeWidth=1.4;}); const h=(B0-BT)*f; bar.setAttribute('y',B0-h); bar.setAttribute('height',h); pct.setAttribute('y',B0-h-6); pct.textContent=Math.round(100*f)+'%';
    out.innerHTML='Radioactive fraction = <span class="v">'+Math.round(100*f)+'%</span>: specific activity is <span class="f">'+Math.round(100*f)+'%</span> of the theoretical value';};
  rng.addEventListener('input',()=>set(+rng.value/100));
  return avPlay(c,3600,u=>{const f=lerp(1,0.2,ease(u)); rng.value=Math.round(f*100); set(f);});
};

const avMoP=65.94, avMoD=6.0067, avLp=Math.LN2/avMoP, avLd=Math.LN2/avMoD, avApF=t=>Math.exp(-avLp*t), avAdF=(t,f)=>f*avLd/(avLd-avLp)*(Math.exp(-avLp*t)-Math.exp(-avLd*t)), avTmax=Math.log(avLd/avLp)/(avLd-avLp);
AV['ingrowth']=root=>avChart(root,{h:258,label:'Parent and daughter activity after elution for Mo-99 and Tc-99m: the daughter rises from zero to a peak and then follows the parent',cap:'The daughter starts at zero, peaks, and then decays with the parent. If only a fraction f of the parent decays feed the daughter, the daughter curve is multiplied by f. Mo-99 and Tc-99m shown.',
  x:{min:0,max:120,ticks:[0,24,48,72,96,120],label:'Time after elution (h)'},y:{min:0,max:1.1,ticks:[0,0.25,0.5,0.75,1],fmt:avPct,label:'Activity (fraction of the initial Mo-99)'},
  series:[{fn:avApF,color:'var(--c1)'}],labels:[{x:76,y:0.8,t:'Mo-99 (parent)',color:'var(--c1)',b:1}],
  slider:{min:0.5,max:1,value:0.88,label:'Fraction f of parent decays that feed the daughter'},
  dyn:f=>({series:[{fn:t=>avAdF(t,f),color:'var(--c2)'}],marks:[{x:avTmax,y:avAdF(avTmax,f),color:'var(--c2)',label:'peak',dx:8,dy:-8}],labels:[{x:46,y:0.12,t:'Tc-99m (daughter)',color:'var(--c2)',b:1}],out:'f = <span class="v">'+f.toFixed(2)+'</span>: the daughter peaks at <span class="f">'+Math.round(avTmax)+' h</span> at '+avPct(avAdF(avTmax,f))+' of the initial parent activity'})});

AV['peak-crossing']=root=>{const A=(t,r)=>Math.exp(-Math.LN2*t/r), D=(t,r)=>r/(r-1)*(Math.exp(-Math.LN2*t/r)-Math.exp(-Math.LN2*t)), T=r=>Math.log(r)/(Math.LN2*(1-1/r));
  return avChart(root,{h:256,label:'Parent and daughter activity against time in daughter half-lives, with the peak of the daughter where the two curves cross',cap:'The daughter activity peaks at the moment it equals the parent activity. The slider sets the ratio of the parent half-life to the daughter half-life.',
  x:{min:0,max:10,ticks:[0,2,4,6,8,10],label:'Time (daughter half-lives)'},y:{min:0,max:1.05,ticks:[0,0.25,0.5,0.75,1],fmt:avPct,label:'Activity (fraction of the initial parent)'},
  slider:{min:1.5,max:100,log:true,value:11,label:'Parent half-life ÷ daughter half-life'},
  dyn:r=>({series:[{fn:t=>A(t,r),color:'var(--c1)'},{fn:t=>D(t,r),color:'var(--c2)'}],vlines:[{x:T(r),label:'peak',dy:150,dx:6}],marks:[{x:T(r),y:A(T(r),r),color:'var(--fg)',r:6,label:'equal',dx:8,dy:-10}],out:'T<sub>p</sub>/T<sub>d</sub> = <span class="v">'+fmt3(r)+'</span>: the daughter peaks at <span class="f">t = '+T(r).toFixed(2)+' T<sub>d</sub></span>, where A<sub>d</sub> = A<sub>p</sub> = '+avPct(A(T(r),r))})});};

AV['equilibrium-types']=root=>{const R=(t,r)=>r/(r-1)*(1-Math.exp(-Math.LN2*(1-1/r)*t)); return avChart(root,{h:256,label:'Ratio of daughter to parent activity against time for three parent to daughter half-life ratios',cap:'Transient: the ratio levels off at T_p/(T_p − T_d), above 1. Secular: the parent half-life is so long that the ratio reaches 1 within about seven daughter half-lives.',
  x:{min:0,max:12,ticks:[0,2,4,6,8,10,12],label:'Time (daughter half-lives)'},y:{min:0,max:1.7,ticks:[0,0.5,1,1.5],label:'Daughter ÷ parent activity'},
  series:[{fn:t=>R(t,3),color:'var(--c1)'},{fn:t=>R(t,11),color:'var(--c2)'},{fn:t=>R(t,1000),color:'var(--c3)'}],vlines:[{x:7,label:'7 T_d',dy:150,dx:5}],
  labels:[{x:11.9,y:1.56,t:'T_p/T_d = 3: 1.50',anchor:'end',color:'var(--c1)',b:1},{x:11.9,y:1.2,t:'11: 1.10',anchor:'end',color:'var(--c2)',b:1},{x:11.9,y:0.88,t:'1000: about 1 (secular)',anchor:'end',color:'var(--c3)',b:1}]});};

AV['mo-tc-generator']=root=>avChart(root,{h:262,label:'Mo-99 and Tc-99m activity after elution, with and without the 88% branching fraction',cap:'The Tc-99m to Mo-99 ratio settles at 1.10 if every Mo-99 decay fed Tc-99m. About 88% do, so the real ratio is about 0.97. Tc-99m peaks about 23 h after elution.',
  x:{min:0,max:120,ticks:[0,24,48,72,96,120],label:'Time after elution (h)'},y:{min:0,max:1.1,ticks:[0,0.25,0.5,0.75,1],fmt:avPct,label:'Activity (fraction of the initial Mo-99)'},
  series:[{fn:avApF,color:'var(--c1)'},{fn:t=>avAdF(t,1),color:'var(--c2)',dash:'6 4',w:1.8},{fn:t=>avAdF(t,0.88),color:'var(--c2)'}],vlines:[{x:avTmax,label:'peak 23 h',dy:150,dx:6}],
  labels:[{x:78,y:0.9,t:'Mo-99',color:'var(--c1)',b:1},{x:52,y:0.2,t:'Tc-99m, f = 1 (dashed)',color:'var(--c2)'},{x:52,y:0.08,t:'Tc-99m, f = 0.88',color:'var(--c2)',b:1}],
  fixed:[20,96],
  dyn:t=>({marks:[{x:t,y:avApF(t),color:'var(--c1)',label:''},{x:t,y:avAdF(t,0.88),color:'var(--c2)',label:''}],out:'t = <span class="v">'+Math.round(t)+' h</span>: A<sub>Tc</sub>/A<sub>Mo</sub> = <span class="f">'+(avAdF(t,1)/avApF(t)).toFixed(2)+'</span> if all decays feed it, <span class="f">'+(avAdF(t,0.88)/avApF(t)).toFixed(2)+'</span> with the 88% branching'})});

AV['indirect-ionization']=root=>avTimeline(root,{h:222,label:'A photon passes through material without ionizing it, until it interacts and sets an electron in motion that ionizes along its track',cap:'Photons are indirectly ionizing. The ionization, and so the dose, is deposited along the track of the electron the photon sets in motion.',dur:5200,build:s=>{
  sv('rect',{x:110,y:56,width:296,height:110,fill:'var(--gr)','fill-opacity':.45},s);
  const ph=sv('path',{d:packetPath(54,8,10),fill:'none',stroke:'var(--c3)','stroke-width':2.2,'stroke-linejoin':'round'},s), ph2=sv('path',{d:packetPath(38,6,9),fill:'none',stroke:'var(--c3)','stroke-width':1.8,'stroke-linejoin':'round'},s);
  const ring=sv('circle',{cx:200,cy:110,r:0,fill:'none',stroke:'var(--mu)','stroke-width':1.6},s), el=sv('circle',{r:6,fill:'var(--c1)'},s), tr=sv('path',{d:'M200 110 L340 134',fill:'none',stroke:'var(--c1)','stroke-width':1.4,'stroke-dasharray':'3 4'},s);
  const dots=[...Array(9)].map((_,i)=>sv('circle',{cx:200+i*16,cy:110+i*3,r:2.6,fill:'var(--c2)'},s));
  const t1=stext(s,12,92,'photon: no ionization on the way in',{'font-size':14,fill:'var(--c3)','font-weight':600}), t2=stext(s,404,198,'electron ionizes along its track',{'text-anchor':'end','font-size':14,fill:'var(--c1)','font-weight':600}), t3=stext(s,226,46,'scattered photon',{'font-size':14,fill:'var(--c3)','font-weight':600});
  return u=>{const a=ease(seg(u,0,.4)); ph.setAttribute('transform','translate('+lerp(6,150,a)+' 110)'); ph.style.display=u>.4?'none':'';
    ring.setAttribute('r',22*seg(u,.4,.52)); ring.style.strokeOpacity=u<.4?0:1-seg(u,.48,.6);
    const e=ease(seg(u,.46,.95)); el.setAttribute('cx',lerp(200,340,e)); el.setAttribute('cy',lerp(110,134,e)); el.style.display=u<.46?'none':''; tr.style.display=u<.46?'none':'';
    dots.forEach((d,i)=>d.style.display=e>i/8.5&&u>.46?'':'none');
    const b=ease(seg(u,.46,.95)); ph2.setAttribute('transform','translate('+lerp(200,352,b)+' '+lerp(110,66,b)+') rotate(-30)'); ph2.style.display=u<.46?'none':'';
    t1.style.display=u>.05?'':'none'; t2.style.display=u>.9?'':'none'; t3.style.display=u>.9?'':'none';};}});

AV['attenuation-curve']=root=>avChart(root,{h:256,label:'Fraction of a narrow photon beam transmitted against absorber thickness in half-value layers',cap:'I = I₀e^(−μx). One HVL halves the beam, one mean free path (1.44 HVL) leaves 36.8%, and one TVL (3.32 HVL) leaves 10%.',
  x:{min:0,max:4,ticks:[0,1,2,3,4],label:'Thickness (half-value layers)'},y:{min:0,max:1,ticks:[0,0.25,0.5,0.75,1],fmt:avPct,label:'Fraction transmitted'},
  series:[{fn:x=>Math.pow(2,-x),color:'var(--c1)'}],vlines:[{x:1,label:'HVL',dy:34,dx:-5,anchor:'end'},{x:1.4427,label:'mean free path',dy:58},{x:3.3219,label:'TVL',dy:34,dx:-5,anchor:'end'}],
  marks:[{x:1,y:0.5,label:'50%',dx:8,dy:-8},{x:1.4427,y:0.3679,label:'36.8%',dx:8,dy:-8},{x:3.3219,y:0.1,label:'10%',dx:8,dy:-8}],
  fixed:[0.5,2],dyn:x=>({marks:[{x,y:Math.pow(2,-x),color:'var(--find)',r:6,label:''}],out:'x = <span class="v">'+x.toFixed(2)+' HVL</span> = '+(x/1.4427).toFixed(2)+' mean free paths: <span class="f">'+fmt3(100*Math.pow(2,-x))+'%</span> transmitted'})});

AV['interaction-regions-anim']=root=>{const Z=E=>E<0.03?'the photoelectric effect':(E<24?'Compton scattering':'pair production'); return avChart(root,{h:232,label:'Which photon interaction dominates in water across photon energy',cap:'In water the photoelectric effect dominates below about 30 keV, Compton scattering from about 30 keV to 24 MeV, and pair production above that. Every therapy beam sits in the Compton band.',
  x:{min:0.01,max:100,log:true,ticks:[0.01,0.1,1,10,100],fmt:v=>String(v),label:'Photon energy (MeV)'},y:{min:0,max:1,ticks:[],label:''},
  bands:[{x0:0.01,x1:0.03,fill:'var(--c1)',op:.3},{x0:0.03,x1:24,fill:'var(--c3)',op:.22},{x0:24,x1:100,fill:'var(--c2)',op:.3}],vlines:[{x:1.022,label:'1.022 MeV',dy:140,dx:-5,anchor:'end'}],
  labels:[{x:0.0173,y:0.55,t:'PE',anchor:'middle',color:'var(--c1)',b:1},{x:0.85,y:0.55,t:'Compton',anchor:'middle',color:'var(--c3)',b:1},{x:49,y:0.55,t:'pair',anchor:'middle',color:'var(--c2)',b:1}],
  fixed:[1.25,20],
  dyn:E=>({vlines:[{x:E,color:'var(--fg)'}],out:'E = <span class="v">'+fmt3(E)+' MeV</span>: <span class="f">'+Z(E)+'</span> dominates in water'})});};

AV['compton-energies']=root=>{const K=(E,th)=>1/(1+(E/0.511)*(1-Math.cos(th*Math.PI/180))); return avChart(root,{h:256,label:'Share of the incident energy kept by the scattered photon and given to the electron against scattering angle, for an incident energy set by the slider',cap:'E′ = E / [1 + (E/511 keV)(1 − cos θ)]. The scattered photon keeps less energy as the angle grows, and the electron receives the most at θ = 180°.',
  x:{min:0,max:180,ticks:[0,45,90,135,180],fmt:v=>v+'°',label:'Scattering angle θ'},y:{min:0,max:1,ticks:[0,0.25,0.5,0.75,1],fmt:avPct,label:'Fraction of the incident energy'},
  labels:[{x:60,y:0.9,t:'scattered photon',color:'var(--c1)',b:1},{x:100,y:0.08,t:'electron',color:'var(--c2)',b:1}],
  slider:{min:0.05,max:10,log:true,value:1,label:'Incident photon energy'},
  dyn:E=>({series:[{fn:th=>K(E,th),color:'var(--c1)'},{fn:th=>1-K(E,th),color:'var(--c2)'}],marks:[{x:180,y:1-K(E,180),color:'var(--c2)',label:'most',dx:-8,dy:-10,anchor:'end'}],
    out:'E = <span class="v">'+fmt3(E)+' MeV</span>: at 90° the photon keeps <span class="f">'+(E*K(E,90)).toFixed(3)+' MeV</span> and the electron gets <span class="f">'+(E*(1-K(E,90))).toFixed(3)+' MeV</span>. At 180° they are '+(E*K(E,180)).toFixed(3)+' and '+(E*(1-K(E,180))).toFixed(3)+' MeV'})});};

function avNist(k,E){const D=DATA.nistarr, L=D.E, V=D[k]; let i=0; while(i<L.length-2&&E>L[i+1]) i++; const a=Math.log(L[i]), b=Math.log(L[i+1]), t=(Math.log(E)-a)/(b-a); return Math.exp(Math.log(V[i])+t*(Math.log(V[i+1])-Math.log(V[i])));}
AV['mv-contrast']=root=>avChart(root,{h:260,label:'Transmission across 10 cm of soft tissue containing a 2 cm bone insert, at a photon energy set by the slider',cap:'Calculated from NIST coefficients for water and cortical bone. At kilovoltage energies bone stands out because of the photoelectric effect. At megavoltage energies the contrast is only the density difference.',
  x:{min:0,max:12,ticks:[0,4,8,12],label:'Position across the object (cm)'},y:{min:0,max:1.1,ticks:[0,0.25,0.5,0.75,1],fmt:avPct,label:'Transmission relative to tissue alone'},
  bands:[{x0:4,x1:8,fill:'var(--gr)',op:.9}],labels:[{x:6,y:0.06,t:'bone',anchor:'middle',color:'var(--mu)',b:1}],
  slider:{min:0.03,max:10,log:true,value:6,label:'Photon energy'},
  dyn:E=>{const mw=avNist('w',E), mb=avNist('b',E), r=Math.exp(-(mb*1.92-mw)*2); return {series:[{pts:[[0,1],[4,1],[4,r],[8,r],[8,1],[12,1]],color:'var(--c1)',w:2.8}],
    out:'E = <span class="v">'+fmt3(E)+' MeV</span>: the bone insert lowers transmission by <span class="f">'+(100*(1-r)).toFixed(1)+'%</span>. Bone to water per gram: '+(mb/mw).toFixed(2)+'; per cm³: '+(mb*1.92/mw).toFixed(2)+' (density ratio 1.92)'};}});

AV['pe-z-cubed']=root=>avBars(root,{rowH:38,label:'Relative photoelectric coefficient proportional to the cube of the atomic number, for soft tissue, bone, tungsten, and lead',cap:'At a fixed energy the photoelectric coefficient scales as Z³, relative to soft tissue (Z about 7.4). Bone gives kilovoltage contrast, and tungsten and lead shield well.',
  m:{l:134,r:48},x:{min:1,max:1e4,log:true,ticks:[1,10,100,1000,1e4],fmt:v=>avLOGT[v],label:'(Z / 7.4)³, log scale'},
  rows:[['soft tissue (7.4)',7.4,'var(--c1)'],['bone (13)',13,'var(--c1)'],['tungsten (74)',74,'var(--c2)'],['lead (82)',82,'var(--c2)']].map(([t,z,col])=>{const v=Math.pow(z/7.4,3); return {t,v,col,val:v<10?v.toFixed(1):Math.round(v)};})});

AV['fluence-box']=root=>{
  const W=420,H=268,{s,c}=avShell(root,W,H,'Photons crossing a patch of area 1 cm², with the photon count and the energy they carry added up as fluence and energy fluence','Each dot is one photon crossing the patch. Fluence Φ counts the dots per cm². Energy fluence Ψ adds up the energy of the dots per cm². A photon with more energy adds more to Ψ and the same one to Φ.');
  const SX=20, SY=34, SQ=170, P=[[28,26],[84,22],[140,28],[54,62],[112,62],[152,86],[26,98],[82,98],[124,116],[50,134],[100,146],[150,148],[28,62],[84,60]], RANK=[3,7,0,10,5,12,1,8,13,2,6,11,4,9];
  stext(s,SX,22,'1 cm² patch, seen along the beam',{'font-size':14,fill:'var(--mu)'});
  sv('rect',{x:SX,y:SY,width:SQ,height:SQ,fill:'none',stroke:'var(--fg)','stroke-width':2.2},s);
  const dots=P.map(([x,y])=>sv('circle',{cx:SX+x,cy:SY+y,r:0},s));
  sv('circle',{cx:SX+10,cy:SY+SQ+26,r:6,fill:'var(--c1)'},s); stext(s,SX+22,SY+SQ+31,'1 MeV photon',{'font-size':13.5}); sv('circle',{cx:SX+122,cy:SY+SQ+26,r:9,fill:'var(--c2)'},s); stext(s,SX+136,SY+SQ+31,'2 MeV',{'font-size':13.5});
  const CX=212, CW=198, card=(y,title,note)=>{sv('rect',{x:CX,y:y,width:CW,height:92,rx:8,fill:'var(--paper-2)',stroke:'var(--rule)'},s); stext(s,CX+14,y+23,title,{'font-size':14,fill:'var(--mu)'}); const big=stext(s,CX+14,y+58,'',{'font-weight':700,'font-size':28}); stext(s,CX+14,y+80,note,{'font-size':13,fill:'var(--mu)'}); return big;};
  const bigPhi=card(SY,'Fluence Φ','photons per cm²: count the dots'), bigPsi=card(SY+104,'Energy fluence Ψ','per cm²: add up the energies');
  bigPsi.setAttribute('fill','var(--find)');
  c.innerHTML='<label>Photons crossing the patch<input id="fb-n" type="range" min="4" max="14" step="1" value="10"></label><label>Photons with 2 MeV<input id="fb-k" type="range" min="0" max="10" step="1" value="4"></label><output class="avo" aria-live="polite"></output>';
  const nr=c.querySelector('#fb-n'), kr=c.querySelector('#fb-k'), out=c.querySelector('output');
  const set=()=>{const n=+nr.value; kr.max=n; if(+kr.value>n) kr.value=n; const k=+kr.value, two=new Set([...Array(n).keys()].sort((a,b)=>RANK.indexOf(a)-RANK.indexOf(b)).slice(0,k)), E=n+k;
    P.forEach((_,i)=>{const on=i<n, w=two.has(i); dots[i].setAttribute('r',on?(w?9:6):0); dots[i].setAttribute('fill',w?'var(--c2)':'var(--c1)');});
    bigPhi.textContent=String(n); bigPsi.textContent=E+' MeV';
    out.innerHTML='Φ = <span class="v">'+n+' photons</span> / cm². Ψ = '+(n-k)+' × 1 MeV + '+k+' × 2 MeV = <span class="f">'+E+' MeV</span> / cm²';};
  nr.addEventListener('input',set); kr.addEventListener('input',set); set(); return {enter(){},leave(){},finish(){}};
};
AV['kerma-split']=root=>{
  const W=420,H=244,{s,c}=avShell(root,W,H,'Kerma is the energy transferred to charged particles; a small fraction g of it is radiated, and the rest is the collision kerma','K = K_col + K_rad, with K_col = K (1 − g) = Ψ μ_en/ρ. g is small at therapy energies (about 0.3% for Co-60 in water), so the slider exaggerates it.');
  const X0=40, BW=340; stext(s,X0,24,'Kerma K: energy transferred to electrons',{'font-weight':600}); sv('rect',{x:X0,y:34,width:BW,height:36,fill:'var(--c1)','fill-opacity':.3,stroke:'var(--c1)','stroke-width':1.6},s);
  sv('line',{x1:X0,y1:70,x2:X0,y2:116,stroke:'var(--mu)','stroke-dasharray':'4 4'},s); sv('line',{x1:X0+BW,y1:70,x2:X0+BW,y2:116,stroke:'var(--mu)','stroke-dasharray':'4 4'},s);
  const col=sv('rect',{y:116,height:36,fill:'var(--c1)','fill-opacity':.75},s), rad=sv('rect',{y:116,height:36,fill:'var(--c2)'},s);
  const lc=stext(s,0,176,'',{'text-anchor':'middle','font-weight':700,fill:'var(--c1)'}), lr=stext(s,X0+BW,176,'',{'text-anchor':'end','font-weight':700,fill:'var(--c2)'});
  stext(s,X0,214,'collision part: becomes absorbed dose near the point',{'font-size':14,fill:'var(--c1)'}); stext(s,X0,234,'radiative part: leaves as bremsstrahlung',{'font-size':14,fill:'var(--c2)'});
  c.innerHTML='<label>Radiative fraction g<input type="range" min="0" max="10" step="0.1" value="3"></label><output class="avo" aria-live="polite"></output>'; const rng=c.querySelector('input'), out=c.querySelector('output');
  const set=g=>{const wc=BW*(1-g); col.setAttribute('x',X0); col.setAttribute('width',wc); rad.setAttribute('x',X0+wc); rad.setAttribute('width',BW*g); lc.setAttribute('x',X0+wc/2); lc.textContent='K_col = (1 − g) K'; lr.textContent=g>0.005?'K_rad = g K':'';
    out.innerHTML='g = <span class="v">'+(100*g).toFixed(1)+'%</span>: K<sub>col</sub> = <span class="f">'+(100*(1-g)).toFixed(1)+'%</span> of K, and K<sub>rad</sub> = '+(100*g).toFixed(1)+'%';};
  rng.addEventListener('input',()=>set(+rng.value/100));
  return avPlay(c,2600,u=>{const g=0.03*ease(u); rng.value=(g*100).toFixed(1); set(g);});
};

const avKmu=0.045, avKk=3.0, avKb=1.05, avKerm=d=>Math.exp(-avKmu*d), avDose=d=>avKb*avKerm(d)*(1-Math.exp(-avKk*d)), avDcross=-Math.log(1-1/avKb)/avKk, avDmaxK=Math.log((avKk+avKmu)/avKmu)/avKk;
AV['buildup-kerma-dose']=root=>avChart(root,{h:258,label:'Absorbed dose and collision kerma against depth in a megavoltage photon beam',cap:'Schematic, with the gap exaggerated. Dose is below kerma in the build-up region, equals it where charged-particle equilibrium is reached, and stays slightly above it beyond d_max: D = β K_col.',
  x:{min:0,max:12,ticks:[0,2,4,6,8,10,12],label:'Depth (cm)'},y:{min:0,max:1.12,ticks:[0,0.5,1],label:'Relative to the surface kerma'},
  bands:[{x0:0,x1:avDcross,fill:'var(--c2)',op:.22}],series:[{fn:avKerm,color:'var(--c2)',dash:'6 4'},{fn:avDose,color:'var(--c1)'}],vlines:[{x:avDmaxK,label:'d_max',dy:150,dx:6}],
  labels:[{x:4.4,y:1.04,t:'dose D = β K_col',color:'var(--c1)',b:1},{x:6.2,y:0.58,t:'kerma K_col',color:'var(--c2)',b:1},{x:1.4,y:0.4,t:'build-up: D < K_col',color:'var(--c2)'}]});

AV['exposure-chain']=root=>avTimeline(root,{h:268,label:'One roentgen converted to charge per kilogram of air and then to dose to air',cap:'1 R = 2.58 × 10⁻⁴ C/kg. Multiplying by W_air/e = 33.97 J/C gives 8.76 × 10⁻³ J/kg, which is 0.876 cGy in air.',dur:4800,build:s=>{
  const mk=avArrowDef(s), R=[['exposure','1 R','var(--fg)'],['charge per kg of air','2.58 × 10⁻⁴ C/kg','var(--fg)'],['× energy per unit charge, W_air/e','33.97 J/C','var(--fg)'],['dose to air','8.76 × 10⁻³ J/kg = 0.876 cGy','var(--find)']];
  const rows=R.map((r,i)=>{const y=44+i*66, g=sv('g',{},s); sv('rect',{x:30,y:y-30,width:360,height:46,rx:7,fill:'none',stroke:i===3?'var(--find)':'var(--fg)','stroke-width':i===3?2.2:1.5},g); stext(g,44,y-14,r[0],{'font-size':13.5,fill:'var(--mu)'}); stext(g,44,y+9,r[1],{'font-weight':700,'font-size':i===3?16:17,fill:r[2]}); return g;});
  const ar=[0,1,2].map(i=>avGrow(s,mk,210,44+i*66+16,210,44+(i+1)*66-32,'var(--mu)',2));
  return u=>{rows.forEach((g,i)=>g.style.display=u>=i*.27?'':'none'); ar.forEach((a,i)=>a(ease(seg(u,i*.27+.08,i*.27+.25))));};}});

AV['equivalent-dose']=root=>avBars(root,{rowH:38,label:'Equivalent dose from the same 1 Gy absorbed dose for photons, electrons, protons, and alpha particles',cap:'1 Gy = 100 cGy = 100 rad. Equivalent dose weights the absorbed dose by the radiation type, so the same 1 Gy is 1, 1, 2, or 20 Sv.',
  m:{l:92,r:56},x:{min:0,max:20,ticks:[0,5,10,15,20],fmt:v=>String(v),label:'Equivalent dose for 1 Gy absorbed (Sv)'},
  rows:[['photons',1],['electrons',1],['protons',2],['α particles',20]].map(([t,w])=>({t,v:w,col:w>=20?'var(--c2)':'var(--c1)',val:w+' Sv'}))});


// ---------------------------------------------------------------- brachytherapy: sources, exposure and air kerma strength, TG-43
const avGL=(r,thDeg,L)=>{const th=thDeg*Math.PI/180, rho=r*Math.sin(th), z=r*Math.cos(th); if(rho<1e-9) return 1/(r*r-L*L/4); return (Math.atan2(z+L/2,rho)-Math.atan2(z-L/2,rho))/(L*rho);};
const avGAM=[['Co-60',13.2],['Ra-226',8.25],['Ir-192',4.69],['Cs-137',3.28],['I-125',1.45]], avWE=0.876;
const avKF=(u,K)=>{for(let i=1;i<K.length;i++){if(u<=K[i][0]){const a=K[i-1],b=K[i],p=(u-a[0])/(b[0]-a[0]||1); return a[1]+(b[1]-a[1])*ease(p);}} return K[K.length-1][1];};

AV['dose-rate-classes']=root=>{const Z=v=>v<2?'LDR':(v<=12?'MDR':'HDR'); return avChart(root,{h:236,label:'The dose rate scale in Gy per hour on a log axis, with the LDR, MDR, and HDR ranges shaded',cap:'ICRU 38: LDR is below 2 Gy/h, MDR is 2 to 12 Gy/h, and HDR is above 12 Gy/h. A permanent I-125 seed implant starts near 0.07 Gy/h.',
  x:{min:0.01,max:100,log:true,ticks:[0.01,0.1,1,10,100],fmt:v=>String(v),label:'Dose rate at the reference point (Gy/h)'},y:{min:0,max:1,ticks:[],label:''},
  bands:[{x0:0.01,x1:2,fill:'var(--c1)',op:.26},{x0:2,x1:12,fill:'var(--gr)',op:.9},{x0:12,x1:100,fill:'var(--c2)',op:.28}],vlines:[{x:2,label:'2',dy:150,dx:4},{x:12,label:'12',dy:150,dx:4}],
  labels:[{x:0.12,y:0.68,t:'LDR',anchor:'middle',color:'var(--c1)',b:1},{x:4.9,y:0.68,t:'MDR',anchor:'middle',color:'var(--mu)',b:1},{x:34,y:0.68,t:'HDR',anchor:'middle',color:'var(--c2)',b:1},{x:0.11,y:0.34,t:'permanent seeds',anchor:'start',color:'var(--c1)'}],
  marks:[{x:0.07,y:0.2,label:'',color:'var(--c1)',r:5}],fixed:[0.5,20],
  dyn:v=>({vlines:[{x:v,color:'var(--fg)'}],out:'D = <span class="v">'+fmt3(v)+' Gy/h</span>: <span class="f">'+Z(v)+'</span>'})});};

AV['isotope-map']=root=>{const D=[['Cs-131',9.69,30,'var(--c1)',-10,-12,'start'],['Pd-103',16.99,21,'var(--c1)',10,18,'start'],['I-125',59.4,28,'var(--c1)',10,16,'start'],['Ir-192',73.8,380,'var(--c2)',10,5,'start'],['Co-60',1925,1250,'var(--mu)',-10,-8,'end'],['Cs-137',10994,662,'var(--mu)',-10,-10,'end'],['Ra-226',584400,830,'var(--mu)',-10,-10,'end']];
  return avChart(root,{h:292,label:'Mean photon energy against half-life for the seed isotopes, Ir-192, and the older sources',cap:'LDR seed isotopes (blue) have low photon energy and short half-lives. Ir-192 (orange), the HDR isotope, has a higher energy and a half-life of 73.8 d. The older sources (grey) have half-lives of years or more.',
  x:{min:5,max:1e6,log:true,ticks:[10,100,1000,1e4,1e5,1e6],fmt:v=>v>=1e4?'10'+avSUP(Math.round(Math.log10(v))):String(v),label:'Half-life (days), log scale'},y:{min:10,max:2000,log:true,ticks:[10,100,1000],fmt:v=>String(v),label:'Mean photon energy (keV)'},
  marks:D.map(d=>({x:d[1],y:d[2],label:d[0],color:d[3],dx:d[4],dy:d[5],anchor:d[6]}))});};

AV['seed-cutaway']=root=>avTimeline(root,{h:228,label:'Cross-section of a seed: a titanium capsule around a marker rod, with photons escaping and electrons stopped by the wall',cap:'The capsule wall stops the electrons and the lowest-energy x-rays. Photons leave sideways with little loss, but the marker and end welds absorb those travelling along the axis, so the dose is slightly anisotropic.',dur:4600,build:s=>{
  const mk=avArrowDef(s);
  sv('rect',{x:70,y:94,width:280,height:42,rx:21,fill:'var(--gr)',stroke:'var(--fg)','stroke-width':2.4},s); sv('rect',{x:104,y:105,width:212,height:20,rx:3,fill:'var(--mu)','fill-opacity':.5,stroke:'var(--fg)','stroke-width':1.2},s);
  stext(s,210,120,'marker rod',{'text-anchor':'middle','font-size':12.5,fill:'var(--fg)'});
  const X=[128,170,210,250,292], up=X.map(x=>avGrow(s,mk,x,92,x,44,'var(--c3)',2.2)), dn=X.map(x=>avGrow(s,mk,x,138,x,186,'var(--c3)',2.2)), lf=avGrow(s,mk,72,115,46,115,'var(--c3)',1.6), rt=avGrow(s,mk,348,115,374,115,'var(--c3)',1.6);
  const el=X.map((x,i)=>sv('circle',{cx:x+16,cy:115,r:4.2,fill:'var(--c1)'},s)); const t1=stext(s,210,28,'photons leave sideways',{'text-anchor':'middle','font-size':14,fill:'var(--c3)','font-weight':600}), t2=stext(s,210,212,'wall stops electrons and low-energy x-rays',{'text-anchor':'middle','font-size':14,fill:'var(--c1)','font-weight':600});
  const t3=stext(s,8,148,'fewer photons',{'font-size':13.5}), t4=stext(s,8,164,'along the axis',{'font-size':13.5});
  return u=>{el.forEach((e,i)=>{const p=ease(seg(u,.04+i*.02,.36)); e.setAttribute('cy',lerp(115,i%2?132:99,p)); e.style.opacity=u>.4?Math.max(0,1-(u-.4)*4):1;});
    up.forEach((a,i)=>a(ease(seg(u,.4+i*.04,.7)))); dn.forEach((a,i)=>a(ease(seg(u,.4+i*.04,.7)))); lf(ease(seg(u,.55,.75))); rt(ease(seg(u,.55,.75))); t1.style.display=u>.7?'':'none'; t2.style.display=u>.4?'':'none'; t3.style.display=t4.style.display=u>.8?'':'none';};}});

AV['hdr-afterloader']=root=>avTimeline(root,{h:214,label:'An HDR source on a cable leaves a shielded afterloader, stops at three dwell positions in a catheter, and returns',cap:'The afterloader keeps the 10 Ci source in a shield, drives it on a cable through the catheter to programmed dwell positions, holds it for the planned dwell time at each, and retracts it. Staff are outside the room.',dur:7200,build:s=>{
  sv('rect',{x:12,y:70,width:84,height:90,rx:6,fill:'var(--gr)',stroke:'var(--fg)','stroke-width':2.2},s); stext(s,54,108,'after-',{'text-anchor':'middle','font-size':14}); stext(s,54,126,'loader',{'text-anchor':'middle','font-size':14});
  sv('line',{x1:96,y1:115,x2:392,y2:115,stroke:'var(--mu)','stroke-width':3,'stroke-dasharray':'2 5'},s); const DW=[200,262,324], dots=DW.map(x=>sv('circle',{cx:x,cy:115,r:9,fill:'none',stroke:'var(--c2)','stroke-width':2},s));
  stext(s,262,64,'dwell positions in the catheter',{'text-anchor':'middle','font-size':14,fill:'var(--c2)','font-weight':600}); stext(s,54,184,'shielded safe',{'text-anchor':'middle','font-size':13.5,fill:'var(--mu)'}); const lab=stext(s,262,186,'',{'text-anchor':'middle','font-size':14,fill:'var(--fg)','font-weight':600});
  const cab=sv('line',{x1:96,y1:115,x2:96,y2:115,stroke:'var(--fg)','stroke-width':2.4},s), src=sv('rect',{x:96,y:110,width:14,height:10,rx:2,fill:'var(--c2)'},s);
  const K=[[0,100],[.1,100],[.34,200],[.44,200],[.54,262],[.64,262],[.74,324],[.84,324],[1,100]];
  return u=>{const x=avKF(u,K); cab.setAttribute('x2',x); src.setAttribute('x',x-4); dots.forEach((d,i)=>{const on=(u>=.34+i*.2&&u<=.44+i*.2+.0); d.style.fill=on?'var(--c2)':(u>.44+i*.2?'var(--c2)':'none'); d.style.fillOpacity=on?.9:.25;});
    lab.textContent=u<.1?'':(u<.85?'source out, dwelling and moving':'source retracted');};}});

AV['dose-chain']=root=>avTimeline(root,{h:292,label:'From activity to exposure rate, air kerma rate, and dose rate in water',cap:'Activity is converted to exposure rate with Γ and the distance, to air kerma rate with W/e = 0.876 cGy/R, and to dose rate in water with Λ and the TG-43 factors.',dur:5200,build:s=>{
  const mk=avArrowDef(s), R=[['activity','A (mCi)','var(--fg)'],['× Γ / r²','exposure rate Ẋ (R/h)','var(--fg)'],['× 0.876 cGy/R','air kerma rate K̇ (cGy/h), S_K = K̇ r² (U)','var(--fg)'],['× Λ, G, g, F','dose rate in water (cGy/h)','var(--find)']];
  const rows=R.map((r,i)=>{const y=40+i*66, g=sv('g',{},s); sv('rect',{x:20,y:y-30,width:380,height:46,rx:7,fill:'none',stroke:i===3?'var(--find)':'var(--fg)','stroke-width':i===3?2.2:1.5},g); stext(g,34,y-14,r[0],{'font-size':13.5,fill:'var(--mu)'}); stext(g,34,y+8,r[1],{'font-weight':700,'font-size':15.5,fill:r[2]}); return g;});
  const ar=[0,1,2].map(i=>avGrow(s,mk,210,40+i*66+16,210,40+(i+1)*66-32,'var(--mu)',2));
  return u=>{rows.forEach((g,i)=>g.style.display=u>=i*.25?'':'none'); ar.forEach((a,i)=>a(ease(seg(u,i*.25+.08,i*.25+.23))));};}});

AV['gamma-compare']=root=>{const R=(g,r)=>g*10/(r*r); return avChart(root,{h:262,label:'Exposure rate against distance for 10 mCi of Ir-192 and of I-125',cap:'At equal activity, Ir-192 gives 3.2 times the exposure rate of I-125 at every distance, because Γ is larger. Both fall as 1/r².',
  x:{min:1,max:20,ticks:[1,5,10,15,20],label:'Distance (cm)'},y:{min:0.001,max:10,log:true,ticks:[0.001,0.01,0.1,1,10],fmt:v=>String(v),label:'Exposure rate (R/h) for 10 mCi'},
  series:[{fn:r=>R(4.69,r),color:'var(--c2)'},{fn:r=>R(1.45,r),color:'var(--c1)'}],labels:[{x:12,y:0.5,t:'Ir-192',color:'var(--c2)',b:1},{x:12,y:0.045,t:'I-125',color:'var(--c1)',b:1}],
  fixed:[5,20],dyn:r=>({marks:[{x:r,y:R(4.69,r),color:'var(--c2)',label:''},{x:r,y:R(1.45,r),color:'var(--c1)',label:''}],out:'r = <span class="v">'+r.toFixed(1)+' cm</span>: Ir-192 '+fmt3(R(4.69,r))+' R/h, I-125 '+fmt3(R(1.45,r))+' R/h, ratio <span class="f">'+(4.69/1.45).toFixed(1)+'</span>'})});};

AV['sphere-shells']=root=>avChart(root,{h:254,label:'Exposure rate from a point source against distance, as a percentage of its value at 1 cm',cap:'At distance r the photons cross a sphere of area 4πr², so the rate falls as 1/r². Doubling the distance spreads the same photons over four times the area.',
  x:{min:1,max:6,ticks:[1,2,3,4,5,6],label:'Distance from the source (cm)'},y:{min:0,max:100,ticks:[0,25,50,75,100],fmt:avPct2,label:'Exposure rate (% of the rate at 1 cm)'},series:[{fn:r=>100/(r*r),color:'var(--c1)'}],
  fixed:[2,5],dyn:r=>({marks:[{x:r,y:100/(r*r),color:'var(--find)',r:6,label:''}],out:'r = <span class="v">'+r.toFixed(1)+' cm</span>: the photons cross <span class="f">'+fmt3(r*r)+' times</span> the area, so the rate is '+fmt3(100/(r*r))+'% of the rate at 1 cm'})});
const avPct2=v=>v+'%';

AV['sk-per-mci']=root=>avBars(root,{rowH:38,label:'Air kerma strength per millicurie for five sources, from 0.876 times the exposure rate constant',cap:'S_K = 0.876 Γ A. Per millicurie, Ir-192 gives 4.1 U, so a 10 Ci (10,000 mCi) HDR source has about 4.1 × 10⁴ U.',
  m:{l:70,r:70},x:{min:0,max:12,ticks:[0,2,4,6,8,10,12],fmt:v=>String(v),label:'Air kerma strength per mCi (U/mCi)'},rows:avGAM.map(([n,g])=>({t:n,v:avWE*g,col:n==='Ir-192'?'var(--c2)':'var(--c1)',val:(avWE*g).toFixed(2)}))});

AV['sk-decay']=root=>{const S=(t)=>0.6*Math.pow(0.5,t/59.4); return avChart(root,{h:254,label:'Air kerma strength of an I-125 seed against time',cap:'S_K decays with the half-life of the source: 0.60 U at calibration falls to 0.30 U after 59.4 d. Seeds are ordered by S_K for the planned implant date.',
  x:{min:0,max:240,ticks:[0,60,120,180,240],label:'Time since calibration (days)'},y:{min:0,max:0.65,ticks:[0,0.15,0.3,0.45,0.6],fmt:v=>String(v),label:'Air kerma strength (U)'},series:[{fn:S,color:'var(--c1)'}],
  marks:[{x:59.4,y:0.3,label:'T½',color:'var(--c2)',dx:8,dy:-8}],fixed:[30,50,200],dyn:t=>({marks:[{x:t,y:S(t),color:'var(--find)',r:6,label:''}],out:'t = <span class="v">'+Math.round(t)+' d</span>: S<sub>K</sub> = <span class="f">'+S(t).toFixed(2)+' U</span>'})});};

AV['tg43-factors']=root=>{const L=0.3, gr=avGL(1,0,L)/avGL(1,90,L), v=[0.965,0.965*gr,0.965*gr*0.370]; return avBars(root,{rowH:44,label:'The dose rate per unit air kerma strength at 1 cm: at the reference point, then on the seed axis with the geometry and anisotropy factors',cap:'For a Model 6711 seed with S_K = 1 U, the reference point gives S_K Λ = 0.965 cGy/h. On the seed axis at 1 cm the geometry ratio raises it by 3%, and the anisotropy function F = 0.370 cuts it to 0.368 cGy/h.',
  m:{l:150,r:60},x:{min:0,max:1.2,ticks:[0,0.3,0.6,0.9,1.2],fmt:v=>String(v),label:'Dose rate (cGy/h per U)'},rows:[{t:'S_K Λ: reference',v:v[0],col:'var(--c1)',val:v[0].toFixed(3)},{t:'× G/G₀ = '+gr.toFixed(3),v:v[1],col:'var(--c1)',val:v[1].toFixed(3)},{t:'× F = 0.370: axis',v:v[2],col:'var(--c2)',val:v[2].toFixed(3)}]});};

AV['geometry-function']=root=>{const A=(r,L)=>1/(1-L*L/(4*r*r)), T=(r,L)=>r*2*Math.atan(L/(2*r))/L; return avChart(root,{h:262,label:'The line-source geometry function divided by the point-source value 1/r², on the axis and across the centre of the seed, for a seed length set by the slider',cap:'G_L divided by 1/r². Close to the seed it is above 1 on the long axis and below 1 across the centre. Beyond about five source lengths both are within 1% of the point-source value.',
  x:{min:0.5,max:5,ticks:[0.5,1,2,3,4,5],fmt:v=>String(v),label:'Distance r (cm)'},y:{min:0.7,max:1.4,ticks:[0.7,0.85,1,1.15,1.3],fmt:v=>String(v),label:'G_L r²'},labels:[{x:3.6,y:1.07,t:'long axis',color:'var(--c2)',b:1},{x:3.6,y:0.93,t:'transverse',color:'var(--c1)',b:1}],
  slider:{min:0.1,max:1,value:0.3,label:'Seed active length L (cm)'},dyn:L=>({series:[{fn:r=>A(r,L),color:'var(--c2)'},{fn:r=>T(r,L),color:'var(--c1)'}],vlines:[{x:Math.min(5,5*L),label:'5L',dy:150,dx:4}],out:'L = <span class="v">'+(L*10).toFixed(1)+' mm</span>: at 1 cm the long axis is <span class="f">'+((A(1,L)-1)*100).toFixed(1)+'%</span> above 1/r², and the transverse axis '+((1-T(1,L))*100).toFixed(1)+'% below'})});};

AV['radial-dose']=root=>avBars(root,{rowH:40,label:'The radial dose function at 2 cm for three seed models and a typical Ir-192 source',cap:'g(1 cm) = 1 by definition. At 2 cm, g is 0.86 and 0.81 for the two I-125 seeds and 0.56 for Pd-103, and close to 1 for Ir-192. Lower photon energy means a steeper fall.',
  m:{l:124,r:62},x:{min:0,max:1.2,ticks:[0,0.3,0.6,0.9,1.2],fmt:v=>String(v),label:'Radial dose function g(2 cm)'},rows:[{t:'Ir-192 (HDR)',v:1.0,col:'var(--c2)',val:'about 1'},{t:'I-125, 6702',v:0.861,col:'var(--c1)',val:'0.861'},{t:'I-125, 6711',v:0.814,col:'var(--c1)',val:'0.814'},{t:'Pd-103, 200',v:0.555,col:'var(--c1)',val:'0.555'}]});

AV['dose-at-2cm']=root=>{const f=(L,g)=>100*avGL(2,90,L)/avGL(1,90,L)*g; const v=[25,f(0.3,0.814),f(0.423,0.555)]; return avBars(root,{rowH:42,label:'Dose rate at 2 cm on the transverse axis as a percentage of the rate at 1 cm, for inverse square alone and two seeds',cap:'Inverse square alone would leave 25% at 2 cm. The radial dose function lowers it for the two seeds, more for the lower-energy Pd-103 (Model 200) than for I-125 (Model 6711).',
  m:{l:128,r:60},x:{min:0,max:30,ticks:[0,10,20,30],fmt:v=>v+'%',label:'Dose rate at 2 cm (% of the rate at 1 cm)'},rows:[{t:'Inverse square',v:v[0],col:'var(--mu)',val:v[0].toFixed(0)+'%'},{t:'I-125, 6711',v:v[1],col:'var(--c1)',val:v[1].toFixed(1)+'%'},{t:'Pd-103, 200',v:v[2],col:'var(--c2)',val:v[2].toFixed(1)+'%'}]});};

AV['cumulative-dose']=root=>{const D=(t,T)=>100*(1-Math.pow(0.5,t/T)); return avChart(root,{h:262,label:'Cumulative dose from a permanent implant as a percentage of the total, for a half-life set by the slider',cap:'The dose rate falls as the sources decay, so half of the total dose is delivered in one half-life and 90% in 3.32 half-lives. The total is 1.44 T½ times the initial dose rate.',
  x:{min:0,max:300,ticks:[0,50,100,150,200,250,300],label:'Time after implant (days)'},y:{min:0,max:100,ticks:[0,25,50,75,90,100],fmt:avPct2,label:'Dose delivered (% of total)'},
  slider:{min:10,max:80,value:59.4,label:'Half-life T½ (d)'},dyn:T=>({series:[{fn:t=>D(t,T),color:'var(--c1)'}],marks:[{x:T,y:50,color:'var(--c2)',label:'50%',dx:8,dy:14},{x:Math.min(300,T*3.3219),y:90,color:'var(--c2)',label:'90%',dx:-8,dy:16,anchor:'end'}],
    out:'T<sub>½</sub> = <span class="v">'+fmt3(T)+' d</span>: half of the dose by <span class="f">'+Math.round(T)+' d</span>, 90% by <span class="f">'+Math.round(T*3.3219)+' d</span>'})});};


// ---------------------------------------------------------------- 3.1 to 3.4: PDD, TMR, scatter, and monitor-unit diagrams
const bmI=(x,xs,ys)=>{if(x<=xs[0]) return ys[0]; for(let i=1;i<xs.length;i++) if(x<=xs[i]) return ys[i-1]+(ys[i]-ys[i-1])*(x-xs[i-1])/(xs[i]-xs[i-1]); return ys[ys.length-1];};
const bmX=k=>DATA.bm[k].map(p=>p[0]), bmY=k=>DATA.bm[k].map(p=>p[1]);
const bmSc=s=>bmI(s,bmX('SC'),bmY('SC')), bmSp=s=>bmI(s,bmX('SP'),bmY('SP')), bmSpLn=s=>bmI(Math.log(s),bmX('SP').map(Math.log),bmY('SP'));
const bmTMR=(d,s)=>{const x=Math.max(0,d-DATA.bm.DMAX); return Math.exp(-DATA.bm.MUINF*x+DATA.bm.DELTA*(1+DATA.bm.BETA*Math.log(s/10))*(1-Math.exp(-x/DATA.bm.LAM)));};
const bmPDD=(d,s,f)=>{f=f||100; const ad=s*(f+d)/f, am=s*(f+DATA.bm.DMAX)/f; return 100*bmTMR(d,ad)*Math.pow((f+DATA.bm.DMAX)/(f+d),2)*bmSpLn(ad)/bmSpLn(am);};
const bmEN={E:[4,6,10,15,18],dmax:[1.0,1.5,2.5,3.0,3.5],s:[0.35,0.30,0.25,0.22,0.20],p10:[62.5,67,73,77,79.5]};
function bmBuild(E){const dmax=bmI(E,bmEN.E,bmEN.dmax), s=bmI(E,bmEN.E,bmEN.s), p10=bmI(E,bmEN.E,bmEN.p10), mu=Math.log(100/p10)/(10-dmax); let lo=0.3,hi=30;
  for(let i=0;i<50;i++){const k=(lo+hi)/2, dst=Math.log((1-s)*(k+mu)/mu)/k; if(dst>dmax) lo=k; else hi=k;} const k=(lo+hi)/2, N=1-(1-s)*Math.exp(-k*dmax);
  return {dmax,s,k,mu,f:d=>100*Math.exp(-mu*(d-dmax))*(1-(1-s)*Math.exp(-k*d))/N};}
// a short helper for rows of horizontal bars that change with a control: returns update(values, labels)
function avBarRows(s,o){const rows=o.rows.map((r,i)=>{const y=o.y0+i*o.rh; stext(s,o.x0-8,y+o.rh*0.62,r,{'text-anchor':'end','font-size':14}); return {bar:sv('rect',{x:o.x0,y:y+4,height:o.rh-10,rx:2},s),val:stext(s,o.x0,y+o.rh*0.62,'',{'font-weight':700,'font-size':14.5})};});
  sv('line',{x1:o.x0,y1:o.y0,x2:o.x0,y2:o.y0+o.rows.length*o.rh,stroke:'var(--fg)','stroke-width':1.5},s);
  return (vals,txt,cols)=>vals.forEach((v,i)=>{const w=Math.max(1,o.w*v/o.max); rows[i].bar.setAttribute('width',w); rows[i].bar.setAttribute('fill',(cols&&cols[i])||'var(--c1)'); rows[i].val.setAttribute('x',o.x0+w+8); rows[i].val.textContent=txt[i];});}

AV['pdd-buildup']=root=>avChart(root,{h:256,label:'Percent depth dose near the surface for photon beams from 4 to 18 MV, with d max and the surface dose',cap:'Typical values for a 10 × 10 cm field; they vary with the machine and the field size. A higher energy moves d_max deeper and lowers the dose in the first centimetre. The dose at the skin itself changes little with energy and depends more on field size and on devices in the beam.',
  x:{min:0,max:12,ticks:[0,2,4,6,8,10,12],label:'Depth (cm)'},y:{min:0,max:100,ticks:[0,20,40,60,80,100],fmt:avPct2,label:'Percent depth dose'},
  slider:{min:4,max:18,value:6,label:'Beam energy (MV)'},
  dyn:E=>{const B=bmBuild(E); return {series:[{fn:B.f,color:'var(--c1)'}],vlines:[{x:B.dmax,label:'d_max',dy:150,dx:5}],marks:[{x:B.dmax,y:100,color:'var(--c2)',label:'',r:5.5}],out:'<span class="v">'+fmt3(E)+' MV</span>: d<sub>max</sub> about <span class="f">'+B.dmax.toFixed(1)+' cm</span>, and the dose at 0.5 cm is '+Math.round(B.f(0.5))+'% of the maximum'};}});

AV['pdd-factors']=root=>{const SZ=[[5,'var(--c1)','5 × 5'],[10,'var(--fg)','10 × 10'],[20,'var(--c3)','20 × 20']]; return avChart(root,{h:262,label:'Percent depth dose for three field sizes at an SSD set by the slider, for a 6 MV beam',cap:'PDD falls with depth and rises with field size (more scatter) and with SSD (a weaker inverse-square fall-off). Illustrative 6 MV data.',
  x:{min:1.5,max:20,ticks:[2,5,10,15,20],fmt:v=>String(v),label:'Depth (cm)'},y:{min:30,max:100,ticks:[40,60,80,100],fmt:avPct2,label:'Percent depth dose'},
  slider:{min:80,max:140,value:100,label:'SSD (cm)'},
  dyn:f=>({series:SZ.map(([s,c])=>({fn:d=>bmPDD(d,s,f),color:c})),labels:[{x:2.4,y:48,t:'20 × 20 cm',color:'var(--c3)',b:1},{x:2.4,y:41,t:'10 × 10 cm',color:'var(--fg)',b:1},{x:2.4,y:34,t:'5 × 5 cm',color:'var(--c1)',b:1}],
    out:'SSD = <span class="v">'+Math.round(f)+' cm</span>: PDD at 10 cm is '+SZ.map(([s])=>'<span class="f">'+bmPDD(10,s,f).toFixed(1)+'%</span>').join(', ')+' for 5 × 5, 10 × 10, and 20 × 20 cm'})});};

AV['mayneord']=root=>{const F=(f2,d)=>{const m=DATA.bm.DMAX; return Math.pow(((f2+m)/(f2+d))/((100+m)/(100+d)),2);}; const P1=()=>bmPDD(10,10,100);
  return avChart(root,{h:262,label:'PDD at 10 cm depth against SSD, estimated from SSD 100 cm with the Mayneord F factor and from the full model',cap:'The Mayneord F factor is the ratio of the inverse-square factors at the new and the old SSD. It ignores the change in scatter, so it differs slightly from the full model.',
  x:{min:80,max:140,ticks:[80,90,100,110,120,130,140],label:'SSD (cm)'},y:{min:58,max:78,ticks:[60,65,70,75],fmt:avPct2,label:'PDD at 10 cm, 10 × 10 cm field'},
  series:[{fn:f=>bmPDD(10,10,f),color:'var(--fg)',dash:'6 4'}],labels:[{x:104,y:61,t:'full model (dashed)',color:'var(--fg)'},{x:104,y:59.2,t:'Mayneord from SSD 100',color:'var(--c2)',b:1}],
  slider:{min:80,max:140,value:120,label:'New SSD (cm)'},
  dyn:f=>({series:[{fn:g=>P1()*F(g,10),color:'var(--c2)'}],marks:[{x:f,y:P1()*F(f,10),color:'var(--c2)',label:''}],out:'SSD = <span class="v">'+Math.round(f)+' cm</span>: F = <span class="f">'+F(f,10).toFixed(3)+'</span>, so PDD = '+(P1()*F(f,10)).toFixed(1)+'% by Mayneord, '+bmPDD(10,10,f).toFixed(1)+'% from the full model'})});};

AV['field-divergence']=root=>{
  const W=420,H=214,{s,c}=avShell(root,W,H,'A diverging beam in which the field at depth is larger than at the surface, in proportion to the distance from the source','The field is defined at the surface. At depth d the distance from the source is f + d, so the field side grows as A (f + d) / f. The lines mark depths of 10 cm and 20 cm. Not to scale: the beam width is exaggerated.');
  const X0=210, SY=20, HW=0.5;
  sv('polygon',{points:`${X0},${SY} ${X0-HW*125},${SY+125} ${X0+HW*125},${SY+125}`,fill:'var(--c3)','fill-opacity':.2,stroke:'var(--c3)','stroke-width':1.6},s); sv('rect',{x:120,y:SY+100,width:180,height:70,fill:'var(--gr)','fill-opacity':.55,stroke:'var(--fg)','stroke-width':1.6},s);
  sv('circle',{cx:X0,cy:SY,r:5,fill:'var(--fg)'},s); stext(s,X0+10,SY+4,'source',{'font-size':14}); stext(s,306,SY+104,'surface',{'font-size':13.5,fill:'var(--mu)'}); stext(s,306,SY+119,'SSD 100 cm',{'font-size':13.5,fill:'var(--mu)'}); stext(s,X0,SY+100-8,'10 cm at the surface',{'text-anchor':'middle','font-size':13.5,fill:'var(--c3)','font-weight':600});
  [[10,'var(--find)'],[20,'var(--c2)']].forEach(([d,col])=>{const r=100+d, hw=HW*r, y=SY+r; sv('line',{x1:X0-hw,x2:X0+hw,y1:y,y2:y,stroke:col,'stroke-width':2.4},s); stext(s,X0+hw+8,y+5,(10*r/100).toFixed(1)+' cm',{'font-size':13.5,'font-weight':700,fill:col});});
  c.innerHTML='<output class="avo" aria-live="polite"></output>'; c.querySelector('output').innerHTML='<span class="v">d = 10 cm</span>: the field is <span class="f">11.0 × 11.0 cm</span>. <span class="v">d = 20 cm</span>: <span class="f">12.0 × 12.0 cm</span>. Both from 10.0 × 10.0 cm at the surface';
  return {enter(){},leave(){},finish(){}};};

AV['isocentric-ssd']=root=>avTimeline(root,{h:262,label:'The gantry turning around a patient cross-section: the isocenter stays fixed while the SSD changes with the beam angle',cap:'In an isocentric treatment the source stays 100 cm from the isocenter, so the SSD changes with every beam angle. PDD depends on the SSD, so the TMR is used instead. One pixel is one centimetre.',dur:9000,build:s=>{
  const cx=210, cy=130, R=100, a=19, b=12;
  sv('circle',{cx,cy,r:R,fill:'none',stroke:'var(--line)','stroke-dasharray':'3 5'},s); sv('ellipse',{cx,cy,rx:a,ry:b,fill:'var(--gr)',stroke:'var(--fg)','stroke-width':1.8},s); sv('circle',{cx,cy,r:3.4,fill:'var(--c2)'},s); stext(s,cx+8,cy+4,'isocenter',{'font-size':12.5,fill:'var(--c2)'});
  const beam=sv('line',{stroke:'var(--c3)','stroke-width':2.2},s), src=sv('circle',{r:7,fill:'var(--fg)'},s), skin=sv('circle',{r:4.5,fill:'var(--c2)'},s), t=stext(s,cx,250,'',{'text-anchor':'middle','font-weight':700,'font-size':15});
  return u=>{const th=u*360, rd=th*Math.PI/180, sx=cx+R*Math.sin(rd), sy=cy-R*Math.cos(rd), r=1/Math.sqrt(Math.sin(rd)**2/(a*a)+Math.cos(rd)**2/(b*b)), kx=cx+r*Math.sin(rd), ky=cy-r*Math.cos(rd);
    src.setAttribute('cx',sx); src.setAttribute('cy',sy); beam.setAttribute('x1',sx); beam.setAttribute('y1',sy); beam.setAttribute('x2',cx); beam.setAttribute('y2',cy); skin.setAttribute('cx',kx); skin.setAttribute('cy',ky);
    t.textContent='gantry '+String(Math.round(th)).padStart(3,' ')+'°: SSD = '+(R-r).toFixed(0)+' cm';};}});

AV['tmr-setup']=root=>{
  const W=420,H=270,{s,c}=avShell(root,W,H,'A point fixed 100 cm from the source with the water surface at two heights above it, so the depth changes and the source-to-point distance does not','TMR compares the dose at depth d with the dose at d_max at the same point, so the source-to-point distance never changes. Only the water above the point changes. The solid line is a depth of 10 cm and the dashed line a depth of 5 cm. Illustrative 6 MV data.');
  const X0=210, SY=18, PY=118;
  sv('polygon',{points:`${X0},${SY} ${X0-26},${PY+100} ${X0+26},${PY+100}`,fill:'var(--c3)','fill-opacity':.18,stroke:'var(--c3)','stroke-width':1.5},s); sv('rect',{x:120,y:PY-10,width:180,height:110,fill:'var(--gr)','fill-opacity':.6,stroke:'var(--fg)','stroke-width':1.6},s);
  sv('circle',{cx:X0,cy:SY,r:5,fill:'var(--fg)'},s); stext(s,X0+10,SY+4,'source',{'font-size':14}); sv('circle',{cx:X0,cy:PY,r:5.5,fill:'var(--c2)'},s); stext(s,X0+12,PY+22,'point, 100 cm from the source',{'font-size':13.5,fill:'var(--c2)','font-weight':600});
  [[10,'var(--find)',false],[5,'var(--c2)',true]].forEach(([d,col,dash])=>{const y=PY-d; sv('line',{x1:128,x2:292,y1:y,y2:y,stroke:col,'stroke-width':2.4,'stroke-dasharray':dash?'5 4':'none'},s); stext(s,134,y-5,'depth '+d+' cm',{'font-size':13.5,fill:col,'font-weight':700});});
  c.innerHTML='<output class="avo" aria-live="polite"></output>'; c.querySelector('output').innerHTML='<span class="v">Depth 10 cm</span>: SSD = 90 cm, source-to-point distance 100 cm, TMR = <span class="f">'+bmTMR(10,10).toFixed(3)+'</span>. <span class="v">Depth 5 cm</span>: SSD = 95 cm, source-to-point distance 100 cm, TMR = <span class="f">'+bmTMR(5,10).toFixed(3)+'</span>';
  return {enter(){},leave(){},finish(){}};};

AV['pdd-vs-tmr']=root=>avChart(root,{h:262,label:'PDD at SSD 100 cm and TMR against depth for a 6 MV 10 × 10 cm field',cap:'The PDD includes the inverse-square fall-off as the point moves away from the source. The TMR does not, so it is larger at every depth beyond d_max. Illustrative 6 MV data.',
  x:{min:1.5,max:20,ticks:[2,5,10,15,20],fmt:v=>String(v),label:'Depth (cm)'},y:{min:0.3,max:1.05,ticks:[0.4,0.6,0.8,1],fmt:v=>String(v),label:'Relative dose'},
  series:[{fn:d=>bmTMR(d,10),color:'var(--c2)'},{fn:d=>bmPDD(d,10,100)/100,color:'var(--c1)'}],labels:[{x:14,y:bmTMR(14,10)+0.07,t:'TMR',color:'var(--c2)',b:1},{x:14,y:bmPDD(14,10,100)/100-0.12,t:'PDD / 100',color:'var(--c1)',b:1}],
  fixed:[5,10,20],dyn:d=>({marks:[{x:d,y:bmTMR(d,10),color:'var(--c2)',label:''},{x:d,y:bmPDD(d,10,100)/100,color:'var(--c1)',label:''}],out:'d = <span class="v">'+d.toFixed(1)+' cm</span>: PDD = '+bmPDD(d,10,100).toFixed(1)+'%, TMR = <span class="f">'+bmTMR(d,10).toFixed(3)+'</span>, ratio '+(bmTMR(d,10)/(bmPDD(d,10,100)/100)).toFixed(2)})});

AV['pdd-to-tmr']=root=>{
  const W=420,H=262,{s,c}=avShell(root,W,H,'The factors that convert a percent depth dose to a TMR at a depth of 10 cm, shown as bars','TMR = PDD/100 × [(f + d)/(f + d_max)]² × S_p(A_dmax)/S_p(A_d). The bars are for a depth of 10 cm. The inverse-square factor does most of the work. 6 MV, 10 × 10 cm at the surface, SSD 100 cm; illustrative data.');
  const upd=avBarRows(s,{rows:['PDD / 100','× inverse square','× S_p ratio','= TMR'],x0:150,y0:20,rh:48,w:210,max:1.4}); c.innerHTML='<output class="avo" aria-live="polite"></output>'; const out=c.querySelector('output');
  const d=10, f=100, m=DATA.bm.DMAX, p=bmPDD(d,10,f)/100, is=Math.pow((f+d)/(f+m),2), sr=bmSpLn(10*(f+m)/f)/bmSpLn(10*(f+d)/f), t=p*is*sr; upd([p,is,sr,t],[p.toFixed(3),is.toFixed(3),sr.toFixed(4),t.toFixed(3)],['var(--c1)','var(--c1)','var(--c1)','var(--c2)']);
  out.innerHTML='d = <span class="v">'+d.toFixed(1)+' cm</span>: '+p.toFixed(3)+' × '+is.toFixed(3)+' × '+sr.toFixed(4)+' = <span class="f">'+t.toFixed(3)+'</span>';
  return {enter(){},leave(){},finish(){}};};

AV['scatter-factors']=root=>avChart(root,{h:262,label:'Collimator, phantom, and total scatter factors against field size',cap:'S_c follows the jaw opening (head scatter) and S_p follows the field irradiating the phantom. S_cp = S_c × S_p, and all three equal 1 for the 10 × 10 cm reference field. Illustrative 6 MV data.',
  x:{min:4,max:40,log:true,ticks:[4,6,10,20,40],fmt:v=>String(v),label:'Field side (cm), log scale'},y:{min:0.92,max:1.12,ticks:[0.95,1,1.05,1.1],fmt:v=>String(v),label:'Scatter factor'},
  series:[{fn:bmSc,color:'var(--c1)'},{fn:bmSp,color:'var(--c2)'},{fn:s=>bmSc(s)*bmSp(s),color:'var(--fg)',dash:'6 4'}],labels:[{x:4.6,y:1.095,t:'S_cp = S_c × S_p (dashed)',color:'var(--fg)'},{x:27,y:1.072,t:'S_c',color:'var(--c1)',b:1},{x:27,y:1.012,t:'S_p',color:'var(--c2)',b:1}],
  fixed:[5,20],dyn:s=>({marks:[{x:s,y:bmSc(s),color:'var(--c1)',label:''},{x:s,y:bmSp(s),color:'var(--c2)',label:''}],out:s.toFixed(1)+' × '+s.toFixed(1)+' cm: S<sub>c</sub> = <span class="v">'+bmSc(s).toFixed(3)+'</span>, S<sub>p</sub> = <span class="f">'+bmSp(s).toFixed(3)+'</span>, S<sub>cp</sub> = '+(bmSc(s)*bmSp(s)).toFixed(3)})});

AV['block-effect']=root=>{
  const W=420,H=262,{s,c}=avShell(root,W,H,'Scatter factors with and without a block under the jaws, which stay at 20 × 20 cm','A block under the collimators narrows the field in the phantom but leaves the jaw opening alone, so S_p changes and S_c does not. Illustrative 6 MV data.');
  sv('rect',{x:20,y:24,width:92,height:92,fill:'none',stroke:'var(--fg)','stroke-width':2.2},s); const inner=sv('rect',{fill:'var(--c3)','fill-opacity':.3,stroke:'var(--c3)','stroke-width':1.8},s); stext(s,66,134,'jaws 20 × 20',{'text-anchor':'middle','font-size':13.5,fill:'var(--mu)'}); const cap=stext(s,66,152,'',{'text-anchor':'middle','font-size':13.5,fill:'var(--c3)','font-weight':600});
  const X0=270, SX=(v)=>X0+(v-0.99)/(1.07-0.99)*130; ['S_c','S_p','S_cp'].forEach((n,i)=>{stext(s,248,52+i*50,n,{'text-anchor':'end','font-size':15}); sv('line',{x1:X0,x2:X0+130,y1:48+i*50,y2:48+i*50,stroke:'var(--gr)','stroke-width':3},s);});
  [1,1.02,1.04,1.06].forEach(v=>{stext(s,SX(v),178,String(v),{'text-anchor':'middle','font-size':12.5,fill:'var(--mu)'}); sv('line',{x1:SX(v),x2:SX(v),y1:40,y2:152,stroke:'var(--gr)'},s);});
  const dots=[0,1,2].map(i=>sv('circle',{cy:48+i*50,r:7,fill:['var(--c1)','var(--c2)','var(--fg)'][i]},s)), vals=[0,1,2].map(i=>stext(s,0,36+i*50,'',{'text-anchor':'middle','font-weight':700,'font-size':14}));
  const {b:B,o:out}=avBtns(c,'Field in the phantom',['Open 20 × 20 cm','Blocked to 10 × 10 cm']);
  const set=k=>{B.forEach((e,i)=>e.setAttribute('aria-pressed',i===k?'true':'false')); const sc=bmSc(20), sp=k?bmSp(10):bmSp(20), cp=sc*sp; [sc,sp,cp].forEach((v,i)=>{dots[i].setAttribute('cx',SX(v)); vals[i].setAttribute('x',SX(v)); vals[i].textContent=v.toFixed(3);});
    inner.setAttribute('x',k?43:20); inner.setAttribute('y',k?47:24); inner.setAttribute('width',k?46:92); inner.setAttribute('height',k?46:92); cap.textContent=k?'block leaves 10 × 10 cm':'open';
    out.innerHTML=(k?'Blocked':'Open')+': S<sub>c</sub> = <span class="v">'+sc.toFixed(3)+'</span>, S<sub>p</sub> = <span class="f">'+sp.toFixed(3)+'</span>, S<sub>cp</sub> = '+cp.toFixed(3);};
  B.forEach((e,i)=>e.addEventListener('click',()=>set(i))); set(0); return avPlay(c,1,()=>{});
};

AV['equivalent-square']=root=>{
  const W=420,H=292,{s,c}=avShell(root,W,H,'A rectangle and its equivalent square, which has the same area-to-perimeter ratio','The equivalent square of an a × b rectangle has side s = 2ab/(a + b). It sits below the square root of the area for elongated fields. Clarkson integration handles irregular fields.');
  const K=7, CX=210, CY=146; const rect=sv('rect',{fill:'var(--c1)','fill-opacity':.22,stroke:'var(--c1)','stroke-width':2},s), sq=sv('rect',{fill:'none',stroke:'var(--find)','stroke-width':2.4,'stroke-dasharray':'6 4'},s);
  stext(s,14,22,'rectangle',{'font-size':14,fill:'var(--c1)','font-weight':600}); stext(s,100,22,'equivalent square (dashed)',{'font-size':14,fill:'var(--find)','font-weight':600});
  c.innerHTML='<label>Side a (cm)<input class="ia" type="range" min="4" max="30" step="0.5" value="8"></label><label>Side b (cm)<input class="ib" type="range" min="4" max="30" step="0.5" value="20"></label><output class="avo" aria-live="polite"></output>'; const ra=c.querySelector('.ia'), rb=c.querySelector('.ib'), out=c.querySelector('output');
  const set=()=>{const a=+ra.value, b=+rb.value, e=2*a*b/(a+b); rect.setAttribute('x',CX-a*K/2); rect.setAttribute('y',CY-b*K/2); rect.setAttribute('width',a*K); rect.setAttribute('height',b*K); sq.setAttribute('x',CX-e*K/2); sq.setAttribute('y',CY-e*K/2); sq.setAttribute('width',e*K); sq.setAttribute('height',e*K);
    out.innerHTML=a.toFixed(1)+' × '+b.toFixed(1)+' cm: s = 2ab/(a + b) = <span class="f">'+e.toFixed(1)+' cm</span>; the square root of the area is '+Math.sqrt(a*b).toFixed(1)+' cm';};
  ra.addEventListener('input',set); rb.addEventListener('input',set); return avPlay(c,1800,u=>{ra.value=4+4*ease(u); rb.value=4+16*ease(u); set();});
};

AV['mu-chain']=root=>avTimeline(root,{h:300,label:'A monitor unit calculation: the factors multiply to the dose per monitor unit, and the prescribed dose divides by it',cap:'SSD technique with an SSD calibration, illustrative factors: dose per MU = 1.000 × S_c × S_p × PDD/100 × 1.000 = 0.7012 cGy/MU, so 300 cGy needs 300 / 0.7012 = 428 MU.',dur:6400,build:s=>{
  const F=[['calibration, cGy/MU',1.0,'1.000'],['S_c',1.017,'× 1.017'],['S_p',1.014,'× 1.014'],['PDD / 100',0.68,'× 0.680'],['inverse-square term',1.0,'× 1.000']]; let run=1;
  const R=F.map((f,i)=>{run*=f[1]; const y=26+i*38, g=sv('g',{},s); stext(g,14,y+4,f[0],{'font-size':14.5}); stext(g,236,y+4,f[2],{'text-anchor':'end','font-weight':700,'font-size':15}); stext(g,258,y+4,'= '+run.toFixed(4).replace(/0+$/,'0'),{'font-size':14.5,fill:'var(--mu)'}); return g;});
  const dpm=run, g2=sv('g',{},s); sv('line',{x1:14,x2:400,y1:26+5*38-14,y2:26+5*38-14,stroke:'var(--fg)','stroke-width':1.5},g2); stext(g2,14,26+5*38+8,'dose per MU',{'font-weight':700,'font-size':15}); stext(g2,236,26+5*38+8,dpm.toFixed(4),{'text-anchor':'end','font-weight':700,'font-size':15}); stext(g2,258,26+5*38+8,'cGy/MU',{'font-size':14.5});
  const g3=sv('g',{},s); stext(g3,14,26+6*38+14,'MU = 300 cGy ÷ '+dpm.toFixed(4)+' =',{'font-weight':700,'font-size':16,fill:'var(--find)'}); stext(g3,400,26+6*38+14,Math.round(300/dpm)+' MU',{'text-anchor':'end','font-weight':700,'font-size':18,fill:'var(--find)'});
  return u=>{R.forEach((g,i)=>g.style.display=u>=i*.12?'':'none'); g2.style.display=u>=.66?'':'none'; g3.style.display=u>=.82?'':'none';};}});

AV['ssd-formula']=root=>avTimeline(root,{h:262,label:'The factors in the SSD technique and what each one corrects for',cap:'SSD technique: dose per MU = calibration × S_c × S_p × PDD/100 × (d_cal / (f + d_max))². Each factor converts the reference conditions to one feature of the treatment.',dur:5600,build:s=>{
  const R=[['cal','1 cGy/MU at the reference conditions'],['S_c','jaw opening (head scatter)'],['S_p','field irradiating the phantom'],['PDD / 100','depth, energy, surface field size'],['(d_cal/(f + d_max))²','SSD against calibration distance']];
  const rows=R.map((r,i)=>{const y=14+i*48, g=sv('g',{},s); sv('rect',{x:14,y:y,width:150,height:36,rx:6,fill:'none',stroke:i===0?'var(--mu)':'var(--fg)','stroke-width':1.6},g); stext(g,89,y+24,r[0],{'text-anchor':'middle','font-weight':700,'font-size':i===4?13.5:15.5}); stext(g,172,y+23,(i?'× ':'')+r[1],{'font-size':14,fill:'var(--text)'}); return g;});
  stext(s,14,258,'With an SSD calibration the last term is 1 at SSD 100 cm.',{'font-size':13.5,fill:'var(--mu)'});
  return u=>rows.forEach((g,i)=>g.style.display=u>=i*.17?'':'none');}});

AV['ssd-term']=root=>avChart(root,{h:262,label:'The inverse-square term of the SSD technique against SSD, for an SSD calibration at 101.5 cm',cap:'The term is (101.5 / (f + 1.5))² for an SSD calibration with d_max = 1.5 cm. It is 1 at SSD 100 cm and falls below 1 at an extended SSD, so the monitor units rise.',
  x:{min:80,max:140,ticks:[80,90,100,110,120,130,140],label:'SSD (cm)'},y:{min:0.5,max:1.5,ticks:[0.5,0.75,1,1.25,1.5],fmt:v=>String(v),label:'Inverse-square term'},series:[{fn:f=>Math.pow(101.5/(f+1.5),2),color:'var(--c1)'}],hlines:[{y:1,label:'1'}],
  fixed:[100,120],dyn:f=>{const t=Math.pow(101.5/(f+1.5),2); return {marks:[{x:f,y:t,color:'var(--find)',r:6,label:''}],out:'SSD = <span class="v">'+Math.round(f)+' cm</span>: term = <span class="f">'+t.toFixed(3)+'</span>, so the MU change by × '+(1/t).toFixed(2)+' compared with SSD 100 cm, other factors equal'};}});

AV['sad-formula']=root=>{
  const W=420,H=262,{s,c}=avShell(root,W,H,'The factors of the SAD technique for an SSD calibration and for a SAD calibration, with the dose per monitor unit','SAD technique: dose per MU = calibration × S_c × S_p × TMR × (d_cal/100)². The last term is 1.030 for an SSD calibration (calibrated at 101.5 cm) and 1.000 for a SAD calibration. Illustrative factors.');
  const upd=avBarRows(s,{rows:['S_c','S_p','TMR','inverse-square term','= dose per MU'],x0:150,y0:12,rh:40,w:210,max:1.4});
  const {b:B,o:out}=avBtns(c,'Calibration',['SSD calibration','SAD calibration']);
  const set=k=>{B.forEach((e,i)=>e.setAttribute('aria-pressed',i===k?'true':'false')); const t=k?1:Math.pow(1.015,2), dp=1.021*1.013*0.738*t, mu=120/dp; upd([1.021,1.013,0.738,t,dp],['1.021','1.013','0.738',t.toFixed(3),dp.toFixed(3)+' cGy/MU'],['var(--c1)','var(--c1)','var(--c1)','var(--c2)','var(--find)']);
    out.innerHTML=(k?'SAD':'SSD')+' calibration: term <span class="v">'+t.toFixed(3)+'</span>, dose per MU <span class="f">'+dp.toFixed(3)+'</span>, so 120 cGy needs '+mu.toFixed(1)+' MU';};
  B.forEach((e,i)=>e.addEventListener('click',()=>set(i))); set(0); return avPlay(c,1,()=>{});
};

AV['accessory-factors']=root=>avChart(root,{h:256,label:'Monitor units against wedge factor for a field needing 180 MU without accessories, with and without a tray factor of 0.97',cap:'MU = MU₀ / (WF × TF). Each factor below 1 lowers the dose per MU, so the monitor units rise as 1/WF and 1/TF.',
  x:{min:0.4,max:1,ticks:[0.4,0.5,0.6,0.7,0.8,0.9,1],fmt:v=>String(v),label:'Wedge factor WF'},y:{min:150,max:480,ticks:[150,250,350,450],fmt:v=>String(v),label:'Monitor units'},
  series:[{fn:w=>180/w,color:'var(--c1)'},{fn:w=>180/(w*0.97),color:'var(--c2)'}],labels:[{x:0.72,y:430,t:'wedge and tray',color:'var(--c2)',b:1},{x:0.72,y:395,t:'wedge only',color:'var(--c1)',b:1}],
  fixed:[0.5,0.66,1],dyn:w=>({marks:[{x:w,y:180/w,color:'var(--c1)',label:''},{x:w,y:180/(w*0.97),color:'var(--c2)',label:''}],out:'WF = <span class="v">'+w.toFixed(2)+'</span>: <span class="f">'+(180/w).toFixed(1)+' MU</span> with the wedge, '+(180/(w*0.97)).toFixed(1)+' MU with the wedge and a tray (TF 0.97)'})});


// ---------------------------------------------------------------- 3.5 to 3.7: profiles, skin dose and bolus, dose calculation algorithms
const avErfc=z=>{const s=z<0?-1:1, x=Math.abs(z), t=1/(1+0.3275911*x), y=1-(((((1.061405429*t-1.453152027)*t)+1.421413741)*t-0.284496736)*t+0.254829592)*t*Math.exp(-x*x); return s>0?1-y:1+y;};
AV['penumbra-geometry']=root=>{const W_=(s,d,c)=>s*((100+d)/c-1), C=[[40,'var(--c2)'],[50,'var(--c1)'],[60,'var(--c3)']]; return avChart(root,{h:262,label:'Geometric penumbra against depth for three source-to-collimator distances and a source size set by the slider, at SSD 100 cm',cap:'w = s [ (f + d) / SCD − 1 ]. The geometric penumbra grows with source size and with depth, and it falls as the source-to-collimator distance (SCD) rises.',
  x:{min:0,max:20,ticks:[0,5,10,15,20],label:'Depth (cm), SSD 100 cm'},y:{min:0,max:14,ticks:[0,4,8,12],fmt:v=>String(v),label:'Geometric penumbra (mm)'},slider:{min:1,max:6,value:3,label:'Source size s (mm)'},
  dyn:s=>({series:C.map(([c,col])=>({fn:d=>W_(s,d,c),color:col})),labels:C.map(([c,col])=>({x:11.6,y:W_(s,11.6,c)+(c===60?-1.6:0.95),t:'SCD '+c+' cm',color:col,b:1})),out:'s = <span class="v">'+s.toFixed(1)+' mm</span>: at 10 cm depth the penumbra is '+C.map(([c])=>'<span class="f">'+W_(s,10,c).toFixed(1)+'</span>').join(', ')+' mm for SCD 40, 50, and 60 cm'})});};

AV['penumbra-energy']=root=>{const SG=[[0.30,'var(--c1)','6 MV'],[0.40,'var(--c2)','18 MV']], prof=(x,sg)=>100*0.5*avErfc(x/(Math.SQRT2*sg)); return avChart(root,{h:262,label:'Beam profile across a field edge for 6 MV and 18 MV, in tissue of a density set by the slider',cap:'Schematic. Electrons set in motion near the edge travel out of the field. Their range is longer at higher energy and in low-density tissue, so the 80%–20% penumbra is wider. Widths are illustrative.',
  x:{min:-2,max:2,ticks:[-2,-1,0,1,2],fmt:v=>String(v),label:'Position from the 50% point (cm)'},y:{min:0,max:100,ticks:[0,20,50,80,100],fmt:avPct2,label:'Dose (% of the central axis)'},
  slider:{min:0.25,max:1,value:1,label:'Tissue density (g/cm³): 0.25 is lung, 1.0 is muscle'},
  dyn:r=>{const f=Math.sqrt(1/r); return {series:SG.map(([sg,c])=>({fn:x=>prof(x,sg*f),color:c})),labels:[{x:0.55,y:30,t:'6 MV',color:'var(--c1)',b:1},{x:0.55,y:12,t:'18 MV',color:'var(--c2)',b:1}],out:'ρ = <span class="v">'+r.toFixed(2)+'</span>: 80%–20% penumbra '+SG.map(([sg,c,n])=>n+' <span class="f">'+(1.683*sg*f*10).toFixed(1)+' mm</span>').join(', ')+' (illustrative)'};}});};

AV['profile-depth']=root=>{const K=d=>d<=10?0.04*(10-d)/8.5:-0.05*(d-10)/10, P=(x,d)=>{const k=K(d), u=x/5, inside=(1+k*(Math.pow(u,4)-0.2))/(1-0.2*k); return 100*inside*0.5*avErfc((Math.abs(x)-5)/(Math.SQRT2*0.3));};
  return avChart(root,{h:262,label:'Profile of a 10 cm wide field at a depth set by the slider, for a beam flattened at 10 cm',cap:'Schematic. At depths shallower than the reference depth the edges are higher than the center (horns). At 10 cm the profile is flat, and deeper the center is higher. The horns are larger at higher energy.',
  x:{min:-7,max:7,ticks:[-6,-3,0,3,6],fmt:v=>String(v),label:'Position across the field (cm)'},y:{min:0,max:115,ticks:[0,50,100],fmt:v=>String(v),label:'Dose (% of the axis value)'},slider:{min:1.5,max:20,value:10,label:'Depth (cm)'},
  dyn:d=>({series:[{fn:x=>P(x,d),color:'var(--c1)'}],hlines:[{y:100,label:'axis'}],out:'d = <span class="v">'+d.toFixed(1)+' cm</span>: the dose near the edges is <span class="f">'+(100*(1+0.8*K(d))/(1-0.2*K(d))).toFixed(0)+'%</span> of the axis dose'+(Math.abs(K(d))<0.002?' (flat)':(K(d)>0?' (horns)':' (center higher)'))})});};

AV['out-of-field']=root=>{const S=x=>8*Math.exp(-x/3), L=0.15; return avChart(root,{h:262,label:'Dose outside the field edge on a logarithmic axis: scattered radiation falls quickly and head leakage stays nearly constant',cap:'Schematic, with illustrative values. Close to the edge the dose is mostly scatter out of the field. Farther away, leakage through the head and collimators dominates. Planning systems predict the far region poorly.',
  x:{min:0,max:30,ticks:[0,5,10,15,20,25,30],label:'Distance from the field edge (cm)'},y:{min:0.01,max:100,log:true,ticks:[0.01,0.1,1,10,100],fmt:v=>String(v),label:'Dose (% of the central axis), log scale'},
  series:[{fn:S,color:'var(--c1)'},{fn:x=>L,color:'var(--c2)',dash:'6 4'},{fn:x=>S(x)+L,color:'var(--fg)',w:2.8}],labels:[{x:6.5,y:2.8,t:'scatter',color:'var(--c1)',b:1},{x:21,y:0.2,t:'leakage',color:'var(--c2)',b:1}],
  fixed:[5,10,20],dyn:x=>({marks:[{x:x,y:S(x)+L,color:'var(--find)',r:6,label:''}],out:'x = <span class="v">'+x.toFixed(0)+' cm</span>: scatter '+fmt3(S(x))+'%, leakage '+fmt3(L)+'%, total <span class="f">'+fmt3(S(x)+L)+'%</span>'})});};

AV['skin-dose']=root=>{const f=s=>1+(s-10)/30; return avChart(root,{h:256,label:'Skin dose as a percentage of the d max dose against field size for a 6 MV beam, from 20% to 40% at 10 by 10 cm and about double at 40 by 40 cm',cap:'Skin dose is about 20%–40% of the d_max dose for a 10 × 10 cm field and about twice that for 40 × 40 cm, because more electrons from the head reach the skin. The dependence on energy at the skin is small.',
  x:{min:10,max:40,ticks:[10,20,30,40],label:'Field side (cm)'},y:{min:0,max:90,ticks:[0,20,40,60,80],fmt:avPct2,label:'Skin dose (% of d_max dose)'},
  series:[{fn:s=>20*f(s),color:'var(--c1)'},{fn:s=>40*f(s),color:'var(--c2)'}],labels:[{x:12,y:44,t:'upper estimate',color:'var(--c2)',b:1},{x:12,y:15,t:'lower estimate',color:'var(--c1)',b:1}],
  fixed:[10,20],dyn:s=>({marks:[{x:s,y:20*f(s),color:'var(--c1)',label:''},{x:s,y:40*f(s),color:'var(--c2)',label:''}],out:s.toFixed(0)+' × '+s.toFixed(0)+' cm: skin dose about <span class="f">'+(20*f(s)).toFixed(0)+'%</span> to <span class="f">'+(40*f(s)).toFixed(0)+'%</span> of the d<sub>max</sub> dose'})});};

AV['device-skin']=root=>{
  const W=420,H=262,{s,c}=avShell(root,W,H,'A beam entering a patient from below through nothing, the couch, or the couch and a vacuum bag, with secondary electrons added by each device','Each device in the beam adds secondary electrons that reach the skin, so the skin dose rises. The couch also attenuates the beam by about 2%. Illustrative, not to scale.');
  sv('rect',{x:110,y:30,width:200,height:90,rx:14,fill:'var(--gr)',stroke:'var(--fg)','stroke-width':2},s); stext(s,210,80,'patient',{'text-anchor':'middle','font-size':15,fill:'var(--mu)'});
  const bag=sv('rect',{x:100,y:124,width:220,height:16,rx:4,fill:'var(--c3)','fill-opacity':.3,stroke:'var(--c3)','stroke-width':1.6},s), bagT=stext(s,326,136,'vacuum bag',{'font-size':13.5,fill:'var(--c3)'});
  const couch=sv('rect',{x:90,y:144,width:240,height:18,rx:4,fill:'var(--c1)','fill-opacity':.3,stroke:'var(--c1)','stroke-width':1.6},s), couchT=stext(s,336,157,'couch',{'font-size':13.5,fill:'var(--c1)'});
  const mk=avArrowDef(s); [160,210,260].forEach(x=>avLine(s,mk,x,226,x,166,'var(--fg)',2.2)); stext(s,210,246,'beam',{'text-anchor':'middle','font-size':14});
  const EX=[130,150,170,190,210,230,250,270,290,150,190,230,270,170,250], el=EX.map((x,i)=>sv('circle',{cx:x,cy:116+(i%3)*2,r:3.6,fill:'var(--c2)'},s)); const sk=stext(s,210,22,'skin dose: lowest',{'text-anchor':'middle','font-weight':700,'font-size':15,fill:'var(--find)'});
  const {b:B,o:out}=avBtns(c,'In the beam',['Open','Couch','Couch and bag']);
  const set=k=>{B.forEach((e,i)=>e.setAttribute('aria-pressed',i===k?'true':'false')); couch.style.display=couchT.style.display=k>=1?'':'none'; bag.style.display=bagT.style.display=k>=2?'':'none'; const n=[3,9,15][k]; el.forEach((e,i)=>e.style.display=i<n?'':'none'); sk.textContent=['skin dose: lowest','skin dose: higher','skin dose: highest'][k];
    out.innerHTML=['<span class="v">Open</span>: only electrons from the head and the air reach the skin.','<span class="v">Couch</span>: about 2% attenuation at depth, and more electrons reach the skin.','<span class="v">Couch and vacuum bag</span>: more material, so the skin dose rises further.'][k];};
  B.forEach((e,i)=>e.addEventListener('click',()=>set(i))); set(0); return avPlay(c,1,()=>{});
};

AV['bolus-shift']=root=>{const B=bmBuild(6); return avChart(root,{h:262,label:'Dose against depth below the skin for a 6 MV beam with and without bolus of a thickness set by the slider',cap:'A tissue-equivalent bolus of thickness t shifts the build-up curve toward the skin: the dose at depth d below the skin is the dose at depth t + d. A bolus equal to d_max puts the maximum at the skin. Schematic 6 MV curve.',
  x:{min:0,max:5,ticks:[0,1,2,3,4,5],label:'Depth below the skin (cm)'},y:{min:0,max:105,ticks:[0,20,40,60,80,100],fmt:avPct2,label:'Dose (% of the maximum)'},series:[{fn:B.f,color:'var(--mu)',dash:'6 4'}],labels:[{x:3.3,y:62,t:'no bolus',color:'var(--mu)'}],
  slider:{min:0,max:2,value:1,label:'Bolus thickness t (cm)'},
  dyn:t=>({series:[{fn:d=>B.f(d+t),color:'var(--c1)',w:2.8}],marks:[{x:Math.max(0,B.dmax-t),y:B.f(Math.max(B.dmax,t)),color:'var(--c2)',label:'',r:5.5}],out:'t = <span class="v">'+t.toFixed(2)+' cm</span>: dose at the skin <span class="f">'+Math.round(B.f(t))+'%</span>, maximum '+Math.max(0,B.dmax-t).toFixed(1)+' cm below the skin'})});};

AV['terma-kernel']=root=>{const MU=0.045, D=(d,L)=>(Math.exp(-MU*d)-Math.exp(-d/L))/(1-MU*L); return avChart(root,{h:262,label:'The TERMA falling exponentially with depth and the dose after convolution with a forward kernel of a length set by the slider',cap:'One-dimensional illustration of D = TERMA ⊗ kernel. The TERMA falls from the surface. The dose builds up because electrons carry the energy forward, and a longer kernel, as at higher energy, puts the peak deeper.',
  x:{min:0,max:8,ticks:[0,2,4,6,8],label:'Depth (cm)'},y:{min:0,max:1.1,ticks:[0,0.25,0.5,0.75,1],fmt:v=>String(v),label:'Relative value'},series:[{fn:d=>Math.exp(-MU*d),color:'var(--c2)',dash:'6 4'}],labels:[{x:5,y:0.9,t:'TERMA',color:'var(--c2)',b:1},{x:5,y:0.66,t:'dose',color:'var(--c1)',b:1}],
  slider:{min:0.1,max:1.5,value:0.35,label:'Kernel length L (cm)'},dyn:L=>{const dm=L*Math.log(1/(MU*L))/(1-MU*L); return {series:[{fn:d=>D(d,L),color:'var(--c1)',w:2.8}],vlines:[{x:dm,label:'d_max',dy:150,dx:5}],out:'L = <span class="v">'+L.toFixed(2)+' cm</span>: the dose peaks at <span class="f">'+dm.toFixed(1)+' cm</span>'};}});};

AV['algorithm-ladder']=root=>avTimeline(root,{h:274,label:'Dose calculation algorithms in order of increasing accuracy, from correction-based methods to Monte Carlo',cap:'Accuracy generally rises with the physics modelled, and so does run time. Monte Carlo is the reference standard.',dur:5000,build:s=>{
  const mk=avArrowDef(s), R=[['Correction-based','Clarkson, TAR, tables'],['Pencil beam','narrow beams, depth kernel'],['Convolution / superposition','TERMA ⊗ density-scaled kernel'],['Acuros XB','Boltzmann equation on a grid'],['Monte Carlo','particle histories']];
  const rows=R.map((r,i)=>{const y=222-i*46, g=sv('g',{},s); sv('rect',{x:60,y:y,width:340,height:38,rx:6,fill:i===4?'var(--c2)':'none','fill-opacity':.14,stroke:i===4?'var(--c2)':'var(--fg)','stroke-width':i===4?2.2:1.5},g); stext(g,72,y+17,r[0],{'font-weight':700,'font-size':14.5}); stext(g,72,y+33,r[1],{'font-size':13,fill:'var(--mu)'}); return g;});
  const up=avGrow(s,mk,30,258,30,20,'var(--c2)',2.6); stext(s,14,14,'accuracy rises',{'font-size':13,fill:'var(--c2)','font-weight':600});
  return u=>{rows.forEach((g,i)=>g.style.display=u>=i*.17?'':'none'); up(ease(seg(u,.05,.85)));};}});

AV['beam-model']=root=>avTimeline(root,{h:246,label:'Three beam-model parameters and what each changes: the photon spectrum changes the PDD slope, head electrons change the superficial dose, and the source size changes the penumbra',cap:'Beam-model parameters are fitted to measured data. A harder spectrum falls off more slowly, switching off head electrons lowers the superficial dose, and a larger source widens the penumbra. Schematic curves.',dur:5600,build:s=>{
  const P=[{x:14,t:'photon spectrum',a:'PDD slope',f:[d=>Math.exp(-0.06*d),d=>Math.exp(-0.04*d)],lab:['softer','harder'],xr:[0,10],yr:[0,1.05]},{x:154,t:'head electrons',a:'superficial dose',f:[d=>0.15+0.85*(1-Math.exp(-3*d)),d=>0.05+0.95*(1-Math.exp(-3*d))],lab:['on','off'],xr:[0,3],yr:[0,1.05]},{x:294,t:'source size',a:'penumbra',f:[x=>0.5*avErfc(x/(Math.SQRT2*0.15)),x=>0.5*avErfc(x/(Math.SQRT2*0.35))],lab:['1 mm','3 mm'],xr:[-1.2,1.2],yr:[0,1.05]}];
  const gs=P.map(p=>{const g=sv('g',{},s); sv('rect',{x:p.x,y:14,width:112,height:140,fill:'none',stroke:'var(--line)','stroke-width':1.2},g);
    p.f.forEach((fn,i)=>{let d=''; for(let k=0;k<=40;k++){const x=p.xr[0]+(p.xr[1]-p.xr[0])*k/40, y=fn(x); d+=(k?'L':'M')+(p.x+6+100*k/40).toFixed(1)+' '+(150-130*y/p.yr[1]).toFixed(1);} sv('path',{d:d,fill:'none',stroke:i?'var(--c2)':'var(--c1)','stroke-width':2.4,'stroke-dasharray':i?'none':'6 4'},g);});
    stext(g,p.x+56,176,p.t,{'text-anchor':'middle','font-weight':700,'font-size':14}); stext(g,p.x+56,194,'→ '+p.a,{'text-anchor':'middle','font-size':13.5,fill:'var(--mu)'}); stext(g,p.x+56,214,p.lab[0]+' (dashed)',{'text-anchor':'middle','font-size':12.5,fill:'var(--c1)'}); stext(g,p.x+56,230,p.lab[1]+' (solid)',{'text-anchor':'middle','font-size':12.5,fill:'var(--c2)'}); return g;});
  return u=>gs.forEach((g,i)=>g.style.display=u>=i*.3?'':'none');}});

AV['lung-bone']=root=>{const MU=0.045, W=d=>100*Math.exp(-MU*d), C=(d,r)=>100*Math.exp(-MU*(d-(1-r)*Math.max(0,Math.min(d-4,6)))); return avChart(root,{h:262,label:'Dose against depth behind a lung slab from 4 to 10 cm, calculated as water and with the lung density set by the slider',cap:'Schematic. Lung attenuates less than water, so the dose beyond the slab is higher than a water-equivalent calculation predicts: by e^(μ (1 − ρ) t). Bone attenuates more.',
  x:{min:0,max:16,ticks:[0,4,8,12,16],label:'Depth (cm)'},y:{min:20,max:105,ticks:[20,40,60,80,100],fmt:avPct2,label:'Relative dose'},bands:[{x0:4,x1:10,fill:'var(--gr)',op:.9}],labels:[{x:5.4,y:30,t:'lung',color:'var(--mu)',b:1}],series:[{fn:W,color:'var(--mu)',dash:'6 4'}],
  slider:{min:0.1,max:1,value:0.3,label:'Lung density (g/cm³)'},dyn:r=>({series:[{fn:d=>C(d,r),color:'var(--c1)',w:2.8}],out:'ρ = <span class="v">'+r.toFixed(2)+'</span>: beyond the lung the dose is <span class="f">'+Math.round(100*(Math.exp(MU*(1-r)*6)-1))+'%</span> higher than the water-equivalent calculation'})});};


// ---------------------------------------------------------------- 3.8 to 3.10: multi-field plans, wedges, blocks and MLC shaping
const avHot=(S,s)=>(100+bmPDD(S-DATA.bm.DMAX,s))/(2*bmPDD(S/2,s));
AV['parallel-opposed']=root=>avChart(root,{h:268,label:'Dose along the axis from two parallel-opposed 6 MV beams for a separation set by the slider, with each beam and their sum',cap:'Each beam falls with depth from its own surface. Their sum, scaled to 100% at the midplane, is highest near the two entrance surfaces: the hot spots. Illustrative 6 MV, 10 × 10 cm.',
  x:{min:0,max:50,ticks:[0,10,20,30,40,50],label:'Depth from one surface (cm)'},y:{min:0,max:190,ticks:[0,50,100,150],fmt:v=>v+'%',label:'Dose'},
  slider:{min:10,max:50,value:30,label:'Separation of the entrance surfaces (cm)'},
  dyn:S=>{const mid=2*bmPDD(S/2,10), ok=d=>d>=DATA.bm.DMAX&&d<=S-DATA.bm.DMAX; return {series:[{fn:d=>ok(d)?bmPDD(d,10):NaN,color:'var(--c1)',dash:'6 4',w:1.8},{fn:d=>ok(d)?bmPDD(S-d,10):NaN,color:'var(--c2)',dash:'6 4',w:1.8},{fn:d=>ok(d)?100*(bmPDD(d,10)+bmPDD(S-d,10))/mid:NaN,color:'var(--fg)',w:3}],
    out:'S = <span class="v">'+Math.round(S)+' cm</span>: dose near each surface <span class="f">'+(100*avHot(S,10)).toFixed(0)+'%</span> of the midplane dose (hot spot ratio '+avHot(S,10).toFixed(2)+')'};}});

AV['hotspot-separation']=root=>avChart(root,{h:262,label:'Hot spot ratio of an equally weighted parallel-opposed 6 MV pair against separation, for two field sizes',cap:'The hot spot ratio rises steeply with separation and is lower for the larger field, whose PDD falls off less steeply. Illustrative 6 MV data.',
  x:{min:10,max:50,ticks:[10,20,30,40,50],label:'Separation (cm)'},y:{min:1,max:1.7,ticks:[1,1.2,1.4,1.6],fmt:v=>String(v),label:'Hot spot ratio'},series:[{fn:S=>avHot(S,10),color:'var(--c2)'},{fn:S=>avHot(S,20),color:'var(--c1)'}],labels:[{x:12,y:1.58,t:'10 × 10 cm',color:'var(--c2)',b:1},{x:12,y:1.5,t:'20 × 20 cm',color:'var(--c1)',b:1}],
  fixed:[20,30,50],dyn:S=>({marks:[{x:S,y:avHot(S,10),color:'var(--c2)',label:''},{x:S,y:avHot(S,20),color:'var(--c1)',label:''}],out:'S = <span class="v">'+Math.round(S)+' cm</span>: ratio <span class="f">'+avHot(S,10).toFixed(2)+'</span> for 10 × 10 cm, '+avHot(S,20).toFixed(2)+' for 20 × 20 cm'})});

AV['beam-count']=root=>{
  const W=420,H=262,{s,c}=avShell(root,W,H,'Equally spaced beams converging on the isocenter of a patient cross-section, with more beams spreading the entrance dose over more surfaces','With more beams the entrance dose at each skin surface is a smaller share of the total, so the superficial hot spot falls. Schematic.');
  const cx=210, cy=126, rx=96, ry=62; sv('ellipse',{cx,cy,rx,ry,fill:'var(--gr)','fill-opacity':.55,stroke:'var(--fg)','stroke-width':1.8},s); sv('circle',{cx,cy,r:4,fill:'var(--c2)'},s);
  const mk=avArrowDef(s), g=sv('g',{},s), {b:B,o:out}=avBtns(c,'Number of equally weighted beams',['2','3','4','6']);
  const set=k=>{B.forEach((e,i)=>e.setAttribute('aria-pressed',i===k?'true':'false')); const n=[2,3,4,6][k]; g.innerHTML='';
    for(let i=0;i<n;i++){const a=(i*360/n+(n===2?90:0))*Math.PI/180, ux=Math.sin(a), uy=-Math.cos(a), ex=cx+ux*rx*0.99/Math.sqrt(1+0), ey=cy+uy*ry*0.99; const sx=cx+ux*rx*1.5, sy=cy+uy*ry*1.9; avLine(g,mk,sx,sy,cx+ux*8,cy+uy*5,'var(--c3)',2.2); sv('circle',{cx:ex,cy:ey,r:Math.max(4,17/Math.pow(n,0.7)),fill:'var(--c2)','fill-opacity':.85},g);}
    out.innerHTML='<span class="v">'+n+' beams</span>: each entrance surface carries about <span class="f">1/'+n+'</span> of the entrance dose (schematic)';};
  B.forEach((e,i)=>e.addEventListener('click',()=>set(i))); set(1); return avPlay(c,1,()=>{});
};

AV['wedge-profile']=root=>{const M=0.045; return avChart(root,{h:262,label:'Dose across a field at depth for a wedge angle set by the slider, falling from the toe to the heel',cap:'Schematic. Along a line at depth, the dose falls as e^(−μ x tan θ), because an isodose tilted by the wedge angle θ is displaced deeper by x tan θ. Here μ is about 0.045 per cm.',
  x:{min:-5,max:5,ticks:[-5,0,5],fmt:v=>String(v),label:'Position across the field (cm), toe at the left'},y:{min:0,max:140,ticks:[0,50,100],fmt:v=>String(v),label:'Dose (% of the axis value)'},labels:[{x:-4.9,y:128,t:'toe',color:'var(--mu)',b:1},{x:4.9,y:128,t:'heel',color:'var(--mu)',b:1,anchor:'end'}],
  slider:{min:0,max:60,value:45,label:'Wedge angle (°)'},dyn:th=>({series:[{fn:x=>100*Math.exp(-M*x*Math.tan(th*Math.PI/180)),color:'var(--c1)'}],out:'θ = <span class="v">'+Math.round(th)+'°</span>: across 10 cm the dose falls to <span class="f">'+Math.round(100*Math.exp(-M*10*Math.tan(th*Math.PI/180)))+'%</span> of its toe value'})});};

AV['wedge-hinge']=root=>avChart(root,{h:256,label:'The wedge angle needed for two beams against the hinge angle between them',cap:'Wedge angle ≈ 90° − φ/2. Parallel-opposed beams (φ = 180°) need no wedge and perpendicular beams (φ = 90°) need 45° wedges, with the heels together.',
  x:{min:0,max:180,ticks:[0,45,90,135,180],fmt:v=>v+'°',label:'Hinge angle φ between the beams'},y:{min:0,max:90,ticks:[0,15,30,45,60,75,90],fmt:v=>v+'°',label:'Wedge angle'},series:[{fn:p=>90-p/2,color:'var(--c1)'}],
  fixed:[50,100],dyn:p=>({marks:[{x:p,y:90-p/2,color:'var(--find)',r:6,label:''}],out:'φ = <span class="v">'+Math.round(p)+'°</span>: wedge angle <span class="f">'+(90-p/2).toFixed(0)+'°</span>'})});

AV['wedge-breast']=root=>{const M=0.045; return avChart(root,{h:262,label:'Dose across a tangent breast field that thickens toward one side, without a wedge and with a wedge angle set by the slider and the heel at the thin side',cap:'Schematic. The tissue thickens by 0.8 cm per cm toward the right, so the open field dose falls. A wedge with the heel at the thin side tilts the dose back up, and it is flat near 39°.',
  x:{min:0,max:10,ticks:[0,2,4,6,8,10],label:'Position across the field (cm), from the thin side'},y:{min:60,max:125,ticks:[60,80,100,120],fmt:v=>v+'%',label:'Dose (% of the thin-side value)'},series:[{fn:x=>100*Math.exp(-M*0.8*x),color:'var(--mu)',dash:'6 4'}],labels:[{x:5.5,y:84,t:'no wedge',color:'var(--mu)'}],
  slider:{min:0,max:60,value:39,label:'Wedge angle (°)'},dyn:th=>({series:[{fn:x=>100*Math.exp(-M*0.8*x+M*x*Math.tan(th*Math.PI/180)),color:'var(--c1)',w:2.8}],out:'θ = <span class="v">'+Math.round(th)+'°</span>: dose at the thick side is <span class="f">'+Math.round(100*Math.exp(-M*8+M*10*Math.tan(th*Math.PI/180)))+'%</span> of the thin side (open field 70%)'})});};

AV['hvl-blocks']=root=>avBars(root,{rowH:38,label:'Fraction of the beam transmitted by a block of one to five half-value layers, on a logarithmic axis',cap:'Each half-value layer halves the beam. Five half-value layers transmit 3.1%, a common design target for shielding blocks.',
  m:{l:70,r:66},x:{min:1,max:100,log:true,ticks:[1,10,100],fmt:v=>v+'%',label:'Transmitted (%), log scale'},rows:[1,2,3,4,5].map(n=>({t:n+' HVL',v:100*Math.pow(0.5,n),col:n===5?'var(--c2)':'var(--c1)',val:(100*Math.pow(0.5,n)).toFixed(n===4?2:(n>2?1:0))+'%'}))});

AV['mlc-leakage']=root=>avBars(root,{rowH:42,label:'Relative dose in the open field, between two leaves, and behind a leaf, on a logarithmic axis',cap:'Transmission through a tungsten leaf is about 1%–1.5%. Leakage through the gap between leaves is about double that. Illustrative values of 1.25% and 2.5%.',
  m:{l:128,r:62},x:{min:0.1,max:100,log:true,ticks:[0.1,1,10,100],fmt:v=>v+'%',label:'Dose (% of the open field), log scale'},rows:[{t:'open field',v:100,col:'var(--c1)',val:'100%'},{t:'between leaves',v:2.5,col:'var(--c2)',val:'2.5%'},{t:'behind a leaf',v:1.25,col:'var(--c2)',val:'1.25%'}]});

AV['mlc-penumbra']=root=>{const R=x=>5+0.01*x*x, F=x=>3+0.25*Math.abs(x); return avChart(root,{h:262,label:'Penumbra width against the position of the collimator edge for a rounded leaf end and for a flat edge that does not diverge with the beam',cap:'Schematic with illustrative widths. A rounded leaf end gives a penumbra that barely changes as the leaf moves across the field. A flat, non-divergent edge is sharp near the axis and wider the farther it is from the axis.',
  x:{min:0,max:15,ticks:[0,5,10,15],label:'Distance of the edge from the central axis (cm)'},y:{min:0,max:8,ticks:[0,2,4,6,8],fmt:v=>String(v),label:'Penumbra width (mm)'},series:[{fn:R,color:'var(--c1)'},{fn:F,color:'var(--c2)'}],labels:[{x:0.4,y:6.3,t:'rounded leaf end',color:'var(--c1)',b:1},{x:8.6,y:3.7,t:'flat edge',color:'var(--c2)',b:1}],
  fixed:[2,10],dyn:x=>({marks:[{x:x,y:R(x),color:'var(--c1)',label:''},{x:x,y:F(x),color:'var(--c2)',label:''}],out:'x = <span class="v">'+x.toFixed(0)+' cm</span>: rounded <span class="f">'+R(x).toFixed(1)+' mm</span>, flat '+F(x).toFixed(1)+' mm'})});};


// ---------------------------------------------------------------- 3.11 and 3.12: electron depth dose and range, field size, penumbra, matching, and obliquity
function avPchip(xs,ys){const n=xs.length,h=[],d=[],m=new Array(n).fill(0); for(let i=0;i<n-1;i++){h.push(xs[i+1]-xs[i]); d.push((ys[i+1]-ys[i])/h[i]);} m[0]=d[0]; m[n-1]=d[n-2];
  for(let i=1;i<n-1;i++) if(d[i-1]*d[i]>0){const w1=2*h[i]+h[i-1], w2=h[i]+2*h[i-1]; m[i]=(w1+w2)/(w1/d[i-1]+w2/d[i]);}
  return x=>{if(x<=xs[0]) return ys[0]; if(x>=xs[n-1]) return ys[n-1]; let i=0; while(xs[i+1]<x) i++; const t=(x-xs[i])/h[i]; return (2*t*t*t-3*t*t+1)*ys[i]+(t*t*t-2*t*t+t)*h[i]*m[i]+(-2*t*t*t+3*t*t)*ys[i+1]+(t*t*t-t*t)*h[i]*m[i+1];};}
const elR=E=>({r90:E/3.3,r80:E/3,r50:E/2.33,rp:E/2});
const elPDD=E=>{const r=elR(E); return avPchip([0,.5*r.r90,.75*r.r90,r.r90,r.r80,(r.r80+r.r50)/2,r.r50,(r.r50+r.rp)/2,r.rp,r.rp+1.5,r.rp+6],[85,99,100,90,80,66,50,24,4,2.5,1.5]);};
AV['electron-pdd']=root=>avChart(root,{h:262,label:'Schematic electron depth dose for a beam energy set by the slider, with R90, R80, R50, and the practical range marked',cap:'Schematic. The dose builds up to a broad maximum, falls steeply but not sharply because of the energy spectrum and scattering, and ends in a bremsstrahlung tail of about 1%–5%.',
  x:{min:0,max:11,ticks:[0,2,4,6,8,10],label:'Depth (cm)'},y:{min:0,max:105,ticks:[0,20,40,60,80,100],fmt:avPct2,label:'Percent depth dose'},slider:{min:6,max:20,value:12,label:'Beam energy (MeV)'},
  dyn:E0=>{const E=Math.round(E0*10)/10, r=elR(E); return {series:[{fn:elPDD(E),color:'var(--c1)',w:2.8}],vlines:[{x:r.r90,label:'R90',dy:16,dx:3},{x:r.r80,label:'R80',dy:32,dx:3},{x:r.r50,label:'R50',dy:16,dx:3},{x:r.rp,label:'Rp',dy:32,dx:3}],
    out:'<span class="v">'+Math.round(E)+' MeV</span>: R<sub>90</sub> '+r.r90.toFixed(1)+', R<sub>80</sub> '+r.r80.toFixed(1)+', R<sub>50</sub> '+r.r50.toFixed(1)+', R<sub>p</sub> <span class="f">'+r.rp.toFixed(1)+'</span> cm'};}});
AV['electron-range']=root=>avChart(root,{h:262,label:'R90, R80, R50, and the practical range against beam energy',cap:'Rules of thumb for E in MeV and depths in cm: R90 ≈ E/3.3, R80 ≈ E/3, R50 ≈ E/2.33, and Rp ≈ E/2.',
  x:{min:4,max:22,ticks:[4,8,12,16,20],label:'Beam energy (MeV)'},y:{min:0,max:11,ticks:[0,2,4,6,8,10],fmt:v=>String(v),label:'Depth (cm)'},series:[{fn:E=>E/3.3,color:'var(--c1)'},{fn:E=>E/3,color:'var(--c3)'},{fn:E=>E/2.33,color:'var(--c2)'},{fn:E=>E/2,color:'var(--fg)'}],
  labels:[{x:16.8,y:4.55,t:'R90',color:'var(--c1)',b:1},{x:16.8,y:6.3,t:'R80',color:'var(--c3)',b:1},{x:16.8,y:8.0,t:'R50',color:'var(--c2)',b:1},{x:16.8,y:9.5,t:'Rp',color:'var(--fg)',b:1}],
  fixed:[5,12,20],dyn:E0=>{const E=Math.round(E0*10)/10; return {marks:[E/3.3,E/3,E/2.33,E/2].map((y,i)=>({x:E,y:y,color:['var(--c1)','var(--c3)','var(--c2)','var(--fg)'][i],label:''})),out:'<span class="v">'+Math.round(E)+' MeV</span>: R<sub>90</sub> '+(E/3.3).toFixed(1)+', R<sub>80</sub> '+(E/3).toFixed(1)+', R<sub>50</sub> '+(E/2.33).toFixed(1)+', R<sub>p</sub> <span class="f">'+(E/2).toFixed(1)+'</span> cm'};}});
AV['electron-fieldsize']=root=>avChart(root,{h:262,label:'Depth of the dose maximum against field size for an electron beam of an energy set by the slider',cap:'Schematic. For fields at least as large as the practical range the PDD no longer changes. Smaller fields lose lateral equilibrium, so the dose maximum moves toward the surface.',
  x:{min:2,max:16,ticks:[2,4,6,8,10,12,14,16],label:'Field side (cm)'},y:{min:0,max:4,ticks:[0,1,2,3,4],fmt:v=>String(v),label:'Depth of the dose maximum (cm)'},slider:{min:6,max:20,value:18,label:'Beam energy (MeV)'},
  dyn:E0=>{const E=Math.round(E0*10)/10, rp=E/2, d0=0.45*E/3.3, f=s=>d0*Math.min(1,Math.pow(s/rp,1.3)); return {series:[{fn:f,color:'var(--c1)',w:2.8}],vlines:[{x:rp,label:'Rp',dy:16,dx:4}],out:'<span class="v">'+Math.round(E)+' MeV</span>: R<sub>p</sub> = <span class="f">'+rp.toFixed(1)+' cm</span>. Fields of that size and larger have d<sub>max</sub> = '+d0.toFixed(1)+' cm, and a 5 × 5 cm field about '+f(5).toFixed(1)+' cm'};}});
AV['electron-penumbra']=root=>{const w8=z=>5+z, w18=z=>2.5+2*z; return avChart(root,{h:262,label:'Schematic penumbra width against depth for 8 MeV and 18 MeV electron beams',cap:'Schematic with illustrative widths. Near the surface the 18 MeV penumbra is smaller, because scattering is more forward-directed. Deeper, it becomes much wider.',
  x:{min:0,max:8,ticks:[0,2,4,6,8],label:'Depth (cm)'},y:{min:0,max:20,ticks:[0,5,10,15,20],fmt:v=>String(v),label:'Penumbra width (mm)'},series:[{fn:w8,color:'var(--c1)'},{fn:w18,color:'var(--c2)'}],labels:[{x:6.2,y:8.2,t:'8 MeV',color:'var(--c1)',b:1},{x:5.0,y:15.8,t:'18 MeV',color:'var(--c2)',b:1}],
  fixed:[1,5],dyn:z=>({marks:[{x:z,y:w8(z),color:'var(--c1)',label:''},{x:z,y:w18(z),color:'var(--c2)',label:''}],out:'d = <span class="v">'+z.toFixed(1)+' cm</span>: 8 MeV <span class="f">'+w8(z).toFixed(1)+' mm</span>, 18 MeV '+w18(z).toFixed(1)+' mm'})});};
AV['electron-matching']=root=>{const hot=g=>30*Math.exp(-g/5), low=g=>-Math.min(40,6*Math.max(0,g-4)); return avChart(root,{h:262,label:'Dose change at the junction of an electron field and a photon field against the gap between them',cap:'Schematic with illustrative values. With no gap there is a hot spot on the photon side, about 30% in one example. A gap lowers it, but a larger gap leaves a low-dose region at the surface.',
  x:{min:0,max:15,ticks:[0,5,10,15],label:'Gap between the fields (mm)'},y:{min:-40,max:35,ticks:[-40,-20,0,20],fmt:v=>(v>0?'+':v<0?'−':'')+Math.abs(v)+'%',label:'Dose change at the junction'},series:[{fn:hot,color:'var(--c2)'},{fn:low,color:'var(--c1)'}],hlines:[{y:0,label:''}],
  labels:[{x:6.2,y:17,t:'hot spot, photon side',color:'var(--c2)',b:1},{x:7.5,y:-31,t:'low dose at the surface',color:'var(--c1)',b:1}],
  fixed:[2,5,10],dyn:g=>({marks:[{x:g,y:hot(g),color:'var(--c2)',label:''},{x:g,y:low(g),color:'var(--c1)',label:''}],out:'gap = <span class="v">'+g.toFixed(0)+' mm</span>: hot spot <span class="f">+'+hot(g).toFixed(0)+'%</span>, surface '+(low(g)<0?'−'+Math.abs(low(g)).toFixed(0)+'%':'no change')})});};
AV['electron-obliquity']=root=>avChart(root,{h:256,label:'Depth of the dose maximum below the skin against the angle of incidence, relative to perpendicular incidence',cap:'First-order geometry: the dose maximum lies at a fixed distance along the beam, so measured from the skin it moves toward the surface as cos θ. Scatter adds to the effect, which is larger at higher energy.',
  x:{min:0,max:60,ticks:[0,15,30,45,60],fmt:v=>v+'°',label:'Angle of incidence from the perpendicular'},y:{min:0.4,max:1.05,ticks:[0.4,0.6,0.8,1],fmt:v=>String(v),label:'d_max relative to perpendicular incidence'},series:[{fn:a=>Math.cos(a*Math.PI/180),color:'var(--c1)'}],
  fixed:[10,30,50],dyn:a=>({marks:[{x:a,y:Math.cos(a*Math.PI/180),color:'var(--find)',r:6,label:''}],out:'θ = <span class="v">'+Math.round(a)+'°</span>: d<sub>max</sub> falls to <span class="f">'+Math.cos(a*Math.PI/180).toFixed(2)+'</span> of its perpendicular value'})});

// ---------------------------------------------------------------- 3.13: electron output and monitor units
AV['electron-mu-chain']=root=>avTimeline(root,{h:250,label:'An electron MU calculation: the prescription is divided by the PDD, the output factor, and the inverse-square term',cap:'9 MeV, SSD 100 cm: prescription 200 cGy at the 90% depth, S_e = 0.97, and an inverse-square term of 1.000, so MU = 200 / (0.90 × 0.97 × 1.000) = 229 MU.',dur:5200,build:s=>{
  const R=[['prescribed dose','200 cGy','200.0'],['÷ PDD/100 (0.90)','dose at d_max','222.2'],['÷ output factor S_e (0.97)','','229.1'],['÷ inverse-square term (1.000)','','229.1']];
  const rows=R.map((r,i)=>{const y=28+i*42, g=sv('g',{},s); stext(g,14,y+4,r[0],{'font-size':14.5}); if(r[1]) stext(g,14,y+22,r[1],{'font-size':12.5,fill:'var(--mu)'}); stext(g,396,y+4,'= '+r[2],{'text-anchor':'end','font-weight':700,'font-size':15}); return g;});
  const g2=sv('g',{},s); sv('line',{x1:14,x2:400,y1:28+4*42-14,y2:28+4*42-14,stroke:'var(--fg)','stroke-width':1.5},g2); stext(g2,14,28+4*42+10,'MU',{'font-weight':700,'font-size':17,fill:'var(--find)'}); stext(g2,396,28+4*42+10,'229 MU',{'text-anchor':'end','font-weight':700,'font-size':18,fill:'var(--find)'});
  return u=>{rows.forEach((g,i)=>g.style.display=u>=i*.16?'':'none'); g2.style.display=u>=.72?'':'none';};}});
AV['virtual-source']=root=>{const inv=g=>Math.pow((85+1.8)/(85+1.8+g),2); return avChart(root,{h:262,label:'The inverse-square term of a 9 MeV electron beam with a virtual source at 85 cm, against SSD',cap:'INV² = [ (SSD_eff + d_max) / (SSD_eff + d_max + g) ]² with SSD_eff = 85 cm, d_max = 1.8 cm, and g = SSD − 100 cm. The virtual-source description is reasonable to an SSD of about 115 cm.',
  x:{min:100,max:120,ticks:[100,105,110,115,120],label:'SSD (cm)'},y:{min:0.6,max:1.02,ticks:[0.6,0.7,0.8,0.9,1],fmt:v=>String(v),label:'Inverse-square term'},series:[{fn:s=>inv(s-100),color:'var(--c1)'}],vlines:[{x:115,label:'limit',dy:150,dx:4}],
  fixed:[100,105],dyn:s=>({marks:[{x:s,y:inv(s-100),color:'var(--find)',r:6,label:''}],out:'SSD = <span class="v">'+Math.round(s)+' cm</span>: INV² = <span class="f">'+inv(s-100).toFixed(3)+'</span>, so the dose per MU is '+(100*(1-inv(s-100))).toFixed(0)+'% lower than at SSD 100 cm'})});};
AV['electron-output']=root=>avChart(root,{h:262,label:'Output factor against field size for an electron beam of an energy set by the slider',cap:'Schematic. When the field is smaller than the practical range, lateral scatter is lost and the output factor falls below 1. Measure S_e for each cutout.',
  x:{min:2,max:16,ticks:[2,4,6,8,10,12,14,16],label:'Field side (cm)'},y:{min:0.6,max:1.05,ticks:[0.6,0.7,0.8,0.9,1],fmt:v=>String(v),label:'Output factor S_e'},slider:{min:6,max:20,value:12,label:'Beam energy (MeV)'},
  dyn:E0=>{const E=Math.round(E0*10)/10, rp=E/2, f=s=>s>=rp?1:1-0.35*Math.pow(1-s/rp,1.5); return {series:[{fn:f,color:'var(--c1)',w:2.8}],vlines:[{x:rp,label:'Rp',dy:16,dx:4}],out:'<span class="v">'+Math.round(E)+' MeV</span>: R<sub>p</sub> = '+rp.toFixed(1)+' cm. A 4 × 4 cm field has S<sub>e</sub> = <span class="f">'+f(4).toFixed(2)+'</span> (illustrative)'};}});

// ---------------------------------------------------------------- 3.14 to 3.16: ICRU volumes and margins, DVHs and conformity, and BED, TCP, and NTCP
AV['icru-volumes']=root=>avTimeline(root,{h:262,label:'Nested ICRU volumes: the GTV inside the CTV inside the ITV inside the PTV, with the treated volume and the irradiated volume outside',cap:'Each target volume adds an expansion to the one inside it. The treated volume follows the prescription isodose. The irradiated volume is typically inside the 50% isodose line.',dur:6500,build:s=>{
  const L=[['GTV','visible disease',34,24,'var(--c2)',0.5,''],['CTV','+ occult disease',52,37,'var(--c3)',0.3,''],['ITV','+ motion',70,49,'var(--c1)',0.22,''],['PTV','+ setup variability',88,61,'var(--mu)',0.16,''],['TV','treated volume',102,72,'none',0,'6 4'],['IV','irradiated volume',122,86,'none',0,'2 4']];
  const els=L.map((o,i)=>{const g=sv('g',{},s); sv('ellipse',{cx:140,cy:132,rx:o[2],ry:o[3],fill:o[4]==='none'?'none':o[4],'fill-opacity':o[5],stroke:o[4]==='none'?'var(--fg)':o[4],'stroke-width':o[4]==='none'?1.5:2,'stroke-dasharray':o[6]},g);
    const y=36+i*38; sv('line',{x1:140+o[2]*0.7,y1:132-o[3]*0.7,x2:272,y2:y-5,stroke:'var(--muted)','stroke-width':0.8},g); stext(g,278,y,o[0],{'font-weight':700,'font-size':15}); stext(g,278,y+15,o[1],{'font-size':12.5,fill:'var(--mu)'}); return g;});
  return u=>els.forEach((g,i)=>g.style.display=u>=i*0.15?'':'none');}});
AV['margin-recipe']=root=>{const m=(S,r)=>2.5*S+0.7*r; return avChart(root,{h:262,label:'PTV margin from the van Herk recipe against the systematic error, for random errors of 2, 3, and 4 mm',cap:'PTV margin = 2.5 Σ + 0.7 σ. The slope against Σ is 2.5 and against σ only 0.7, so reducing the systematic error shrinks the margin most. Lines: σ = 2 mm (blue), 3 mm (green), 4 mm (orange).',
  x:{min:0,max:5,ticks:[0,1,2,3,4,5],label:'Systematic error Σ (mm)'},y:{min:0,max:16,ticks:[0,4,8,12,16],fmt:v=>String(v),label:'PTV margin (mm)'},series:[{fn:S=>m(S,2),color:'var(--c1)'},{fn:S=>m(S,3),color:'var(--c3)'},{fn:S=>m(S,4),color:'var(--c2)'}],
  fixed:[1,2,5],dyn:S0=>{const S=Math.round(S0*10)/10; return {marks:[2,3,4].map((r,i)=>({x:S,y:m(S,r),color:['var(--c1)','var(--c3)','var(--c2)'][i],label:''})),out:'Σ = <span class="v">'+S.toFixed(1)+' mm</span>: margin '+m(S,2).toFixed(1)+' mm for σ = 2, <span class="f">'+m(S,3).toFixed(1)+'</span> for σ = 3, '+m(S,4).toFixed(1)+' for σ = 4'};}});};
AV['prescription-elements']=root=>avTimeline(root,{h:210,label:'The five parts of an ASTRO prescription: L_Lung, Photons, 200 cGy × 32 to 6400 cGy',cap:'Site, delivery method, dose per fraction, number of fractions, and total dose, in cGy and in this order. The total is the dose per fraction times the number of fractions.',dur:5200,build:s=>{
  const P=[['L_Lung','site'],['Photons','delivery'],['200 cGy','per fraction'],['× 32','fractions'],['6400 cGy','total dose']], W=[80,82,84,62,104], gs=[]; let x=4;
  P.forEach((p,i)=>{const g=sv('g',{},s), w=W[i]-6; sv('rect',{x:x,y:60,width:w,height:46,rx:6,fill:'var(--paper-2)',stroke:'var(--fg)','stroke-width':1.4},g); stext(g,x+w/2,89,p[0],{'text-anchor':'middle','font-weight':700,'font-size':15}); stext(g,x+w/2,126,p[1],{'text-anchor':'middle','font-size':12,fill:'var(--mu)'}); gs.push(g); x+=W[i];});
  const g2=sv('g',{},s); stext(g2,210,178,'200 × 32 = 6400 cGy',{'text-anchor':'middle','font-weight':700,'font-size':17,fill:'var(--find)'});
  return u=>{gs.forEach((g,i)=>g.style.display=u>=i*0.14?'':'none'); g2.style.display=u>=0.8?'':'none';};}});
const erfcA=x=>{const z=Math.abs(x), t=1/(1+0.3275911*z), y=t*(0.254829592+t*(-0.284496736+t*(1.421413741+t*(-1.453152027+t*1.061405429))))*Math.exp(-z*z); return x>=0?y:2-y;};
const dvhP=D=>50*erfcA((D-50)/(Math.SQRT2*1.4)), dvhO=D=>100*Math.exp(-Math.pow(D/18,1.5));
AV['dvh-curve']=root=>avChart(root,{h:262,label:'Cumulative dose-volume histograms of a PTV and of a parallel organ at risk',cap:'Each point is the percentage of the volume that receives at least that dose. The PTV curve stays high and drops sharply near the prescription dose. The organ curve falls gradually. Illustrative curves.',
  x:{min:0,max:70,ticks:[0,10,20,30,40,50,60,70],label:'Dose (Gy)'},y:{min:0,max:100,ticks:[0,25,50,75,100],fmt:v=>v+'%',label:'Volume receiving at least the dose'},series:[{fn:dvhP,color:'var(--c1)',w:2.8},{fn:dvhO,color:'var(--c2)',w:2.8}],labels:[{x:28,y:92,t:'PTV',color:'var(--c1)',b:1},{x:10,y:42,t:'organ at risk',color:'var(--c2)',b:1}],
  fixed:[10,45,50],dyn:D0=>{const D=Math.round(D0); return {marks:[{x:D,y:dvhP(D),color:'var(--c1)',label:''},{x:D,y:dvhO(D),color:'var(--c2)',label:''}],out:'D = <span class="v">'+D+' Gy</span>: <span class="f">'+dvhP(D).toFixed(0)+'%</span> of the PTV and '+dvhO(D).toFixed(0)+'% of the organ receive at least this dose'};}});
AV['conformity-index']=root=>{
  const W=420,H=190,{s,c}=avShell(root,W,H,'Three stereotactic plans for a 30 cc target: ideal, over-coverage, and a displaced dose, with their conformity index and Paddick index','CI = V_P/V_T ignores where the dose volume is: the displaced plan has CI = 1 but covers half of the target. The Paddick index, coverage × selectivity, is 0.25 for it.');
  const upd=avBarRows(s,{rows:['V_T target','V_P at Rx dose','V_TP target covered'],x0:150,y0:12,rh:50,w:230,max:50});
  const S=[['Ideal',30,30,30],['Over-coverage',30,45,28],['Displaced',30,30,15]], {b:btns,o:out}=avBtns(c,'Plan',S.map(x=>x[0]));
  const show=i=>{const [n,vt,vp,vtp]=S[i], ci=vp/vt, pad=(vtp/vt)*(vtp/vp); upd([vt,vp,vtp],[vt+' cc',vp+' cc',vtp+' cc'],['var(--c1)','var(--c3)','var(--c2)']); btns.forEach((b,k)=>b.setAttribute('aria-pressed',String(k===i)));
    out.innerHTML='<span class="v">'+n+'</span>: CI = '+ci.toFixed(2)+', coverage '+(vtp/vt).toFixed(2)+', selectivity '+(vtp/vp).toFixed(2)+', Paddick <span class="f">'+pad.toFixed(3)+'</span>';};
  btns.forEach((b,k)=>b.addEventListener('click',()=>show(k))); show(1); return {enter(){},leave(){},finish(){}};};
AV['serial-parallel']=root=>avTimeline(root,{h:250,label:'Serial organs are limited by the maximum dose to a small volume, and parallel organs by the mean dose and the volume above a threshold',cap:'A serial organ fails if any part is damaged. A parallel organ has many independent units and tolerates damage to part of it.',dur:5600,build:s=>{
  const cols=[[10,'Serial organ',['spinal cord, optic nerve,','brainstem','Damage to any part','can cause loss of function.','Limit: the maximum dose','to a small volume.'],'var(--c2)'],[214,'Parallel organ',['lung, liver, kidney','Many independent units,','part can be damaged','without losing function.','Limit: the mean dose and','the volume above a threshold,','such as V_20 Gy.'],'var(--c1)']];
  const gs=cols.map(([x,t,L,col])=>{const g=sv('g',{},s); sv('rect',{x:x,y:14,width:196,height:216,rx:8,fill:'none',stroke:col,'stroke-width':2},g); stext(g,x+12,42,t,{'font-weight':700,'font-size':17,fill:col}); L.forEach((l,i)=>stext(g,x+12,72+i*24+(i>1?10:0)+(i>3?6:0),l,{'font-size':14.5}));return g;});
  return u=>gs.forEach((g,i)=>g.style.display=u>=i*0.35?'':'none');}});
AV['lq-survival']=root=>{const A=0.3, sf=(ab,D)=>Math.exp(-A*D-(A/ab)*D*D); return avChart(root,{h:262,label:'Linear-quadratic cell survival curve for an α/β set by the slider, with the curve for α/β = 10 Gy dashed, on a logarithmic axis',cap:'SF = e^(−αd − βd²) with α = 0.3 per Gy and β = α / (α/β). The quadratic term gives the shoulder. A lower α/β means a larger β, a more pronounced shoulder, and a lower surviving fraction at 2 Gy, as in late-responding tissue. The dashed curve is α/β = 10 Gy. Illustrative parameters.',
  x:{min:0,max:8,ticks:[0,2,4,6,8],label:'Dose (Gy)'},y:{min:0.0001,max:1,log:true,ticks:[0.0001,0.001,0.01,0.1,1],fmt:v=>String(v),label:'Surviving fraction, log scale'},slider:{min:1,max:20,value:3,label:'α/β (Gy)'},
  dyn:ab0=>{const ab=Math.round(ab0*2)/2; return {series:[{fn:D=>sf(10,D),color:'var(--mu)',dash:'5 4'},{fn:D=>sf(ab,D),color:'var(--c2)',w:2.8}],marks:[{x:2,y:sf(ab,2),color:'var(--find)',r:6,label:''}],out:'α/β = <span class="v">'+ab.toFixed(1)+' Gy</span>: the surviving fraction after 2 Gy is <span class="f">'+sf(ab,2).toFixed(3)+'</span>, against '+sf(10,2).toFixed(3)+' for α/β = 10 Gy'};}});};

AV['bed-compare']=root=>{
  const W=420,H=262,{s,c}=avShell(root,W,H,'BED of four regimens for a tumour with α/β = 10 Gy and for a late-responding tissue with α/β = 3 Gy','BED = D (1 + d/(α/β)). A larger dose per fraction raises the BED much more when α/β is low, so large fractions matter most for late-responding tissue.');
  const R=[['60 Gy / 30 fx',60,2],['50 Gy / 20 fx',50,2.5],['30 Gy / 10 fx',30,3],['32 Gy / 4 fx',32,8]], upd=avBarRows(s,{rows:R.map(r=>r[0]),x0:112,y0:14,rh:56,w:250,max:130}), {b:btns,o:out}=avBtns(c,'Tissue',['Tumour, α/β = 10 Gy','Late tissue, α/β = 3 Gy']);
  const show=i=>{const ab=[10,3][i], v=R.map(r=>r[1]*(1+r[2]/ab)); upd(v,v.map(x=>x.toFixed(1)),v.map(()=>i?'var(--c2)':'var(--c1)')); btns.forEach((b,k)=>b.setAttribute('aria-pressed',String(k===i)));
    out.innerHTML='α/β = <span class="v">'+ab+' Gy</span>: 32 Gy / 4 fx has a BED of <span class="f">'+v[3].toFixed(1)+'</span> Gy, against '+v[0].toFixed(1)+' Gy for 60 Gy / 30 fx';};
  btns.forEach((b,k)=>b.addEventListener('click',()=>show(k))); show(0); return {enter(){},leave(){},finish(){}};};
AV['tcp-ntcp']=root=>{const ntcp=D=>1/(1+Math.exp(-(D-62)/4)); return avChart(root,{h:262,label:'Tumour control probability and normal tissue complication probability against dose, for a number of clonogens set by the slider',cap:'TCP = exp(−N e^(−α BED)) with α = 0.3 per Gy and BED = 1.2 D for 2 Gy fractions (α/β = 10 Gy). A larger number of clonogens N moves the TCP curve to higher dose, so a larger tumour needs more dose and the therapeutic window between the curves narrows. The NTCP curve is illustrative.',
  x:{min:30,max:80,ticks:[30,40,50,60,70,80],label:'Dose in 2 Gy fractions (Gy)'},y:{min:0,max:1,ticks:[0,0.25,0.5,0.75,1],fmt:v=>Math.round(v*100)+'%',label:'Probability'},slider:{min:5,max:9,value:7,label:'log₁₀ of the number of clonogens N'},
  dyn:n0=>{const n=Math.round(n0*2)/2, N=Math.pow(10,n), tcp=D=>Math.exp(-N*Math.exp(-0.3*1.2*D)), d50=Math.log(N/Math.LN2)/(0.3*1.2); return {series:[{fn:tcp,color:'var(--c1)',w:2.8},{fn:ntcp,color:'var(--c2)',w:2.8}],labels:[{x:32,y:0.9,t:'TCP',color:'var(--c1)',b:1},{x:66,y:0.82,t:'NTCP',color:'var(--c2)',b:1}],marks:[{x:60,y:tcp(60),color:'var(--c1)',label:''},{x:60,y:ntcp(60),color:'var(--c2)',label:''}],out:'N = 10<sup>'+n.toFixed(1)+'</sup>: 50% control needs <span class="f">'+d50.toFixed(0)+' Gy</span>. At 60 Gy the TCP is '+(100*tcp(60)).toFixed(0)+'% and the NTCP is '+(100*ntcp(60)).toFixed(0)+'%'};}});};

// ---------------------------------------------------------------- 3.17 to 3.19: inverse planning, IMRT and VMAT delivery, and MLC effects
AV['forward-inverse']=root=>avTimeline(root,{h:262,label:'Forward planning: the planner chooses the beams and the computer calculates the dose. Inverse planning: the planner specifies the dose and the computer finds the fluence',cap:'In forward planning the planner chooses the beam angles and MLC shapes and reviews the dose. In inverse planning the planner specifies the wanted dose, and the computer calculates the fluence and the leaf sequence. The planner still chooses the beam arrangement.',dur:6400,build:s=>{
  const wr=(t,n)=>{const w=t.split(' '),l=[]; let c=''; w.forEach(x=>{if((c+' '+x).trim().length>n){l.push(c);c=x;}else c=(c+' '+x).trim();}); l.push(c); return l;};
  const rows=[['Forward planning',['Planner chooses beam angles and MLC shapes','Computer calculates the dose','Planner reviews and adjusts'],'var(--c1)'],['Inverse planning',['Planner specifies the wanted dose','Computer optimizes the fluence','Leaf sequence, then final dose calculation'],'var(--c2)']], gs=[];
  rows.forEach(([name,boxes,col],r)=>{const y0=40+r*118, g0=sv('g',{},s); stext(g0,8,y0-12,name,{'font-weight':700,'font-size':15,fill:col}); gs.push(g0);
    boxes.forEach((txt,i)=>{const g=sv('g',{},s), x=6+i*138; sv('rect',{x:x,y:y0,width:126,height:70,rx:6,fill:'var(--paper-2)',stroke:col,'stroke-width':1.8},g); wr(txt,17).forEach((l,k)=>stext(g,x+63,y0+24+k*16,l,{'text-anchor':'middle','font-size':12.5})); if(i<2) stext(g,x+132,y0+40,'→',{'text-anchor':'middle','font-size':16,fill:'var(--mu)'}); gs.push(g);});});
  return u=>gs.forEach((g,i)=>g.style.display=u>=(i<4?i:i-0)*0.1?'':'none');}});
AV['cost-function']=root=>avChart(root,{h:262,label:'The cost of one target voxel against its dose for an intended dose of 78 Gy, with a weight set by the slider',cap:'f = w (d − 78)². The cost grows with the square of the deviation, so a shortfall of 12 Gy costs four times as much as one of 6 Gy. The weight w sets how much the structure counts in the total.',
  x:{min:66,max:90,ticks:[66,72,78,84,90],label:'Voxel dose (Gy)'},y:{min:0,max:450,ticks:[0,150,300,450],fmt:v=>String(v),label:'Cost of the voxel'},slider:{min:0.5,max:3,value:1,label:'Weight w'},
  dyn:w0=>{const w=Math.round(w0*10)/10; return {series:[{fn:d=>w*(d-78)*(d-78),color:'var(--c1)',w:2.8}],marks:[{x:72,y:w*36,color:'var(--find)',label:''},{x:66,y:w*144,color:'var(--find)',label:''}],out:'weight <span class="v">'+w.toFixed(1)+'</span>: a voxel 6 Gy below the intended dose costs <span class="f">'+(36*w).toFixed(0)+'</span>, and 12 Gy below costs '+(144*w).toFixed(0)};}});
AV['plan-tradeoff']=root=>{const oar=r=>20+12/(1+r), d95=r=>78-8*r/(1+r); return avChart(root,{h:262,label:'Organ mean dose and target D95 against the weight given to the organ',cap:'Schematic with illustrative numbers. Raising the weight of the organ term lowers the organ dose and lowers the target coverage. The optimized plan is a compromise for the weights chosen.',
  x:{min:0,max:5,ticks:[0,1,2,3,4,5],label:'Organ weight relative to the target weight'},y:{min:15,max:80,ticks:[20,40,60,80],fmt:v=>String(v),label:'Dose (Gy)'},series:[{fn:oar,color:'var(--c2)'},{fn:d95,color:'var(--c1)'}],labels:[{x:3.3,y:73,t:'target D95',color:'var(--c1)',b:1},{x:3.1,y:29,t:'organ mean dose',color:'var(--c2)',b:1}],
  fixed:[0,1,3],dyn:r0=>{const r=Math.round(r0*10)/10; return {marks:[{x:r,y:oar(r),color:'var(--c2)',label:''},{x:r,y:d95(r),color:'var(--c1)',label:''}],out:'weight ratio <span class="v">'+r.toFixed(1)+'</span>: organ mean <span class="f">'+oar(r).toFixed(1)+' Gy</span>, target D95 '+d95(r).toFixed(1)+' Gy'};}});};
AV['fluence-segments']=root=>{const SEG=[[5,40],[4,30],[3,20],[1.5,10]], F=(x,k)=>SEG.slice(0,k).reduce((a,sg)=>a+(Math.abs(x)<=sg[0]?sg[1]:0),0); return avChart(root,{h:262,label:'Fluence from step-and-shoot segments added one at a time',cap:'Each segment is an open MLC shape delivered for a set number of MU. The fluence at a point is the sum of the MU of the segments that leave the point open.',
  x:{min:0,max:6,ticks:[0,1,2,3,4,5,6],label:'Position from the center (cm)'},y:{min:0,max:110,ticks:[0,25,50,75,100],fmt:v=>String(v),label:'Fluence (MU)'},slider:{min:1,max:4,value:4,label:'Segments delivered'},
  dyn:k0=>{const k=Math.max(1,Math.min(4,Math.round(k0))); return {series:[{fn:x=>F(x,k),color:'var(--c1)',w:2.8}],out:'<span class="v">'+k+' segment'+(k>1?'s':'')+'</span>: fluence at the center '+F(0,k)+' MU, at 3.5 cm <span class="f">'+F(3.5,k)+' MU</span>'};}});};
AV['delivery-methods']=root=>avTimeline(root,{h:262,label:'Five ways of delivering a modulated fluence',cap:'Step-and-shoot turns the beam off between shapes. Dynamic MLC keeps the beam on while the leaves move. VMAT adds a rotating gantry. Tomotherapy treats one slice at a time with a binary MLC. A compensator modulates with metal thickness.',dur:6000,build:s=>{
  const R=[['Step-and-shoot','beam off while the leaves move','var(--c1)'],['Dynamic MLC','beam on, leaves slide at set speeds','var(--c2)'],['VMAT','gantry rotates as the leaves move','var(--c3)'],['Tomotherapy','binary MLC, helical, one slice at a time','var(--mu)'],['Compensator','metal thickness set by the fluence map','var(--fg)']];
  const gs=R.map(([n,d,col],i)=>{const g=sv('g',{},s), y=16+i*48; sv('rect',{x:6,y:y,width:6,height:36,fill:col},g); stext(g,22,y+15,n,{'font-weight':700,'font-size':15}); stext(g,22,y+32,d,{'font-size':13,fill:'var(--mu)'}); return g;});
  return u=>gs.forEach((g,i)=>g.style.display=u>=i*0.17?'':'none');}});
AV['beam-time']=root=>avChart(root,{h:262,label:'Beam-on time against monitor units for a dose rate set by the slider',cap:'Time = MU / dose rate. A higher dose rate makes the line less steep, so the same MU takes less time. A VMAT arc cannot be shorter than the gantry needs to turn through it.',
  x:{min:0,max:1200,ticks:[0,300,600,900,1200],fmt:v=>String(v),label:'Monitor units'},y:{min:0,max:360,ticks:[0,120,240,360],fmt:v=>String(v),label:'Beam-on time (s)'},slider:{min:200,max:1400,value:600,label:'Dose rate (MU/min)'},
  dyn:R0=>{const R=Math.round(R0/50)*50; return {series:[{fn:m=>m/R*60,color:'var(--c1)',w:2.8}],marks:[{x:600,y:600/R*60,color:'var(--find)',r:6,label:''}],out:'dose rate <span class="v">'+R+' MU/min</span>: 600 MU takes <span class="f">'+(600/R*60).toFixed(0)+' s</span>, and 1200 MU takes '+(1200/R*60).toFixed(0)+' s'};}});

AV['leakage-mu']=root=>{
  const W=420,H=230,{s,c}=avShell(root,W,H,'Leakage dose to a point under the leaves for a conventional plan and for two IMRT plans with more monitor units','Leakage dose = MU × leaf transmission (1.5% here), for an output of 1 cGy/MU. An IMRT plan with r times the MU has r times the leakage dose, so the plans with 3.5 times and 6 times the MU leak 3.5 and 6 times as much as the conventional plan. Illustrative values.');
  const upd=avBarRows(s,{rows:['Conventional, 250 MU','IMRT, 875 MU (3.5×)','IMRT, 1500 MU (6×)'],x0:170,y0:14,rh:62,w:200,max:25}); c.innerHTML='<output class="avo" aria-live="polite"></output>'; const out=c.querySelector('output'), v=[250,875,1500].map(m=>m*0.015);
  upd(v,v.map(x=>x.toFixed(2)+' cGy'),['var(--c1)','var(--c2)','var(--c2)']); out.innerHTML='Leakage = MU × 1.5%: <span class="f">'+v[0].toFixed(2)+' cGy</span> for 250 MU, '+v[1].toFixed(2)+' cGy for 875 MU (3.5×), and '+v[2].toFixed(2)+' cGy for 1500 MU (6×)';
  return {enter(){},leave(){},finish(){}};};

AV['dlg-error']=root=>avChart(root,{h:262,label:'Fractional dose error from a 0.5 mm error in the dosimetric leaf gap against the nominal gap, for a dosimetric leaf gap set by the slider',cap:'Error = δ / (g + DLG), with δ = 0.5 mm. A larger DLG makes the effective gap larger, so the same error matters less. For every DLG the error is far larger for the small gaps used in IMRT than for large ones.',
  x:{min:2,max:30,ticks:[2,5,10,20,30],fmt:v=>String(v),label:'Nominal gap (mm)'},y:{min:0,max:25,ticks:[0,5,10,15,20,25],fmt:v=>v+'%',label:'Dose error'},slider:{min:0.5,max:3,value:1.5,label:'Dosimetric leaf gap DLG (mm)'},
  dyn:D0=>{const D=Math.round(D0*10)/10, err=g=>100*0.5/(g+D); return {series:[{fn:err,color:'var(--c1)',w:2.8}],marks:[{x:5,y:err(5),color:'var(--find)',r:6,label:''},{x:20,y:err(20),color:'var(--find)',r:6,label:''}],out:'DLG = <span class="v">'+D.toFixed(1)+' mm</span>: the error is <span class="f">'+err(5).toFixed(1)+'%</span> for a 5 mm gap and '+err(20).toFixed(1)+'% for a 20 mm gap'};}});

AV['tongue-groove']=root=>{const dip=(x,n)=>100-(6/n)*Math.exp(-x*x/(2*0.6*0.6)); return avChart(root,{h:262,label:'Dose across the boundary between two adjacent leaves, with the tongue-and-groove underdose, for a number of fields',cap:'Schematic with illustrative values. For a single field the strip along the boundary can be several percent low. Delivering from several angles, with the boundaries in different places, averages the dip out.',
  x:{min:-4,max:4,ticks:[-4,-2,0,2,4],label:'Position across the leaf boundary (mm)'},y:{min:90,max:102,ticks:[90,94,98,102],fmt:v=>v+'%',label:'Relative dose'},slider:{min:1,max:8,value:1,label:'Number of fields'},
  dyn:n0=>{const n=Math.max(1,Math.round(n0)); return {series:[{fn:x=>dip(x,n),color:'var(--c1)',w:2.8}],out:'<span class="v">'+n+' field'+(n>1?'s':'')+'</span>: the dip at the boundary is <span class="f">'+(6/n).toFixed(1)+'%</span> (illustrative)'};}});};
AV['sliding-window-mu']=root=>avChart(root,{h:262,label:'Monitor units delivered at a point by a 1 cm sliding gap against the leaf speed, for a dose rate set by the slider',cap:'MU = R × g / v. A higher dose rate delivers more MU at the same leaf speed. The leaves cannot go faster than their maximum speed, about 2.5 cm/s here, so a point that needs fewer MU than R × g / v_max requires a lower dose rate.',
  x:{min:0.5,max:5,ticks:[0.5,1,2,3,4,5],fmt:v=>String(v),label:'Leaf speed (cm/s)'},y:{min:0,max:40,ticks:[0,10,20,30,40],fmt:v=>String(v),label:'MU delivered at the point'},vlines:[{x:2.5,label:'max speed',dy:20,dx:4}],slider:{min:2,max:20,value:10,label:'Dose rate R (MU/s)'},
  dyn:R0=>{const R=Math.round(R0); return {series:[{fn:v=>R/v,color:'var(--c1)',w:2.8}],marks:[{x:2.5,y:R/2.5,color:'var(--find)',r:6,label:''}],out:'R = <span class="v">'+R+' MU/s</span>: at the maximum leaf speed of 2.5 cm/s the point still receives <span class="f">'+(R/2.5).toFixed(1)+' MU</span>, so a point that needs fewer MU needs a lower dose rate'};}});

// ---------------------------------------------------------------- 4.1: radiographic image quality
AV['contrast-energy']=root=>{const EK=[30,40,50,60,80,100,150,200], EX=[4.359840,2.018920,1.175128,0.797032,0.488536,0.370920,0.267320,0.228656], lg=Math.log, expo=E=>{let i=0; while(i<EK.length-2&&E>EK[i+1]) i++; const t=lg(E/EK[i])/lg(EK[i+1]/EK[i]); return Math.exp(lg(EX[i])+t*(lg(EX[i+1])-lg(EX[i])));}, ratio=(E,t)=>Math.exp(expo(E)*t/2);
  return avChart(root,{h:262,label:'Contrast ratio between a path through bone and a path through soft tissue against photon energy, for a bone thickness set by the slider',cap:'ratio = e^((μ_bone − μ_water) t), from NIST attenuation coefficients, with the bone replacing the same thickness of water. A thicker bone gives more contrast at every energy, and the contrast falls steeply from kilovoltage to megavoltage energies, where only density matters.',
  x:{min:30,max:200,log:true,ticks:[30,50,100,200],label:'Photon energy (keV)'},y:{min:1,max:10000,log:true,ticks:[1,10,100,1000,10000],fmt:v=>String(v),label:'Contrast ratio'},slider:{min:0.5,max:4,value:2,label:'Bone thickness (cm)'},
  dyn:t0=>{const t=Math.round(t0*10)/10; return {series:[{fn:E=>ratio(E,t),color:'var(--c1)',w:2.8}],marks:[{x:50,y:ratio(50,t),color:'var(--find)',r:6,label:''}],out:'bone <span class="v">'+t.toFixed(1)+' cm</span> thick: the contrast ratio at 50 keV is <span class="f">'+ratio(50,t).toFixed(1)+'</span>, and at 30 keV it is '+ratio(30,t).toFixed(0)};}});};

AV['magnification']=root=>avChart(root,{h:262,label:'Magnification and edge blur against the distance of the object from the detector, for a source-to-detector distance of 100 cm and a source size set by the slider',cap:'The magnification m = 100 / (100 − b) does not depend on the source size. The blur of the edge, s·b/a = s × b / (100 − b), is proportional to the source size, so the slider changes the slope of the blur curve. The blur also grows as the object moves away from the detector.',
  x:{min:0,max:40,ticks:[0,10,20,30,40],label:'Object to detector distance b (cm)'},y:{min:0,max:3,ticks:[0,0.5,1,1.5,2,2.5,3],fmt:v=>String(v),label:'Magnification, or blur in mm'},slider:{min:0.3,max:2,value:1,label:'Source size s (mm)'},
  dyn:s0=>{const s=Math.round(s0*10)/10; return {series:[{fn:b=>100/(100-b),color:'var(--c1)',w:2.8},{fn:b=>s*b/(100-b),color:'var(--c2)',w:2.8}],labels:[{x:2,y:1.42,t:'magnification',color:'var(--c1)',b:1},{x:3,y:s*3/97+0.25,t:'blur (mm)',color:'var(--c2)',b:1}],marks:[{x:20,y:1.25,color:'var(--c1)',label:''},{x:20,y:s*0.25,color:'var(--c2)',label:''}],out:'source size <span class="v">'+s.toFixed(1)+' mm</span>: at b = 20 cm the magnification is 1.25 and the blur is <span class="f">'+(s*0.25).toFixed(2)+' mm</span>'};}});

AV['snr-photons']=root=>avChart(root,{h:262,label:'Signal-to-noise ratio against exposure, with an illustrative 2000 photons per pixel for each mAs',cap:'N = 2000 × mAs photons per pixel (illustrative), noise = √N, and SNR = N / √N = √N. Four times the exposure doubles the SNR.',
  x:{min:0,max:20,ticks:[0,5,10,15,20],label:'Exposure (mAs)'},y:{min:0,max:250,ticks:[0,50,100,150,200,250],fmt:v=>String(v),label:'SNR'},series:[{fn:m=>Math.sqrt(2000*m),color:'var(--c1)',w:2.8}],
  fixed:[5,20],dyn:m0=>{const m=Math.round(m0); return {marks:[{x:m,y:Math.sqrt(2000*m),color:'var(--find)',r:6,label:''}],out:'<span class="v">'+m+' mAs</span>: N = '+(2000*m)+' photons per pixel, SNR = <span class="f">'+Math.sqrt(2000*m).toFixed(0)+'</span>'};}});
AV['scatter-grid']=root=>avTimeline(root,{h:236,label:'An anti-scatter grid: a primary photon passes between the fins and a scattered photon is stopped',cap:'The fins point back toward the source. A photon travelling along a line to the source passes between them. A scattered photon travels in another direction and is stopped by a fin, so it does not add to the image.',dur:5200,build:s=>{
  const SX=210; sv('circle',{cx:SX,cy:22,r:7,fill:'var(--fg)'},s); stext(s,SX+14,26,'source',{'font-size':13,fill:'var(--mu)'});
  sv('rect',{x:70,y:70,width:280,height:60,rx:10,fill:'var(--paper-2)',stroke:'var(--rule)','stroke-width':1.5},s); stext(s,82,90,'patient',{'font-size':13,fill:'var(--mu)'});
  const G=150; for(let i=0;i<13;i++){const x=90+i*20, dx=(x-SX)/(G-22)*16; sv('line',{x1:x,y1:G,x2:x+dx,y2:G+16,stroke:'var(--fg)','stroke-width':2.2},s);}
  stext(s,356,162,'grid',{'font-size':13,fill:'var(--mu)'}); sv('rect',{x:70,y:200,width:280,height:12,fill:'var(--fg)'},s); stext(s,356,210,'detector',{'font-size':13,fill:'var(--mu)'});
  const g1=sv('g',{},s); sv('line',{x1:SX,y1:29,x2:220,y2:200,stroke:'var(--c1)','stroke-width':2.4},g1); stext(g1,228,120,'primary photon passes',{'font-size':12.5,fill:'var(--c1)','font-weight':700});
  const g2=sv('g',{},s); sv('line',{x1:SX-4,y1:29,x2:150,y2:100,stroke:'var(--c2)','stroke-width':2.4},g2); sv('line',{x1:150,y1:100,x2:189,y2:157,stroke:'var(--c2)','stroke-width':2.4,'stroke-dasharray':'5 3'},g2); stext(g2,189,163,'×',{'text-anchor':'middle','font-size':16,fill:'var(--c2)','font-weight':700}); stext(g2,70,230,'scattered photon stopped',{'font-size':12.5,fill:'var(--c2)','font-weight':700});
  return u=>{g1.style.display=u>=0.1?'':'none'; g2.style.display=u>=0.55?'':'none';};}});

// ---------------------------------------------------------------- 4.2: digital images, DICOM, and PACS
AV['bit-depth']=root=>avChart(root,{h:262,label:'Number of grayscale levels against the bit depth of an image',cap:'Levels = 2^n. One bit gives black and white, 8 bits give 256 levels, and the 16 bits that medical images often use give 65,536 levels.',
  x:{min:1,max:12,ticks:[1,2,4,6,8,10,12],label:'Bit depth (bits)'},y:{min:1,max:4096,log:true,ticks:[1,16,256,4096],fmt:v=>String(v),label:'Grayscale levels, log scale'},series:[{fn:n=>Math.pow(2,n),color:'var(--c1)',w:2.8}],
  fixed:[1,4,8,12],dyn:n0=>{const n=Math.round(n0); return {marks:[{x:n,y:Math.pow(2,n),color:'var(--find)',r:6,label:''}],out:'<span class="v">'+n+' bit'+(n>1?'s':'')+'</span>: <span class="f">'+Math.pow(2,n)+' levels</span>'+(n===16?'':'; the 16 bits of a medical image give 65,536')};}});
AV['storage-size']=root=>{
  const W=420,H=262,{s,c}=avShell(root,W,H,'Storage needed by four kinds of image, uncompressed and with lossless or lossy compression','Storage = pixels × bytes per pixel. Lossless compression saves a factor of about 2 or 3, here 2.5. Lossy compression saves a factor of 10 or more, here 10, but it cannot be reversed.');
  const R=[['CT slice, 512 × 512',512*512*2/1e6],['CT slice, 1024 × 1024',1024*1024*2/1e6],['Radiograph, 2000 × 2500',2000*2500*2/1e6],['CT study, 200 slices',200*512*512*2/1e6]], upd=avBarRows(s,{rows:R.map(r=>r[0]),x0:150,y0:14,rh:52,w:200,max:110}), {b:btns,o:out}=avBtns(c,'Storage',['Uncompressed','Lossless, ÷ 2.5','Lossy, ÷ 10']);
  const F=[1,2.5,10], show=i=>{const v=R.map(r=>r[1]/F[i]); upd(v,v.map(x=>(x<10?x.toFixed(2):x.toFixed(1))+' MB'),v.map(()=>'var(--c1)')); btns.forEach((b,k)=>b.setAttribute('aria-pressed',String(k===i))); out.innerHTML=['Uncompressed','Lossless, a factor of 2.5','Lossy, a factor of 10'][i]+': the 200-slice CT study needs <span class="f">'+v[3].toFixed(i?0:1)+' MB</span>';};
  btns.forEach((b,k)=>b.addEventListener('click',()=>show(k))); show(0); return {enter(){},leave(){},finish(){}};};
AV['informatics-map']=root=>avTimeline(root,{h:262,label:'Five terms of medical imaging informatics and what each one is',cap:'DICOM is a standard and DICOM-RT extends it to therapy. A PACS stores images and uses DICOM. The EHR holds the general record. The OIS holds the oncology record and drives the linacs.',dur:6000,build:s=>{
  const R=[['DICOM','the standard for storing and transferring images','var(--c1)'],['DICOM-RT','adds structure sets, plans, doses, and RT images','var(--c3)'],['PACS','a system that stores images, using DICOM','var(--c2)'],['EHR','general patient record: history, medications, results','var(--mu)'],['OIS','oncology record, drives the linacs: Aria, Mosaiq','var(--fg)']];
  const gs=R.map(([n,d,col],i)=>{const g=sv('g',{},s), y=16+i*48; sv('rect',{x:6,y:y,width:6,height:36,fill:col},g); stext(g,22,y+15,n,{'font-weight':700,'font-size':15}); stext(g,22,y+32,d,{'font-size':13,fill:'var(--mu)'}); return g;});
  return u=>gs.forEach((g,i)=>g.style.display=u>=i*0.17?'':'none');}});

// ---------------------------------------------------------------- 4.3 and 4.4: CT reconstruction, Hounsfield units, acquisition, image quality, and artifacts
AV['backprojection']=root=>{
  const W=420,H=250,{s,c}=avShell(root,W,H,'Backprojection from a number of angles: each profile smears the signal along the beam path, and the bands cross where the object is','Each band is one backprojected profile. One angle shows only that the object lies somewhere along a band. Where many bands cross, the signal adds up and the object appears. Real reconstruction also applies a filter to each profile first.');
  const CX=210, CY=118, bands=[]; for(let i=0;i<12;i++){const a=i*Math.PI/12, L=190; bands.push(sv('line',{x1:CX-L*Math.cos(a),y1:CY-L*Math.sin(a),x2:CX+L*Math.cos(a),y2:CY+L*Math.sin(a),stroke:'var(--c1)','stroke-width':9,'stroke-opacity':0.3,'stroke-linecap':'butt'},s));}
  sv('circle',{cx:CX,cy:CY,r:8,fill:'var(--fg)'},s);
  c.innerHTML='<label>Number of angles<input type="range" min="1" max="12" step="1" value="6"></label><output class="avo" aria-live="polite"></output>'; const rng=c.querySelector('input'), out=c.querySelector('output');
  const set=k=>{bands.forEach((b,i)=>b.style.display=i<k?'':'none'); out.innerHTML='<span class="v">'+k+' angle'+(k>1?'s':'')+'</span>: '+(k===1?'the object lies somewhere along one band':'the bands cross where the object is, and add only a faint haze elsewhere');};
  rng.addEventListener('input',()=>set(+rng.value)); set(6); return {enter(){},leave(){},finish(){}};};
AV['hu-scale']=root=>avChart(root,{h:262,label:'Hounsfield unit against the linear attenuation coefficient relative to water',cap:'HU = 1000 × (μ / μ_water − 1). Air (μ = 0) is −1000 HU, water is 0 HU, and a material with twice the attenuation of water is +1000 HU. Bone lies at about +500 to +1000 HU.',
  x:{min:0,max:2,ticks:[0,0.5,1,1.5,2],fmt:v=>String(v),label:'μ / μ of water'},y:{min:-1000,max:1000,ticks:[-1000,-500,0,500,1000],fmt:v=>(v>0?'+':'')+v,label:'Hounsfield units'},series:[{fn:r=>1000*(r-1),color:'var(--c1)',w:2.8}],
  fixed:[0,1,1.1,2],dyn:r0=>{const r=Math.round(r0*20)/20, h=Math.round(1000*(r-1)); return {marks:[{x:r,y:1000*(r-1),color:'var(--find)',r:6,label:''}],out:'μ/μ<sub>water</sub> = <span class="v">'+r.toFixed(2)+'</span>: <span class="f">'+(h>0?'+':'')+h+' HU</span>'};}});
AV['ct-density']=root=>{const P=[[-1000,0.001],[-800,0.20],[-100,0.93],[0,1.00],[100,1.07],[1000,1.60],[2000,2.20]], rho=h=>{let i=0; while(i<P.length-2&&h>P[i+1][0]) i++; const t=(h-P[i][0])/(P[i+1][0]-P[i][0]); return P[i][1]+t*(P[i+1][1]-P[i][1]);}; return avChart(root,{h:262,label:'An illustrative CT-to-density calibration: mass density against Hounsfield unit',cap:'Illustrative values only. The relationship is non-linear, and it differs between scanners and tube voltages, so each scanner needs a calibration measured with a phantom of known inserts.',
  x:{min:-1000,max:2000,ticks:[-1000,0,1000,2000],fmt:v=>String(v),label:'Hounsfield units'},y:{min:0,max:2.4,ticks:[0,0.5,1,1.5,2],fmt:v=>String(v),label:'Mass density (g/cm³)'},series:[{fn:rho,color:'var(--c1)',w:2.8}],
  fixed:[-800,0,1000],dyn:h0=>{const h=Math.round(h0/10)*10; return {marks:[{x:h,y:rho(h),color:'var(--find)',r:6,label:''}],out:'<span class="v">'+h+' HU</span>: density <span class="f">'+rho(h).toFixed(2)+' g/cm³</span> (illustrative)'};}});};
AV['pitch-time']=root=>avChart(root,{h:262,label:'Time to scan 200 mm against the pitch, for a slice thickness of 5 mm and a rotation time set by the slider',cap:'The table travels d = p × S per rotation and the time is (200 / d) × T = 40 T / p. A larger pitch covers the volume faster, and so does a faster gantry. The cost of a large pitch is a degraded slice sensitivity profile.',
  x:{min:0.75,max:2.5,ticks:[1,1.5,2,2.5],fmt:v=>String(v),label:'Pitch'},y:{min:0,max:60,ticks:[0,15,30,45,60],fmt:v=>String(v),label:'Scan time (s)'},slider:{min:0.25,max:1,value:0.5,label:'Rotation time T (s)'},
  dyn:T0=>{const T=Math.round(T0*20)/20; return {series:[{fn:p=>40*T/p,color:'var(--c1)',w:2.8}],marks:[{x:1.5,y:40*T/1.5,color:'var(--find)',r:6,label:''}],out:'rotation time <span class="v">'+T.toFixed(2)+' s</span>: at pitch 1.5 the table moves 7.5 mm per rotation, so 200 mm takes <span class="f">'+(40*T/1.5).toFixed(1)+' s</span>'};}});

AV['ct-noise']=root=>{const nz=(m,S)=>Math.sqrt(1000/(m*S)); return avChart(root,{h:262,label:'Relative CT noise against mAs for three slice thicknesses',cap:'Noise relative to 200 mAs and 5 mm slices, taken as 1: noise ∝ 1 / √(mAs × slice thickness). More mAs or thicker slices collect more photons and lower the noise. The mA does not change the spatial resolution.',
  x:{min:50,max:400,ticks:[50,100,200,300,400],fmt:v=>String(v),label:'Exposure (mAs)'},y:{min:0,max:3,ticks:[0,1,2,3],fmt:v=>String(v),label:'Relative noise'},series:[{fn:m=>nz(m,2.5),color:'var(--c2)'},{fn:m=>nz(m,5),color:'var(--c1)'},{fn:m=>nz(m,10),color:'var(--c3)'}],
  labels:[{x:260,y:1.55,t:'2.5 mm',color:'var(--c2)',b:1},{x:260,y:1.1,t:'5 mm',color:'var(--c1)',b:1},{x:260,y:0.62,t:'10 mm',color:'var(--c3)',b:1}],
  fixed:[100,300],dyn:m0=>{const m=Math.round(m0/10)*10; return {marks:[2.5,5,10].map((S,i)=>({x:m,y:nz(m,S),color:['var(--c2)','var(--c1)','var(--c3)'][i],label:''})),out:'<span class="v">'+m+' mAs</span>: relative noise '+nz(m,2.5).toFixed(2)+' for 2.5 mm slices, <span class="f">'+nz(m,5).toFixed(2)+'</span> for 5 mm, '+nz(m,10).toFixed(2)+' for 10 mm'};}});};
AV['cbct-compare']=root=>avTimeline(root,{h:250,label:'Diagnostic CT compared with cone-beam CT on a linac',cap:'A cone-beam scan covers the volume in one revolution, which suits a C-arm linac, but it takes about a minute and has more scatter. Motion degrades the image and the HU are less accurate.',dur:5600,build:s=>{
  const cols=[[10,'Diagnostic CT',['fan beam, thin slices','rotation under 1 s','little scatter','HU close to μ'],'var(--c1)'],[214,'Cone-beam CT',['large detector, cone beam','whole volume in one rotation','about 700 images, about 1 min','more scatter, HU not accurate'],'var(--c2)']];
  const gs=cols.map(([x,t,L,col])=>{const g=sv('g',{},s); sv('rect',{x:x,y:14,width:196,height:216,rx:8,fill:'none',stroke:col,'stroke-width':2},g); stext(g,x+12,42,t,{'font-weight':700,'font-size':17,fill:col}); L.forEach((l,i)=>stext(g,x+12,78+i*34,l,{'font-size':14.5})); return g;});
  return u=>gs.forEach((g,i)=>g.style.display=u>=i*0.35?'':'none');}});
AV['ct-artifacts']=root=>avTimeline(root,{h:262,label:'Four CT artifacts and the cause of each',cap:'Cupping and streaking both involve beam hardening, and cupping adds the larger scatter in the center. Motion is a patient effect, and a ring is a detector fault.',dur:6000,build:s=>{
  const R=[['Cupping','scatter and beam hardening: the center looks less dense','var(--c1)'],['Streaking','beam hardening between two dense objects: a dark streak','var(--c2)'],['Motion','anatomy moves during the scan, for example a gas bubble','var(--c3)'],['Ring','a faulty or miscalibrated detector pixel','var(--fg)']];
  const gs=R.map(([n,d,col],i)=>{const g=sv('g',{},s), y=20+i*58; sv('rect',{x:6,y:y,width:6,height:44,fill:col},g); stext(g,22,y+18,n,{'font-weight':700,'font-size':16}); stext(g,22,y+38,d,{'font-size':13,fill:'var(--mu)'}); return g;});
  return u=>gs.forEach((g,i)=>g.style.display=u>=i*0.2?'':'none');}});

// ---------------------------------------------------------------- 4.5 to 4.7: MRI physics, pulse sequences, and distortion
AV['larmor-field']=root=>avChart(root,{h:262,label:'Larmor frequency of hydrogen against the main magnetic field',cap:'f = 42.6 MHz/T × B₀. Doubling the field doubles the precession frequency. Clinical fields of 1 to 3 T give radiofrequencies of 43 to 128 MHz.',
  x:{min:0,max:3,ticks:[0,0.5,1,1.5,2,2.5,3],fmt:v=>String(v),label:'Main field B₀ (T)'},y:{min:0,max:130,ticks:[0,40,80,120],fmt:v=>String(v),label:'Larmor frequency (MHz)'},series:[{fn:b=>42.6*b,color:'var(--c1)',w:2.8}],
  fixed:[0.35,1.5,3],dyn:b0=>{const b=Math.round(b0*20)/20; return {marks:[{x:b,y:42.6*b,color:'var(--find)',r:6,label:''}],out:'B<sub>0</sub> = <span class="v">'+b.toFixed(2).replace(/0$/,'')+' T</span>: f = <span class="f">'+(42.6*b).toFixed(1)+' MHz</span>'};}});
AV['precession-coil']=root=>avTimeline(root,{h:226,label:'How the MRI signal arises: precession, an RF pulse at the Larmor frequency, and a current in the readout coil',cap:'Nuclei precess at the Larmor frequency. An RF pulse at that frequency flips the spins. The precessing moments change the flux through the coil, and Faraday\'s law gives a measurable current.',dur:5400,build:s=>{
  const R=[['1  Precession','nuclear moments precess about B₀ at f = γ̄ B₀','var(--c1)'],['2  Resonance','an RF pulse at the Larmor frequency flips the spins','var(--c2)'],['3  Signal','the changing flux induces a current in the coil','var(--c3)']];
  const gs=R.map(([n,d,col],i)=>{const g=sv('g',{},s), y=18+i*62; sv('rect',{x:6,y:y,width:6,height:46,fill:col},g); stext(g,22,y+19,n,{'font-weight':700,'font-size':16}); stext(g,22,y+39,d,{'font-size':13.5,fill:'var(--mu)'}); return g;});
  return u=>gs.forEach((g,i)=>g.style.display=u>=i*0.3?'':'none');}});
AV['gradient-slice']=root=>avChart(root,{h:262,label:'Larmor frequency along the patient for a gradient strength set by the slider',cap:'f = 42.6 × (1 + G z) MHz, with z positive toward the inferior end. A stronger gradient makes the frequency change faster with position, so the same RF bandwidth excites a thinner slice: thickness = bandwidth / (42.58 MHz/T × G).',
  x:{min:-25,max:25,ticks:[-25,-10,0,10,25],fmt:v=>String(v),label:'Position along the patient (cm), inferior positive'},y:{min:42.3,max:42.9,ticks:[42.4,42.6,42.8],fmt:v=>v.toFixed(1),label:'Larmor frequency (MHz)'},slider:{min:1,max:20,value:6,label:'Gradient strength G (mT/m)'},
  dyn:G0=>{const G=Math.round(G0*2)/2, f=z=>42.6*(1+G*1e-3*z/100), kHz=0.426*G, th=10/kHz; return {series:[{fn:f,color:'var(--c1)',w:2.8}],marks:[{x:10,y:f(10),color:'var(--find)',r:6,label:''}],out:'G = <span class="v">'+G.toFixed(1)+' mT/m</span>: the frequency changes by <span class="f">'+kHz.toFixed(1)+' kHz per cm</span>, so an RF bandwidth of 1 kHz excites a slice <span class="f">'+th.toFixed(1)+' mm</span> thick'};}});

AV['mz-recovery']=root=>{const mz=(t,t1)=>1-Math.exp(-t/t1); return avChart(root,{h:262,label:'Recovery of the longitudinal magnetization after a 90° pulse for fat and for cerebrospinal fluid',cap:'M_z / M_0 = 1 − e^(−t/T1), with illustrative T1 = 250 ms for fat and 3000 ms for CSF. At a short TR the two differ a great deal, which is T1 weighting. At a long TR both have recovered.',
  x:{min:0,max:4500,ticks:[0,1000,2000,3000,4000],fmt:v=>String(v),label:'Time after the pulse, TR (ms)'},y:{min:0,max:1.05,ticks:[0,0.25,0.5,0.75,1],fmt:v=>String(v),label:'M_z / M_0'},series:[{fn:t=>mz(t,250),color:'var(--c2)',w:2.8},{fn:t=>mz(t,3000),color:'var(--c1)',w:2.8}],
  labels:[{x:1700,y:0.86,t:'fat',color:'var(--c2)',b:1},{x:3300,y:0.5,t:'CSF',color:'var(--c1)',b:1}],fixed:[500,4000],dyn:t0=>{const t=Math.round(t0/50)*50; return {marks:[{x:t,y:mz(t,250),color:'var(--c2)',label:''},{x:t,y:mz(t,3000),color:'var(--c1)',label:''}],out:'TR <span class="v">'+t+' ms</span>: M<sub>z</sub>/M<sub>0</sub> = <span class="f">'+mz(t,250).toFixed(2)+'</span> for fat and '+mz(t,3000).toFixed(2)+' for CSF'};}});};
AV['te-decay']=root=>{const mx=(t,t2)=>Math.exp(-t/t2); return avChart(root,{h:262,label:'Decay of the transverse magnetization for brain and for cerebrospinal fluid',cap:'M_xy / M_0 = e^(−TE/T2), with illustrative T2 = 90 ms for brain and 2000 ms for CSF. The difference grows with TE, so a long TE gives T2 weighting, with CSF bright.',
  x:{min:0,max:300,ticks:[0,50,100,150,200,250,300],fmt:v=>String(v),label:'Echo time TE (ms)'},y:{min:0,max:1.05,ticks:[0,0.25,0.5,0.75,1],fmt:v=>String(v),label:'M_xy / M_0'},series:[{fn:t=>mx(t,90),color:'var(--c2)',w:2.8},{fn:t=>mx(t,2000),color:'var(--c1)',w:2.8}],
  labels:[{x:150,y:0.17,t:'brain',color:'var(--c2)',b:1},{x:150,y:0.93,t:'CSF',color:'var(--c1)',b:1}],fixed:[15,100],dyn:t0=>{const t=Math.round(t0/5)*5; return {marks:[{x:t,y:mx(t,90),color:'var(--c2)',label:''},{x:t,y:mx(t,2000),color:'var(--c1)',label:''}],out:'TE <span class="v">'+t+' ms</span>: M<sub>xy</sub>/M<sub>0</sub> = <span class="f">'+mx(t,90).toFixed(2)+'</span> for brain and '+mx(t,2000).toFixed(2)+' for CSF'};}});};
AV['inversion-recovery']=root=>avChart(root,{h:262,label:'Recovery of the longitudinal magnetization after a 180° inversion pulse, for a T1 set by the slider',cap:'M_z / M_0 = 1 − 2 e^(−t/T1). The magnetization passes through zero at t = T1 ln 2, so the inversion time that nulls a tissue is set by its T1: a longer T1 needs a longer inversion time.',
  x:{min:0,max:6000,ticks:[0,1000,2000,3000,4000,5000,6000],fmt:v=>String(v),label:'Time after the inversion pulse (ms)'},y:{min:-1,max:1,ticks:[-1,-0.5,0,0.5,1],fmt:v=>String(v),label:'M_z / M_0'},slider:{min:200,max:4000,value:3000,label:'T1 (ms)'},
  dyn:T0=>{const T=Math.round(T0/50)*50, tn=T*Math.LN2; return {series:[{fn:t=>1-2*Math.exp(-t/T),color:'var(--c1)',w:2.8}],vlines:[{x:tn,label:'null',dy:20,dx:4}],marks:[{x:tn,y:0,color:'var(--find)',r:6,label:''}],out:'T1 = <span class="v">'+T+' ms</span>: M<sub>z</sub> is zero at <span class="f">'+tn.toFixed(0)+' ms</span> = T1 ln 2, so starting the sequence then nulls this tissue'};}});

AV['field-shift']=root=>avChart(root,{h:262,label:'Apparent shift of a pixel against the local field error, for a gradient strength set by the slider',cap:'Shift = ΔB / G. The same field error moves the pixel farther when the gradient is weaker, so the slope of the line falls as the gradient rises. Illustrative gradients of 2 to 30 mT/m.',
  x:{min:0,max:0.1,ticks:[0,0.025,0.05,0.075,0.1],fmt:v=>String(v),label:'Local field error ΔB (mT)'},y:{min:0,max:50,ticks:[0,10,20,30,40,50],fmt:v=>String(v),label:'Shift (mm)'},slider:{min:2,max:30,value:10,label:'Gradient strength G (mT/m)'},
  dyn:G0=>{const G=Math.round(G0); return {series:[{fn:b=>b/G*1000,color:'var(--c1)',w:2.8}],marks:[{x:0.05,y:0.05/G*1000,color:'var(--find)',r:6,label:''}],out:'G = <span class="v">'+G+' mT/m</span>: a field error of 0.05 mT moves the pixel by <span class="f">'+(0.05/G*1000).toFixed(1)+' mm</span>'};}});

AV['mri-artifact-list']=root=>avTimeline(root,{h:262,label:'Four MRI distortions and artifacts and the cause of each',cap:'Each one moves signal to the wrong place or removes it. Geometric accuracy matters in radiation oncology, so distortion is measured with a grid phantom.',dur:6000,build:s=>{
  const R=[['Susceptibility','metal distorts the local field: a signal void','var(--c1)'],['Gradient distortion','gradient larger than the system assumes: image stretched','var(--c2)'],['Chemical shift','different chemical environments: signal shifted','var(--c3)'],['B₀ inhomogeneity','field bows out at the bore edge: grid bent','var(--fg)']];
  const gs=R.map(([n,d,col],i)=>{const g=sv('g',{},s), y=20+i*58; sv('rect',{x:6,y:y,width:6,height:44,fill:col},g); stext(g,22,y+18,n,{'font-weight':700,'font-size':16}); stext(g,22,y+38,d,{'font-size':13,fill:'var(--mu)'}); return g;});
  return u=>gs.forEach((g,i)=>g.style.display=u>=i*0.2?'':'none');}});

// ---------------------------------------------------------------- 4.8 and 4.9: radioisotopes, SPECT, and PET
AV['production-route']=root=>avTimeline(root,{h:200,label:'Three ways of producing the isotopes of nuclear medicine imaging',cap:'Neutron-rich isotopes come from reactors and decay by beta-minus with long half-lives. Proton-rich isotopes come from cyclotrons and decay by beta-plus or electron capture with shorter half-lives. Tc-99m comes from a generator.',dur:4800,build:s=>{
  const R=[['Reactor','neutron-rich, beta-minus, long half-life: I-131, Xe-133','var(--c1)'],['Cyclotron','proton-rich, beta-plus or electron capture: F-18, I-123, In-111','var(--c2)'],['Generator','Mo-99 decays to Tc-99m, which is milked on site','var(--c3)']];
  const gs=R.map(([n,d,col],i)=>{const g=sv('g',{},s), y=14+i*62; sv('rect',{x:6,y:y,width:6,height:46,fill:col},g); stext(g,22,y+19,n,{'font-weight':700,'font-size':16}); stext(g,22,y+39,d,{'font-size':13,fill:'var(--mu)'}); return g;});
  return u=>gs.forEach((g,i)=>g.style.display=u>=i*0.3?'':'none');}});
AV['gamma-camera']=root=>avTimeline(root,{h:262,label:'The path from a decay in the patient to a SPECT image',cap:'The collimator gives the direction, the scintillator converts the photon to light, and the photomultiplier tubes give the position. The head rotates around the patient and the projections are reconstructed.',dur:6000,build:s=>{
  const R=[['1  Emission','the radiopharmaceutical decays and emits single photons','var(--c1)'],['2  Collimator','only photons travelling in the allowed direction pass','var(--c2)'],['3  Scintillator','the photon is converted to light','var(--c3)'],['4  Photomultiplier tubes','the light is registered, with its position','var(--mu)'],['5  Rotation','the head rotates and the projections are reconstructed','var(--fg)']];
  const gs=R.map(([n,d,col],i)=>{const g=sv('g',{},s), y=8+i*50; sv('rect',{x:6,y:y,width:6,height:38,fill:col},g); stext(g,22,y+16,n,{'font-weight':700,'font-size':15}); stext(g,22,y+33,d,{'font-size':13,fill:'var(--mu)'}); return g;});
  return u=>gs.forEach((g,i)=>g.style.display=u>=i*0.18?'':'none');}});
AV['activity-remaining']=root=>{const T={'Ga-68':67.6/60,'F-18':109.8/60,'Tc-99m':6.0,'I-123':13.2}, f=(t,h)=>100*Math.pow(0.5,t/h), cols=['var(--c2)','var(--c1)','var(--c3)','var(--fg)'];
  return avChart(root,{h:262,label:'Percentage of the activity remaining against the time after preparation for four imaging isotopes',cap:'Fraction remaining = 2^(−t/T½). A short half-life is lost quickly: after 6 h only 10% of the F-18 and 2% of the Ga-68 remain, but half of the Tc-99m and 73% of the I-123.',
  x:{min:0,max:24,ticks:[0,6,12,18,24],fmt:v=>String(v),label:'Time after preparation (h)'},y:{min:0,max:100,ticks:[0,25,50,75,100],fmt:v=>v+'%',label:'Activity remaining'},series:Object.keys(T).map((k,i)=>({fn:t=>f(t,T[k]),color:cols[i],w:2.6})),
  labels:[{x:14,y:93,t:'I-123, 13.2 h',color:cols[3],b:1},{x:14,y:83,t:'Tc-99m, 6.0 h',color:cols[2],b:1},{x:14,y:73,t:'F-18, 110 min',color:cols[1],b:1},{x:14,y:63,t:'Ga-68, 68 min',color:cols[0],b:1}],fixed:[6],
  dyn:t=>({marks:Object.keys(T).map((k,i)=>({x:t,y:f(t,T[k]),color:cols[i],label:''})),out:'<span class="v">'+t+' h</span> after preparation: Tc-99m <span class="f">'+f(t,6).toFixed(0)+'%</span>, F-18 '+f(t,T['F-18']).toFixed(0)+'%, I-123 '+f(t,13.2).toFixed(0)+'%, Ga-68 '+f(t,T['Ga-68']).toFixed(0)+'%'})});};

AV['lor-events']=root=>{
  const W=420,H=262,{s,c}=avShell(root,W,H,'Lines of response from annihilation events in a detector ring: the lines cross at the position of the source','Each coincident pair of 511 keV photons defines one line of response through the annihilation point. One line leaves the position along it unknown. Where many lines cross, the source is found by tomographic reconstruction.');
  const CX=210, CY=118, R=104, S=[228,106]; sv('circle',{cx:CX,cy:CY,r:R,fill:'none',stroke:'var(--rule)','stroke-width':1.5},s);
  for(let i=0;i<48;i++){const a=i*Math.PI/24; sv('rect',{x:CX+(R+5)*Math.cos(a)-4,y:CY+(R+5)*Math.sin(a)-4,width:8,height:8,rx:1.5,fill:'var(--mu)',transform:'rotate('+(a*180/Math.PI)+' '+(CX+(R+5)*Math.cos(a))+' '+(CY+(R+5)*Math.sin(a))+')'},s);}
  const lines=[]; for(let k=0;k<12;k++){const th=k*Math.PI/12+0.2, dx=Math.cos(th), dy=Math.sin(th), px=S[0]-CX, py=S[1]-CY, b=px*dx+py*dy, cc=px*px+py*py-R*R, q=Math.sqrt(b*b-cc), t1=-b+q, t2=-b-q;
    lines.push(sv('line',{x1:S[0]+t1*dx,y1:S[1]+t1*dy,x2:S[0]+t2*dx,y2:S[1]+t2*dy,stroke:'var(--c1)','stroke-width':1.6,'stroke-opacity':0.6},s));}
  sv('circle',{cx:S[0],cy:S[1],r:5,fill:'var(--find)'},s);
  c.innerHTML='<label>Number of events<input type="range" min="1" max="12" step="1" value="6"></label><output class="avo" aria-live="polite"></output>'; const rng=c.querySelector('input'), out=c.querySelector('output');
  const set=k=>{lines.forEach((l,i)=>l.style.display=i<k?'':'none'); out.innerHTML='<span class="v">'+k+' event'+(k>1?'s':'')+'</span>: '+(k===1?'the annihilation lies somewhere along one line':'the lines cross at the source'); };
  rng.addEventListener('input',()=>set(+rng.value)); set(6); return {enter(){},leave(){},finish(){}};};
AV['suv-calc']=root=>avChart(root,{h:262,label:'Standardized uptake value against the activity concentration, for 370 MBq injected and a body weight set by the slider',cap:'SUV = concentration / (injected activity per gram of body weight). With 370 MBq injected, the activity per gram is 370,000 kBq divided by the weight in grams, so a heavier patient has less activity per gram and a higher SUV for the same concentration.',
  x:{min:0,max:50,ticks:[0,10,20,30,40,50],fmt:v=>String(v),label:'Activity concentration (kBq/mL)'},y:{min:0,max:18,ticks:[0,6,12,18],fmt:v=>String(v),label:'SUV'},slider:{min:40,max:120,value:74,label:'Body weight (kg)'},
  dyn:W0=>{const kg=Math.round(W0), per=370000/(kg*1000); return {series:[{fn:c=>c/per,color:'var(--c1)',w:2.8}],marks:[{x:20,y:20/per,color:'var(--find)',r:6,label:''}],out:'weight <span class="v">'+kg+' kg</span>: the injected activity per gram is '+per.toFixed(2)+' kBq/g, so a concentration of 20 kBq/mL gives an SUV of <span class="f">'+(20/per).toFixed(1)+'</span>'};}});

AV['pet-attenuation']=root=>{const MU=0.0960; return avChart(root,{h:262,label:'Attenuation correction factor of a line of response against the path length, for an absorber of the density set by the slider',cap:'Both photons escape with probability e^(−μL), whatever the position of the annihilation along the line, and the correction factor is e^(μL). At 511 keV μ is nearly proportional to the density, so the curve is steeper for denser tissue: lung, about 0.25 g/cm³, attenuates far less than soft tissue at 1.0 or bone at about 1.9.',
  x:{min:0,max:30,ticks:[0,10,20,30],fmt:v=>String(v),label:'Path length L (cm)'},y:{min:0,max:20,ticks:[0,5,10,15,20],fmt:v=>String(v),label:'Correction factor'},slider:{min:0.2,max:2,value:1,label:'Density (g/cm³): lung 0.25, soft tissue 1.0, bone 1.9'},
  dyn:r0=>{const r=Math.round(r0*20)/20, mu=MU*r; return {series:[{fn:L=>Math.exp(mu*L),color:'var(--c1)',w:2.8}],marks:[{x:15,y:Math.exp(mu*15),color:'var(--find)',r:6,label:''}],out:'density <span class="v">'+r.toFixed(2)+' g/cm³</span> (μ = '+mu.toFixed(3)+' per cm): through 15 cm both photons escape in <span class="f">'+(100*Math.exp(-mu*15)).toFixed(1)+'%</span>, so the correction factor is '+Math.exp(mu*15).toFixed(1)};}});};

AV['tracer-map']=root=>avTimeline(root,{h:262,label:'Five PET tracers, the process each follows, and a typical use',cap:'FDG is the most widely used. The others probe perfusion, bone metabolism, receptors, or hypoxia.',dur:6000,build:s=>{
  const R=[['F-18 FDG','glucose metabolism: oncology, neurology, cardiology','var(--c1)'],['F-18 fluoride','bone metabolism: oncology','var(--c2)'],['F-18 FMISO','hypoxia: the response to radiotherapy','var(--c3)'],['N-13 ammonia','blood perfusion: the myocardium','var(--mu)'],['O-15 water','blood perfusion: brain activation studies','var(--fg)']];
  const gs=R.map(([n,d,col],i)=>{const g=sv('g',{},s), y=12+i*50; sv('rect',{x:6,y:y,width:6,height:38,fill:col},g); stext(g,22,y+16,n,{'font-weight':700,'font-size':15.5}); stext(g,22,y+33,d,{'font-size':13,fill:'var(--mu)'}); return g;});
  return u=>gs.forEach((g,i)=>g.style.display=u>=i*0.18?'':'none');}});

// ---------------------------------------------------------------- a real clinical plan: CT, contours, isodose lines, and DVH (OpenKBP patient 14)
let caseP=null;
function caseLoad(){ if(caseP) return caseP; const C=DATA.case, ld=src=>new Promise(r=>{const im=new Image(); im.onload=()=>r(im); im.src=src;});
  caseP=Promise.all([ld(C.ct),ld(C.dose)]).then(([a,b])=>{const mk=im=>{const cv=document.createElement('canvas'); cv.width=im.width; cv.height=im.height; const g=cv.getContext('2d',{willReadFrequently:true}); g.drawImage(im,0,0); return {cv,g};};
    const A=mk(a), B=mk(b); C._ct=A.cv; C._dose=B.g.getImageData(0,0,b.width,b.height).data; C._dw=b.width; return C;}); return caseP;}
const caseDose=(C,k,r,c)=>C._dose[((Math.floor(k/C.cols)*C.h+r)*C._dw+(k%C.cols)*C.w+c)*4]*C.level;
const caseImg=(C,k)=>{C._im=C._im||{}; if(!C._im[k]){const cv=document.createElement('canvas'); cv.width=C.w; cv.height=C.h; cv.getContext('2d').drawImage(C._ct,(k%C.cols)*C.w,Math.floor(k/C.cols)*C.h,C.w,C.h,0,0,C.w,C.h); C._im[k]=cv.toDataURL('image/png');} return C._im[k];};
const caseWash=(C,k)=>{C._wa=C._wa||{}; if(!C._wa[k]){const cv=document.createElement('canvas'); cv.width=C.w; cv.height=C.h; const g=cv.getContext('2d'), id=g.createImageData(C.w,C.h), stops=[[0,[40,70,255]],[0.33,[0,200,220]],[0.55,[80,220,80]],[0.78,[255,220,0]],[1,[255,40,40]]];
    for(let r=0;r<C.h;r++)for(let c=0;c<C.w;c++){const d=caseDose(C,k,r,c), o=(r*C.w+c)*4; if(d<10){id.data[o+3]=0; continue;} const t=Math.min(1,(d-10)/64); let i=0; while(i<stops.length-2&&t>stops[i+1][0]) i++; const f=(t-stops[i][0])/(stops[i+1][0]-stops[i][0]); for(let q=0;q<3;q++) id.data[o+q]=Math.round(stops[i][1][q]+f*(stops[i+1][1][q]-stops[i][1][q])); id.data[o+3]=130;}
    g.putImageData(id,0,0); C._wa[k]=cv.toDataURL('image/png');} return C._wa[k];};
function caseIso(C,k,L){let d=''; const w=C.w,h=C.h, v=(r,c)=>caseDose(C,k,r,c), pt=(pa,pb,ax,ay,bx,by)=>{const t=(L-pa)/(pb-pa); return [ax+(bx-ax)*t, ay+(by-ay)*t];};
  for(let r=0;r<h-1;r++)for(let c=0;c<w-1;c++){const a=v(r,c), b=v(r,c+1), e=v(r+1,c+1), f=v(r+1,c), idx=(a>=L?8:0)|(b>=L?4:0)|(e>=L?2:0)|(f>=L?1:0); if(idx===0||idx===15) continue;
    const top=()=>pt(a,b,c,r,c+1,r), right=()=>pt(b,e,c+1,r,c+1,r+1), bottom=()=>pt(f,e,c,r+1,c+1,r+1), left=()=>pt(a,f,c,r,c,r+1), seg=(p,q)=>{d+='M'+p[0].toFixed(2)+' '+p[1].toFixed(2)+'L'+q[0].toFixed(2)+' '+q[1].toFixed(2);}, m=(a+b+e+f)/4;
    switch(idx){case 1:case 14:seg(left(),bottom());break; case 2:case 13:seg(bottom(),right());break; case 3:case 12:seg(left(),right());break; case 4:case 11:seg(top(),right());break; case 6:case 9:seg(top(),bottom());break; case 7:case 8:seg(left(),top());break;
      case 5: if(m>=L){seg(left(),top());seg(bottom(),right());}else{seg(left(),bottom());seg(top(),right());} break; case 10: if(m>=L){seg(top(),right());seg(left(),bottom());}else{seg(left(),top());seg(bottom(),right());} break;}}
  return d;}
const caseArea=(C,k,L)=>{let n=0; for(let r=0;r<C.h;r++)for(let c=0;c<C.w;c++) if(caseDose(C,k,r,c)>=L) n++; return n*C.dx*C.dx/100;};                      // cm2 on one slice
const caseSt=n=>DATA.case.structures.find(s=>s.name===n);
const caseMid=()=>{const p=caseSt('PTV70'), ks=Object.keys(p.contours).map(Number); return Math.round((Math.min(...ks)+Math.max(...ks))/2);};
const casePoly=(poly)=>{let d=''; for(let i=0;i<poly.length;i+=2) d+=(i?'L':'M')+poly[i]+' '+poly[i+1]; return d+'Z';};
function caseSlicer(root,label,cap,mode){
  const C=DATA.case, W=420, S=W/C.w, IH=S*C.h, {s,c}=avShell(root,W,Math.round(IH)+6,label,cap), kmid=caseMid();
  const im=sv('image',{x:0,y:0,width:W,height:IH,preserveAspectRatio:'none'},s), wash=sv('image',{x:0,y:0,width:W,height:IH,preserveAspectRatio:'none',opacity:0},s), g=sv('g',{transform:`translate(${S/2} ${S/2}) scale(${S})`},s);
  const NS={'vector-effect':'non-scaling-stroke',fill:'none','stroke-linejoin':'round'}, tx=stext(s,8,IH-8,'',{'font-size':13,fill:'#fff','paint-order':'stroke',stroke:'rgba(0,0,0,.7)','stroke-width':3});
  const names=C.structures.map(x=>x.name), isos=[[70,'70 Gy','#ff3b3b'],[66.5,'66.5 Gy','#ff9f1c'],[63,'63 Gy','#ffd60a'],[56,'56 Gy','#7bd957'],[35,'35 Gy','#2ec4b6'],[20,'20 Gy','#4da3ff']];
  const labels=mode==='volumes'?names:isos.map(x=>x[1]).concat(['Colour wash']), on=mode==='volumes'?names.map(()=>true):[false,true,false,true,true,false,false], {b:btns,o:out}=avBtns(c,mode==='volumes'?'Structures':'Isodose lines (66.5 Gy is 95% of 70 Gy)',labels);
  btns.forEach((e,i)=>{e.setAttribute('aria-pressed',String(!!on[i])); if(mode==='volumes') e.style.borderLeft='7px solid '+C.structures[i].color; else if(i<isos.length) e.style.borderLeft='7px solid '+isos[i][2];});
  const lab=document.createElement('label'); lab.innerHTML='Slice<input type="range" min="0" max="'+(C.nz-1)+'" step="1" value="'+kmid+'">'; c.insertBefore(lab,out); const rng=lab.querySelector('input'); let ready=false;
  const draw=()=>{ if(!ready) return; const k=+rng.value; im.setAttribute('href',caseImg(C,k)); g.innerHTML=''; const zmm=Math.round((k-kmid)*C.dz), zt=(zmm>0?'+':'')+zmm+' mm from the middle of PTV70', here=[];
    if(mode==='volumes'){ C.structures.forEach((st,i)=>{const polys=st.contours[String(k)]; if(!polys) return; here.push(st.name); if(btns[i].getAttribute('aria-pressed')==='true') polys.forEach(p=>sv('path',Object.assign({d:casePoly(p),stroke:st.color,'stroke-width':2},NS),g));});
      tx.textContent='slice '+k+', '+zt; out.innerHTML='<span class="v">slice '+k+'</span> ('+zt+'). Structures contoured on this slice: <span class="f">'+(here.length?here.join(', '):'none')+'</span>';}
    else{ const wsh=btns[isos.length].getAttribute('aria-pressed')==='true'; wash.setAttribute('href',wsh?caseWash(C,k):''); wash.setAttribute('opacity',wsh?1:0);
      ['PTV70','SpinalCord'].forEach(n=>{const st=caseSt(n), polys=st.contours[String(k)]; if(polys) polys.forEach(p=>sv('path',Object.assign({d:casePoly(p),stroke:st.color,'stroke-width':1.6,'stroke-dasharray':'4 3'},NS),g));});
      const parts=[]; isos.forEach(([L,nm,col],i)=>{ if(btns[i].getAttribute('aria-pressed')!=='true') return; sv('path',Object.assign({d:caseIso(C,k,L),stroke:col,'stroke-width':2},NS),g); parts.push(nm+': '+caseArea(C,k,L).toFixed(1)+' cm²');});
      tx.textContent='slice '+k+', '+zt; out.innerHTML='<span class="v">slice '+k+'</span> ('+zt+'). Area enclosed on this slice: <span class="f">'+(parts.length?parts.join(', '):'no isodose line selected')+'</span>. Dashed lines: PTV70 and spinal cord.';}};
  btns.forEach((e,i)=>e.addEventListener('click',()=>{e.setAttribute('aria-pressed',String(e.getAttribute('aria-pressed')!=='true')); draw();})); rng.addEventListener('input',draw);
  caseLoad().then(()=>{ready=true; draw();}); return {enter(){},leave(){},finish(){}};}
AV['case-volumes']=root=>caseSlicer(root,'Axial CT slices of a head-and-neck patient with the planning target volumes and organs at risk contoured','Real head-and-neck IMRT plan from the OpenKBP dataset, patient 14: the CT, the planning target volumes at 70, 63, and 56 Gy, and the organs at risk. The voxels are 3.9 × 3.9 × 3 mm. Data: Babier et al., Med Phys 2021.','volumes');
AV['case-dose']=root=>caseSlicer(root,'Axial CT slices of a head-and-neck patient with the isodose lines of the delivered IMRT dose','The delivered dose of the same plan. The 66.5 Gy line, 95% of the prescription, wraps the PTV70, and the dose falls steeply toward the spinal cord. The colour wash runs from blue, about 10 Gy, to red, about 74 Gy. Data: Babier et al., Med Phys 2021.','dose');
AV['case-dvh']=root=>{
  const C=DATA.case, W=420, H=340, {s,c}=avShell(root,W,H,'Cumulative dose-volume histograms of the target volumes and organs at risk of the real IMRT plan','Cumulative DVHs computed from the delivered dose of the same plan. D is the dose received by at least a given volume, read at 95%, 50%, and 2%. V is the volume receiving at least a given dose, read at 66.5 Gy, which is 95% of the 70 Gy prescription. Data: Babier et al., Med Phys 2021.');
  const X0=46, X1=408, Y0=26, Y1=262, px=d=>X0+(X1-X0)*d/80, py=v=>Y1-(Y1-Y0)*v/100, st=C.structures, step=C.dvhStep;
  [0,25,50,75,100].forEach(v=>{sv('line',{x1:X0,y1:py(v),x2:X1,y2:py(v),stroke:'var(--gr)','stroke-width':1},s); stext(s,X0-6,py(v)+4,String(v),{'text-anchor':'end','font-size':12,fill:'var(--mu)'});});
  [0,20,40,60,80].forEach(d=>{sv('line',{x1:px(d),y1:Y0,x2:px(d),y2:Y1,stroke:'var(--gr)','stroke-width':1},s); stext(s,px(d),Y1+16,String(d),{'text-anchor':'middle','font-size':12,fill:'var(--mu)'});});
  sv('line',{x1:X0,y1:Y1,x2:X1,y2:Y1,stroke:'var(--fg)','stroke-width':1.5},s); sv('line',{x1:X0,y1:Y0,x2:X0,y2:Y1,stroke:'var(--fg)','stroke-width':1.5},s); stext(s,(X0+X1)/2,Y1+34,'Dose (Gy)',{'text-anchor':'middle','font-size':13}); stext(s,X0,Y0-12,'Volume (%)',{'font-size':13,fill:'var(--mu)'});
  const curves=st.map(x=>sv('path',{d:'M'+x.dvh.map((v,i)=>px(i*step).toFixed(1)+' '+py(v).toFixed(1)).join('L'),fill:'none',stroke:x.color,'stroke-width':1.8,'stroke-linejoin':'round'},s));
  const {b:btns,o:out}=avBtns(c,'Structure',st.map(x=>x.name)); btns.forEach((e,i)=>e.style.borderLeft='7px solid '+st[i].color); let sel=0;
  const Vat=(x,d)=>{const f=d/step, i=Math.min(x.dvh.length-2,Math.floor(f)); return x.dvh[i]+(x.dvh[i+1]-x.dvh[i])*(f-i);};
  const Dat=(x,v)=>{const a=x.dvh; if(v>=a[0]) return 0; for(let i=1;i<a.length;i++) if(a[i]<=v){return ((i-1)+(a[i-1]-v)/(a[i-1]-a[i]))*step;} return 80;};
  const vl=sv('line',{x1:px(66.5),x2:px(66.5),y1:Y0,y2:Y1,stroke:'var(--fg)','stroke-width':1,'stroke-dasharray':'4 3'},s); stext(s,px(66.5)-4,Y0+12,'66.5 Gy',{'text-anchor':'end','font-size':12,fill:'var(--mu)'}); const dots=[0,1,2,3].map(()=>sv('circle',{r:5,fill:'var(--find)'},s));
  const draw=()=>{const x=st[sel], V=Vat(x,66.5), D=[95,50,2].map(v=>Dat(x,v));
    btns.forEach((e,i)=>e.setAttribute('aria-pressed',String(i===sel))); curves.forEach((p,i)=>{p.setAttribute('stroke-width',i===sel?3.6:1.4); p.setAttribute('opacity',i===sel?1:0.55);});
    dots[0].setAttribute('cx',px(66.5)); dots[0].setAttribute('cy',py(V)); [95,50,2].forEach((v,i)=>{dots[i+1].setAttribute('cx',px(D[i])); dots[i+1].setAttribute('cy',py(v));});
    out.innerHTML='<span class="v">'+x.name+'</span> ('+x.stats.volume.toFixed(0)+' cm³): D<sub>95%</sub> = <span class="f">'+D[0].toFixed(1)+' Gy</span>, D<sub>50%</sub> = '+D[1].toFixed(1)+' Gy, D<sub>2%</sub> = '+D[2].toFixed(1)+' Gy; V<sub>66.5 Gy</sub> = <span class="f">'+V.toFixed(1)+'%</span>; mean dose '+x.stats.mean.toFixed(1)+' Gy, maximum '+x.stats.max.toFixed(1)+' Gy';};
  btns.forEach((e,i)=>e.addEventListener('click',()=>{sel=i; draw();})); draw(); return {enter(){},leave(){},finish(){}};};

// ---------------------------------------------------------------- simulated CT effects on a real slice: the reference beside the image with the effect
function galView(root,ids,label,cap,G0){
  const G=G0||DATA.gal, items=ids.map(i=>G.items.find(x=>x.id===i)), W=420, wide=!!(G.stats&&G.stats.W&&G.stats.H&&G.stats.W/G.stats.H>1.4);
  if(wide){const PW=W-8, PH=Math.round(PW*G.stats.H/G.stats.W), {s,c}=avShell(root,W,2*PH+52,label,cap);
    stext(s,W/2,15,'Reference, no effect',{'text-anchor':'middle','font-size':13,fill:'var(--mu)'}); const a=sv('image',{x:4,y:22,width:PW,height:PH,preserveAspectRatio:'xMidYMid meet'},s); const rt=stext(s,W/2,PH+42,'',{'text-anchor':'middle','font-size':13,'font-weight':700}), b=sv('image',{x:4,y:PH+48,width:PW,height:PH,preserveAspectRatio:'xMidYMid meet'},s);
    return galWire(c,items,a,b,rt);}
  const P=204, {s,c}=avShell(root,W,P+34,label,cap);
  stext(s,P/2+4,16,'Reference, no artifact',{'text-anchor':'middle','font-size':13,fill:'var(--mu)'}); const rt=stext(s,W-P/2-4,16,'',{'text-anchor':'middle','font-size':13,'font-weight':700});
  const a=sv('image',{x:4,y:24,width:P,height:P,preserveAspectRatio:'xMidYMid meet'},s), b=sv('image',{x:W-P-4,y:24,width:P,height:P,preserveAspectRatio:'xMidYMid meet'},s);
  return galWire(c,items,a,b,rt);}
function galWire(c,items,a,b,rt){
  const {b:btns,o:out}=avBtns(c,'Effect',items.map(x=>x.label));
  const show=i=>{const it=items[i]; a.setAttribute('href',it.ref); b.setAttribute('href',it.img); rt.textContent=it.label; btns.forEach((e,k)=>e.setAttribute('aria-pressed',String(k===i))); out.innerHTML='<span class="v">'+it.label+'</span>: '+it.cap+' <span class="f">'+it.facts+'</span>';};
  btns.forEach((e,i)=>e.addEventListener('click',()=>show(i))); show(0); return {enter(){},leave(){},finish(){}};}
AV['ct-gallery-noise']=root=>galView(root,['noise-high','noise-mid','noise-low','filter-sharp','filter-smooth'],'A real CT slice with simulated noise at three exposures and with a sharp and a smooth reconstruction filter, each beside the clean reference','Simulated on a real axial CT slice of a head-and-neck patient (OpenKBP, 3.9 mm voxels interpolated to 1 mm). The physics is simulated: a polychromatic spectrum, NIST attenuation, Poisson noise, and filtered backprojection. Left: the clean reference. Right: with the effect. These are simulations, not clinical scans.');
AV['ct-gallery-artifacts']=root=>galView(root,['beam-hardening','metal','ring','motion','scatter'],'A real CT slice with simulated beam hardening, metal, ring, motion, and scatter artifacts, each beside the clean reference','Simulated on a real axial CT slice of a head-and-neck patient (OpenKBP, 3.9 mm voxels interpolated to 1 mm). Each artifact comes from its physical cause: a polychromatic spectrum, a dense metal object, a miscalibrated detector channel, patient motion during the scan, or scattered photons. Left: the clean reference. Right: with the artifact. These are simulations, not clinical scans.');

// ---------------------------------------------------------------- a real CT slice: tap to read the HU, change the window and level, and degrade the bit depth and the matrix
function huData(){const G=DATA.gal; if(!G._hu){const b=atob(G.hu), u=new Uint8Array(b.length); for(let i=0;i<b.length;i++) u[i]=b.charCodeAt(i); G._hu=new Int16Array(u.buffer);} return G._hu;}
function huView(root,mode,label,cap){
  const G=DATA.gal, n=G.n, A=huData(), W=420, H=412, {s,c}=avShell(root,W,H,label,cap), SZ=400, ox=10, oy=6, MATS=[16,24,32,48,64,96,192], RNG=G.hu_max-G.hu_min+1;
  const im=sv('image',{x:ox,y:oy,width:SZ,height:SZ,preserveAspectRatio:'xMidYMid meet'},s), mk=sv('circle',{r:7,fill:'none',stroke:'#ffd60a','stroke-width':2.5,display:'none'},s), cv=document.createElement('canvas'); cv.width=cv.height=n; const g2=cv.getContext('2d');
  const st={w:400,l:40,bits:8,mat:6,px:null,py:null}, names=mode==='hu'?['Soft-tissue window','Bone window','Wide window','Air','Fat','Muscle','Bone']:['Soft-tissue window','Full-range window'], {b:btns,o:out}=avBtns(c,mode==='hu'?'Window, and tissues to read':'Window',names);
  const sl=(t,min,max,stp,val)=>{const l=document.createElement('label'); l.innerHTML=t+'<input type="range" min="'+min+'" max="'+max+'" step="'+stp+'" value="'+val+'">'; c.insertBefore(l,out); return l.querySelector('input');};
  const rw=mode==='hu'?sl('Window width (HU)',50,4000,10,400):null, rl=mode==='hu'?sl('Window level (HU)',-1000,2000,10,40):null, rb=mode==='bits'?sl('Bits per pixel',1,12,1,8):null, rm=mode==='bits'?sl('Matrix: 16, 24, 32, 48, 64, 96, 192 pixels across',0,6,1,6):null;
  const cls=h=>h<-900?'the air range':h<-30&&h>-200?'the fat range':h>=0&&h<=100?'the soft-tissue range':h>300?'the bone range':'between the usual tissue ranges';
  const paint=()=>{const id=g2.createImageData(n,n), lo=st.l-st.w/2, m=MATS[st.mat], f=n/m, Lv=Math.pow(2,st.bits); let src=A;
    if(m<n){src=new Float32Array(n*n); for(let by=0;by<m;by++)for(let bx=0;bx<m;bx++){let sum=0; for(let y=by*f;y<(by+1)*f;y++)for(let x=bx*f;x<(bx+1)*f;x++) sum+=A[y*n+x]; const v=sum/(f*f); for(let y=by*f;y<(by+1)*f;y++)for(let x=bx*f;x<(bx+1)*f;x++) src[y*n+x]=v;}}
    for(let i=0;i<n*n;i++){let v=src[i]; if(mode==='bits'&&st.bits<12){const q=Math.min(Lv-1,Math.max(0,Math.floor((v-G.hu_min)/RNG*Lv))); v=G.hu_min+(q+0.5)/Lv*RNG;} const gr=Math.max(0,Math.min(255,Math.round((v-lo)/st.w*255))); id.data[i*4]=id.data[i*4+1]=id.data[i*4+2]=gr; id.data[i*4+3]=255;}
    g2.putImageData(id,0,0); im.setAttribute('href',cv.toDataURL('image/png')); btns.forEach((e,i)=>{const on=mode==='hu'?(i===0&&st.w===400&&st.l===40)||(i===1&&st.w===2000&&st.l===500)||(i===2&&st.w===4000&&st.l===1000):(i===0&&st.w===400)||(i===1&&st.w===4096); if(i<(mode==='hu'?3:2)) e.setAttribute('aria-pressed',String(on));});
    const lo2=Math.round(lo), hi2=Math.round(lo+st.w), win='Window '+st.w+', level '+st.l+': HU below '+lo2+' appear black and above '+hi2+' white.';
    if(mode==='hu'){ let t=win; if(st.px!==null){const h=A[st.py*n+st.px]; mk.setAttribute('cx',ox+(st.px+0.5)/n*SZ); mk.setAttribute('cy',oy+(st.py+0.5)/n*SZ); mk.setAttribute('display','inline'); t='HU at the marker: <span class="f">'+h+'</span>, in '+cls(h)+'. '+win;} else mk.setAttribute('display','none'); out.innerHTML=t;}
    else{const per=RNG/Lv; out.innerHTML='<span class="v">'+st.bits+' bits</span>: '+Lv+' levels, each '+(per>=1?per.toFixed(per<10?1:0):per.toFixed(2))+' HU wide, so a window of '+st.w+' HU holds <span class="f">'+(st.w/per).toFixed(st.w/per<10?1:0)+' levels</span>. Matrix '+m+' × '+m+': pixels of '+(G.fov_mm/m).toFixed(1)+' mm.';}};
  const place=(x,y)=>{st.px=x; st.py=y; paint();};
  if(mode==='hu'){ s.addEventListener('click',e=>{const r=s.getBoundingClientRect(), x=(e.clientX-r.left)/r.width*W-ox, y=(e.clientY-r.top)/r.height*H-oy; if(x<0||y<0||x>=SZ||y>=SZ) return; place(Math.floor(x/SZ*n),Math.floor(y/SZ*n));}); s.style.cursor='crosshair';
    btns[0].addEventListener('click',()=>{st.w=400;st.l=40; rw.value=400; rl.value=40; paint();}); btns[1].addEventListener('click',()=>{st.w=2000;st.l=500; rw.value=2000; rl.value=500; paint();}); btns[2].addEventListener('click',()=>{st.w=4000;st.l=1000; rw.value=4000; rl.value=1000; paint();});
    ['air','fat','muscle','bone'].forEach((k,i)=>btns[3+i].addEventListener('click',()=>place(G.picks[k].x,G.picks[k].y))); rw.addEventListener('input',()=>{st.w=+rw.value; paint();}); rl.addEventListener('input',()=>{st.l=+rl.value; paint();});}
  else{ btns[0].addEventListener('click',()=>{st.w=400; st.l=40; paint();}); btns[1].addEventListener('click',()=>{st.w=4096; st.l=1024; paint();}); rb.addEventListener('input',()=>{st.bits=+rb.value; paint();}); rm.addEventListener('input',()=>{st.mat=+rm.value; paint();});}
  paint(); return {enter(){},leave(){},finish(){}};}
AV['ct-hu-explorer']=root=>huView(root,'hu','A real axial CT slice with an adjustable window and level and a readout of the Hounsfield unit of air, fat, muscle, and bone','A real axial CT slice of a head-and-neck patient (OpenKBP, 3.9 mm voxels interpolated to 1 mm). The window width and level choose which HU range is spread over the grey scale. Data: Babier et al., Med Phys 2021.');
AV['ct-bits']=root=>huView(root,'bits','The same real CT slice stored with fewer bits per pixel and fewer pixels','The same real CT slice. The 4096 HU of the CT range are divided into 2^n levels, so each level is 4096 / 2^n HU wide. With few bits the soft-tissue differences fall into a single level and disappear. A smaller matrix makes the pixels larger and the image coarser. Data: Babier et al., Med Phys 2021.');
AV['drr-gallery-contrast']=root=>galView(root,['mv'],'A simulated kilovoltage radiograph of a real patient and the same radiograph made with a megavoltage beam','Simulated radiographs of a real patient: an AP projection of the CT volume of a head-and-neck patient (OpenKBP). The imaging physics is simulated: polychromatic kV and megavoltage spectra, NIST attenuation of water and bone, Poisson noise, a scatter background, and an anti-scatter grid. Top: the clean kV reference. Bottom: with the effect. These are simulations, not clinical radiographs.',DATA.drr);
AV['drr-gallery-noise']=root=>galView(root,['noise-high','noise-mid','noise-low'],'A simulated radiograph of a real patient at three exposures','Simulated radiographs of a real patient: an AP projection of the CT volume of a head-and-neck patient (OpenKBP). The imaging physics is simulated: polychromatic kV and megavoltage spectra, NIST attenuation of water and bone, Poisson noise, a scatter background, and an anti-scatter grid. Top: the clean kV reference. Bottom: with the effect. These are simulations, not clinical radiographs.',DATA.drr);
AV['drr-gallery-scatter']=root=>galView(root,['scatter','grid'],'A simulated radiograph of a real patient with scatter and with an anti-scatter grid','Simulated radiographs of a real patient: an AP projection of the CT volume of a head-and-neck patient (OpenKBP). The imaging physics is simulated: polychromatic kV and megavoltage spectra, NIST attenuation of water and bone, Poisson noise, a scatter background, and an anti-scatter grid. Top: the clean kV reference. Bottom: with the effect. These are simulations, not clinical radiographs.',DATA.drr);

// ---------------------------------------------------------------- real brain anatomy with a simulated MR contrast: the image changes with TR, TE, and TI
let mrP=null;
function mrLoad(){ if(mrP) return mrP; const M=DATA.mr; mrP=new Promise(r=>{const im=new Image(); im.onload=()=>{const cv=document.createElement('canvas'); cv.width=im.width; cv.height=im.height; const g=cv.getContext('2d',{willReadFrequently:true}); g.drawImage(im,0,0); M._f=g.getImageData(0,0,im.width,im.height).data; r(M);}; im.src=M.frac;}); return mrP;}
const mrSig=(t,TR,TE,TI)=>{const e1=Math.exp(-TR/t.T1), s=TI>0?Math.abs(1-2*Math.exp(-TI/t.T1)+e1):(1-e1); return t.PD*s*Math.exp(-TE/t.T2);};
AV['mr-contrast']=root=>{
  const M=DATA.mr, W=420, IW=300, IH=Math.round(IW*M.h/M.w), {s,c}=avShell(root,W,IH+8,'A real axial brain slice with a simulated MR contrast that changes with the repetition time, the echo time, and the inversion time','The anatomy is a real axial slice of the ICBM152 average brain, with its gray-matter and white-matter probability maps and the CSF in between. The signal of each tissue is simulated from its PD, T1, and T2 (illustrative values at 1.5 T). The image changes with the sequence, TR, TE, and TI because the signals of the tissues change. These are simulations, not scanner images.');
  const im=sv('image',{x:(W-IW)/2,y:4,width:IW,height:IH,preserveAspectRatio:'none'},s), cv=document.createElement('canvas'); cv.width=M.w; cv.height=M.h; const g2=cv.getContext('2d');
  const {b:btns,o:out}=avBtns(c,'Sequence',['T1-weighted','T2-weighted','PD-weighted','FLAIR']); const PRE=[[500,15,0],[4000,100,0],[4000,15,0],[9000,100,2370]];
  const mk=(t,min,max,stp,val)=>{const l=document.createElement('label'); l.innerHTML=t+'<input type="range" min="'+min+'" max="'+max+'" step="'+stp+'" value="'+val+'">'; c.insertBefore(l,out); return l.querySelector('input');};
  const rTR=mk('Repetition time TR (ms)',100,10000,50,500), rTE=mk('Echo time TE (ms)',5,200,5,15), rTI=mk('Inversion time TI (ms), 0 = no inversion',0,3500,10,0); let ready=false;
  const draw=()=>{ if(!ready) return; const TR=+rTR.value, TE=+rTE.value, TI=+rTI.value, T=M.tissue, S={CSF:mrSig(T.CSF,TR,TE,TI),GM:mrSig(T.GM,TR,TE,TI),WM:mrSig(T.WM,TR,TE,TI)}, mx=Math.max(S.CSF,S.GM,S.WM,1e-6), id=g2.createImageData(M.w,M.h), F=M._f;
    for(let i=0;i<M.w*M.h;i++){const v=(F[i*4]*S.CSF+F[i*4+1]*S.GM+F[i*4+2]*S.WM)/255/mx, gr=Math.max(0,Math.min(255,Math.round(255*v))); id.data[i*4]=id.data[i*4+1]=id.data[i*4+2]=gr; id.data[i*4+3]=255;}
    g2.putImageData(id,0,0); im.setAttribute('href',cv.toDataURL('image/png'));
    const pre=PRE.findIndex(p=>p[0]===TR&&p[1]===TE&&p[2]===TI); btns.forEach((e,k)=>e.setAttribute('aria-pressed',String(k===pre)));
    out.innerHTML='TR <span class="v">'+TR+' ms</span>, TE <span class="v">'+TE+' ms</span>, '+(TI>0?'TI <span class="v">'+TI+' ms</span>':'no inversion')+': relative signal WM <span class="f">'+(S.WM/mx).toFixed(2)+'</span>, GM <span class="f">'+(S.GM/mx).toFixed(2)+'</span>, CSF <span class="f">'+(S.CSF/mx).toFixed(2)+'</span>';};
  btns.forEach((e,k)=>e.addEventListener('click',()=>{rTR.value=PRE[k][0]; rTE.value=PRE[k][1]; rTI.value=PRE[k][2]; draw();})); [rTR,rTE,rTI].forEach(r=>r.addEventListener('input',draw));
  mrLoad().then(()=>{ready=true; draw();}); return {enter(){},leave(){},finish(){}};};
AV['mr-gallery-artifacts']=root=>galView(root,['distortion','gradient','susceptibility'],'A real brain slice with a simulated B0 distortion, a gradient 5% too strong, and a metal susceptibility artifact, each beside the clean reference','The anatomy is a real axial slice of the ICBM152 average brain, with a 20 mm grid that plays the part of a distortion phantom. Each artifact follows from its physical cause: a change of the local field moves the pixel by the field error divided by the gradient, a stronger gradient compresses the image, and a metal object leaves a signal void and shifts the pixels around it. Left: the clean reference. Right: with the artifact. These are simulations, not scanner images.',DATA.mrg);
// ---------------------------------------------------------------- real clinical images from TCIA collections (tools/make_real_*.py): a figure is one view of one to four panels, or several views to choose between
function realFig(root,id){
  const F=DATA.real.figs[id], noop={enter(){},leave(){},finish(){}}; if(!F){root.remove(); return noop;}
  const W=420, G=8, LH=19, SH=18, V=F.views;
  const lay=V.map(v=>{const cw=(W-(v.cols+1)*G)/v.cols, cells=[]; let y=G;                                                                        // every view is laid out first, so that the figure keeps one height whichever view is shown
    for(let i=0;i<v.panels.length;i+=v.cols){const row=v.panels.slice(i,i+v.cols), ih=Math.max(...row.map(p=>p.h*cw/p.w)), top=y+(row.some(p=>p.label)?LH:0);
      row.forEach((p,j)=>cells.push({p,x:G+j*(cw+G),y:top,w:cw,h:p.h*cw/p.w,ly:y+14,sy:top+ih+15})); y=top+ih+(row.some(p=>p.sub)?SH:0)+G;}
    return {cells,h:y};});
  const H=Math.ceil(Math.max(...lay.map(l=>l.h))), {s,c}=avShell(root,W,H,F.label,F.cap), g=sv('g',{},s); let out=null, btns=null;
  const draw=k=>{g.innerHTML=''; const dy=Math.round((H-lay[k].h)/2); lay[k].cells.forEach(({p,x,y,w,h,ly,sy})=>{ y+=dy; ly+=dy; sy+=dy;                          // a view shorter than the tallest one sits in the middle of the figure
      if(p.label) stext(g,x+w/2,ly,p.label,{'text-anchor':'middle','font-size':14,'font-weight':700});
      sv('image',{x,y,width:w,height:h,href:p.img,preserveAspectRatio:'none'},g);
      if(p.sub) stext(g,x+w/2,sy,p.sub,{'text-anchor':'middle','font-size':13,fill:'var(--mu)'});});
    if(btns) btns.forEach((b,i)=>b.setAttribute('aria-pressed',String(i===k))); if(out) out.innerHTML=V[k].facts||'';};
  if(V.length>1){const r=avBtns(c,F.head||'View',V.map(v=>v.label)); btns=r.b; out=r.o; btns.forEach((b,i)=>b.addEventListener('click',()=>draw(i)));}
  else if(V[0].facts){out=document.createElement('output'); out.className='avo'; out.setAttribute('aria-live','polite'); c.appendChild(out);}
  draw(0); return noop;}
AV['real-ct-noise']=root=>realFig(root,'real-ct-noise');
AV['real-ct-kernel']=root=>realFig(root,'real-ct-kernel');
AV['real-ct-cbct']=root=>realFig(root,'real-ct-cbct');
AV['real-ct-metal']=root=>realFig(root,'real-ct-metal');
AV['real-pet-ac']=root=>realFig(root,'real-pet-ac');
AV['real-pet-suv']=root=>realFig(root,'real-pet-suv');
AV['real-pet-tracers']=root=>realFig(root,'real-pet-tracers');
AV['real-nm-bone']=root=>realFig(root,'real-nm-bone');
AV['real-mr-seq']=root=>realFig(root,'real-mr-seq');
AV['real-dx-chest']=root=>realFig(root,'real-dx-chest');
AV['real-ct-motion']=root=>realFig(root,'real-ct-motion');

let avIO=null, avList=[];
function bindAV(){
  avList.forEach(a=>a.leave()); avList=[]; if(avIO){avIO.disconnect(); avIO=null;}
  const els=[...document.querySelectorAll('figure.av[data-av]')]; if(!els.length) return;
  els.forEach(el=>{const f=AV[el.dataset.av]; if(!f){el.remove(); return;} el._av=f(el); avList.push(el._av); if(REDUCE) el._av.finish();});
  if(REDUCE) return;
  if(!('IntersectionObserver' in window)){avList.forEach(a=>a.enter()); return;}
  avIO=new IntersectionObserver(es=>es.forEach(en=>{const a=en.target._av; if(a){ if(en.isIntersecting) a.enter(); else a.leave(); }}),{threshold:.35});
  els.forEach(el=>{ if(el._av) avIO.observe(el); });
}
// ---------------------------------------------------------------- practice questions on the topic page
function paintQ(el,sel,persist){
  const key=el.dataset.key.split(','), ok=sel.length===key.length&&sel.every(k=>key.includes(k));
  el.classList.add('done');
  el.querySelectorAll('.opt').forEach(b=>{
    const k=b.dataset.k, picked=sel.includes(k), right=key.includes(k);
    b.setAttribute('aria-pressed',picked?'true':'false'); b.classList.toggle('right',right); b.classList.toggle('wrong',picked&&!right);
    const old=b.querySelector('.tag'); if(old) old.remove();
    if(right||picked){const s=document.createElement('span'); s.className='tag'; s.textContent=right?'Correct answer':'Your answer'; b.appendChild(s);}
  });
  el.querySelector('.res').textContent=ok?'Correct.':(key.length>1?'Not correct. The answers are '+key.join(', ')+'.':'Not correct. The answer is '+key[0]+'.');
  el.querySelector('.fb').hidden=false; el.querySelector('.chkrow').hidden=true; moreSync(el,ok);
  if(persist){
    ansRec(el,{sel,ok,sig:el.dataset.sig,t:new Date().toISOString()},el.dataset.multi==='1'?'multi':'mc',ok,[...sel].sort().join('')); markSeen(el.dataset.id);
    const r=el.querySelector('.fb').getBoundingClientRect();
    if(r.bottom>window.innerHeight-16) window.scrollBy({top:Math.min(r.bottom-window.innerHeight+32,Math.max(0,r.top-80)),behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth'});
  }
}
// ---- 'Show more details' in the text and 'Explain further' in the feedback: one button that opens a hidden region
function bindMore(){const m=$('#main'); if(m._more) return; m._more=true;
  m.addEventListener('click',e=>{const b=e.target.closest('.more-btn'); if(!b) return; const body=b.parentElement.querySelector('.more-body'); if(!body) return; const open=body.hidden, fb=!!b.closest('.fb');
    body.hidden=!open; b.setAttribute('aria-expanded',String(open)); b.textContent=open?(fb?'Hide explanation':'Hide details'):(fb?'Explain further':'Show more details');
    if(open&&ANALYTICS){
      if(fb){const q=b.closest('.pq'); if(q){q._help=true; track('more_q',{item:itemOf(q),state:q.classList.contains('done')?(q._ok?'after_correct':'after_wrong'):'before_answer'});}}
      else{let h=b.closest('.more'); while(h&&h.tagName!=='H2') h=h.previousElementSibling; const sm=h&&h.id.match(/-s(\d+)$/), tp=location.hash.split('/')[1]; if(sm&&tp) track('more_s',{topic:tp,section:sm[1]});}
    }});}
function moreSync(el,ok){el._ok=ok; const m=el.querySelector('.more'); if(!m) return; m.classList.toggle('wrong',!ok); const b=m.querySelector('.more-btn'), body=m.querySelector('.more-body'); body.hidden=true; b.setAttribute('aria-expanded','false'); b.textContent='Explain further';}
function resetQ(el){
  el.classList.remove('done');
  el.querySelectorAll('.opt').forEach(b=>{b.setAttribute('aria-pressed','false'); b.classList.remove('right','wrong'); const t=b.querySelector('.tag'); if(t) t.remove();});
  el.querySelector('.fb').hidden=true; el.querySelector('.chkrow').hidden=false; el.querySelector('.chk').disabled=true;
  ansClear(el);
}

// ---------------------------------------------------------------- sorting, matching, ranking, and typed-number questions
function bindSort(el){
  const id=el.dataset.id, key=el.dataset.key.split(','), want=key.map(k=>+k.split('>')[1]), cap=+el.dataset.cap||0;
  const chips=[...el.querySelectorAll('.chip')], bins=[...el.querySelectorAll('.bin')], tray=el.querySelector('.tray'), chk=el.querySelector('.chk'), fb=el.querySelector('.fb'), rst=el.querySelector('.reset');
  const place=chips.map(()=>-1); let sel=null;
  const slot=b=>b<0?tray:bins[b].querySelector('.slot');
  const render=()=>{
    const ae=document.activeElement, keep=ae&&ae.classList&&ae.classList.contains('chip')&&el.contains(ae)?ae:null;   // moving a node drops focus, so put it back
    chips.forEach(c=>{const i=+c.dataset.i; slot(place[i]).appendChild(c); c.setAttribute('aria-pressed',sel===i?'true':'false');});
    if(keep) keep.focus();
    tray.classList.toggle('empty',!tray.querySelector('.chip'));
    const done=el.classList.contains('done'); el.querySelectorAll('.place').forEach(b=>b.hidden=sel===null||done);
    chk.disabled=place.some(p=>p<0); rst.hidden=done||!place.some(p=>p>=0);
  };
  const put=(i,b)=>{
    if(el.classList.contains('done')) return;
    const old=place[i], had=!!(document.activeElement&&el.contains(document.activeElement)&&document.activeElement!==document.body);
    if(b>=0&&cap){const inb=chips.filter(c=>place[+c.dataset.i]===b&&+c.dataset.i!==i); if(inb.length>=cap) place[+inb[0].dataset.i]=old;}
    place[i]=b; sel=null; render();
    if(had){const c=chips.find(x=>+x.dataset.i===i); if(c) c.focus();}
  };
  chips.forEach(c=>{
    const i=+c.dataset.i; let noclick=false;
    c.addEventListener('click',()=>{ if(noclick||el.classList.contains('done')) return; sel=sel===i?null:i; render(); });
    c.addEventListener('pointerdown',e=>{
      if(el.classList.contains('done')||(e.pointerType==='mouse'&&e.button!==0)) return;
      const r=c.getBoundingClientRect(), sx=e.clientX, sy=e.clientY, ox=sx-r.left, oy=sy-r.top; let moved=false, ghost=null;
      try{c.setPointerCapture(e.pointerId);}catch(_){}
      const over=(x,y)=>{const t=document.elementFromPoint(x,y); return t?(t.closest('.bin')||t.closest('.tray')):null;};
      const move=ev=>{
        if(!moved){ if(Math.hypot(ev.clientX-sx,ev.clientY-sy)<7) return; moved=true; ghost=c.cloneNode(true); ghost.classList.add('drag'); ghost.style.width=r.width+'px'; document.body.appendChild(ghost); c.style.opacity='.35'; }
        ghost.style.left=(ev.clientX-ox)+'px'; ghost.style.top=(ev.clientY-oy)+'px';
        el.querySelectorAll('.bin.over').forEach(b=>b.classList.remove('over')); const o=over(ev.clientX,ev.clientY); if(o&&o.classList.contains('bin')) o.classList.add('over');
      };
      const up=ev=>{
        c.removeEventListener('pointermove',move); c.removeEventListener('pointerup',up); c.removeEventListener('pointercancel',up); try{c.releasePointerCapture(e.pointerId);}catch(_){}
        if(ghost){ghost.remove(); c.style.opacity='';} el.querySelectorAll('.bin.over').forEach(b=>b.classList.remove('over'));
        if(moved){ noclick=true; setTimeout(()=>{noclick=false;},60); const o=ev.type==='pointerup'?over(ev.clientX,ev.clientY):null; if(o) put(i,o.classList.contains('bin')?bins.indexOf(o):-1); }
      };
      c.addEventListener('pointermove',move); c.addEventListener('pointerup',up); c.addEventListener('pointercancel',up);
    });
  });
  bins.forEach((bn,b)=>{
    bn.addEventListener('click',e=>{ if(e.target.closest('.chip')||e.target.closest('.place')) return; if(sel!==null) put(sel,b); });
    bn.querySelector('.place').addEventListener('click',()=>{ if(sel!==null) put(sel,b); });
  });
  tray.addEventListener('click',e=>{ if(e.target.closest('.chip')) return; if(sel!==null) put(sel,-1); });
  el.addEventListener('keydown',e=>{ if(e.key==='Escape'&&sel!==null){sel=null; render();} });
  const paint=persist=>{
    el.classList.add('done'); sel=null; let n=0;
    chips.forEach(c=>{const i=+c.dataset.i, ok=place[i]===want[i]; if(ok) n++; c.classList.toggle('right',ok); c.classList.toggle('wrong',!ok); c.setAttribute('aria-pressed','false');
      const old=c.querySelector('.tg'); if(old) old.remove(); if(!ok){const t=document.createElement('span'); t.className='tg'; t.textContent='Belongs in: '+bins[want[i]].querySelector('.bh').textContent; c.appendChild(t);} });
    el.querySelector('.res').textContent=n===chips.length?'All correct.':n+' of '+chips.length+' in the right place.'; fb.hidden=false; moreSync(el,n===chips.length); el.querySelector('.chkrow').hidden=true; render();
    if(persist) ansRec(el,{sel:place.map((b,i)=>i+'>'+b),sig:el.dataset.sig,t:new Date().toISOString()},el.dataset.mode==='match'?'match':el.dataset.mode==='rank'?'rank':'sort',n===chips.length,chips.reduce((m,c)=>m+(place[+c.dataset.i]===want[+c.dataset.i]?(1<<+c.dataset.i):0),0));
  };
  const reset=clear=>{ el.classList.remove('done'); place.fill(-1); sel=null; chips.forEach(c=>{c.classList.remove('right','wrong'); const t=c.querySelector('.tg'); if(t) t.remove();}); fb.hidden=true; el.querySelector('.chkrow').hidden=false; if(clear) ansClear(el); render(); };
  chk.addEventListener('click',()=>{ if(!place.some(p=>p<0)) paint(true); });
  rst.addEventListener('click',()=>reset(false)); el.querySelector('.again').addEventListener('click',()=>reset(true));
  const saved=qSel(id); if(saved){ saved.forEach(s=>{const [i,b]=s.split('>').map(Number); if(i>=0&&i<place.length) place[i]=b;}); render(); paint(false); } else render();
}
const NUMSUP={'⁰':0,'¹':1,'²':2,'³':3,'⁴':4,'⁵':5,'⁶':6,'⁷':7,'⁸':8,'⁹':9};
function parseNum(s){
  s=String(s).trim().replace(/[−–]/g,'-').replace(/,/g,'');
  s=s.replace(/10([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)/g,(m,g)=>'10^'+(g[0]==='⁻'?'-':'')+g.replace('⁻','').split('').map(ch=>NUMSUP[ch]).join(''));
  s=s.replace(/\s*[×x·*]\s*10\s*\^?\s*/gi,'e').replace(/\s+/g,'');
  return /^[+-]?(\d+\.?\d*|\.\d+)(e[+-]?\d+)?$/i.test(s)?parseFloat(s):NaN;
}
function bindNum(el){
  const id=el.dataset.id, ans=+el.dataset.ans, tol=+el.dataset.tol, show=el.dataset.show, inp=el.querySelector('.numin'), chk=el.querySelector('.chk'), fb=el.querySelector('.fb'), msg=el.querySelector('.msg'), res=el.querySelector('.res');
  const paint=(txt,persist)=>{
    const x=parseNum(txt); if(Number.isNaN(x)){msg.textContent='Enter a number, such as 357 or 3.57e2.'; msg.hidden=false; return;} msg.hidden=true;
    const ok=Math.abs(x-ans)<=tol*Math.abs(ans)+1e-12; el.classList.add('done'); inp.readOnly=true; inp.classList.toggle('right',ok); inp.classList.toggle('wrong',!ok);
    res.textContent=ok?'Correct.':'Not quite. The answer is '+show+'.'; fb.hidden=false; moreSync(el,ok); el.querySelector('.chkrow').hidden=true;
    if(persist) ansRec(el,{sel:[String(txt)],sig:el.dataset.sig,t:new Date().toISOString()},'typed',ok,Number(x.toPrecision(3)));
  };
  inp.addEventListener('input',()=>{chk.disabled=!inp.value.trim(); msg.hidden=true;});
  inp.addEventListener('keydown',e=>{ if(e.key==='Enter'&&!chk.disabled) chk.click(); });
  chk.addEventListener('click',()=>paint(inp.value,true));
  el.querySelector('.again').addEventListener('click',()=>{ el.classList.remove('done'); inp.readOnly=false; inp.value=''; inp.classList.remove('right','wrong'); fb.hidden=true; el.querySelector('.chkrow').hidden=false; chk.disabled=true; ansClear(el); inp.focus(); });
  const saved=qSel(id); if(saved){inp.value=saved[0]; chk.disabled=false; paint(saved[0],false);}
}

// ---------------------------------------------------------------- tap-the-figure questions
function bindFig(el){
  const id=el.dataset.id, S=JSON.parse(el.dataset.spec), T=JSON.parse(el.dataset.targets), box=el.querySelector('.fgb'), chk=el.querySelector('.chk'), fb=el.querySelector('.fb');
  const W=420, H=S.h||290, m={l:S.y&&S.y.ticks&&S.y.ticks.length?(S.y.fmt==='pct'?58:46):30,r:14,t:14,b:S.x.label?50:34}, pw=W-m.l-m.r, ph=H-m.t-m.b;
  const fx=v=>S.x.log?Math.log10(v):v, fy=v=>S.y.log?Math.log10(v):v, ix=v=>S.x.log?Math.pow(10,v):v, iy=v=>S.y.log?Math.pow(10,v):v;
  const X=v=>m.l+(fx(v)-fx(S.x.min))/(fx(S.x.max)-fx(S.x.min))*pw, Y=v=>m.t+ph-(fy(v)-fy(S.y.min))/(fy(S.y.max)-fy(S.y.min))*ph;
  const dx=px=>ix(fx(S.x.min)+(px-m.l)/pw*(fx(S.x.max)-fx(S.x.min))), dy=py=>iy(fy(S.y.min)+(m.t+ph-py)/ph*(fy(S.y.max)-fy(S.y.min)));
  const col=n=>!n?'var(--text)':(/^plot-/.test(n)?`var(--${n})`:n), tfmt=(a,v)=>a.fmt==='pct'?v+'%':(a.fmt==='pow'&&v>=1e4?'10'+String(Math.round(Math.log10(v))).replace(/\d/g,d=>'⁰¹²³⁴⁵⁶⁷⁸⁹'[d]):String(v)), N=(t,a,p)=>{const e=document.createElementNS('http://www.w3.org/2000/svg',t); for(const k in (a||{})) e.setAttribute(k,a[k]); if(p) p.appendChild(e); return e;};
  const svg=N('svg',{viewBox:`0 0 ${W} ${H}`,role:'application',tabindex:'0','aria-label':(S.label||'Figure')+'. Tap or use the arrow keys to place your answer.'},box);
  (S.y.ticks||[]).forEach(t=>{const y=Y(t); N('line',{x1:m.l,y1:y,x2:W-m.r,y2:y,stroke:'var(--rule)','stroke-width':1},svg); const e=N('text',{x:m.l-8,y:y+5,'text-anchor':'end','font-size':13,fill:'var(--muted)'},svg); e.textContent=tfmt(S.y,t);});
  (S.x.ticks||[]).forEach(t=>{const x=X(t); N('line',{x1:x,y1:m.t,x2:x,y2:m.t+ph,stroke:'var(--rule)','stroke-width':1},svg); const e=N('text',{x:x,y:m.t+ph+18,'text-anchor':'middle','font-size':13,fill:'var(--muted)'},svg); e.textContent=tfmt(S.x,t);});
  N('line',{x1:m.l,y1:m.t+ph,x2:W-m.r,y2:m.t+ph,stroke:'var(--ink)','stroke-width':1.6},svg); N('line',{x1:m.l,y1:m.t,x2:m.l,y2:m.t+ph,stroke:'var(--ink)','stroke-width':1.6},svg);
  const subs=t=>t.replace(/<sub>(.*?)<\/sub>/g,'_$1').replace(/<\/?sup>/g,'');           // an axis label may carry <sub>: stext draws it as a subscript
  if(S.x.label) stext(svg,m.l+pw/2,H-8,subs(S.x.label),{'text-anchor':'middle','font-size':14,fill:'var(--text)'});
  if(S.y.label) stext(svg,0,0,subs(S.y.label),{transform:`translate(14 ${m.t+ph/2}) rotate(-90)`,'text-anchor':'middle','font-size':14,fill:'var(--text)'});
  (S.cells||[]).forEach(([cx,cy,t])=>{N('rect',{x:X(cx-.5),y:Y(cy+.5),width:X(cx+.5)-X(cx-.5),height:Y(cy-.5)-Y(cy+.5),fill:'var(--paper)',stroke:'var(--line)','stroke-width':1.4},svg); const e=N('text',{x:X(cx),y:Y(cy)+5,'text-anchor':'middle','font-size':14,'font-weight':600,fill:'var(--ink)'},svg); e.textContent=t;});
  (S.vlines||[]).forEach(v=>{N('line',{x1:X(v.x),y1:m.t,x2:X(v.x),y2:m.t+ph,stroke:'var(--muted)','stroke-width':1.4,'stroke-dasharray':'5 4'},svg);});
  (S.series||[]).forEach(s=>{let d='', pen=false; s.pts.forEach(([a,b])=>{ if(a<S.x.min||a>S.x.max||b<S.y.min||b>S.y.max){pen=false; return;} d+=(pen?'L':'M')+X(a).toFixed(1)+' '+Y(b).toFixed(1); pen=true;}); N('path',{d:d,fill:'none',stroke:col(s.color),'stroke-width':s.w||2.8,'stroke-linejoin':'round','stroke-dasharray':s.dash?'6 4':'none'},svg);});
  (S.dots||[]).forEach(d=>N('circle',{cx:X(d.x),cy:Y(d.y),r:d.r||6,fill:col(d.color)},svg));
  (S.texts||[]).forEach(t=>{const e=N('text',{x:X(t.x),y:Y(t.y),'text-anchor':t.anchor||'start','font-size':14,'font-weight':t.b?700:400,fill:col(t.color)},svg); e.textContent=t.t;});
  const tg=N('g',{},svg), mk=N('g',{class:'mk'},svg), hit=N('rect',{class:'fx',x:m.l,y:m.t,width:pw,height:ph,fill:'transparent'},svg);
  const gl=N('line',{y1:m.t,y2:m.t+ph},mk), dot=N('circle',{r:S.cells?9:7},mk); if(S.cells){gl.style.display='none'; dot.style.fill='none';} mk.style.display='none'; let pt=null;
  const inT=([x0,x1,y0,y1],p)=>(x0===null||p[0]>=x0)&&(x1===null||p[0]<=x1)&&(y0===null||p[1]>=y0)&&(y1===null||p[1]<=y1);
  const put=p=>{ if(el.classList.contains('done')) return; pt=p; gl.setAttribute('x1',X(p[0])); gl.setAttribute('x2',X(p[0])); dot.setAttribute('cx',X(p[0])); dot.setAttribute('cy',Y(p[1])); mk.style.display=''; chk.disabled=false; };
  hit.addEventListener('pointerdown',e=>{ if(e.pointerType==='mouse'&&e.button!==0) return; const r=svg.getBoundingClientRect(), s=W/r.width, px=(e.clientX-r.left)*s, py=(e.clientY-r.top)*s; put([dx(px),dy(py)]); });
  svg.addEventListener('keydown',e=>{ const k=e.key; if(!/^Arrow/.test(k)||el.classList.contains('done')) return; e.preventDefault();
    const stepx=S.cells?1:(fx(S.x.max)-fx(S.x.min))*(e.shiftKey?.1:.02), stepy=S.cells?1:(fy(S.y.max)-fy(S.y.min))*(e.shiftKey?.1:.02);
    let a=pt?fx(pt[0]):(fx(S.x.min)+fx(S.x.max))/2, b=pt?fy(pt[1]):(fy(S.y.min)+fy(S.y.max))/2; if(S.cells&&!pt){a=Math.round(a); b=Math.round(b);}
    if(pt){ if(k==='ArrowLeft') a-=stepx; if(k==='ArrowRight') a+=stepx; if(k==='ArrowUp') b+=stepy; if(k==='ArrowDown') b-=stepy; }
    a=Math.max(fx(S.x.min),Math.min(fx(S.x.max),a)); b=Math.max(fy(S.y.min),Math.min(fy(S.y.max),b)); put([ix(a),iy(b)]); });
  const dec=S.xdec===undefined?1:S.xdec, show=p=>{const a=S.x.log?+p[0].toPrecision(3):p[0].toFixed(dec); return (S.cells?'N = '+Math.round(p[0])+', Z = '+Math.round(p[1]):(S.xname||(S.x.label?S.x.label.replace(/\s*\(.*\)/,''):'x'))+' = '+a+(S.xunit||''));};
  const paint=persist=>{
    const ok=T.some(t=>inT(t,pt)); el.classList.add('done'); mk.classList.toggle('wrong',!ok); chk.closest('.chkrow').hidden=true;
    T.forEach(([x0,x1,y0,y1])=>{const a=x0===null?S.x.min:x0, b=x1===null?S.x.max:x1, c=y0===null?S.y.min:y0, d=y1===null?S.y.max:y1; N('rect',{class:'tgt',x:X(a),y:Y(d),width:Math.max(4,X(b)-X(a)),height:Math.max(4,Y(c)-Y(d))},tg);});
    const l=N('text',{class:'tgl',x:W-m.r-4,y:m.t+16,'text-anchor':'end'},tg); l.textContent='correct region';
    el.querySelector('.res').textContent=ok?'Correct.':'Not quite. The correct region is shaded.'; el.querySelector('.tapped').textContent='You tapped '+show(pt)+'.'; fb.hidden=false; moreSync(el,ok);
    if(persist){const pc=(f,v,lo,hi)=>Math.max(0,Math.min(100,Math.round((f(v)-f(lo))/(f(hi)-f(lo))*50)*2));
      ansRec(el,{sel:[pt[0].toPrecision(7)+','+pt[1].toPrecision(7)],sig:el.dataset.sig,t:new Date().toISOString()},'fig',ok,pc(fx,pt[0],S.x.min,S.x.max)+','+pc(fy,pt[1],S.y.min,S.y.max));}
  };
  chk.addEventListener('click',()=>{ if(pt) paint(true); });
  el.querySelector('.again').addEventListener('click',()=>{ el.classList.remove('done'); mk.classList.remove('wrong'); tg.innerHTML=''; mk.style.display='none'; pt=null; fb.hidden=true; chk.closest('.chkrow').hidden=false; chk.disabled=true; ansClear(el); });
  el._fig={toClient:(x,y)=>{const r=svg.getBoundingClientRect(), s=r.width/W; return {x:r.left+X(x)*s, y:r.top+Y(y)*s};}, marker:()=>pt};
  const saved=qSel(id); if(saved){const v=saved[0].split(',').map(Number); if(v.length===2&&v.every(Number.isFinite)){put(v); paint(false);}}
}
function bindQ(){
  if(qIO){qIO.disconnect(); qIO=null;} qWatched.clear();
  document.querySelectorAll('.pq').forEach(el=>{
    qWatch(el);
    if(el.dataset.kind==='sort'){bindSort(el); return;} if(el.dataset.kind==='num'){bindNum(el); return;} if(el.dataset.kind==='fig'){bindFig(el); return;}
    const multi=el.dataset.multi==='1', chk=el.querySelector('.chk');
    el.querySelectorAll('.opt').forEach(b=>b.addEventListener('click',()=>{
      if(el.classList.contains('done')) return;
      if(multi) b.setAttribute('aria-pressed',b.getAttribute('aria-pressed')==='true'?'false':'true');
      else el.querySelectorAll('.opt').forEach(o=>o.setAttribute('aria-pressed',o===b?'true':'false'));
      chk.disabled=!el.querySelector('.opt[aria-pressed="true"]');
    }));
    chk.addEventListener('click',()=>{const sel=[...el.querySelectorAll('.opt[aria-pressed="true"]')].map(o=>o.dataset.k); if(sel.length) paintQ(el,sel,true);});
    el.querySelector('.again').addEventListener('click',()=>resetQ(el)); initCalc(el);
    let sel=qSel(el.dataset.id); if(sel){sel=sel.filter(k=>el.querySelector('.opt[data-k="'+CSS.escape(k)+'"]')); if(sel.length) paintQ(el,sel,false);}
  });
}
function studyView(dk,i){
  const N=dk.cards.length; if(!N) return '<p class="empty">Nothing here.</p>';
  i=Math.max(0,Math.min(i,N));
  const crumb=dk.kind==='t'?`Flash cards › ${esc(dk.title)} · <a href="${dk.back}">${dk.backLabel}</a>`:`Flash cards › ${esc(dk.title)}`;
  const head=`<div class="top-row"><div class="stat"><b>${i<N?`Card ${i+1} of ${N}`:`${N} of ${N}`}</b><br>${crumb}</div></div><div class="lin"><i style="width:${Math.round(100*i/N)}%"></i></div>`;
  if(i>=N){
    let nxt='';
    if(dk.kind==='t'){const j=DATA.topics.findIndex(x=>x.id===dk.key),nt=DATA.topics[j+1]; if(nt) nxt=`<a class="btn primary" href="#t/${nt.id}/c">Next deck</a>`;}
    return `<div class="fc">${head}<div class="done"><b>${N} of ${N}</b><p style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:0"><a class="btn" href="${dk.base}">Restart</a>${dk.kind==='t'?`<a class="btn" href="${dk.back}">${dk.backLabel}</a>`:''}${nxt}</p></div></div>`;
  }
  const x=dk.cards[i], t=topic(x.topic);
  const fact=x.a.length===1?`<p>${x.a[0]}</p>`:`<ul>${x.a.map(a=>`<li>${a}</li>`).join('')}</ul>`;
  const work=x.w.length?`<div class="key"><div class="hd">Working</div><ol>${x.w.map(a=>`<li>${a}</li>`).join('')}</ol></div>`:'';
  return `<div class="fc fact" id="fc" data-next="${slideHref(dk.base,i+1)}" data-prev="${i>0?slideHref(dk.base,i-1):''}" data-id="${x.id}">${head}
    <div class="card"><div class="meta">${esc(dom(x.dom).roman)}. ${esc(dom(x.dom).name)} · ${esc(t.title)}</div><div class="ftitle">${x.q}</div><div class="fbody">${fact}${work}</div>${figHTML(x)}</div>
    <div class="acts">${i>0?`<a class="btn" id="prevq" href="${slideHref(dk.base,i-1)}">Previous</a>`:''}<a class="btn primary" id="nextq" href="${slideHref(dk.base,i+1)}">${i<N-1?'Next':'Finish'}</a></div>
    <p class="kbd"><span class="kb"><kbd>→</kbd> or <kbd>Space</kbd> next · <kbd>←</kbd> previous</span><span class="sw">Swipe left for the next card, right for the previous</span></p></div>`;
}
function planSummary(){const nb=DATA.topics.length, np=(DATA.plan||[]).length, tot=nb+np, q=DATA.cards.filter(c=>c.opts).length; return `${nb} of ${tot} planned topics are built (${Math.round(100*nb/tot)}%). Each built topic averages ${Math.round(q/nb)} questions, so the full course would hold about ${Math.round(q/nb*tot).toLocaleString('en-US')}. The list is the plan: a title leaves it when its topic is written. Ford chapters are shown in brackets.`;}
function planBlocks(){const out=[];
  for(const d of DATA.domains){const nb=DATA.topics.filter(t=>t.dom===d.n).length, np=(DATA.plan||[]).filter(x=>d.subs.some(s=>s[0]===x.sub)).length;
    out.push(`<div class="ph">${esc(d.roman)}. ${esc(d.name)} <span class="muted">${nb} of ${nb+np} topics built</span></div>`);
    for(const [code,name] of d.subs){const b=DATA.topics.filter(t=>t.sub===code).length, pl=(DATA.plan||[]).filter(x=>x.sub===code), head=`<span class="pn">${esc(code)} ${esc(name)}</span><span class="pc">${b} built · ${pl.length?pl.length+' to build':'complete'}</span>`;
      out.push(pl.length?`<details class="sub" data-sub="${esc(code)}" data-b="${b}" data-p="${pl.length}"><summary>${head}</summary><ul>${pl.map(x=>`<li>${esc(x.title)} <span class="muted">(Ford ${esc(x.ford)})</span></li>`).join('')}</ul></details>`:`<div class="sub" data-sub="${esc(code)}" data-b="${b}" data-p="0"><div class="row">${head}</div></div>`);}}
  return out.join('');}
function refView(){
  const rows=[];
  for(const d of DATA.domains){
    rows.push(`<tr class="cathead"><td colspan="4">${esc(d.roman)}. ${esc(d.name)} <span class="muted" style="font-weight:400;font-size:14px">${esc(d.weight)} of the exam</span></td></tr>`);
    for(const [code,name] of d.subs){
      const ts=DATA.topics.filter(t=>t.sub===code), qz=ts.flatMap(t=>quizOf(t.id)), fl=ts.flatMap(t=>flashOf(t.id));
      const kq=qz.filter(c=>qSel(c.id)).length, kf=seenCount(fl);
      rows.push(`<tr class="${ts.length?'':'gap'}"><td>${esc(code)} ${esc(name)}</td><td class="n">${ts.length||''}</td><td class="n">${qz.length?kq+' / '+qz.length:(ts.length?'none yet':'')}</td><td class="n">${fl.length?kf+' / '+fl.length:''}</td></tr>`);
    }
  }
  const read=DATA.topics.map(t=>`<tr><td>${esc(t.title)}</td><td>${esc(t.ref.aapm||'')}</td><td>${esc(t.ref.khan||'')}</td><td>${esc(t.ref.ford||'')}</td></tr>`).join('');
  const nf=seenCount(allFlash()), nqa=DATA.cards.filter(c=>c.opts&&qSel(c.id)).length;
  const sections=[['ref-coverage','Coverage by ABR subsection'],['ref-plan','Course plan'],['ref-reading','Reading'],['ref-data','Beam data tables'],['ref-nist','Photon attenuation data'],['ref-sources','Sources'],['ref-conventions','Text conventions'],['ref-progress','Progress']];
  return `<h1>Reference</h1>
  <p class="lead"><a href="#about">About and how to cite</a> · <a href="https://www.theabr.org/wp-content/uploads/2025/07/2023-ABR-RO-Physics-IC-Study-Guide.pdf" target="_blank" rel="noopener">Study guide (ABR, 2023)</a> · <a href="https://doi.org/10.1016/j.ijrobp.2023.08.063" target="_blank" rel="noopener">AAPM/ASTRO 2023 core curriculum</a></p>
  <p class="small">${esc(DATA.about.notice)}</p>
  <nav class="toc" aria-label="On this page"><div class="hd">On this page</div><ol>${sections.map(([id,t])=>`<li><a href="#ref" data-go="${id}">${t}</a></li>`).join('')}</ol></nav>
  <h2 id="ref-coverage">Coverage by ABR subsection</h2>
  <div class="tblwrap"><table class="cov"><tr><th>Subsection</th><th style="text-align:right">Topics</th><th style="text-align:right">Questions answered</th><th style="text-align:right">Flash cards seen</th></tr>${rows.join('')}</table></div>
  <p class="small">Red rows: ABR subsections with no topics yet. Weights are the ABR's ranges.</p>
  <h2 id="ref-plan">Course plan</h2>
  <p class="small">${planSummary()}</p>
  <div class="plan">${planBlocks()}</div>
  <h2 id="ref-reading">Reading</h2>
  <div class="tblwrap"><table class="tbl"><tr><th>Topic</th><th>AAPM/ASTRO 2023</th><th>Khan</th><th>Ford</th></tr>${read}</table></div>
  <p class="small">AAPM/ASTRO 2023 gives the curriculum section. Khan is <i>The Physics of Radiation Therapy</i>; chapter numbers vary by edition. Ford is <i>Primer on Radiation Oncology Physics</i>, 2nd edition.</p>
  <h2 id="ref-data">Beam data tables</h2>
  <p class="small">PDD, TMR, scatter, wedge, and tray tables for 6, 10, 15, and 18 MV are in <a href="#mu/tables/6">MU calc, Tables</a>. They are illustrative teaching data, not measured.</p>
  <p class="small">One illustrative 6 MV beam, used by the practice questions that ask for a lookup. The numbers come from a smooth model, not from a machine, and the three tables agree with each other: the PDD is generated from the TMR and S<sub>p</sub> with the conversion formula in the TMR chapter. Do not use them clinically.</p>
  <h2 id="ref-nist">Photon attenuation data</h2>
  <p class="small">Mass attenuation (μ/ρ) and mass energy-absorption (μ<sub>en</sub>/ρ) coefficients for water, cortical bone, and lead, used by the practice questions that ask for a lookup. Source: NIST Standard Reference Database 126 (Hubbell and Seltzer). Selected photon energies only.</p>
  ${DATA.nist}
  <h2 id="ref-sources">Sources</h2>
  <p class="small">Scope: ABR study guide and the AAPM/ASTRO 2023 curriculum. Attenuation and energy-absorption coefficients are from NIST SRD 126. Half-lives and branching fractions are rounded. Factors in worked examples are illustrative, not machine data. Verify values against your own commissioning data before clinical use.</p>
  <p class="small">Real images. The scans in the figures marked as real come from open collections of The Cancer Imaging Archive (TCIA), read as DICOM through the NCI Imaging Data Commons. All are released under a Creative Commons Attribution licence, CC BY 3.0 or CC BY 4.0, and the images are de-identified. The platforms are described by Clark et al., J Digit Imaging 2013;26:1045-1057 (TCIA) and Fedorov et al., Cancer Res 2021;81:4188-4193 (NCI Imaging Data Commons). The head-and-neck plan figures use the OpenKBP dataset (Babier et al., Med Phys 2021;48:5549-5561).</p>
  <ul class="small realsrc">${DATA.real.sources.map(s=>{const used=DATA.topics.filter(t=>s.figs.some(f=>t.html.includes('data-av="'+f+'"'))); return `<li><a href="https://doi.org/${esc(s.doi)}" target="_blank" rel="noopener">${esc(s.collection)}</a> (${esc(s.license)}). ${esc(s.citation)}${used.length?' Used in '+used.map(t=>`<a href="#t/${esc(t.id)}">${esc(t.title)}</a>`).join(', ')+'.':''}</li>`;}).join('')}</ul>
  <h2 id="ref-conventions">Text conventions</h2>
  <p class="small"><span class="v">Blue</span> marks given values, <span class="f">orange</span> marks the quantity to find, and <span class="t">green bold</span> marks a key term where it is first defined.</p>
  <p class="small">Questions come in several forms. Multiple choice has one answer, or says to select all that apply. <b>Sort</b> and <b>True or false</b> put items in bins, <b>Match</b> pairs each item with its partner, and <b>Rank</b> puts items in order. In each of these, drag an item to a bin, or tap the item and then tap the bin. <b>Type the answer</b> takes a number with no options to guess from, and counts an answer within the stated tolerance as correct.</p>
  <p class="small">Monitor-unit questions say which calibration they use. SSD calibration (1 cGy/MU at d<sub>max</sub> with the surface at 100 cm) is the convention at this clinic. SAD calibration puts the point at 100 cm. The chapter and the questions cover both.</p>
  <h2 id="ref-progress">Progress</h2>
  <p class="small">Stored in this browser only. ${Math.round(100*courseStats().read)}% of the chapter text read, ${nf} flash card${nf===1?'':'s'} seen, ${nqa} question${nqa===1?'':'s'} answered, ${MUC().filter(c=>muDone(c.id)).length} of ${MUC().length} MU cases tried.</p>
  <div class="btnrow"><button class="btn sm" id="exp">Export</button><button class="btn sm" id="imp">Import</button><button class="btn sm" id="clr">Clear</button><button class="btn sm" data-theme-btn>Light / dark</button><input type="file" id="impf" accept="application/json" style="display:none"></div>`;
}

// ---------------------------------------------------------------- About and how to cite (the text comes from src/about.py; the privacy section follows the usage events this build can send)
function aboutBlock(b){
  const k=b[0];
  if(k==='p') return `<p>${b[1]}</p>`;
  if(k==='h3') return `<h3>${b[1]}</h3>`;
  if(k==='ul') return `<ul>${b[1].map(x=>`<li>${x}</li>`).join('')}</ul>`;
  if(k==='table') return `<div class="tblwrap"><table class="tbl"><tr>${b[1].map(h=>`<th>${h}</th>`).join('')}</tr>${b[2].map(r=>`<tr>${r.map(c=>`<td>${c}</td>`).join('')}</tr>`).join('')}</table></div>`;
  if(k==='kv') return `<table class="tbl kv">${b[1].map(([a,v])=>`<tr><th scope="row">${a}</th><td>${v}</td></tr>`).join('')}</table>`;
  if(k==='cite') return `<div class="cite"><div class="ch"><b>${esc(b[1])}</b><button type="button" class="btn sm" data-copy="${esc(b[3])}">Copy</button></div><pre id="cite-${esc(b[3])}">${esc(b[2])}</pre></div>`;
  return '';
}
function aboutView(){
  const A=DATA.about, secs=A.sections;
  const body=secs.map(s=>{const bl=s.variants?s.variants[ANALYTICS?(ANALYTICS.backend==='endpoint'?'endpoint':'goatcounter'):'off']:s.blocks; return `<h2 id="${s.id}">${esc(s.title)}</h2>${bl.map(aboutBlock).join('')}`;}).join('');
  return `<h1>About and how to cite</h1>
  <p class="lead"><a href="#ref">Reference</a></p>
  <p class="small">${esc(A.notice)}</p>
  <nav class="toc" aria-label="On this page"><div class="hd">On this page</div><ol>${secs.map(s=>`<li><a href="#about" data-go="${s.id}">${esc(s.title)}</a></li>`).join('')}</ol></nav>
  <div class="about">${body}</div>`;
}
function copyText(t){
  if(navigator.clipboard&&navigator.clipboard.writeText) return navigator.clipboard.writeText(t);
  return new Promise((res,rej)=>{const ta=document.createElement('textarea'); ta.value=t; ta.setAttribute('readonly',''); ta.style.cssText='position:fixed;top:0;left:0;opacity:0'; document.body.appendChild(ta); ta.select(); let ok=false; try{ok=document.execCommand('copy');}catch(_){} ta.remove(); ok?res():rej(new Error('copy failed'));});
}

// ---------------------------------------------------------------- navigation
// the sections of the open chapter, under its entry in the menu: the one being read is bold, the ones already reached take the accent colour
function secList(t){const nq=quizOf(t.id).length;
  return `<ol class="secs" data-topic="${t.id}" aria-label="Sections of ${esc(t.title)}">`+(t.secs||[]).map(x=>`<li><a class="sec" href="#t/${t.id}" data-go="${esc(x.id)}" data-sec="${esc(x.id)}"><span class="sn">${esc(x.n)}</span><span class="st">${x.t}</span>${x.mk?'<span class="mk" title="Has a Must know box"></span>':''}</a></li>`).join('')+(nq?`<li><a class="sec" href="#t/${t.id}" data-go="${t.id}-q" data-sec="${t.id}-q"><span class="sn"></span><span class="st">Practice questions</span></a></li>`:'')+'</ol>';}
function spySide(){const ol=document.querySelector('#side ol.secs'); if(!ol) return;
  const links=[...ol.querySelectorAll('a.sec')], hs=links.map(a=>document.getElementById(a.dataset.sec)), f=readOf(ol.dataset.topic), mx=document.documentElement.scrollHeight-innerHeight;
  let act=-1; hs.forEach((h,i)=>{if(h&&h.getBoundingClientRect().top<=110) act=i;});
  let changed=false;
  links.forEach((a,i)=>{const h=hs[i], pos=(h&&mx>0)?(h.getBoundingClientRect().top+scrollY)/mx:0, on=i===act, rd=!on&&(i<act||pos<=f);
    if(a.classList.contains('on')!==on){a.classList.toggle('on',on); if(on) changed=true;} a.classList.toggle('rd',rd);});
  if(changed){const sd=$('#side'), a=links[act], ar=a.getBoundingClientRect(), sr=sd.getBoundingClientRect(); if(ar.top<sr.top+70||ar.bottom>sr.bottom-30) sd.scrollTop+=ar.top-sr.top-sr.height/3;}}
function sideHTML(cur,mode,openN){
  const cards=mode==='cards', qm=mode==='q', suf=cards?'/c':(qm?'/q':'');
  const out=[];
  if(cards) out.push(`<a class="top-link${cur==='mix'?' on':''}" href="#mix">Mix all topics</a>`);
  out.push('<nav class="acc" aria-label="Topics by domain">');
  for(const d of activeDoms()){const open=d.n===openN;
    out.push(`<div class="blk${open?' open':''}" data-dom="${d.n}"><button type="button" class="nm" aria-expanded="${open}" aria-controls="sb-${d.n}"><span class="chev" aria-hidden="true"></span><span class="rn">${esc(d.roman)}.</span><span class="dnm">${esc(d.name)}</span></button><div class="items" id="sb-${d.n}"><div class="in">${topicsOfDom(d.n).map(t=>`<a class="wk${cur===('t/'+t.id+suf)?' on':''}" href="#t/${t.id}${suf}"><span class="n">${esc(t.num)}</span><span>${esc(t.title)}</span></a>${(!suf&&cur==='t/'+t.id)?secList(t):''}`).join('')}</div></div></div>`);}
  out.push('</nav>'); return out.join('');
}
function jumpHTML(mode){
  const cards=mode==='cards', suf=cards?'/c':(mode==='q'?'/q':'');
  const o=[`<optgroup label="Sections"><option value="#home">Home</option><option value="#cards">Flash cards</option><option value="#questions">Questions</option><option value="#mu">MU calc</option><option value="#mu/tables/6">MU tables</option><option value="#ref">Reference</option></optgroup>`];
  if(cards) o.push(`<optgroup label="Flash cards"><option value="#mix">All topics, mixed</option></optgroup>`);
  for(const d of activeDoms()) o.push(`<optgroup label="${esc(d.roman)}. ${esc(d.name)}">${topicsOfDom(d.n).map(t=>`<option value="#t/${t.id}${suf}">${esc(t.num)} ${esc(t.title)}</option>`).join('')}</optgroup>`);
  return o.join('');
}
// @@MU@@
let muPend=null, lastView=null;
function route(){
  const h=location.hash.replace(/^#/,'')||'home'; const p=h.split('/');
  flushReads(); let html='', tab='', cur='home', jv='#home', mode='contents', openN=0, list=true; progMode=null; progFn=null; sideManual=false; sideHold=0;
  const ctx=(p[0]==='t'&&topic(p[1]))?p[1]:(topic(LS.get('ro.last',''))||DATA.topics[0]).id;      // the topic the menu items open: the one on the page, else the last one visited
  if(p[0]==='ref'){html=refView(); tab='ref'; cur='ref'; jv='#ref';}
  else if(p[0]==='about'){html=aboutView(); tab='ref'; cur='about'; jv='#ref';}
  else if(p[0]==='cards'){location.replace('#t/'+ctx+'/c'); return;}
  else if(p[0]==='mix'){const dk=deck('mix'), ii=idx(p[1]); html=studyView(dk,ii); tab='cards'; cur='mix'; jv='#mix'; mode='cards'; progFn=showCourse;}
  else if(p[0]==='questions'){location.replace('#t/'+ctx+'/q'); return;}
  else if(p[0]==='mu'){list=false; tab='mu'; cur='mu'; jv='#mu';      // the MU calculation module: practice cases and the full tables, on a page of their own
    if(p[1]==='tables'){html=muTablesView(+p[2]||6); jv='#mu/tables/6';} else {const r=muPractice(p[1]); if(r.redirect){location.replace(r.redirect); return;} html=r.html; muPend=r;}}
  else if(p[0]==='t'&&topic(p[1])){
    openN=topic(p[1]).dom; LS.set('ro.last',p[1]);
    if(p[2]==='c'){const dk=deck('t',p[1]), ii=idx(p[3]); html=studyView(dk,ii); tab='cards'; cur='t/'+p[1]+'/c'; jv='#t/'+p[1]+'/c'; mode='cards'; progFn=showCourse;}
    else if(p[2]==='q'){html=topicQuestions(p[1]); tab='questions'; cur='t/'+p[1]+'/q'; jv='#t/'+p[1]+'/q'; mode='q'; progFn=showCourse;}
    else{html=topicView(p[1]); cur='t/'+p[1]; jv='#t/'+p[1]; progMode='scroll'; progFn=chapterProg(p[1]);}
  }
  else if(p[0]==='study'){location.replace('#home'); return;}
  else if(/^d\d+$/.test(p[0])){ if(p[1]==='c'){location.replace('#cards'); return;} const f=topicsOfDom(+p[0].slice(1))[0]; location.replace(f?'#t/'+f.id:'#home'); return; }      // a domain opens its first topic
  else {html=homeView(); tab='home';}
  const lp=!!progFn;
  $('#main').innerHTML=html; $('#side').innerHTML=list?(lp?lpHTML():'')+sideHTML(cur,mode,openN):''; $('#lpm').innerHTML=lp?lpHTML():'';
  document.body.classList.toggle('cp',lp); document.body.classList.toggle('nolist',!list);
  const sel=$('#jump'); sel.innerHTML=jumpHTML(mode); sel.value=jv;
  document.querySelectorAll('.tabs a').forEach(a=>{a.classList.toggle('on',a.dataset.tab===tab); if(a.dataset.tab==='cards') a.setAttribute('href','#t/'+ctx+'/c'); if(a.dataset.tab==='questions') a.setAttribute('href','#t/'+ctx+'/q');});
  window.scrollTo(0,0); bind(); refreshProgress();
  if(ANALYTICS){const rk=location.hash.replace(/^#/,'').split('/').filter(x=>x&&!/^\d+$/.test(x)).join('/')||'home'; if(rk!==lastView){lastView=rk; track('view',{route:rk}); if(p[0]==='about') track('about',{});}}
}
function bind(){
  bindDial(); bindQ(); bindAV(); bindMU(muPend); muPend=null; bindMore();
  document.querySelectorAll('a[data-go]').forEach(a=>a.addEventListener('click',e=>{e.preventDefault(); const el=document.getElementById(a.dataset.go); if(el) el.scrollIntoView({behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth',block:'start'});}));
  const fcEl=$('#fc'); if(fcEl){let sx=null,sy=0,st=0;
    fcEl.addEventListener('touchstart',e=>{const t=e.changedTouches[0]; sx=t.clientX; sy=t.clientY; st=Date.now();},{passive:true});
    fcEl.addEventListener('touchend',e=>{if(sx===null) return; const t=e.changedTouches[0], dx=t.clientX-sx, dy=t.clientY-sy; sx=null;
      if(Math.abs(dx)<60||Math.abs(dx)<2*Math.abs(dy)||Date.now()-st>800) return;
      if(dx<0){location.hash=fcEl.dataset.next;} else if(fcEl.dataset.prev) location.hash=fcEl.dataset.prev;},{passive:true});
    markSeen(fcEl.dataset.id); track('card',{card:fcEl.dataset.id,action:'seen'});}                                   // a fact counts as seen when it is shown
  document.querySelectorAll('[data-copy]').forEach(b=>b.addEventListener('click',()=>{const el=document.getElementById('cite-'+b.dataset.copy); if(!el) return;
    copyText(el.textContent).then(()=>{b.textContent='Copied'; setTimeout(()=>{b.textContent='Copy';},1800);}).catch(()=>{b.textContent='Select the text and copy it'; setTimeout(()=>{b.textContent='Copy';},3000);});}));
  document.querySelectorAll('[data-theme-btn]').forEach(b=>b.addEventListener('click',()=>{
    const cur=document.documentElement.dataset.theme||(matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
    const next=cur==='dark'?'light':'dark'; document.documentElement.dataset.theme=next; LS.set('ro.theme',next);}));
  const ex=$('#exp'); if(ex) ex.addEventListener('click',()=>{
    const blob=new Blob([JSON.stringify(prog,null,1)],{type:'application/json'}); const a=document.createElement('a');
    a.href=URL.createObjectURL(blob); a.download='ro-physics-progress.json'; document.body.appendChild(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(a.href),1000);});
  const im=$('#imp'), imf=$('#impf'); if(im&&imf){im.addEventListener('click',()=>imf.click());
    imf.addEventListener('change',e=>{const f=e.target.files&&e.target.files[0]; if(!f) return; const r=new FileReader();
      r.onload=()=>{try{const o=JSON.parse(r.result); if(o&&typeof o==='object'&&!Array.isArray(o)){const ids=new Set(DATA.cards.map(c=>c.id)); for(const k of Object.keys(o)) if(ids.has(k)&&o[k]&&typeof o[k]==='object'&&o[k].s) prog[k]={s:1,t:String(o[k].t||'')}; LS.set('ro.cards',prog); route();}}catch(err){alert('That file is not a progress export.');}};
      r.readAsText(f);});}
  const cl=$('#clr'); if(cl) cl.addEventListener('click',()=>{if(confirm('Clear all progress in this browser?')){prog={};LS.set('ro.cards',prog);qs={};reads={};readDirty=false;LS.set('ro.read',reads);muStore={};LS.set('ro.mu',muStore);saveQ();route();}});
}
document.addEventListener('keydown',e=>{
  if(e.metaKey||e.ctrlKey||e.altKey) return;
  if(e.target.closest&&e.target.closest('input,select,textarea')) return;
  const el=$('#fc'); if(!el) return;
  if(e.key===' '||e.key==='ArrowRight'){e.preventDefault(); location.hash=el.dataset.next;}
  else if(e.key==='ArrowLeft'){ if(el.dataset.prev) location.hash=el.dataset.prev; }
});
$('#side').addEventListener('click',e=>{const bt=e.target.closest('.nm'); if(!bt) return; const b=bt.closest('.blk'), n=+b.dataset.dom; document.querySelectorAll('#side .blk.pt').forEach(x=>x.classList.remove('pt')); openDom(b.classList.contains('open')?0:n); sideManual=true;});
window.addEventListener('scroll',()=>{ if(progMode!=='scroll'||progRaf) return; progRaf=requestAnimationFrame(()=>{progRaf=0; refreshProgress();}); },{passive:true});
window.addEventListener('resize',()=>refreshProgress());
window.addEventListener('pagehide',flushReads);
window.addEventListener('hashchange',route);
$('#jump').addEventListener('change',e=>{location.hash=e.target.value;});
route();

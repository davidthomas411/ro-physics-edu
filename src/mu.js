// ---------------------------------------------------------------- MU calculation module: practice cases and the full beam data tables
const MUD=()=>DATA.mu.energies, MUC=()=>DATA.mu.cases;
let muStore=LS.get('ro.mu',{}); if(!muStore||typeof muStore!=='object'||Array.isArray(muStore)) muStore={};
const muSave=()=>{LS.set('ro.mu',muStore); if(typeof refreshProgress==='function') refreshProgress();};
const muDone=id=>{const v=muStore[id]; return !!(v&&typeof v==='object'&&(v.n>0||v.v));};
let muRandCase=null, muLevel='Moderate';

// ---- the engine: the printed tables are read with the interpolation one would do by hand
const muRect=(a,b)=>2*a*b/(a+b), muR=(x,n)=>Math.round(x*Math.pow(10,n))/Math.pow(10,n);
function muBracket(xs,x){const L=xs.length; if(x<=xs[0]) return [0,0,0]; if(x>=xs[L-1]) return [L-1,L-1,0]; let i=0; while(xs[i+1]<x) i++; return [i,i+1,(x-xs[i])/(xs[i+1]-xs[i])];}
function muRead(T,kind,d,s){const ds=kind==='pdd'?T.depths:T.tmr_depths, rows=kind==='pdd'?T.pdd:T.tmr, [c0,c1,tc]=muBracket(T.sizes,s), rv=r=>rows[r][c0]+(rows[r][c1]-rows[r][c0])*tc, [r0,r1,tr]=muBracket(ds,d); return rv(r0)+(rv(r1)-rv(r0))*tr;}
function muLine(T,key,s){const [i,j,t]=muBracket(T.sizes,s); return T[key][i]+(T[key][j]-T[key][i])*t;}
function muWF(T,ang,s){const [i,j,t]=muBracket(T.wf_sizes,s), r=T.wf[ang]; return r[i]+(r[j]-r[i])*t;}
function muSolve(c){
  const T=MUD()[c.E], dm=T.dmax, ssd=c.tech==='SSD', f=ssd?c.f:100, sq=muR(muRect(c.field[0],c.field[1]),2), scs=muR(ssd?sq*100/f:sq,2);
  const o={c,T,dm,f,ssd,sq,scs,rect:c.field[0]!==c.field[1],proj:ssd&&f!==100};
  o.Df=muR(c.dose*c.w,2); o.Sc=muR(muLine(T,'sc',scs),4); o.Sp=muR(muLine(T,'sp',sq),4);
  o.DD=ssd?muR(muRead(T,'pdd',c.d,sq),2):muR(muRead(T,'tmr',c.d,sq),4);
  o.F=o.proj?muR(Math.pow(((f+dm)/(f+c.d))/((100+dm)/(100+c.d)),2),4):1;
  o.dcal=c.cal==='SSD'?100+dm:100; o.dist=ssd?f+dm:100; o.ISF=muR(Math.pow(o.dcal/o.dist,2),4);
  o.WF=c.wedge?muR(muWF(T,c.wedge,scs),4):1; o.TF=c.tray?T.tf:1;
  o.perMU=o.Sc*o.Sp*(ssd?o.DD/100:o.DD)*o.F*o.ISF*o.WF*o.TF; o.mu=o.Df/o.perMU; return o;
}
// ---- the entries of the worksheet for a case: what to read or calculate, the answer, the tolerance, and a hint that says where to look without giving the value
const muNote=(xs,x)=>{const [i,j,t]=muBracket(xs,x); return t===0||t===1?'':`, interpolated between ${xs[i]} and ${xs[j]}`;};
function muSlots(o){
  const c=o.c, T=o.T, S=[], pdd=o.ssd, nm=pdd?'PDD':'TMR', fld=o.ssd?'at the surface':'at the isocenter';
  if(c.w<1) S.push({k:'Df',sym:'D<sub>f</sub>',name:'dose from this field (cGy)',exp:o.Df,rel:0.003,dec:1,hint:`This field gives ${Math.round(c.w*100)}% of the ${c.dose} cGy.`});
  if(o.rect) S.push({k:'sq',sym:'A',name:'equivalent square of the field (cm)',exp:o.sq,abs:0.06,dec:2,hint:'The equivalent square of an a × b rectangle is 2ab / (a + b).'});
  if(o.proj) S.push({k:'scs',sym:'A<sub>c</sub>',name:'collimator opening, equivalent square at 100 cm (cm)',exp:o.scs,abs:0.06,dec:2,hint:`The collimator opening is the field ${fld} × 100 / SSD, as an equivalent square.`});
  S.push({k:'Sc',sym:'S<sub>c</sub>',name:'collimator scatter factor',exp:o.Sc,rel:0.0025,dec:4,hint:`S<sub>c</sub> is read for the collimator opening, ${o.scs} cm${muNote(T.sizes,o.scs)}.`});
  S.push({k:'Sp',sym:'S<sub>p</sub>',name:'phantom scatter factor',exp:o.Sp,rel:0.0025,dec:4,hint:`S<sub>p</sub> is read for the field that irradiates the phantom, ${o.sq} cm ${fld}${muNote(T.sizes,o.sq)}.`});
  if(pdd) S.push({k:'DD',sym:'PDD',name:'percent depth dose, SSD 100 cm table (%)',exp:o.DD,rel:0.005,dec:2,hint:`Read the PDD table at ${c.d} cm depth${muNote(T.depths,c.d)} for the ${o.sq} cm field${muNote(T.sizes,o.sq)}. The table is in percent.`});
  else S.push({k:'DD',sym:'TMR',name:'tissue maximum ratio',exp:o.DD,rel:0.004,dec:4,hint:`Read the TMR table at ${c.d} cm depth${muNote(T.tmr_depths,c.d)} for the ${o.sq} cm field${muNote(T.sizes,o.sq)}.`});
  if(o.proj) S.push({k:'F',sym:'F',name:'Mayneord F factor, SSD 100 cm to SSD '+o.f+' cm',exp:o.F,rel:0.003,dec:4,hint:`F = [ ((f + d<sub>max</sub>)/(f + d)) ÷ ((100 + d<sub>max</sub>)/(100 + d)) ]², with f = ${o.f} cm, d = ${c.d} cm, d<sub>max</sub> = ${o.dm} cm.`});
  S.push({k:'ISF',sym:'ISF',name:'inverse-square term',exp:o.ISF,rel:0.003,dec:4,hint:`ISF = (d<sub>cal</sub> / distance)². With ${c.cal==='SSD'?'an SSD':'a SAD'} calibration d<sub>cal</sub> = ${c.cal==='SSD'?'100 + d<sub>max</sub> = '+o.dcal:'100 cm'}, and the source-to-point distance is ${o.ssd?'f + d<sub>max</sub> = '+o.dist:'100 cm'}.`});
  if(c.wedge) S.push({k:'WF',sym:'WF',name:`wedge factor, ${c.wedge}° wedge`,exp:o.WF,rel:0.003,dec:4,hint:`Read the ${c.wedge}° row of the wedge table for the collimator field, ${o.scs} cm${muNote(T.wf_sizes,o.scs)}.`});
  if(c.tray) S.push({k:'TF',sym:'TF',name:'tray factor',exp:o.TF,rel:0.002,dec:3,hint:'The tray factor is a single value for the energy.'});
  S.push({k:'MU',sym:'MU',name:'monitor units for this field',exp:o.mu,rel:0.01,dec:0,hint:`MU = D<sub>f</sub> ÷ (dose per MU). Check the factors above first.`,final:true});
  return S;
}
function muFormula(o){const c=o.c, t=['S<sub>c</sub>','S<sub>p</sub>',o.ssd?'PDD/100':'TMR']; if(o.proj) t.push('F'); t.push('ISF'); if(c.wedge) t.push('WF'); if(c.tray) t.push('TF'); return `MU = ${c.w<1?'D<sub>f</sub>':'D'} ÷ ( ${t.join(' × ')} )`;}
function muSteps(o){
  const c=o.c, T=o.T, f4=(x,n)=>x.toFixed(n), st=[], fld=o.ssd?'at the surface':'at the isocenter';
  st.push(c.w<1?`Dose from this field: ${c.dose} × ${c.w} = <b>${f4(o.Df,1)} cGy</b>.`:`Dose to the point: <b>${f4(o.Df,0)} cGy</b>.`);
  if(o.rect) st.push(`Equivalent square of ${c.field[0]} × ${c.field[1]} cm: 2 × ${c.field[0]} × ${c.field[1]} / (${c.field[0]} + ${c.field[1]}) = <b>${f4(o.sq,2)} cm</b>.`);
  if(o.proj) st.push(`Collimator opening at 100 cm: ${f4(o.sq,2)} × 100 / ${o.f} = <b>${f4(o.scs,2)} cm</b>.`);
  st.push(`S<sub>c</sub> for ${f4(o.scs,2)} cm${muNote(T.sizes,o.scs)}: <b>${f4(o.Sc,4)}</b>.`);
  st.push(`S<sub>p</sub> for ${f4(o.sq,2)} cm ${fld}${muNote(T.sizes,o.sq)}: <b>${f4(o.Sp,4)}</b>.`);
  st.push(o.ssd?`PDD at ${c.d} cm${muNote(T.depths,c.d)} for ${f4(o.sq,2)} cm: <b>${f4(o.DD,2)}%</b>.`:`TMR at ${c.d} cm${muNote(T.tmr_depths,c.d)} for ${f4(o.sq,2)} cm: <b>${f4(o.DD,4)}</b>.`);
  if(o.proj) st.push(`Mayneord F = [ ((${o.f} + ${o.dm})/(${o.f} + ${c.d})) ÷ ((100 + ${o.dm})/(100 + ${c.d})) ]² = <b>${f4(o.F,4)}</b>.`);
  st.push(`Inverse-square term: (${f4(o.dcal,1)} / ${f4(o.dist,1)})² = <b>${f4(o.ISF,4)}</b> (${c.cal==='SSD'?'SSD':'SAD'} calibration, ${o.ssd?'SSD technique':'SAD technique'}).`);
  if(c.wedge) st.push(`Wedge factor, ${c.wedge}° wedge, collimator field ${f4(o.scs,2)} cm${muNote(T.wf_sizes,o.scs)}: <b>${f4(o.WF,4)}</b>.`);
  if(c.tray) st.push(`Tray factor: <b>${f4(o.TF,3)}</b>.`);
  const parts=[f4(o.Sc,4),f4(o.Sp,4),o.ssd?f4(o.DD/100,4):f4(o.DD,4)]; if(o.proj) parts.push(f4(o.F,4)); parts.push(f4(o.ISF,4)); if(c.wedge) parts.push(f4(o.WF,4)); if(c.tray) parts.push(f4(o.TF,3));
  st.push(`Dose per MU = ${parts.join(' × ')} = <b>${f4(o.perMU,4)} cGy/MU</b> (the calibration is 1.000 cGy/MU).`);
  st.push(`MU = ${f4(o.Df,1)} / ${f4(o.perMU,4)} = <b>${f4(o.mu,1)}</b>, so about <b>${Math.round(o.mu)} MU</b>.`);
  return st;
}
// ---- a random case at a chosen level
function muRandom(level){
  const pick=a=>a[Math.floor(Math.random()*a.length)], E=pick([6,10,15,18]), T=MUD()[E], tech=pick(['SSD','SAD']);
  const sq=pick(level==='Easy'?[5,8,10,12,15,20]:[5,6,7,8,9,10,12,15,18,20,25]), rect=level!=='Easy'&&Math.random()<0.4;
  let field=[sq,sq]; if(rect){const a=pick([6,8,10,12,15,18]), b=pick([6,8,10,12,15,18,20]); field=[a,b];}
  const depths=level==='Easy'?[5,6,8,10,12,15,20].filter(d=>d>T.dmax):[];
  const d=level==='Easy'?pick(depths):Math.max(T.dmax+1,Math.round((T.dmax+1+Math.random()*(level==='Challenging'?22:14))*2)/2);
  const c={level,E,tech,f:100,cal:'SSD',field,d,dose:level==='Easy'?pick([180,200,250,300]):pick([150,160,180,200,220,240,250,300]),w:1,wedge:0,tray:false,ctx:'A random case.',note:'',id:'r'};
  const eq=muRect(field[0],field[1]); const feats=[];
  if(level!=='Easy'){feats.push(()=>{c.w=0.5; c.ctx='One field of an equally weighted opposed pair.';}); if(eq<=15) feats.push(()=>{c.wedge=pick([15,30,45,60]);}); feats.push(()=>{c.tray=true;}); if(tech==='SSD') feats.push(()=>{c.f=pick([90,110,120,130]);}); feats.push(()=>{c.cal='SAD';});}
  const n=level==='Moderate'?1:(level==='Challenging'?2:0); const pool=feats.slice(); for(let i=0;i<n&&pool.length;i++) pool.splice(Math.floor(Math.random()*pool.length),1)[0]();
  if(c.wedge&&muRect(...c.field)*100/(c.tech==='SSD'?c.f:100)>20){c.wedge=0;}
  return c;
}
// ---- tables
const muF=(v,n)=>(+v).toFixed(n);
function muTbl(T,kind,o){      // o: {pick:true} makes the cells buttons that fill the matching entry
  const pk=o&&o.pick, cell=(v,slot,r,cc,n)=>pk?`<td><button type="button" class="mcell" data-slot="${slot}" data-v="${muF(v,n)}" data-r="${r}" data-c="${cc}" title="${muF(v,n)}">${muF(v,n)}</button></td>`:`<td>${muF(v,n)}</td>`;
  const head=(first,cols)=>`<thead><tr><th scope="col">${first}</th>${cols.map(x=>`<th scope="col">${x}</th>`).join('')}</tr></thead>`, sz=T.sizes.map(s=>`${s}×${s}`);
  if(kind==='pdd') return `<table class="mut">${head('Depth (cm)',sz)}<tbody>${T.depths.map((d,r)=>`<tr${d===T.dmax?' class="dmx"':''}><th scope="row">${d}${d===T.dmax?' <span class="muted">d<sub>max</sub></span>':''}</th>${T.pdd[r].map((v,cc)=>cell(v,'DD',r,cc,1)).join('')}</tr>`).join('')}</tbody></table>`;
  if(kind==='tmr') return `<table class="mut">${head('Depth (cm)',sz)}<tbody>${T.tmr_depths.map((d,r)=>`<tr${d===T.dmax?' class="dmx"':''}><th scope="row">${d}${d===T.dmax?' <span class="muted">d<sub>max</sub></span>':''}</th>${T.tmr[r].map((v,cc)=>cell(v,'DD',r,cc,3)).join('')}</tr>`).join('')}</tbody></table>`;
  if(kind==='scat'){const scp=T.sc.map((v,i)=>v*T.sp[i]); return `<table class="mut">${head('Field size (cm)',sz)}<tbody><tr><th scope="row">S<sub>c</sub></th>${T.sc.map((v,cc)=>cell(v,'Sc',0,cc,3)).join('')}</tr><tr><th scope="row">S<sub>p</sub></th>${T.sp.map((v,cc)=>cell(v,'Sp',1,cc,3)).join('')}</tr>${pk?'':`<tr><th scope="row">S<sub>cp</sub></th>${scp.map(v=>`<td>${muF(v,3)}</td>`).join('')}</tr>`}</tbody></table>`;}
  if(kind==='wf') return `<table class="mut">${head('Wedge angle',T.wf_sizes.map(s=>`${s}×${s}`))}<tbody>${T.wf_angles.map((a,r)=>`<tr><th scope="row">${a}°</th>${T.wf[a].map((v,cc)=>cell(v,'WF',r,cc,3)).join('')}</tr>`).join('')}</tbody></table>`;
  if(kind==='tf') return `<table class="mut"><thead><tr><th scope="col">Blocking tray</th></tr></thead><tbody><tr>${cell(T.tf,'TF',0,0,3)}</tr></tbody></table>`;
  return '';
}
const muWrap=h=>`<div class="tblwrap">${h}</div>`;
// ---- the full tables for one energy
function muTablesView(E){
  const T=MUD()[E]||MUD()[6], en=Object.keys(MUD()).map(Number).sort((a,b)=>a-b);
  const nav=`<nav class="mu-nav" aria-label="MU calculation"><a href="#mu">Practice</a><a class="on" href="#mu/tables/${T.energy}">Tables</a></nav>`;
  const picker=`<div class="mu-en" role="group" aria-label="Energy">${en.map(e=>`<a class="btn${e===T.energy?' primary':''}" href="#mu/tables/${e}" aria-current="${e===T.energy}">${e} MV</a>`).join('')}</div>`;
  const isf=(cal,tech,f)=>muF(Math.pow((cal==='SSD'?100+T.dmax:100)/(tech==='SSD'?f+T.dmax:100),2),4);
  const conv=`<table class="mut conv"><thead><tr><th scope="col">Inverse-square term, ${T.energy} MV (d<sub>max</sub> = ${T.dmax} cm)</th><th scope="col">SSD calibration</th><th scope="col">SAD calibration</th></tr></thead><tbody>
    <tr><th scope="row">SAD technique</th><td>${isf('SSD','SAD')}</td><td>${isf('SAD','SAD')}</td></tr>
    <tr><th scope="row">SSD technique, SSD 100 cm</th><td>${isf('SSD','SSD',100)}</td><td>${isf('SAD','SSD',100)}</td></tr>
    <tr><th scope="row">SSD technique, SSD 110 cm</th><td>${isf('SSD','SSD',110)}</td><td>${isf('SAD','SSD',110)}</td></tr>
    <tr><th scope="row">SSD technique, SSD 120 cm</th><td>${isf('SSD','SSD',120)}</td><td>${isf('SAD','SSD',120)}</td></tr></tbody></table>`;
  return `${nav}<h1>MU calculation</h1>${picker}
  <p class="small">Illustrative data for teaching, not measured: d<sub>max</sub> ${T.dmax} cm, PDD(10 cm, 10 × 10) = ${T.pdd10}%, TPR<sub>20,10</sub> = ${T.tpr}. Field sizes are equivalent squares, in cm. Calibration: 1.000 cGy/MU at d<sub>max</sub> for 10 × 10 cm.</p>
  <h2>Percent depth dose, SSD 100 cm</h2><p class="small">Field size at the surface. Between the surface and d<sub>max</sub> the dose builds up.</p>${muWrap(muTbl(T,'pdd'))}
  <h2>Tissue maximum ratio</h2><p class="small">Field size at the point. The table starts at d<sub>max</sub>, where the TMR is 1.</p>${muWrap(muTbl(T,'tmr'))}
  <h2>Scatter factors</h2><p class="small">S<sub>c</sub> by the collimator opening projected to 100 cm, S<sub>p</sub> by the field that irradiates the phantom, and their product S<sub>cp</sub>.</p>${muWrap(muTbl(T,'scat'))}
  <h2>Wedge factors</h2><p class="small">Physical wedges, by the collimator field size.</p>${muWrap(muTbl(T,'wf'))}
  <h2>Tray factor</h2>${muWrap(muTbl(T,'tf'))}
  <h2>Inverse-square terms</h2>${muWrap(conv)}
  <h2>Formulas</h2>
  <ul class="small"><li>Equivalent square of an a × b rectangle: 2ab / (a + b).</li><li>SSD technique: dose per MU = S<sub>c</sub>(A<sub>c</sub>) · S<sub>p</sub>(A) · PDD/100 · F · ISF · WF · TF, with F = 1 at SSD 100 cm.</li><li>SAD technique: dose per MU = S<sub>c</sub>(A) · S<sub>p</sub>(A) · TMR(d, A) · ISF · WF · TF.</li>
  <li>Mayneord F = [ ((f + d<sub>max</sub>)/(f + d)) ÷ ((100 + d<sub>max</sub>)/(100 + d)) ]² converts a PDD from SSD 100 cm to SSD f.</li><li>MU = dose from the field ÷ dose per MU.</li></ul>`;
}
// ---- the practice page for one case
function muStatus(id){const v=muStore[id]; return !v?'':(v.ok?'ok':(v.v?'view':'try'));}
function muPractice(arg){
  if(!arg){const last=LS.get('ro.mulast',0), first=MUC().find(c=>!muDone(c.id)); return {redirect:'#mu/'+(MUC().some(c=>c.id===last)?last:(first||MUC()[0]).id)};}
  let c; if(arg==='r'){ if(!muRandCase) muRandCase=muRandom(muLevel); c=muRandCase; } else { c=MUC().find(x=>x.id===+arg); if(!c) return {redirect:'#mu'}; LS.set('ro.mulast',c.id); }
  const o=muSolve(c), S=muSlots(o), T=o.T, idx=arg==='r'?0:MUC().findIndex(x=>x.id===c.id), n=MUC().length, pv=idx>0?MUC()[idx-1]:null, nx=idx<n-1?MUC()[idx+1]:null;
  const ssd=o.ssd, field=c.field[0]===c.field[1]?`${c.field[0]} × ${c.field[0]}`:`${c.field[0]} × ${c.field[1]}`;
  const givens=[['Beam',`${c.E} MV photons, ${ssd?`SSD technique, SSD ${c.f} cm`:'SAD technique, SAD 100 cm'}`],['Field',`${field} cm ${ssd?'at the surface':'at the isocenter'}`],['Point',`${c.d} cm depth`],['Dose',`${c.dose} cGy to the point${c.w<1?`; this field delivers ${Math.round(c.w*100)}% of it`:''}`]];
  const mods=[c.wedge?`${c.wedge}° wedge`:'',c.tray?'blocking tray':''].filter(Boolean); if(mods.length) givens.push(['In the beam',mods.join(' and ')]);
  givens.push(['Calibration',`1 cGy/MU at d<sub>max</sub> with the ${c.cal==='SSD'?'surface':'point'} at 100 cm (${c.cal} calibration)`]);
  const chips=MUC().map(x=>`<a class="mc ${muStatus(x.id)}${x.id===c.id&&arg!=='r'?' on':''}" href="#mu/${x.id}" title="Case ${x.id}${muStatus(x.id)==='ok'?', correct':''}" aria-label="Case ${x.id}${muStatus(x.id)==='ok'?', correct':''}">${x.id}</a>`).join('');
  const slots=S.map(s=>`<div class="mu-slot${s.final?' final':''}" data-k="${s.k}"><label for="mu-${s.k}"><b>${s.sym}</b> <span>${s.name}</span></label><span class="mu-in"><input id="mu-${s.k}" inputmode="decimal" autocomplete="off" aria-describedby="muh-${s.k}"><span class="st" aria-hidden="true"></span></span><p class="mu-h" id="muh-${s.k}" hidden></p></div>`).join('');
  const kinds=[[ssd?'pdd':'tmr',ssd?'PDD':'TMR'],['scat','S<sub>c</sub>, S<sub>p</sub>']]; if(c.wedge) kinds.push(['wf','Wedge']); if(c.tray) kinds.push(['tf','Tray']);
  const tabs=kinds.map(([k,l],i)=>`<button type="button" class="mtab" role="tab" aria-selected="${i===0}" data-tab="${k}">${l}</button>`).join(''), panes=kinds.map(([k],i)=>`<div class="mpane" data-pane="${k}"${i?' hidden':''}>${muWrap(muTbl(T,k,{pick:true}))}</div>`).join('');
  const lvName={Easy:'Open fields',Moderate:'One modifier',Challenging:'Two modifiers'}, lv=['Easy','Moderate','Challenging'].map(l=>`<button type="button" class="mrand${l===muLevel?' on':''}" data-lvl="${l}" title="${l==='Easy'?'Tabulated field sizes and depths, no wedge, tray, extended SSD, opposed pair, or SAD calibration':'Wedge, tray, extended SSD, opposed pair, or SAD calibration, with ordinary or interpolated values'}">${lvName[l]}</button>`).join('');
  return {html:`<nav class="mu-nav" aria-label="MU calculation"><a class="on" href="#mu">Practice</a><a href="#mu/tables/${c.E}">Tables</a></nav><h1>MU calculation</h1>
  <div class="mu-chips" role="navigation" aria-label="Cases">${chips}</div><p class="small mu-rr">Random case: ${lv}</p>
  <article class="mu-case" data-id="${c.id}"><p class="meta">${arg==='r'?'Random case':`Case ${c.id} of ${n}`}</p>${c.ctx?`<p class="mu-ctx">${c.ctx}</p>`:''}
  <dl class="mu-dl">${givens.map(([a,b])=>`<div><dt>${a}</dt><dd>${b}</dd></div>`).join('')}</dl></article>
  <section class="mu-ws" aria-label="Worksheet"><p class="mu-eq">${muFormula(o)}</p><p class="small">Read each value from the tables below, or work it out, and type it in. Clicking a table cell fills the matching entry.</p>${slots}
  <div class="mu-acts"><button type="button" class="btn primary" id="mu-check">Check</button><button type="button" class="btn" id="mu-sol">Show solution</button></div><div class="mu-fb" id="mu-fb" role="status" aria-live="polite"></div><div class="mu-solution" id="mu-solution" hidden></div></section>
  <section class="mu-tbl" aria-label="Tables"><div class="mu-tabs" role="tablist">${tabs}<a class="small" href="#mu/tables/${c.E}">All ${c.E} MV tables</a></div>${panes}</section>
  <div class="endrow">${pv?`<a class="btn" href="#mu/${pv.id}">Previous</a>`:''}${nx?`<a class="btn primary" href="#mu/${nx.id}">Next case</a>`:''}<button type="button" class="btn" id="mu-new">New random case</button></div>`, o, S, c};
}
let muCtx=null;
function bindMU(ctx){
  const root=$('#main'); if(!root.querySelector('.mu-ws')||!ctx) return; const {o,S,c}=ctx; muCtx=ctx;
  const num=el=>{const v=parseFloat(String(el.value).replace(',','.')); return Number.isFinite(v)?v:NaN;};
  root.querySelectorAll('.mtab').forEach(b=>b.addEventListener('click',()=>{root.querySelectorAll('.mtab').forEach(x=>x.setAttribute('aria-selected',String(x===b))); root.querySelectorAll('.mpane').forEach(p=>p.hidden=p.dataset.pane!==b.dataset.tab);}));
  root.querySelectorAll('.mcell').forEach(b=>b.addEventListener('click',()=>{const inp=$('#mu-'+b.dataset.slot); if(!inp) return; inp.value=b.dataset.v; root.querySelectorAll(`.mcell[data-slot="${b.dataset.slot}"]`).forEach(x=>x.classList.toggle('pick',x===b)); const sl=inp.closest('.mu-slot'); sl.classList.remove('bad','good'); sl.querySelector('.st').textContent=''; sl.querySelector('.mu-h').hidden=true;}));
  root.querySelectorAll('.mu-slot input').forEach(i=>{i.addEventListener('input',()=>{const sl=i.closest('.mu-slot'); sl.classList.remove('bad','good'); sl.querySelector('.st').textContent=''; sl.querySelector('.mu-h').hidden=true; root.querySelectorAll(`.mcell[data-slot="${sl.dataset.k}"]`).forEach(x=>x.classList.toggle('pick',x.dataset.v===i.value));}); i.addEventListener('keydown',e=>{if(e.key==='Enter'){e.preventDefault(); $('#mu-check').click();}});});
  const fb=$('#mu-fb');
  $('#mu-check').addEventListener('click',()=>{
    let empty=0, wrong=0; const bad=[];
    S.forEach(s=>{const sl=root.querySelector(`.mu-slot[data-k="${s.k}"]`), inp=sl.querySelector('input'), v=num(inp), h=sl.querySelector('.mu-h'), st=sl.querySelector('.st'); sl.classList.remove('bad','good'); h.hidden=true;
      if(!Number.isFinite(v)){empty++; return;}
      const tol=s.abs!==undefined?s.abs:Math.abs(s.exp)*s.rel, ok=Math.abs(v-s.exp)<=Math.max(tol,s.k==='MU'?0.5:0);
      if(ok){sl.classList.add('good'); st.textContent='✓';} else {wrong++; bad.push(s.k); sl.classList.add('bad'); st.textContent='✗'; let m=s.hint; if(s.k==='DD'&&o.ssd&&v<=2) m='The PDD table is in percent: enter 83.7, not 0.837. '+m; if(s.k==='MU'&&!bad.slice(0,-1).length) m=`Expected about ${Math.round(s.exp)} MU. ${m}`; h.innerHTML=m; h.hidden=false;}});
    if(empty){fb.className='mu-fb'; fb.textContent=`Fill in all ${S.length} entries, then check.`; return;}
    track('mu',{case:String(c.id),action:'tried'});
    const rec=muStore[c.id]||{}; if(c.id!=='r'){muStore[c.id]={ok:rec.ok||!wrong,v:rec.v||false,n:(rec.n||0)+1,t:new Date().toISOString()}; muSave(); const ch=root.querySelector(`.mc[href="#mu/${c.id}"]`); if(ch){ch.className='mc '+muStatus(c.id)+' on';}}
    fb.className='mu-fb '+(wrong?'bad':'good'); fb.textContent=wrong?(bad.length===1&&bad[0]==='MU'?'The factors are right. Recheck the final division.':(bad.includes('MU')?`${wrong-1} factor${wrong-1===1?' is':'s are'} wrong, and so is the MU. Each hint says where to look.`:`${wrong} entr${wrong===1?'y is':'ies are'} wrong, though the MU is right. Each hint says where to look.`)):`All ${S.length} entries are correct: ${Math.round(o.mu)} MU.`;
  });
  $('#mu-sol').addEventListener('click',()=>{track('mu',{case:String(c.id),action:'solution'}); const box=$('#mu-solution'); box.innerHTML=`<h2>Solution</h2><ol>${muSteps(o).map(s=>`<li>${s}</li>`).join('')}</ol>${c.note?`<p class="small"><b>Note.</b> ${c.note}</p>`:''}`; box.hidden=false;
    if(c.id!=='r'){const rec=muStore[c.id]||{}; muStore[c.id]={ok:!!rec.ok,v:true,n:rec.n||0,t:new Date().toISOString()}; muSave(); const ch=root.querySelector(`.mc[href="#mu/${c.id}"]`); if(ch) ch.className='mc '+muStatus(c.id)+' on';}
    root.querySelectorAll('.mcell').forEach(b=>b.classList.remove('near'));
    const near=(kind,vals)=>{vals.forEach(([r,cc])=>{const b=root.querySelector(`.mcell[data-slot="${kind}"][data-r="${r}"][data-c="${cc}"]`); if(b) b.classList.add('near');});};
    const T=o.T, pair=(xs,x)=>{const [i,j]=muBracket(xs,x); return i===j?[i]:[i,j];};
    const cols=pair(T.sizes,o.sq), rows=pair(o.ssd?T.depths:T.tmr_depths,c.d); near('DD',rows.flatMap(r=>cols.map(cc=>[r,cc]))); near('Sc',pair(T.sizes,o.scs).map(cc=>[0,cc])); near('Sp',pair(T.sizes,o.sq).map(cc=>[1,cc]));
    if(c.wedge){const ri=T.wf_angles.indexOf(c.wedge); near('WF',pair(T.wf_sizes,o.scs).map(cc=>[ri,cc]));} if(c.tray) near('TF',[[0,0]]);
    box.scrollIntoView({block:'nearest'});});
  root.querySelectorAll('.mrand').forEach(b=>b.addEventListener('click',()=>{muLevel=b.dataset.lvl; muRandCase=muRandom(muLevel); if(location.hash==='#mu/r') route(); else location.hash='#mu/r';}));
  $('#mu-new').addEventListener('click',()=>{muRandCase=muRandom(c.level&&['Easy','Moderate','Challenging'].includes(c.level)?c.level:muLevel); muLevel=muRandCase.level; if(location.hash==='#mu/r') route(); else location.hash='#mu/r';});
}

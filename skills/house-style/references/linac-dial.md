# Linac dial

Navigation built around the rotating linac illustration, used on the ABR study site's year pages and progress ring. For radiation oncology projects only; the illustration comes from the group's retreat poster.

## Assets

`assets/linac/base.webp`, `gantry.webp`, `couch.webp`: transparent 1000 × 1000 layers. Draw in that order, with only the gantry layer rotating. The pivot is at 49.4% and 47% of the image (pixel 494, 470). Inline them as data URIs.

## Rules

- The gantry cannot pass 180°. Keep every angle between −180° and +180° and always travel through 0. Never animate to 360°.
- Idle motion: sweep 0 → 180 → 0 → −180 → 0 over 220 s, ease-in-out on each leg (CSS below).
- Sections are equal: N categories get 360/N degrees each, starting at the top (−90°) and running clockwise, with a 3° gap. Arcs are 9 px strokes in `--line`, `--ink` on hover or focus. Names go outside the arc (text anchor by side; labels on the top stack upward), numerals inside, a hairline ring at radius − 26.
- Hover, focus, or touch on a section turns the gantry toward it: read the live angle, cancel the sweep, set the live angle with transitions off, force a reflow, turn transitions on, then set the target. At exactly ±180 the sign comes from the animation phase. This avoids a jump and keeps the route through 0.
- The progress ring uses fraction × 180 for the gantry and a 5 px stroke that fills clockwise.
- Desktop viewBox 1120 × 740: center (560, 370), radius 245, image 500, label offset 30, name 24 px, small 13 px, numeral 24 px. Phone viewBox 760 × 780: center (380, 390), radius 200, image 360, offset 26, name 26 px, small 17 px, numeral 22 px, long names split at " · ". Render the phone dial separately; do not hide the dial on phones.
- Honor `prefers-reduced-motion`: no sweep, no transition.

## Code (tested; adapt `DATA.cats`, `catCards`, `knownCount`, `LINAC`, `esc` to the project)

```js
function catAngles(y){const A0=-90,A1=270,gap=3,span=(A1-A0)/DATA.cats.length;return DATA.cats.map((c,i)=>[A0+i*span+gap/2,A0+(i+1)*span-gap/2]);}
const rad=d=>d*Math.PI/180;
const lim=a=>{a=((a%360)+360)%360;return a>180?a-360:a;};
function arcPath(cx,cy,r,a0,a1){const x0=cx+r*Math.cos(rad(a0)),y0=cy+r*Math.sin(rad(a0)),x1=cx+r*Math.cos(rad(a1)),y1=cy+r*Math.sin(rad(a1));return `M${x0.toFixed(1)},${y0.toFixed(1)} A${r},${r} 0 ${a1-a0>180?1:0} 1 ${x1.toFixed(1)},${y1.toFixed(1)}`;}
function linacGroup(cx,cy,size,angle){const s=size,x=cx-0.494*s,y=cy-0.47*s;return `<image href="${LINAC.base}" x="${x}" y="${y}" width="${s}" height="${s}"/><g class="gantry" style="transform:rotate(${lim(angle)}deg)"><image href="${LINAC.gantry}" x="${x}" y="${y}" width="${s}" height="${s}"/></g><image href="${LINAC.couch}" x="${x}" y="${y}" width="${s}" height="${s}"/>`;}
function dialSVG(yn, mobile){
  const y=yearOf(yn); const angs=catAngles(y);
  const G = mobile ? {vw:760,vh:780,cx:380,cy:390,R:200,S:360,fn:26,fs:17,fnum:22,lo:26} : {vw:1120,vh:740,cx:560,cy:370,R:245,S:500,fn:24,fs:13,fnum:24,lo:30};
  const {cx,cy,R,S}=G; let out=[`<circle class="ring" cx="${cx}" cy="${cy}" r="${R-26}"/>`];
  DATA.cats.forEach((c,ci)=>{
    const [a0,a1]=angs[ci], am=(a0+a1)/2, cards=catCards(y,c.n), k=knownCount(cards);
    const cs=Math.cos(rad(am)), sn=Math.sin(rad(am));
    const anchor = cs>0.3?'start':(cs<-0.3?'end':'middle');
    const lx=cx+(R+G.lo)*cs, ly=cy+(R+G.lo)*sn, nx=cx+(R-62)*cs, ny=cy+(R-62)*sn;
    const lines = mobile && c.short.length>14 ? c.short.split(' · ') : [c.short];
    const lh=G.fn*1.05;
    const nameY = sn<-0.3 ? ly-6-(lines.length-1)*lh : ly+16;   // top labels stack upward, away from the arc
    const smY = sn<-0.3 ? nameY-lh : ly-10;
    const name = lines.map((t,i)=>`<tspan x="${lx.toFixed(1)}" dy="${i?lh:0}">${esc(t)}</tspan>`).join('');
    out.push(`<a href="#y${yn}/c${c.n}" class="seg" data-ang="${am.toFixed(1)}"><path d="${arcPath(cx,cy,R,a0,a1)}"/>
      <text class="num" style="font-size:${G.fnum}px" x="${nx.toFixed(1)}" y="${(ny+8).toFixed(1)}" text-anchor="middle">${c.n}</text>
      <text class="sm" style="font-size:${G.fs}px" x="${lx.toFixed(1)}" y="${smY.toFixed(1)}" text-anchor="${anchor}">${cards.length} cards · ${k} seen</text>
      <text class="name" style="font-size:${G.fn}px" x="${lx.toFixed(1)}" y="${nameY.toFixed(1)}" text-anchor="${anchor}">${name}</text></a>`);
  });
  return `<svg viewBox="0 0 ${G.vw} ${G.vh}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="ABR categories">${linacGroup(cx,cy,S,0)}${out.join('')}</svg>`;
}
function ringSVG(frac){const r=46,c=2*Math.PI*r;return `<svg class="ring" viewBox="0 0 120 120" aria-hidden="true"><circle class="track" cx="60" cy="60" r="${r}"/><circle class="fill" id="ringfill" cx="60" cy="60" r="${r}" stroke-dasharray="${c.toFixed(1)}" stroke-dashoffset="${(c*(1-frac)).toFixed(1)}"/>${linacGroup(60,60,84,frac*180)}</svg>`;}
```

Hover handler (inside the function that binds events after each render):

```js
document.querySelectorAll('.dial').forEach(dial=>{const g=dial.querySelector('.gantry');
    const live=()=>{const t=getComputedStyle(g).transform; if(!t||t==='none') return 0; const v=t.match(/matrix\(([^)]+)\)/)[1].split(',').map(Number); let a=Math.atan2(v[1],v[0])*180/Math.PI; if(Math.abs(a)>179.9){const an=g.getAnimations()[0]; a=an&&(an.currentTime%220000)>=110000?-180:180;} return Math.round(a*100)/100;};
    dial.querySelectorAll('.seg').forEach(s=>{const turn=()=>{const from=live(), to=lim((+s.dataset.ang)+90); dial.classList.remove('spin'); g.style.transition='none'; g.style.transform=`rotate(${from}deg)`; void g.getBoundingClientRect(); g.style.transition=''; g.style.transform=`rotate(${to}deg)`;}; s.addEventListener('mouseenter',turn); s.addEventListener('focus',turn); s.addEventListener('touchstart',turn,{passive:true});});});
```

## CSS

```css
.dial{position:relative;margin:10px 0 24px;max-width:760px}
.dial svg{width:100%;height:auto;display:block;overflow:visible}
.dial .gantry{transform-box:fill-box;transform-origin:49.4% 47%;transition:transform 1.2s cubic-bezier(.4,.1,.2,1)}
.dial.spin .gantry{animation:sweep 220s infinite}
@keyframes sweep{0%{transform:rotate(0deg);animation-timing-function:ease-in-out}25%{transform:rotate(180deg);animation-timing-function:ease-in-out}50%{transform:rotate(0deg);animation-timing-function:ease-in-out}75%{transform:rotate(-180deg);animation-timing-function:ease-in-out}100%{transform:rotate(0deg)}}
@media (prefers-reduced-motion:reduce){.dial.spin .gantry{animation:none}.dial .gantry{transition:none}*{transition:none!important}}
.dial a{text-decoration:none}
.dial .seg path{stroke:var(--line);stroke-width:9;fill:none;transition:stroke .3s}
.dial .seg.on path,.dial .seg:hover path{stroke:var(--ink)}
.dial .seg text.name{font-size:24px;fill:var(--ink);font-weight:600}
.dial .seg:hover text.name{text-decoration:underline}
.dial .seg text.sm{font-size:13px;fill:var(--muted)}
.dial .seg text.num{font-size:24px;fill:var(--line)}
.dial line.tick{stroke:var(--line);stroke-width:1.2}
.dial .ring{fill:none;stroke:var(--rule);stroke-width:1}
```

Progress ring:

```css
.ring{width:96px;height:96px;flex:none}
.ring .gantry{transform-box:fill-box;transform-origin:49.4% 47%;transition:transform .6s ease}
.ring circle.track{fill:none;stroke:var(--rule);stroke-width:5}
.ring circle.fill{fill:none;stroke:var(--ink);stroke-width:5;stroke-linecap:round;transform:rotate(-90deg);transform-origin:50% 50%;transition:stroke-dashoffset .5s ease}
```

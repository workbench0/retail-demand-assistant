"""Animated landing hero (Apple-style light): self-contained HTML/CSS/JS in an iframe. Data comes from real app results."""
W, H, PX, PY = 640, 280, 24, 26

TEMPLATE = """
<style>
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","SF Pro Text","Helvetica Neue",Arial,sans-serif;color:#2B2622}
.hero{position:relative;overflow:hidden;border-radius:28px;padding:40px 40px;min-height:500px;
 background:linear-gradient(145deg,#FFFFFF 0%,#FAF7F2 60%,#F6E7DB 100%);border:1px solid rgba(0,0,0,.06);
 box-shadow:0 10px 40px rgba(0,0,0,.06)}
.hero::before{content:"";position:absolute;inset:0;pointer-events:none;
 background:radial-gradient(480px circle at var(--mx,72%) var(--my,20%),rgba(201,100,66,.13),transparent 60%)}
.blob{position:absolute;border-radius:50%;filter:blur(80px);animation:float 16s ease-in-out infinite}
.b1{width:300px;height:300px;background:#C96442;opacity:.16;top:-100px;left:-60px}
.b2{width:260px;height:260px;background:#2F4F4F;opacity:.13;bottom:-110px;right:10%;animation-delay:-5s}
.b3{width:200px;height:200px;background:#D9A441;opacity:.13;top:45%;left:44%;animation-delay:-9s}
@keyframes float{0%,100%{transform:translate(0,0)}50%{transform:translate(28px,-22px)}}
.grid{position:relative;display:flex;flex-wrap:wrap;gap:30px;align-items:center}
.left{flex:1 1 360px;min-width:300px}.right{flex:1 1 380px;min-width:300px}
.badge{display:inline-block;padding:6px 14px;border-radius:999px;font-size:12px;font-weight:500;
 background:rgba(201,100,66,.08);color:#C96442;animation:up .8s both}
h1{font-family:"Iowan Old Style","Palatino Linotype",Georgia,serif;font-size:48px;line-height:1.08;margin:18px 0 14px;font-weight:600;letter-spacing:-.02em;animation:up .8s .1s both}
.grad{background:linear-gradient(90deg,#C96442,#D9A441,#2F4F4F,#C96442);background-size:200% auto;-webkit-background-clip:text;
 background-clip:text;color:transparent;animation:shine 7s linear infinite}
@keyframes shine{to{background-position:200% center}}
p.sub{color:#7A6F66;font-size:17px;line-height:1.5;margin:0 0 24px;max-width:470px;animation:up .8s .2s both}
.stats{display:flex;gap:12px;flex-wrap:wrap;animation:up .8s .3s both}
.stat{padding:14px 18px;border-radius:18px;background:#fff;border:1px solid rgba(0,0,0,.06);
 box-shadow:0 2px 10px rgba(0,0,0,.05);min-width:100px;transition:transform .25s,box-shadow .25s}
.stat:hover{transform:translateY(-4px);box-shadow:0 12px 26px rgba(0,0,0,.10)}
.stat b{display:block;font-size:28px;font-weight:700;letter-spacing:-.02em}.stat span{font-size:12px;color:#7A6F66}
.card{border-radius:22px;padding:18px 18px 10px;background:#fff;border:1px solid rgba(0,0,0,.06);
 box-shadow:0 18px 50px rgba(0,0,0,.10);animation:up .9s .25s both}
.card .t{font-size:13px;color:#7A6F66;padding:0 4px 6px;font-weight:500}
.legend{display:block;margin-top:4px;font-size:12px;white-space:nowrap}
.legend i{display:inline-block;width:16px;height:3px;border-radius:2px;margin:0 6px 2px 0}
.legend i+i,.legend span{margin-left:0}
svg{width:100%;height:auto;display:block}
.line{fill:none;stroke-width:2.8;stroke-linecap:round;stroke-linejoin:round;stroke-dasharray:1;stroke-dashoffset:1}
.h{stroke:url(#gh);animation:draw 2.2s .5s ease forwards}
.f{stroke:#2F4F4F;filter:drop-shadow(0 0 5px rgba(47,79,79,.55));animation:draw 1.6s 2.5s ease forwards}
@keyframes draw{to{stroke-dashoffset:0}}
.area{fill:url(#ga);opacity:0;animation:fade 1.2s 1.6s forwards}
@keyframes fade{to{opacity:1}}
.cut{stroke:rgba(0,0,0,.25);stroke-dasharray:4 5;opacity:0;animation:fade .6s 2.4s forwards}
.lab{fill:#9A8F85;font-size:11px;opacity:0;animation:fade .6s 2.6s forwards}
.dot{fill:#C96442;stroke:#fff;stroke-width:2;opacity:0;animation:fade .3s 2.5s forwards}
.pulse{fill:none;stroke:#2F4F4F;opacity:0;transform-box:fill-box;transform-origin:center;animation:ring 2s 3s infinite}
@keyframes ring{0%{opacity:.8;transform:scale(1)}100%{opacity:0;transform:scale(3.4)}}
@keyframes up{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:none}}
@media (prefers-reduced-motion:reduce){*{animation:none!important;opacity:1!important;stroke-dashoffset:0!important}}
</style>
<div class="hero" id="hero">
 <div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div>
 <div class="grid">
  <div class="left">
   <span class="badge">Decision-support prototype &middot; historical M5 data</span>
   <h1>Know what to stock <span class="grad">before the shelf is empty.</span></h1>
   <p class="sub">Forecast 28 days of demand, turn it into suggested order quantities, and ask an AI assistant to explain every number.</p>
   <div class="stats">
    <div class="stat"><b data-t="__N_PROD__">0</b><span>products</span></div>
    <div class="stat"><b data-t="__HORIZON__">0</b><span>day forecast</span></div>
    <div class="stat"><b data-t="__GAIN__" data-d="1" data-s="%">0</b><span>lower MAE than baseline</span></div>
   </div>
  </div>
  <div class="right">
   <div class="card">
    <div class="t">Total daily units, 20 products
     <span class="legend"><i style="background:#C96442"></i>history (7-day avg) &nbsp;&nbsp;<i style="background:#2F4F4F"></i>LightGBM forecast</span></div>
    <svg viewBox="0 0 __W__ __H__">
     <defs>
      <linearGradient id="gh" x1="0" x2="1"><stop offset="0" stop-color="#C96442"/><stop offset="1" stop-color="#D9A441"/></linearGradient>
      <linearGradient id="ga" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#C96442" stop-opacity=".20"/><stop offset="1" stop-color="#C96442" stop-opacity="0"/></linearGradient>
     </defs>
     <path class="area" d="__AREA__"/>
     <path class="line h" pathLength="1" d="__HIST__"/>
     <line class="cut" x1="__CUTX__" x2="__CUTX__" y1="8" y2="__BASE__"/>
     <text class="lab" x="__CUTX__" y="20" text-anchor="end" dx="-8">historical</text>
     <text class="lab" x="__CUTX__" y="20" dx="8">forecast</text>
     <path class="line f" pathLength="1" d="__FC__"/>
     <circle class="dot" cx="__CUTX__" cy="__CUTY__" r="5"/>
     <circle class="pulse" cx="__CUTX__" cy="__CUTY__" r="5"/>
    </svg>
   </div>
  </div>
 </div>
</div>
<script>
document.querySelectorAll('[data-t]').forEach(function(el){
 var t=+el.dataset.t,d=+el.dataset.d||0,s=el.dataset.s||'',st=null;
 function step(ts){if(!st)st=ts;var p=Math.min((ts-st)/1500,1),e=1-Math.pow(1-p,3);
  el.textContent=(t*e).toFixed(d)+s;if(p<1)requestAnimationFrame(step)}
 requestAnimationFrame(step)});
var h=document.getElementById('hero');
h.addEventListener('mousemove',function(e){var r=h.getBoundingClientRect();
 h.style.setProperty('--mx',(e.clientX-r.left)+'px');h.style.setProperty('--my',(e.clientY-r.top)+'px')});
</script>
"""


def _path(pts):
    return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)


def build_hero(n_products, horizon, gain_pct, hist, fc):
    n = len(hist) + len(fc)
    lo, hi = min(hist + fc), max(hist + fc)
    dx = (W - 2 * PX) / (n - 1)
    y = lambda v: PY + (1 - (v - lo) / ((hi - lo) or 1)) * (H - 2 * PY)
    hp = [(PX + i * dx, y(v)) for i, v in enumerate(hist)]
    fp = [hp[-1]] + [(PX + (len(hist) + i) * dx, y(v)) for i, v in enumerate(fc)]
    base = H - PY
    area = _path(hp) + f" L {hp[-1][0]:.1f} {base} L {hp[0][0]:.1f} {base} Z"
    rep = {"__N_PROD__": str(n_products), "__HORIZON__": str(horizon), "__GAIN__": f"{gain_pct:.1f}",
           "__W__": str(W), "__H__": str(H), "__AREA__": area, "__HIST__": _path(hp), "__FC__": _path(fp),
           "__CUTX__": f"{hp[-1][0]:.1f}", "__CUTY__": f"{hp[-1][1]:.1f}", "__BASE__": str(base)}
    html = TEMPLATE
    for k, v in rep.items():
        html = html.replace(k, v)
    return html

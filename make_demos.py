#!/usr/bin/env python3
"""Build 3 day-view design demos (A dark / B editorial / C planner) from real data."""
import re, os, json
HOME=os.path.expanduser("~")
BASE=f"{HOME}/mt-sites/bi-dashboards/mt-time-tracker"
src=open(f"{BASE}/index.pre-redesign.html",encoding="utf-8").read()
def g(p):
    m=re.search(p,src,re.S)
    if not m: raise SystemExit("miss "+p[:30])
    return m.group(1)
favicon=g(r'rel="icon"[^>]*href="(data:image/png;base64,[^"]+)"')
logo=g(r'class="info-hdr-logo"[^>]*src="(data:image/png;base64,[^"]+)"')
CATS=g(r'(const CATS = \[.*?\n\];)')
REAL=g(r'(const REAL_EVENTS = \{.*?\n\};)')
OURA=g(r'(const OURA_DATA = \{.*?\n\};)')

DATA = CATS+"\n"+REAL+"\n"+OURA+r"""
const CM=Object.fromEntries(CATS.map(c=>[c.key,c]));
const WORK=['strategy','people','product','operations','external','global','growth'];
const ACTIVE=CATS.filter(c=>c.key!=='sleep');
function genDay(ds){const evs=[];const push=(cat,sub,t,s,e,tg=[])=>evs.push({cat,sub,title:t,start:s,end:e,tags:tg});
 const ou=OURA_DATA[ds];
 if(ou&&ou.hrs>0){const hrs=ou.hrs,wake=Math.min(9.5,Math.max(5,6+(7-hrs)*0.3));push('sleep','','睡眠',0,Math.round(wake*4)/4);
  const bed=24-Math.max(0,hrs-wake);if(bed<24)push('sleep','','入睡',Math.round(bed*4)/4,24);}
 (REAL_EVENTS[ds]||[]).forEach(e=>push(e.cat,e.sub,e.title,e.start,e.end,e.tags));
 return evs.sort((a,b)=>a.start-b.start);}
function catMins(evs){const m={};evs.forEach(e=>{m[e.cat]=(m[e.cat]||0)+(e.end-e.start)*60;});return m;}
function fmtDur(min){min=Math.round(min);const h=Math.floor(min/60),m=min%60;return h&&m?h+'h'+m+'m':h?h+'h':m+'m';}
function h2t(h){const hh=Math.floor(h),mm=Math.round((h-hh)*60);return String(hh%24).padStart(2,'0')+':'+String(mm).padStart(2,'0');}
function hexA(hex,a){const n=parseInt(hex.slice(1),16);return `rgba(${n>>16&255},${n>>8&255},${n&255},${a})`;}
// busiest day
let DS=Object.keys(REAL_EVENTS).sort((a,b)=>(REAL_EVENTS[b].length-REAL_EVENTS[a].length))[0];
const EVS=genDay(DS),M=catMins(EVS),OU=OURA_DATA[DS];
const SLEEP=M.sleep||0, AWAKE=24*60-SLEEP, WK=WORK.reduce((s,k)=>s+(M[k]||0),0);
const RANK=ACTIVE.filter(c=>(M[c.key]||0)>0).sort((a,b)=>M[b.key]-M[a.key]);
const TOTACT=RANK.reduce((s,c)=>s+M[c.key],0)||1;
const D=new Date(DS+'T00:00:00');const WKD=['周日','周一','周二','周三','周四','周五','周六'][D.getDay()];
// positioned timeline (shared A/C)
function posTL(from,to,pph){
 const ev=EVS.filter(e=>e.end>from&&e.start<to).sort((a,b)=>a.start-b.start);
 const lanes=[];ev.forEach(e=>{let li=lanes.findIndex(end=>end<=e.start+1e-6);if(li<0){li=lanes.length;lanes.push(e.end);}else lanes[li]=e.end;e._l=li;});
 const N=Math.max(1,lanes.length),H=(to-from)*pph;
 let grid='';for(let h=from;h<=to;h+=2)grid+=`<div class="hl" style="top:${(h-from)*pph}px"><span>${String(h%24).padStart(2,'0')}:00</span></div>`;
 const blk=ev.map(e=>{const c=CM[e.cat],top=(Math.max(from,e.start)-from)*pph,hgt=Math.max(18,(Math.min(to,e.end)-Math.max(from,e.start))*pph-3),w=100/N;
  return `<div class="blk${e.cat==='sleep'?' slp':''}" style="top:${top}px;height:${hgt}px;left:${e._l*w}%;width:calc(${w}% - 4px);--c:${c.color}">
   <b>${e.title}</b><i>${h2t(e.start)}–${h2t(e.end)} · ${c.label}</i></div>`;}).join('');
 return `<div class="tlg" style="height:${H}px">${grid}<div class="track">${blk}</div></div>`;
}
"""

PAGE = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>__TITLE__</title><link rel="icon" href="__FAV__">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@400;500;600;700;800;900&family=Inter:wght@400;500;600;700;800;900&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
<style>__CSS__</style></head><body><div id="app"></div><script>__DATA__
__RENDER__</script></body></html>"""

def build(name,title,css,render):
    html=(PAGE.replace("__TITLE__",title).replace("__FAV__",favicon)
          .replace("__CSS__",css).replace("__DATA__",DATA).replace("__RENDER__",render))
    html=html.replace("__LOGO__",logo)
    open(f"{BASE}/demos/{name}.html","w",encoding="utf-8").write(html)
    print("wrote",name,len(html))

os.makedirs(f"{BASE}/demos",exist_ok=True)

# ============ DEMO A — DARK PREMIUM (WHOOP/Oura/Linear) ============
CSS_A=r"""
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0C0D10;color:#EDEEF2;font-family:'Inter','Noto Sans SC',sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:760px;margin:0 auto;padding:22px 18px 60px}
.top{display:flex;align-items:center;gap:10px;margin-bottom:4px}
.top .dot{width:8px;height:8px;border-radius:50%;background:#19E57D;box-shadow:0 0 10px #19E57D}
.top b{font-weight:800;letter-spacing:.04em;font-size:15px}
.top .d{margin-left:auto;color:#7A8090;font-size:13px;font-weight:600}
.eyebrow{color:#6B7280;font-size:11px;letter-spacing:.2em;text-transform:uppercase;font-weight:700;margin:22px 0 14px}
.rings{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.rg{background:#15171C;border:1px solid #21242B;border-radius:18px;padding:18px 8px 16px;display:flex;flex-direction:column;align-items:center;gap:12px}
.rgw{position:relative;width:124px;height:124px}
.rgw svg{position:absolute;inset:0;width:124px;height:124px;transform:rotate(-90deg)}
.rgw .rbg{fill:none;stroke:#23262E;stroke-width:9}
.rgw .rfg{fill:none;stroke-width:9;stroke-linecap:round;filter:drop-shadow(0 0 5px var(--g))}
.rgw .rv{position:absolute;inset:0;display:flex;align-items:center;justify-content:center}
.rgw .rv b{font-size:31px;font-weight:800;line-height:1}.rgw .rv b small{font-size:14px;color:#7A8090;font-weight:700}
.rg .lab{font-size:13px;font-weight:700;letter-spacing:.04em;color:#C4C9D2;text-align:center}
.rg .lab span{display:block;font-size:10.5px;color:#6B7280;font-weight:600;margin-top:3px;letter-spacing:.02em}
.card{background:#15171C;border:1px solid #21242B;border-radius:18px;padding:18px;margin-top:14px}
.ch{display:flex;align-items:baseline;margin-bottom:14px}.ch b{font-size:13px;font-weight:800;letter-spacing:.02em}.ch span{margin-left:auto;color:#6B7280;font-size:12px;font-weight:600}
.alloc{display:flex;height:10px;border-radius:6px;overflow:hidden;gap:1.5px;background:#23262E;margin-bottom:14px}
.alloc i{height:100%;box-shadow:0 0 8px var(--c)}
.crow{display:flex;align-items:center;gap:11px;padding:9px 0;border-top:1px solid #1D2026}.crow:first-child{border-top:0}
.crow .dt{width:9px;height:9px;border-radius:3px}.crow .nm{font-size:13px;font-weight:600;min-width:80px;color:#D6D9DF}
.crow .tk{flex:1;height:6px;border-radius:4px;background:#23262E;overflow:hidden}.crow .tk i{height:100%;border-radius:4px}
.crow .vl{font-size:13px;font-weight:800;min-width:50px;text-align:right;font-variant-numeric:tabular-nums}
.crow .pc{font-size:11px;color:#6B7280;min-width:34px;text-align:right;font-weight:600}
.tlg{position:relative;margin-top:4px}
.hl{position:absolute;left:0;right:0;height:0;border-top:1px solid #1B1E24}.hl span{position:absolute;left:0;top:-7px;font-size:10px;color:#5A606B;background:#15171C;padding-right:6px;font-variant-numeric:tabular-nums}
.track{position:absolute;left:48px;right:4px;top:0;bottom:0}
.blk{position:absolute;border-radius:9px;padding:6px 9px;background:var(--c);background:linear-gradient(180deg,color-mix(in srgb,var(--c) 30%,#15171C),color-mix(in srgb,var(--c) 16%,#15171C));border-left:3px solid var(--c);overflow:hidden}
.blk b{display:block;font-size:12px;font-weight:700;color:#F2F3F6;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.blk i{font-size:10.5px;color:#A7AEBC;font-style:normal;white-space:nowrap}
.blk.slp{background:#15171C;border-left-color:#3A3F49;border:1px dashed #2A2E36}
"""
RENDER_A=r"""
function ring(val,unit,p,label,sub,g){const r=54,c=2*Math.PI*r;
 return `<div class="rg"><div class="rgw"><svg viewBox="0 0 124 124"><circle class="rbg" cx="62" cy="62" r="54"></circle><circle class="rfg" cx="62" cy="62" r="54" stroke="${g}" stroke-dasharray="${c}" stroke-dashoffset="${c*(1-Math.min(1,p))}" style="--g:${g}"></circle></svg><div class="rv"><b>${val}<small>${unit}</small></b></div></div><div class="lab">${label}<span>${sub}</span></div></div>`;}
const recC=OU&&OU.rec>=67?'#19E57D':OU&&OU.rec>=34?'#FFD91C':'#FF5C7A';
document.getElementById('app').innerHTML=`<div class="wrap">
 <div class="top"><span class="dot"></span><b>ZOE · 时间</b><span class="d">${DS} · ${WKD}</span></div>
 <div class="eyebrow">Today · 今日概览</div>
 <div class="rings">
  ${ring(Math.round(WK/60),'h',WK/AWAKE,'清醒工作',Math.round(WK/AWAKE*100)+'% 清醒','#BEDA6E')}
  ${ring(OU?OU.hrs:'--','h',OU?OU.hrs/8:0,'睡眠',OU?'Oura':'无数据','#5AD1FF')}
  ${ring(OU?OU.rec:'--','',OU?OU.rec/100:0,'恢复分',OU?(OU.rec>=67?'已恢复':OU.rec>=34?'适度':'需休整'):'',recC)}
 </div>
 <div class="card"><div class="ch"><b>时间分配</b><span>清醒 ${fmtDur(AWAKE)}</span></div>
  <div class="alloc">${RANK.map(c=>`<i style="width:${M[c.key]/TOTACT*100}%;background:${c.color};--c:${c.color}"></i>`).join('')}</div>
  ${RANK.map(c=>`<div class="crow"><span class="dt" style="background:${c.color}"></span><span class="nm">${c.icon} ${c.label}</span>
   <span class="tk"><i style="width:${M[c.key]/M[RANK[0].key]*100}%;background:${c.color}"></i></span>
   <span class="vl">${fmtDur(M[c.key])}</span><span class="pc">${Math.round(M[c.key]/TOTACT*100)}%</span></div>`).join('')}</div>
 <div class="card"><div class="ch"><b>24h 时间线</b><span>${EVS.length} 段</span></div>${posTL(0,24,30)}</div>
</div>`;
"""

# ============ DEMO B — LIGHT EDITORIAL (refined MTVI) ============
CSS_B=r"""
*{box-sizing:border-box;margin:0;padding:0}
body{background:#F6F2EA;color:#1D1D1D;font-family:'Hanken Grotesk','Noto Sans SC',sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:680px;margin:0 auto;padding:30px 26px 70px}
.bz{font-size:11px;letter-spacing:.26em;text-transform:uppercase;color:#9A9387;font-weight:700;display:flex;gap:10px;align-items:center}
.bz img{height:18px}
.hd{margin:18px 0 8px;font-family:'Hanken Grotesk';font-weight:800;letter-spacing:-.04em;font-size:54px;line-height:.98}
.hd small{font-size:26px;color:#A29A8C;font-weight:700}
.sub{color:#8A8475;font-size:14px;border-bottom:1px solid #E2DACB;padding-bottom:22px;margin-bottom:6px}
.kpi{display:flex;gap:34px;padding:22px 0;border-bottom:1px solid #E2DACB}
.kpi .k b{font-size:30px;font-weight:800;letter-spacing:-.02em}.kpi .k b small{font-size:15px;color:#A29A8C}
.kpi .k span{display:block;font-size:12px;color:#8A8475;font-weight:600;letter-spacing:.04em;margin-top:1px}
.sec{margin-top:34px}
.sct{font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:#9A9387;font-weight:700;margin-bottom:18px}
.bar{display:flex;flex-direction:column;gap:14px}
.bl{display:grid;grid-template-columns:120px 1fr auto;align-items:center;gap:14px}
.bl .nm{font-size:14px;font-weight:600}.bl .nm em{font-style:normal;color:#A29A8C;font-size:12px}
.bl .tk{height:3px;background:#E2DACB;position:relative}.bl .tk i{position:absolute;left:0;top:-1px;height:5px}
.bl .vl{font-size:14px;font-weight:800;font-variant-numeric:tabular-nums;min-width:84px;text-align:right}
.bl .vl span{color:#A29A8C;font-weight:600;font-size:12px;margin-left:5px}
.ag{display:grid;grid-template-columns:58px 1fr;gap:18px;padding:18px 0;border-top:1px solid #E2DACB}
.ag:first-child{border-top:0}
.agt{font-size:13px;font-weight:800;font-variant-numeric:tabular-nums;line-height:1.5}.agt span{display:block;color:#B3AB9B;font-weight:600}
.agc{position:relative;padding-left:18px}.agc::before{content:'';position:absolute;left:0;top:4px;bottom:4px;width:3px;border-radius:2px;background:var(--c)}
.agn{font-size:16px;font-weight:700;letter-spacing:-.01em;line-height:1.3}
.agm{font-size:12.5px;color:#8A8475;margin-top:4px;font-weight:600}.agm b{color:var(--cd);font-weight:700}
"""
RENDER_B=r"""
function darker(hex){const n=parseInt(hex.slice(1),16),f=.62;return `rgb(${(n>>16&255)*f|0},${(n>>8&255)*f|0},${(n&255)*f|0})`;}
document.getElementById('app').innerHTML=`<div class="wrap">
 <div class="bz"><img src="__LOGO__">Zoe · 时间 — CEO × MOM</div>
 <div class="hd">${Math.floor(WK/60)}<small>h ${Math.round(WK%60)}m</small> 今日工作</div>
 <div class="sub">${DS} · ${WKD} &nbsp;·&nbsp; 占清醒时间 ${Math.round(WK/AWAKE*100)}%</div>
 <div class="kpi">
  <div class="k"><b>${OU?OU.hrs:'--'}<small>h</small></b><span>睡眠</span></div>
  <div class="k"><b>${OU?OU.rec:'--'}</b><span>恢复分</span></div>
  <div class="k"><b>${fmtDur(M.family||0)}</b><span>家庭</span></div>
  <div class="k"><b>${EVS.filter(e=>e.cat!=='sleep').length}</b><span>日程</span></div>
 </div>
 <div class="sec"><div class="sct">时间分配 · Allocation</div><div class="bar">
  ${RANK.map(c=>`<div class="bl"><div class="nm">${c.label} <em>${c.icon}</em></div>
   <div class="tk"><i style="width:${M[c.key]/M[RANK[0].key]*100}%;background:${c.color}"></i></div>
   <div class="vl">${fmtDur(M[c.key])}<span>${Math.round(M[c.key]/TOTACT*100)}%</span></div></div>`).join('')}
 </div></div>
 <div class="sec"><div class="sct">今日时间线 · Timeline</div>
  ${EVS.map(e=>{const c=CM[e.cat];return `<div class="ag"><div class="agt">${h2t(e.start)}<span>${h2t(e.end)}</span></div>
   <div class="agc" style="--c:${c.color};--cd:${darker(c.color)}"><div class="agn">${e.title}</div>
   <div class="agm"><b>${c.label}</b>${e.sub?' · '+e.sub:''} · ${fmtDur((e.end-e.start)*60)}</div></div></div>`;}).join('')}
 </div>
</div>`;
"""

# ============ DEMO C — CALENDAR / PLANNER (Fantastical/Sunsama) ============
CSS_C=r"""
*{box-sizing:border-box;margin:0;padding:0}
body{background:#FBFAF7;color:#26261F;font-family:'Hanken Grotesk','Noto Sans SC',sans-serif;-webkit-font-smoothing:antialiased}
.wrap{max-width:860px;margin:0 auto;padding:18px 18px 60px}
.top{display:flex;align-items:center;gap:12px;padding-bottom:14px;border-bottom:1px solid #ECE7DD}
.top img{height:24px}.top b{font-weight:800;font-size:16px}.top .pill{margin-left:auto;background:#1D1D1D;color:#fff;font-size:12px;font-weight:700;padding:6px 13px;border-radius:20px}
.wkstrip{display:grid;grid-template-columns:repeat(7,1fr);gap:6px;margin:14px 0 16px}
.wkstrip .d{text-align:center;padding:9px 0;border-radius:11px;border:1px solid #ECE7DD;background:#fff;cursor:pointer}
.wkstrip .d.on{background:#1D1D1D;color:#fff;border-color:#1D1D1D}
.wkstrip .d .w{font-size:10px;color:#A39C8C;font-weight:600}.wkstrip .d.on .w{color:#C9C3B5}
.wkstrip .d .n{font-size:16px;font-weight:800;margin-top:2px}
.layout{display:grid;grid-template-columns:1fr 250px;gap:16px}
@media(max-width:680px){.layout{grid-template-columns:1fr}}
.grid{position:relative;background:#fff;border:1px solid #ECE7DD;border-radius:14px;padding:8px 10px 8px 0}
.tlg{position:relative}
.hl{position:absolute;left:0;right:0;border-top:1px solid #F0EBE1}.hl span{position:absolute;left:8px;top:-7px;font-size:10px;color:#B3AB9B;background:#fff;padding-right:5px;font-variant-numeric:tabular-nums;font-weight:600}
.track{position:absolute;left:52px;right:6px;top:0;bottom:0}
.blk{position:absolute;border-radius:8px;padding:5px 9px;background:var(--c);border-left:3px solid color-mix(in srgb,var(--c) 70%,#000);overflow:hidden;box-shadow:0 1px 2px rgba(0,0,0,.05)}
.blk b{display:block;font-size:12px;font-weight:700;color:#1D1D1D;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.blk i{font-size:10px;color:rgba(29,29,29,.6);font-style:normal;white-space:nowrap}
.blk.slp{background:#F1EEE7;border-left-color:#CFC8B8}
.side .box{background:#fff;border:1px solid #ECE7DD;border-radius:14px;padding:15px;margin-bottom:12px}
.side .bt{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:#A39C8C;font-weight:700;margin-bottom:12px}
.side .st{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:9px}
.side .st b{font-size:22px;font-weight:800}.side .st b small{font-size:13px;color:#A39C8C}.side .st span{font-size:12px;color:#8A8475;font-weight:600}
.crow{display:flex;align-items:center;gap:9px;padding:7px 0;font-size:13px}
.crow .dt{width:9px;height:9px;border-radius:3px}.crow .nm{font-weight:600}.crow .vl{margin-left:auto;font-weight:800;font-variant-numeric:tabular-nums}
"""
RENDER_C=r"""
let ws=new Date(D);ws.setDate(D.getDate()-((D.getDay()+6)%7));
const strip=Array.from({length:7},(_,i)=>{const dd=new Date(ws);dd.setDate(ws.getDate()+i);
 return `<div class="d${dd.getDate()===D.getDate()?' on':''}"><div class="w">${['一','二','三','四','五','六','日'][i]}</div><div class="n">${dd.getDate()}</div></div>`;}).join('');
document.getElementById('app').innerHTML=`<div class="wrap">
 <div class="top"><img src="__LOGO__"><b>Zoe · 时间</b><span class="pill">${D.getMonth()+1}月${D.getDate()}日 ${WKD}</span></div>
 <div class="wkstrip">${strip}</div>
 <div class="layout">
  <div class="grid">${posTL(6,24,40)}</div>
  <div class="side">
   <div class="box"><div class="bt">今日合计</div>
    <div class="st"><b>${Math.floor(WK/60)}<small>h${Math.round(WK%60)?Math.round(WK%60)+'m':''}</small></b><span>工作</span></div>
    <div class="st"><b>${OU?OU.hrs:'--'}<small>h</small></b><span>睡眠</span></div>
    <div class="st"><b>${OU?OU.rec:'--'}</b><span>恢复分</span></div></div>
   <div class="box"><div class="bt">时间分配</div>
    ${RANK.slice(0,7).map(c=>`<div class="crow"><span class="dt" style="background:${c.color}"></span><span class="nm">${c.label}</span><span class="vl">${fmtDur(M[c.key])}</span></div>`).join('')}</div>
  </div>
 </div>
</div>`;
"""

build("demo_a_dark","深色高级 · Demo A",CSS_A,RENDER_A)
build("demo_b_editorial","浅色编辑 · Demo B",CSS_B,RENDER_B)
build("demo_c_planner","日历计划器 · Demo C",CSS_C,RENDER_C)
print("demo day =", "(busiest)")

#!/usr/bin/env python3
"""复刻「爱时间」：24h 时钟盘 + 时间线 + 统计 + 目标，用 Zoe 的真实数据。
   输出 demos/itime.html（验证用）；满意后 promote 到 index.html。"""
import re, os, base64
HOME=os.path.expanduser("~"); BASE=os.path.dirname(os.path.abspath(__file__))  # 脚本自身目录，抗迁移
src=open(f"{BASE}/index.pre-redesign.html",encoding="utf-8").read()
def g(p):
    m=re.search(p,src,re.S)
    if not m: raise SystemExit("miss "+p[:30])
    return m.group(1)
FAV="data:image/png;base64,"+base64.b64encode(open(f"{BASE}/icon.png","rb").read()).decode()  # 新 logo B
CATS=g(r'(const CATS = \[.*?\n\];)')
REAL=g(r'(const REAL_EVENTS = \{.*?\n\};)')
OURA=g(r'(const OURA_DATA = \{.*?\n\};)')

HTML=r'''<!DOCTYPE html><html lang="zh-CN"><head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="时间">
<meta name="theme-color" content="#1D1D1D">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"><meta http-equiv="Pragma" content="no-cache"><meta http-equiv="Expires" content="0">
<title>Zoe · 时间</title>
<link rel="icon" type="image/png" href="__FAV__"><link rel="apple-touch-icon" href="__FAV__">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Hanken+Grotesk:wght@500;600;700;800&family=Noto+Sans+SC:wght@400;500;700;900&display=swap" rel="stylesheet" media="print" onload="this.media='all'">
<style>
:root{--mid:#1D1D1D;--tang:#F37434;--lime:#BEDA6E;--sand:#EAE1D2;
 --ink:#1D1D1D;--mut:#8A8475;--mut2:#C2BCAD;--line:#ECE4D8;--bg:#FBFAF6;--soft:#F2ECE0}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
body{font-family:'Hanken Grotesk','Noto Sans SC',-apple-system,'PingFang SC',sans-serif;background:#E6E0D3;color:var(--ink);-webkit-font-smoothing:antialiased}
.phone{max-width:440px;margin:0 auto;min-height:100vh;background:var(--bg);display:flex;flex-direction:column;position:relative;box-shadow:0 0 40px rgba(29,29,29,.08)}
/* header */
.hdr{background:var(--mid);color:#FAFBF9;padding:calc(14px + env(safe-area-inset-top)) 16px 14px;display:flex;align-items:center;gap:10px;position:sticky;top:0;z-index:10}
.hdr .nav{display:flex;align-items:center;gap:14px;margin:0 auto}
.hdr .nav b{font-size:17px;font-weight:800;min-width:78px;text-align:center}
.hdr .nav span{font-size:11px;opacity:.85;display:block;font-weight:500}
.hdr .a{width:38px;height:38px;border-radius:11px;background:rgba(255,255,255,.18);display:flex;align-items:center;justify-content:center;font-size:19px;cursor:pointer;border:0;color:#fff}
.hdr .a:active{background:rgba(255,255,255,.3)}
.body{flex:1;padding-bottom:76px;overflow-x:clip}
/* clock */
.clockwrap{display:flex;flex-direction:column;align-items:center;padding:18px 0 6px}
.clock{position:relative;width:300px;height:300px}
.clock svg{width:300px;height:300px;display:block}
.clock .ctr{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;pointer-events:none}
.clock .ctr .rg{font-size:14px;color:var(--mut);font-variant-numeric:tabular-nums;font-weight:600}
.clock .ctr .lb{font-size:12px;color:var(--mut);margin-top:9px}
.clock .ctr .big{font-size:26px;font-weight:800;margin-top:2px;letter-spacing:-.01em}
/* health + role overview */
.ov{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border-top:1px solid var(--line);border-bottom:1px solid var(--line);margin-top:8px}
.ovi{background:var(--bg);padding:13px 6px;text-align:center}
.ovi b{font-size:21px;font-weight:800;letter-spacing:-.01em;display:block;line-height:1}
.ovi b i{font-size:13px;font-style:normal;color:var(--mut);font-weight:700}
.ovi span{font-size:11px;color:var(--mut);font-weight:600;margin-top:4px;display:block}
.rcheck{display:flex;align-items:center;gap:10px 14px;flex-wrap:wrap;padding:11px 18px;background:var(--soft);border-bottom:1px solid var(--line);font-size:12.5px;font-weight:600;color:var(--ink)}
.rcheck .rlab{font-weight:800;font-size:10px;letter-spacing:.05em;color:var(--mut)}
.rcheck .rc-i b{font-weight:800;font-variant-numeric:tabular-nums}
.rcheck .rc-i b.g{color:#5E9C6B}.rcheck .rc-i b.w{color:#C2562F}
.kidgrid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:9px;margin:12px 0}
.kb{border:2px solid var(--line);background:var(--bg);border-radius:13px;padding:13px 0;font-family:inherit;font-size:14.5px;font-weight:700;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:7px;color:var(--ink)}
.kb .d{width:10px;height:10px;border-radius:50%}
.kb.on{border-color:var(--mid);background:var(--soft)}
.kok{width:100%;border:0;background:var(--mid);color:#FAFBF9;font-family:inherit;font-weight:800;font-size:15px;padding:13px 0;border-radius:13px;cursor:pointer;margin-bottom:8px}
.edit2{width:100%;border:1.5px solid var(--line);background:var(--bg);color:var(--ink);font-family:inherit;font-weight:700;font-size:14.5px;padding:12px 0;border-radius:13px;cursor:pointer;margin-bottom:8px}
.dtt .dhint{font-weight:500;color:var(--mut);font-size:10.5px;margin-left:7px}
.bdlist{max-height:52vh;overflow-y:auto;margin:4px 0 8px}
.bdrow{display:flex;align-items:center;gap:9px;padding:10px 4px;border-bottom:1px solid var(--line);font-size:13px;cursor:pointer}
.bdrow:active{background:var(--soft)}
.bdrow .bdd{color:var(--mut);font-weight:700;width:34px;flex:0 0 auto;font-variant-numeric:tabular-nums}
.bdrow .bdt{color:var(--mut);font-weight:600;width:88px;flex:0 0 auto;font-variant-numeric:tabular-nums;font-size:12px}
.bdrow .bdn{flex:1;font-weight:600;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.bdrow .bdu{color:var(--mut);font-weight:700;flex:0 0 auto;font-size:12px}
.bdempty{text-align:center;color:var(--mut2);padding:22px 0;font-size:13px}
.bdhint{font-size:11px;color:var(--mut2);text-align:center;margin-bottom:8px}
.bdel{border:0;background:var(--soft);border-radius:9px;padding:6px 10px;cursor:pointer;font-size:14px;flex:0 0 auto}
.srow .du .tgl{font-style:normal;color:var(--mut2);font-weight:600;font-size:11px}
.toast{position:fixed;top:14px;left:50%;transform:translateX(-50%);background:#1D1D1D;color:#FAFBF9;font-size:13px;font-weight:700;padding:9px 18px;border-radius:20px;z-index:99;box-shadow:0 4px 14px rgba(29,29,29,.25)}
@keyframes spin{to{transform:rotate(360deg)}}
#reloadB.spinning{animation:spin .7s linear infinite}
.anote{width:100%;box-sizing:border-box;border:1.5px solid var(--line);background:var(--bg);border-radius:12px;padding:11px 13px;font-family:inherit;font-size:14px;color:var(--ink);margin-bottom:11px;outline:none}
.anote:focus{border-color:var(--tang)}
.aitog{border:1.5px solid var(--line);background:var(--bg);color:var(--mut);font-family:inherit;font-weight:800;font-size:13px;padding:8px 14px;border-radius:18px;cursor:pointer;margin:0 0 11px}
.aitog.on{background:#1D1D1D;color:#BEDA6E;border-color:#1D1D1D}
.stp .tin{border:0;background:none;font-family:inherit;font-size:17px;font-weight:800;color:var(--ink);width:78px;text-align:center;outline:none;padding:0}
.stp .tin::-webkit-calendar-picker-indicator{display:none}
/* timeline list */
.tl{padding:6px 0 10px}
.tli{display:flex;align-items:center;gap:13px;padding:13px 18px;border-top:1px solid var(--line);cursor:pointer}
.tli:active{background:var(--soft)}
.tli .tm{font-size:12px;color:var(--mut);font-variant-numeric:tabular-nums;width:48px;line-height:1.5;font-weight:600}
.tli .dot{width:11px;height:11px;border-radius:50%;flex:none}
.tli .nm{font-size:15px;font-weight:600;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tli .nm .catpx{font-weight:800;font-size:12.5px;letter-spacing:-.02em}
.dot,.balrow em,.leg2 em,.kcell .kn em,.cb .d,.kb .d{box-shadow:inset 0 0 0 1px rgba(29,29,29,.16)}
.tli .du{font-size:12.5px;color:var(--mut);font-weight:600;white-space:nowrap}
.tli .ch{color:var(--mut2);font-size:16px}
.tl .empty{text-align:center;color:var(--mut2);font-size:14px;padding:36px 0}
.tl .gap{margin:6px 16px;padding:11px 14px;border:1.5px dashed var(--sand);border-radius:12px;color:#A99C86;font-size:12.5px;font-weight:600;cursor:pointer;text-align:center}
.tl .gap:active{background:var(--soft)}
.tli .mtag{font-size:9.5px;font-weight:800;color:var(--tang);background:#FBEEE3;padding:1px 6px;border-radius:6px;margin-left:6px;vertical-align:middle}
.fab{position:fixed;right:calc(50% - 220px + 18px);bottom:90px;width:54px;height:54px;border-radius:50%;border:0;background:var(--tang);color:#fff;font-size:28px;font-weight:300;line-height:1;cursor:pointer;box-shadow:0 6px 18px rgba(243,116,52,.42);z-index:25;display:flex;align-items:center;justify-content:center}
.fab:active{transform:scale(.94)}
@media(max-width:472px){.fab{right:18px}}
/* stats */
.seg2{display:flex;gap:6px;padding:8px 16px;position:sticky;top:var(--hdrH,66px);z-index:9;background:var(--bg);box-shadow:0 1px 0 var(--line)}
.seg2 button{flex:1;border:0;background:var(--soft);color:var(--mut);font-family:inherit;font-weight:700;font-size:13.5px;padding:7px 0;border-radius:10px;cursor:pointer}
.seg2 button.on{background:var(--mid);color:#FAFBF9}
.sthdr{display:flex;justify-content:space-between;padding:14px 18px 6px;font-size:12.5px;color:var(--mut);font-weight:600}
.srow{padding:13px 18px;border-top:1px solid var(--line)}
.srow .t{display:flex;align-items:center;gap:9px;margin-bottom:9px}
.srow .dot{width:11px;height:11px;border-radius:50%}.srow .nm{font-size:15px;font-weight:700}
.srow .du{font-size:12.5px;color:var(--mut);font-weight:500;margin-left:2px}
.srow .pc{margin-left:auto;font-size:15px;font-weight:800;font-variant-numeric:tabular-nums}
.srow .bar{height:7px;border-radius:5px;background:var(--soft);position:relative}
.srow .bar i{border-radius:5px}
.srow .bar .tgt2{position:absolute;top:-3px;width:2px;height:13px;background:var(--mid);border-radius:1px}
.slpdot{background:#FFF !important;background-image:radial-gradient(#D9D2C2 1.2px,transparent 1.2px) !important;background-size:6px 6px !important}
.dpsheet{max-width:340px;border-radius:20px;padding:16px}
.dphd{display:flex;align-items:center;gap:6px;margin-bottom:12px}
.dphd b{flex:1;text-align:center;font-size:15px;font-weight:800}
.dpnav{border:0;background:var(--soft);border-radius:9px;width:34px;height:32px;font-size:15px;font-weight:800;cursor:pointer;color:var(--ink)}
.dpwk{display:grid;grid-template-columns:repeat(7,1fr);gap:2px;font-size:11px;color:var(--mut);text-align:center;margin-bottom:4px}
.dpgrid{display:grid;grid-template-columns:repeat(7,1fr);gap:3px}
.dpgrid button{border:0;background:none;aspect-ratio:1;border-radius:10px;font-family:inherit;font-size:14px;font-weight:600;color:var(--ink);cursor:pointer}
.dpgrid button:active{background:var(--soft)}
.dpgrid button.on{background:var(--tang);color:#fff;font-weight:800}
.dpgrid button.fut{color:var(--mut2);opacity:.4;cursor:default}
.dpc-today{width:100%;border:1.5px solid var(--line);background:var(--bg);color:var(--ink);font-family:inherit;font-weight:700;font-size:14px;padding:11px 0;border-radius:13px;cursor:pointer;margin-top:12px}
.fab2{position:fixed;right:calc(50% - 220px + 18px);bottom:152px;width:44px;height:44px;border-radius:50%;border:1.5px solid var(--line);background:var(--bg);font-size:20px;cursor:pointer;box-shadow:0 4px 12px rgba(29,29,29,.12);z-index:25;display:flex;align-items:center;justify-content:center}
.timerbar{position:fixed;left:50%;transform:translateX(-50%);bottom:calc(84px + env(safe-area-inset-bottom));max-width:400px;width:calc(100% - 40px);background:var(--mid);color:#FAFBF9;border-radius:24px;padding:12px 18px;display:flex;align-items:center;gap:10px;z-index:30;cursor:pointer;box-shadow:0 6px 20px rgba(29,29,29,.35);font-weight:700;font-size:14px}
.timerbar .pulse{width:9px;height:9px;border-radius:50%;background:#FF5A3C;animation:tpulse 1.2s ease-in-out infinite}
@keyframes tpulse{0%,100%{opacity:1}50%{opacity:.25}}
.timerbar .tdur{margin-left:auto;font-variant-numeric:tabular-nums;font-weight:800}
.srow .bar i{display:block;height:100%;border-radius:5px}
.srow-u{cursor:pointer}.srow-u:active{background:var(--soft)}
.srow-u .uadd{font-size:9.5px;font-weight:800;color:var(--tang);background:#FBEEE3;padding:1px 7px;border-radius:6px;margin-left:7px;vertical-align:middle}
.snote{font-size:12px;color:var(--mut);line-height:1.65;margin:14px 18px 4px;padding-top:12px;border-top:1px solid var(--line)}
.snote b{color:var(--ink);font-weight:800}
/* goals */
.goals{padding:14px 16px}
.gcard{border-radius:18px;padding:16px 18px;margin-bottom:12px;color:#fff;position:relative;overflow:hidden}
.gcard .gn{font-size:17px;font-weight:800}
.gcard .gg{font-size:12.5px;opacity:.92;margin-top:4px;font-weight:600;display:flex;align-items:center;gap:8px}
.gcard .now{font-size:12.5px;opacity:.92;font-weight:600}
.gcard .ring{position:absolute;right:18px;top:50%;transform:translateY(-50%);width:54px;height:54px}
.gcard .ring .pv{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:800}
.gcard{cursor:pointer}
.goalhint{font-size:12px;color:var(--mut);padding:14px 18px 2px;font-weight:600}
.ge-row{display:flex;gap:8px;margin-bottom:14px}
.ge-p{flex:1;padding:11px;border:1px solid var(--line);border-radius:12px;background:var(--bg);font-family:inherit;font-weight:700;font-size:14px;color:var(--mut);cursor:pointer}
.ge-p.on{background:var(--mid);color:#FAFBF9;border-color:var(--mid)}
.ge-stepper{display:flex;align-items:center;gap:14px;margin-bottom:14px}
.ge-stepper button{width:52px;height:52px;border-radius:14px;border:1px solid var(--line);background:var(--soft);font-size:26px;font-weight:300;color:var(--ink);cursor:pointer}
.ge-stepper button:active{background:var(--sand)}
.ge-val{flex:1;text-align:center;font-size:22px;font-weight:800;font-variant-numeric:tabular-nums}
/* 类别详情 + 趋势 */
.detail{position:fixed;inset:0;max-width:440px;margin:0 auto;background:var(--bg);z-index:50;display:flex;flex-direction:column;animation:up .2s ease}
.detail .dhead{display:flex;align-items:center;background:var(--mid);color:#FAFBF9;padding:calc(14px + env(safe-area-inset-top)) 14px 14px}
.detail .dhead b{margin:0 auto;font-size:16px;font-weight:800}
.detail .dhead button{background:none;border:0;color:#FAFBF9;font-family:inherit;font-size:14px;font-weight:700;cursor:pointer;opacity:.92}
.detail .dbody{padding:18px 18px 30px;overflow-y:auto}
.dstat{display:flex;gap:10px;margin-bottom:22px}
.dstat .ds{flex:1;background:var(--soft);border-radius:13px;padding:13px 8px;text-align:center}
.dstat .ds b{font-size:19px;font-weight:800;display:block;font-variant-numeric:tabular-nums}
.dstat .ds b.up{color:#5E9C6B}.dstat .ds b.dn{color:#C2562F}
.dstat .ds span{font-size:10.5px;color:var(--mut);font-weight:600;margin-top:3px;display:block}
.dtt{font-size:14px;color:#1D1D1D;font-weight:800;margin:26px 0 10px}
.dbody .dtt:first-of-type{margin-top:18px}
.trend{position:relative;height:200px;display:flex;align-items:flex-end;gap:5px;border-bottom:1px solid var(--line);padding-bottom:0}
.trend .goalline{position:absolute;left:0;right:0;border-top:1.5px dashed var(--mid);opacity:.55;z-index:1}
.trend .tcol{flex:1;height:100%;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:4px}
.trend .tval{font-size:9.5px;color:var(--mut);font-weight:700;font-variant-numeric:tabular-nums}
.trend .tbar{width:100%;max-width:26px;border-radius:5px 5px 0 0}
.trend .tlb{font-size:9px;color:var(--mut2);font-weight:600;white-space:nowrap}
/* 30天每日趋势：柱更密、标签稀疏、均值线 */
.trend.d30{gap:2px}
.trend.d30 .tbar{max-width:12px}
.trend.d30 .tval{display:none}
.trend.d30 .tlb{font-size:8px;transform:rotate(0)}
.trend .avgline{position:absolute;left:0;right:0;border-top:1.5px solid var(--tang);opacity:.7;z-index:1}
.trend .avgtag{position:absolute;right:2px;font-size:9px;font-weight:800;color:var(--tang);background:var(--bg);padding:0 3px;transform:translateY(-100%)}
.trend .goaltag{position:absolute;right:2px;font-size:9px;font-weight:800;color:var(--mid);background:var(--bg);padding:0 3px;transform:translateY(-100%)}
.dnote{font-size:12.5px;color:var(--mut);margin-top:16px;line-height:1.6}
/* bottom tabs */
.tabs{position:fixed;bottom:0;left:50%;transform:translateX(-50%);width:100%;max-width:440px;background:rgba(255,255,255,.94);backdrop-filter:blur(12px);border-top:1px solid var(--line);display:flex;padding:8px 0 calc(8px + env(safe-area-inset-bottom));z-index:20}
.tabs button{flex:1;border:0;background:none;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:3px;color:var(--mut2);font-family:inherit}
.tabs button .ic{font-size:21px;line-height:1}.tabs button .tx{font-size:10.5px;font-weight:700}
.tabs button.on{color:var(--tang)}
/* 改类弹层 */
.mask{position:fixed;inset:0;background:rgba(29,29,29,.42);z-index:40;display:flex;align-items:flex-end;justify-content:center}
.sheet{width:100%;max-width:440px;background:var(--bg);border-radius:20px 20px 0 0;padding:18px 16px calc(18px + env(safe-area-inset-bottom));animation:up .18s ease}
@keyframes up{from{transform:translateY(100%)}to{transform:translateY(0)}}
.sheet .sh-t{font-size:13px;color:var(--mut);font-weight:600;margin-bottom:4px}
.sheet .sh-n{font-size:15px;font-weight:800;margin-bottom:14px;line-height:1.3}
.sheet .grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}
.addtime{display:flex;gap:10px;margin-bottom:14px}
.att{flex:1;background:var(--soft);border-radius:13px;padding:9px 10px;text-align:center}
.att>span{font-size:11px;color:var(--mut);font-weight:600;display:block;margin-bottom:5px}
.att .stp{display:flex;align-items:center;justify-content:space-between;gap:6px}
.att .stp button{width:34px;height:34px;border-radius:10px;border:1px solid var(--line);background:var(--bg);font-size:19px;font-weight:300;color:var(--ink);cursor:pointer}
.att .stp b{font-size:17px;font-weight:800;font-variant-numeric:tabular-nums}
.sheet .cb{display:flex;align-items:center;gap:9px;padding:12px 13px;border:1px solid var(--line);border-radius:13px;background:var(--bg);font-family:inherit;font-size:14px;font-weight:700;cursor:pointer;color:var(--ink)}
.sheet .cb .d{width:12px;height:12px;border-radius:50%;flex:none}
.sheet .cb:active{background:var(--soft)}
.sheet .del{width:100%;margin-top:12px;padding:13px;border:1px solid #E7C3B6;border-radius:13px;background:#FBEEE9;color:#C2562F;font-family:inherit;font-weight:800;font-size:14px;cursor:pointer}
.sheet .del:active{background:#F6E0D7}
.sheet .cancel{width:100%;margin-top:8px;padding:13px;border:0;border-radius:13px;background:var(--soft);color:var(--mut);font-family:inherit;font-weight:700;font-size:14px;cursor:pointer}
/* 洞察 */
.ins{padding:14px 16px}
.icard{background:var(--bg);border:1px solid var(--line);border-radius:16px;padding:16px;margin-bottom:12px}
.icard .it{font-size:13px;font-weight:800;letter-spacing:.02em;margin-bottom:3px}
.icard .isub{font-size:11.5px;color:var(--mut);margin-bottom:14px;font-weight:500}
.verdict{background:var(--mid);color:#FAFBF9;border-radius:16px;padding:16px 18px;margin-bottom:12px}
.verdict .vt{font-size:11px;letter-spacing:.18em;text-transform:uppercase;color:var(--lime);font-weight:700;margin-bottom:8px}
.verdict .vc{font-size:15px;font-weight:700;line-height:1.5}
.verdict .vc b{color:var(--lime)}
/* 本周建议 */
.sugg{background:var(--bg);border:1px solid var(--line);border-radius:16px;padding:16px;margin-bottom:12px}
.sugg .st{font-size:13px;font-weight:800;letter-spacing:.02em;margin-bottom:3px}
.sugg .ssub{font-size:11.5px;color:var(--mut);margin-bottom:12px;font-weight:500}
.sugg ul{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:10px}
.sugg li{display:flex;gap:10px;align-items:flex-start;font-size:13px;line-height:1.55;color:var(--ink);font-weight:600}
.sugg li .si{flex:none;width:24px;height:24px;border-radius:8px;background:var(--soft);display:flex;align-items:center;justify-content:center;font-size:13px;margin-top:1px}
.sugg li b{font-weight:800}
.sugg li em{font-style:normal;color:var(--tang);font-weight:800;font-variant-numeric:tabular-nums}
.sugg .sempty{font-size:12.5px;color:var(--mut);font-weight:600;line-height:1.6}
.alloc2{display:flex;height:12px;border-radius:7px;overflow:hidden;gap:1.5px;background:var(--soft);margin-bottom:12px}
.alloc2 i{height:100%}
.leg2{display:flex;flex-wrap:wrap;gap:6px 14px;margin-bottom:13px}
.leg2 span{display:flex;align-items:center;gap:6px;font-size:12px;color:var(--ink);font-weight:600}
.leg2 em{width:9px;height:9px;border-radius:3px;display:inline-block}
.famnudge{font-size:13px;color:var(--ink);padding-top:13px;border-top:1px solid var(--line);line-height:1.65;font-weight:600}
.famnudge b{font-weight:800}
.up{color:#5E9C6B;font-weight:800}.dn{color:#C2562F;font-weight:800}
.brow{margin-bottom:13px}
.brow .bl{display:flex;align-items:baseline;font-size:13px;margin-bottom:6px}
.brow .bl .nm{font-weight:700}.brow .bl .vv{margin-left:auto;font-weight:800;font-variant-numeric:tabular-nums}
.brow .bl .vv em{font-style:normal;color:var(--mut);font-weight:600;font-size:11.5px;margin-left:5px}
.brow .tk{position:relative;height:8px;border-radius:5px;background:var(--soft);overflow:visible}
.brow .tk i{display:block;height:100%;border-radius:5px}
.brow .tk .tgt{position:absolute;top:-3px;width:2px;height:14px;background:var(--mid);border-radius:1px}
.mgrid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.mcell{background:var(--soft);border-radius:13px;padding:12px 13px}
.mcell b{font-size:20px;font-weight:800;display:block;line-height:1.1;font-variant-numeric:tabular-nums}
.mcell b.warn{color:#C2562F}
.mcell span{font-size:11px;color:var(--mut);font-weight:600;margin-top:3px;display:block}
.ecorr{display:flex;gap:10px}
.ecorr .ec{flex:1;background:var(--soft);border-radius:13px;padding:13px;text-align:center}
.ecorr .ec b{font-size:24px;font-weight:800;display:block;line-height:1}
.ecorr .ec b.g{color:#5E9C6B}.ecorr .ec b.r{color:#C2562F}
.ecorr .ec span{font-size:11px;color:var(--mut);font-weight:600;margin-top:4px;display:block}
.inote{font-size:12px;color:var(--mut);line-height:1.6;margin-top:12px;padding-top:12px;border-top:1px solid var(--line)}
.inote b{color:var(--ink)}
/* 洞察维度切换 */
.segI{display:flex;gap:6px;padding:8px 16px;position:sticky;top:var(--hdrH,66px);z-index:9;background:var(--bg);box-shadow:0 1px 0 var(--line)}
.segI button{flex:1;border:0;background:var(--soft);color:var(--mut);font-family:inherit;font-weight:700;font-size:13.5px;padding:7px 0;border-radius:10px;cursor:pointer}
.segI button.on{background:var(--mid);color:#FAFBF9}
/* 工作×生活 圆环 */
.balwrap{display:flex;align-items:center;gap:18px;margin-bottom:14px}
.donut{width:104px;height:104px;border-radius:50%;flex:0 0 auto;display:flex;align-items:center;justify-content:center}
.donut .dhole{width:62px;height:62px;border-radius:50%;background:var(--bg);display:flex;flex-direction:column;align-items:center;justify-content:center}
.donut .dhole b{font-size:20px;font-weight:800;line-height:1;font-variant-numeric:tabular-nums}
.donut .dhole span{font-size:10px;color:var(--mut);font-weight:700;margin-top:2px}
.ballist{flex:1;display:flex;flex-direction:column;gap:10px}
.balrow{display:flex;align-items:center;font-size:13px}
.balrow em{width:10px;height:10px;border-radius:3px;margin-right:9px;flex:0 0 auto}
.balrow .bn{font-weight:700;color:var(--ink)}
.balrow .bp{margin-left:auto;font-weight:800;font-variant-numeric:tabular-nums}
.balrow .bh{width:52px;text-align:right;color:var(--mut);font-weight:600;font-variant-numeric:tabular-nums}
/* 家庭·自身 页 */
.fam{padding:14px 16px}
.fcard{background:var(--bg);border:1px solid var(--line);border-radius:16px;padding:16px;margin-bottom:12px}
.fcard .fhd{display:flex;align-items:center;margin-bottom:10px}
.fcard .ft{font-size:14px;font-weight:800;letter-spacing:.02em}
.fbadge{margin-left:auto;font-size:12px;font-weight:800;color:#7A6A3C;background:#FBEED9;border:1px solid #EDD9AE;padding:4px 10px;border-radius:20px;font-variant-numeric:tabular-nums}
.fbadge.warn{color:#B4531F;background:#FBE6D8;border-color:#F0C7AC}
.sleepsvg{width:100%;height:auto;display:block;margin:2px 0 4px}
.fnote{font-size:12px;color:var(--mut);line-height:1.6;margin-top:10px}
.kgrid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-top:4px}
.kcell{background:var(--soft);border-radius:13px;padding:13px 10px}
.kcell .kn{display:flex;align-items:center;gap:6px;font-size:12.5px;font-weight:700;color:var(--ink)}
.kcell .kn em{width:8px;height:8px;border-radius:50%;display:inline-block}
.kcell .kh{font-size:24px;font-weight:800;margin-top:8px;font-variant-numeric:tabular-nums}
.kcell .kh i{font-size:13px;font-style:normal;color:var(--mut);font-weight:700}
/* 说明弹窗 */
.amask{position:fixed;inset:0;background:rgba(29,29,29,.42);z-index:40;display:flex;align-items:flex-end;justify-content:center}
.asheet{background:var(--bg);width:100%;max-width:440px;max-height:88vh;border-radius:20px 20px 0 0;display:flex;flex-direction:column;overflow:hidden}
.asheet .ahd{display:flex;align-items:center;padding:18px 18px 12px;border-bottom:1px solid var(--line)}
.asheet .ahd b{font-size:16px;font-weight:800}
.asheet .aclose{margin-left:auto;border:0;background:var(--soft);width:30px;height:30px;border-radius:50%;font-size:15px;cursor:pointer;color:var(--mut)}
.abody{overflow-y:auto;padding:6px 18px 30px}
.asec{padding:14px 0;border-bottom:1px solid var(--line)}
.asec:last-child{border-bottom:0}
.asec h4{font-size:13.5px;font-weight:800;margin:0 0 6px}
.asec p{font-size:13px;color:var(--ink);line-height:1.72;margin:5px 0;font-weight:500}
.asec p b{font-weight:800}
.asec .amut{color:var(--mut);font-size:12px;font-weight:500}
</style></head><body><div class="phone">
<div class="hdr">
  <button class="a" id="todayB" title="今天">●</button>
  <div class="nav"><button class="a" id="prevB" style="background:none;font-size:20px">‹</button>
   <div id="dpick" style="cursor:pointer"><b id="dlab">今天</b><span id="dsub"></span></div>
   <button class="a" id="nextB" style="background:none;font-size:20px">›</button></div>
  <button class="a" id="aboutB" title="说明">ⓘ</button>
  <button class="a" id="reloadB" title="刷新">⟳</button>
  <div style="font-size:14px;font-weight:800;letter-spacing:.02em;opacity:.95;text-align:right;min-width:24px">Zoe</div>
</div>
<div class="body" id="body"></div>
<div class="tabs">
  <button data-v="clock" class="on"><span class="ic">🕘</span><span class="tx">时钟</span></button>
  <button data-v="stats"><span class="ic">📊</span><span class="tx">统计</span></button>
  <button data-v="timer"><span class="ic">⏱</span><span class="tx">计时</span></button>
  <button data-v="insights"><span class="ic">💡</span><span class="tx">洞察</span></button>
  <button data-v="family"><span class="ic">🏡</span><span class="tx">家庭</span></button>
  <button data-v="goals"><span class="ic">🎯</span><span class="tx">目标</span></button>
</div>
</div>
<script>
// 自动缓存清除：检测版本变化，自动清除 Service Worker 和浏览器缓存
(function(){
  const VER='__VERSION__';
  const lastVer=localStorage.getItem('ztAppVersion');
  if(lastVer!==VER){
    console.log('[缓存清除] 版本从',lastVer,'→',VER);
    localStorage.setItem('ztAppVersion',VER);
    // 清除所有 Service Worker
    navigator.serviceWorker?.getRegistrations?.().then(regs=>{
      regs.forEach(reg=>reg.unregister());
      console.log('[缓存清除] Service Worker 已清除');
    });
    // 清除 IndexedDB（PWA 缓存）
    indexedDB.databases?.().then(dbs=>{
      dbs.forEach(db=>indexedDB.deleteDatabase(db.name));
      console.log('[缓存清除] IndexedDB 已清除');
    });
  }
})();
__CATS__
__REAL_EVENTS__
__OURA_DATA__
// 全新调色板（明快、克制、区分度高），覆盖旧的发闷棕黑灰
const PAL={strategy:'#F37434',people:'#A6C061',product:'#C56B4A',operations:'#D69A3C',external:'#B4643E',global:'#8C6E45',growth:'#818A7D',family:'#8A6BA4',self:'#E2A3B3',travel:'#A79E8C',sleep:'#FFFFFF'};
CATS.forEach(c=>{if(PAL[c.key])c.color=PAL[c.key];});
CATS.forEach(c=>{if(c.key==='operations')c.label='日常运营';});   // 改名:运营财务→日常运营
{const _sl=CATS.find(c=>c.key==='sleep');if(_sl)_sl.label='睡眠·在床';} // 时间账本里的 sleep 类=在床区间(bs→wake+nb→24)；概览/家庭/趋势的「睡眠」=WHOOP 实际睡眠 hrs。标注开，两口径不再混淆
const CM=Object.fromEntries(CATS.map(c=>[c.key,c]));
// ── 云同步：所有编辑实时写飞书多维表格（Zoe+助理共享），localStorage 只是离线缓存 ──
const SYNC='https://zoe-time-sync.zoe-mt.workers.dev';
const ZT_TOKEN='41326c953ec9ceb6227a27adc2cc83e583b9db05454e77f0'; // 与 Worker 共享的静态口令：挡住无凭据的公网扫描
const DEV=localStorage.getItem('ztDevice')||(()=>{const d='dev-'+Math.random().toString(36).slice(2,8);localStorage.setItem('ztDevice',d);return d;})();
function _obx(){try{return JSON.parse(localStorage.getItem('ztOutbox')||'[]');}catch(e){return[];}}
function _obxSave(q){try{localStorage.setItem('ztOutbox',JSON.stringify(q.slice(-100)));}catch(e){}}
function cloud(kind,payload){const body={kind,device:DEV,...payload};
 try{fetch(SYNC+'/save',{method:'POST',headers:{'Content-Type':'application/json','X-ZT-Token':ZT_TOKEN},body:JSON.stringify(body)})
  .then(r=>{if(!r.ok)throw 0;})
  .catch(()=>{const q=_obx();q.push(body);_obxSave(q);});}
 catch(e){const q=_obx();q.push(body);_obxSave(q);}}
async function flushOutbox(){const q=_obx();if(!q.length)return;const rest=[];
 for(const b of q){try{const r=await fetch(SYNC+'/save',{method:'POST',headers:{'Content-Type':'application/json','X-ZT-Token':ZT_TOKEN},body:JSON.stringify(b)});if(!r.ok)rest.push(b);}catch(e){rest.push(b);}}
 _obxSave(rest);}
// 改类回流：本地修正表（title -> {cat,sub}），长按时间线一条即可改
const CORR=JSON.parse(localStorage.getItem('ztCorrections')||'{}');
function applyCorr(title,cat,sub){return CORR[title]?[CORR[title].cat,CORR[title].sub]:[cat,sub];}
function saveCorr(title,cat,sub,kids){CORR[title]={cat,sub,kids:kids||[]};localStorage.setItem('ztCorrections',JSON.stringify(CORR));cloud('correction',{title,cat,sub,kids:(kids||[]).join(',')});}
// 删除/不参加：按"日期|标题|开始"记一条实例，不计入任何统计
const DELETED=new Set(JSON.parse(localStorage.getItem('ztDeleted')||'[]'));
function delKey(ds,t,s){return ds+'|'+t+'|'+s;}
function saveDel(k){DELETED.add(k);localStorage.setItem('ztDeleted',JSON.stringify([...DELETED]));const p=k.split('|');cloud('delete',{key:k,ds:p[0]||'',title:p[1]||''});}
// 手动补录：{ds:[{cat,sub,title,start,end}]}
const MANUAL=JSON.parse(localStorage.getItem('ztManual')||'{}');
function saveManual(ds,ev){if(!Number.isFinite(+ev.start)||!Number.isFinite(+ev.end)||+ev.end<=+ev.start)return;   // NaN/倒置时段绝不落账、绝不上云
 (MANUAL[ds]=MANUAL[ds]||[]).push(ev);localStorage.setItem('ztManual',JSON.stringify(MANUAL));cloud('manual',{ds,cat:ev.cat,sub:ev.sub||'',start:ev.start,end:ev.end,note:ev.note||'',kids:(ev.tags||[]).join(',')});}
function delManual(ds,i){if(MANUAL[ds]){const e=MANUAL[ds][i];MANUAL[ds].splice(i,1);localStorage.setItem('ztManual',JSON.stringify(MANUAL));if(e)cloud('delManual',{ds,start:e.start,cat:e.cat});}}
// 日历行程的改名/改时间：按「日期|原标题|原开始」记一条覆盖（原始日历不动，纯展示层修改）
const EDITS=JSON.parse(localStorage.getItem('ztEdits')||'{}');
function saveEdit(ds,t,s0,patch){if(patch&&((patch.start!=null&&!Number.isFinite(+patch.start))||(patch.end!=null&&!Number.isFinite(+patch.end))))return;   // NaN 不写 EDITS 不上云
 const k=delKey(ds,t,s0);EDITS[k]={...(EDITS[k]||{}),...patch};localStorage.setItem('ztEdits',JSON.stringify(EDITS));const v=EDITS[k];cloud('edit',{key:k,ds,title:v.title||'',start:v.start,end:v.end});}
// 启动时拉云端合并（云端=共享真相），完成后重渲染
async function cloudPull(){try{ await flushOutbox();
 const r=await fetch(SYNC+'/sync',{cache:'no-store',headers:{'X-ZT-Token':ZT_TOKEN}});if(!r.ok)return;const d=await r.json();
 Object.entries(d.corrections||{}).forEach(([t,v])=>{CORR[t]={cat:v.cat,sub:v.sub||'',kids:(v.kids?String(v.kids).split(',').filter(Boolean):[])};});localStorage.setItem('ztCorrections',JSON.stringify(CORR));
 (d.deleted||[]).forEach(k=>DELETED.add(k));localStorage.setItem('ztDeleted',JSON.stringify([...DELETED]));
 const seen=new Set();Object.keys(MANUAL).forEach(ds=>(MANUAL[ds]||[]).forEach(e=>seen.add(ds+'|'+e.start+'|'+e.cat)));
 Object.entries(d.manual||{}).forEach(([ds,arr])=>(arr||[]).forEach(e=>{const key=ds+'|'+e.start+'|'+e.cat;
   /* Number.isFinite=类型敏感校验：云端脏行(null/NaN)不进本机；+null===0 的坑，勿改回 isFinite(+x) */
   if(!seen.has(key)&&Number.isFinite(e.start)&&Number.isFinite(e.end)){seen.add(key);(MANUAL[ds]=MANUAL[ds]||[]).push({cat:e.cat,sub:e.sub||'',title:e.note||((CM[e.cat]||{}).label||e.cat),note:e.note||'',tags:(e.kids?String(e.kids).split(',').filter(Boolean):[]),start:+e.start,end:+e.end});}}));
 localStorage.setItem('ztManual',JSON.stringify(MANUAL));
 Object.entries(d.edits||{}).forEach(([k,v])=>{EDITS[k]={title:v.title||'',start:(v.start!=null?+v.start:undefined),end:(v.end!=null?+v.end:undefined)};});
 localStorage.setItem('ztEdits',JSON.stringify(EDITS));
 Object.entries(d.goals||{}).forEach(([k,v])=>{GOV[k]={...(GOV[k]||{}),period:v.period||GOV[k]?.period,target:(v.target!=null?+v.target:GOV[k]?.target)};});
 localStorage.setItem('ztGoals',JSON.stringify(GOV));
 render();
}catch(e){}}
const WORK=['strategy','people','product','operations','external','global','growth'];
const ACTIVE=CATS.filter(c=>c.key!=='sleep');
function genDay(ds){const evs=[];const push=(cat,sub,t,s,e,tg=[],man=false,mi=-1,ot=null,os=null)=>{if(!CM[cat])cat='operations';evs.push({cat,sub,title:t,start:s,end:e,tags:(tg||[]).map(x=>x==='Don'?'Donald':x),man,mi,ot:ot||t,os:(os!=null?os:s)});};
 const ou=OURA_DATA[ds];
 const pushSleep=(t,a,b2)=>{const k=delKey(ds,t,a);if(DELETED.has(k))return;const ed=EDITS[k]||{};
  push('sleep','',t,(ed.start!=null?ed.start:a),(ed.end!=null?ed.end:b2),[],false,-1,t,a);};   // 睡眠块可被 EDITS 修正(设备偶尔判错起床点)
 if(ou&&(ou.hrs>0||ou.wake!=null)){
  if(ou.wake!=null){ // WHOOP 真实起止：不再估计
   if(ou.bs!=null)pushSleep('睡眠',ou.bs,ou.wake);   // 过午夜才睡：bs→wake
   else pushSleep('睡眠',0,ou.wake);                 // 前夜入睡：0→真实起床
  }else{const hrs=ou.hrs,wake=Math.min(9.5,Math.max(5,6+(7-hrs)*0.3));pushSleep('睡眠(约)',0,Math.round(wake*4)/4);}
  if(ou.nb!=null)pushSleep('入睡',ou.nb,24);          // 当晚真实入睡时刻
  else if(ou.wake==null&&ou.hrs>0){const hrs=ou.hrs,wake=Math.min(9.5,Math.max(5,6+(7-hrs)*0.3));const bed=24-Math.max(0,hrs-wake);if(bed<24)pushSleep('入睡(约)',Math.round(bed*4)/4,24);}}
 (REAL_EVENTS[ds]||[]).forEach(e=>{const k0=delKey(ds,e.title,e.start);if(DELETED.has(k0))return;
   const cr=CORR[e.title];const c=cr?cr.cat:e.cat,s=cr?cr.sub:e.sub,tg=(cr&&cr.kids&&cr.kids.length)?[...new Set([...cr.kids,...(e.tags||[])])]:e.tags;
   const ed=EDITS[k0]||{};
   push(c,s,ed.title||e.title,(ed.start!=null?ed.start:e.start),(ed.end!=null?ed.end:e.end),tg,false,-1,e.title,e.start);});
 (MANUAL[ds]||[]).forEach((e,i)=>push(e.cat,e.sub,e.title,e.start,e.end,e.tags||[],true,i));
 return evs.sort((a,b)=>a.start-b.start);}
function genOura(ds){return OURA_DATA[ds]||null;}
function catMins(evs){const m={};evs.forEach(e=>{m[e.cat]=(m[e.cat]||0)+(e.end-e.start)*60;});return m;}
function fmtDur(min){min=Math.round(min);const h=Math.floor(min/60),m=min%60;return h&&m?h+'小时'+m+'分':h?h+'小时':m+'分';}
function fmtShort(min){min=Math.round(min);const h=Math.floor(min/60),m=min%60;return h&&m?h+'h'+m+'m':h?h+'h':m+'m';}
function fmtU(min){min=Math.round(min);const h=Math.floor(min/60),m=min%60;return h&&m?h+'<i>h</i>'+m+'<i>m</i>':h?h+'<i>h</i>':m+'<i>m</i>';}
function h2t(h){h=((h%24)+24)%24;const hh=Math.floor(h),mm=Math.round((h-hh)*60);return String(hh).padStart(2,'0')+':'+String(mm===60?0:mm).padStart(2,'0');}
function addDays(d,n){const r=new Date(d);r.setDate(r.getDate()+n);return r;}
function dateStr(d){return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;}
function weekStart(d){const r=new Date(d);r.setDate(r.getDate()-((r.getDay()+6)%7));r.setHours(0,0,0,0);return r;}
function today(){const d=new Date();d.setHours(0,0,0,0);return d;}
const WKD=['周日','周一','周二','周三','周四','周五','周六'];
let TBASE=today();   // 永远锚定真实今天；空天就诚实显示空（旧"演示最忙一天"回退已移除）

/* ---------- 24h 时钟盘 ---------- */
function polar(cx,cy,r,h){const a=(h/24*360-90)*Math.PI/180;return[cx+r*Math.cos(a),cy+r*Math.sin(a)];}
function sector(cx,cy,r1,r2,h1,h2,fill){
 if(h2-h1<=0.001)return'';
 const[x1o,y1o]=polar(cx,cy,r2,h1),[x2o,y2o]=polar(cx,cy,r2,h2),[x2i,y2i]=polar(cx,cy,r1,h2),[x1i,y1i]=polar(cx,cy,r1,h1);
 const lg=(h2-h1)>12?1:0;
 return `<path d="M${x1o} ${y1o} A${r2} ${r2} 0 ${lg} 1 ${x2o} ${y2o} L${x2i} ${y2i} A${r1} ${r1} 0 ${lg} 0 ${x1i} ${y1i} Z" fill="${fill}"/>`;}
function clock(evs,d){
 const cx=150,cy=150,R=128,ri=96;let s='';
 s+=`<defs><pattern id="slp" width="7" height="7" patternUnits="userSpaceOnUse"><rect width="7" height="7" fill="#FFFFFF"/><circle cx="3.5" cy="3.5" r="1.15" fill="#D9D2C2"/></pattern></defs>`;
 s+=`<circle cx="${cx}" cy="${cy}" r="${(R+ri)/2}" fill="none" stroke="#EEE7DB" stroke-width="${R-ri}"/>`;
 evs.forEach(e=>{const col=e.cat==='sleep'?'url(#slp)':CM[e.cat].color;let a=e.start,b=Math.min(e.end,24);
   if(e.end>24){s+=sector(cx,cy,ri,R,a,24,col);s+=sector(cx,cy,ri,R,0,e.end-24,col);}else s+=sector(cx,cy,ri,R,a,b,col);});
 // 今天：剩余时间灰色 + now 指针
 const isToday=dateStr(d)===dateStr(today());
 if(isToday){const now=new Date();const nh=now.getHours()+now.getMinutes()/60;
   s+=sector(cx,cy,ri,R,nh,24,'rgba(138,132,117,.14)');
   const[px,py]=polar(cx,cy,R+4,nh),[ix,iy]=polar(cx,cy,ri-4,nh);
   s+=`<line x1="${ix}" y1="${iy}" x2="${px}" y2="${py}" stroke="#1D1D1D" stroke-width="2"/><circle cx="${px}" cy="${py}" r="3.4" fill="#1D1D1D"/>`;}
 // 刻度 + 数字
 for(let h=0;h<24;h++){const[tx,ty]=polar(cx,cy,R+2,h),[tx2,ty2]=polar(cx,cy,R+ (h%6===0?9:6),h);
   s+=`<line x1="${tx}" y1="${ty}" x2="${tx2}" y2="${ty2}" stroke="#C9CFD6" stroke-width="${h%6===0?1.4:0.8}"/>`;
   if(h%3===0){const[nx,ny]=polar(cx,cy,R+20,h);s+=`<text x="${nx}" y="${ny}" font-size="12" fill="#9AA0A8" font-weight="700" text-anchor="middle" dominant-baseline="central">${h}</text>`;}}
 return `<svg id="clocksvg" viewBox="-16 -16 332 332" style="cursor:pointer">${s}</svg>`;
}

/* ---------- 实时计时:点表盘"现在"或⏱ → 选类目开始;点底部计时条 → 结束落账 ---------- */
function toast(msg){const t=document.createElement('div');t.className='toast';t.textContent=msg;document.body.appendChild(t);setTimeout(()=>t.remove(),2600);}
// HTML 转义：所有用户可输入文本（标题/备注，含云端同步来的）进 innerHTML 前必须过这层（防存储型注入）
const esc=s=>String(s==null?'':s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
function tGet(){try{const t=JSON.parse(localStorage.getItem('ztTimer')||'null');
 if(t&&!(typeof t.start==='number'&&isFinite(t.start)&&t.start<=Date.now()+60000&&Date.now()-t.start<7*86400000)){
  localStorage.removeItem('ztTimer');toast('⏱ 计时状态异常，已重置');return null;}   // 未来/损坏/超7天的 start：一律清掉，绝不落账
 return t;}catch(e){return null;}}
function tSet(t){t?localStorage.setItem('ztTimer',JSON.stringify(t)):localStorage.removeItem('ztTimer');renderTimerBar();}
function startTimerFlow(){
 if(tGet()){renderTimerBar();return;}
 catSheet('现在开始做什么？','⏱ 开始计时（结束时自动记录时长）',k=>{
  const c=CM[k];const go=(kids,sub)=>tSet({start:Date.now(),cat:k,sub:sub||(c.sub&&c.sub[0])||'',kids:kids||[]});
  if(k==='family')openKids(kids=>go(kids,''));
  else if(SUBMAP[k])openSubs(k,sub=>go([],sub));
  else go([],'');
 },'<button class="kok" id="tskip">⏱ 先计时 · 结束再选做了什么</button>');
 setTimeout(()=>{const b=document.getElementById('tskip');if(b)b.onclick=ev=>{ev.stopPropagation();
  document.querySelector('.mask').remove();tSet({start:Date.now(),cat:null,sub:'',kids:[]});};},0);}
function stopTimerSheet(){
 const t=tGet();if(!t)return;
 const calcMins=()=>Math.max(1,Math.round((Date.now()-t.start)/60000));
 const c=t.cat?(CM[t.cat]||{label:t.cat}):{icon:'❓',label:'还没选类'};
 const m=document.createElement('div');m.className='mask';m.style.zIndex=60;
 const hdr=()=>`⏱ ${c.icon||''} ${c.label}${t.sub?' · '+t.sub:''} · 已计 ${fmtDur(calcMins())}`;
 m.innerHTML=`<div class="sheet"><div class="sh-t" id="tshdr">${hdr()}</div>
  ${calcMins()>720?'<div class="sh-t" style="color:#C2562F;font-weight:800">⚠ 已连续计时超过 12 小时——若是忘了关，建议「丢弃」后用 ＋ 手动补录真实时段</div>':''}
  <input class="anote" id="tnote" placeholder="备注几个字：做了什么(可选)" maxlength="30">
  <button class="aitog" id="tai" type="button">⚡ 用了 AI</button>
  <button class="kok">结束并保存</button>
  <button class="edit2">继续计时</button>
  <button class="del">丢弃这次计时</button></div>`;
 const _iv=setInterval(()=>{if(!document.body.contains(m)){clearInterval(_iv);return;}const el=m.querySelector('#tshdr');if(el)el.textContent=hdr();},30000);   // 挂起久了「已计」也不失真
 m.onclick=ev=>{
  if(ev.target.id==='tai'){ev.target.classList.toggle('on');return;}
  if(ev.target===m||ev.target.classList.contains('edit2')){m.remove();return;}
  if(ev.target.classList.contains('del')){
   if(!ev.target.dataset.arm){ev.target.dataset.arm='1';ev.target.textContent='⚠ 再点一次确认丢弃';return;}   // 二次确认：单击误触不再一键销毁
   tSet(null);m.remove();return;}
  if(ev.target.classList.contains('kok')){
   const endTs=Date.now();   // 结束时刻=点「结束并保存」这一刻；补选类目挂起多久都不再膨胀时长
   const finMins=Math.max(1,Math.round((endTs-t.start)/60000));
   const note=(m.querySelector('#tnote').value||'').trim();
   if(m.querySelector('#tai').classList.contains('on')&&!(t.kids||[]).includes('AI'))t.kids=[...(t.kids||[]),'AI'];
   const doSave=(cat,sub,kids)=>{
    const cc=CM[cat]||{label:cat};
    if(!(typeof t.start==='number'&&isFinite(t.start)&&t.start<=endTs)){tSet(null);toast('⏱ 计时状态异常，未入账');render();return;}   // 异常状态直接丢弃：不落 MANUAL 不上云
    const st=new Date(t.start),en=new Date(endTs);
    const sh=st.getHours()+st.getMinutes()/60, eh=en.getHours()+en.getMinutes()/60;
    const sds=dateStr(st), eds=dateStr(en);
    const tg=[...new Set([...(kids||[]),...(t.kids||[])])];
    const base={cat,sub:sub||'',note,tags:tg};
    const ttl=note||sub||cc.label;
    if(sds===eds) saveManual(sds,{...base,title:ttl,start:Math.round(sh*100)/100,end:Math.max(Math.round(sh*100)/100+0.02,Math.round(eh*100)/100)});
    else{ saveManual(sds,{...base,title:ttl,start:Math.round(sh*100)/100,end:24});            // 跨午夜：首日 sh→24
          for(let dd=addDays(st,1);dateStr(dd)<eds;dd=addDays(dd,1))saveManual(dateStr(dd),{...base,title:ttl,start:0,end:24});   // 中间整天 0→24（跨多个午夜不再丢天）
          saveManual(eds,{...base,title:ttl,start:0,end:Math.max(0.02,Math.round(eh*100)/100)}); }
    tSet(null);render();};
   m.remove();
   if(t.cat){doSave(t.cat,t.sub,t.kids);return;}
   catSheet('刚才这 '+fmtDur(finMins)+' 做的是什么？','⏱ 补上类目就入账',k=>{
    const cc=CM[k];
    if(k==='family')openKids(kids=>doSave(k,'',kids));
    else if(SUBMAP[k])openSubs(k,sub=>doSave(k,sub,[]));
    else doSave(k,(cc.sub&&cc.sub[0])||'',[]);
   });}};
 document.body.appendChild(m);}
function renderTimerBar(){
 const old=document.getElementById('timerbar');if(old)old.remove();
 const t=tGet();if(!t)return;
 const c=t.cat?(CM[t.cat]||{label:t.cat}):{icon:'❓',label:'结束时再选'};
 const mins=Math.max(0,Math.round((Date.now()-t.start)/60000));
 const b=document.createElement('div');b.className='timerbar';b.id='timerbar';
 b.innerHTML=`<span class="pulse"></span>计时中 · ${c.icon||''} ${c.label}${t.sub?' · '+t.sub:''}<span class="tdur">${fmtDur(mins)}</span>`;
 b.onclick=stopTimerSheet;
 document.body.appendChild(b);}
setInterval(renderTimerBar, 30000);
/* ---------- 视图 ---------- */
let view='clock', off=0, statScope='week', insScope='week';
const INS_WIN={week:7,month:30,quarter:90,year:365};
function scopeName(){return {week:'本周',month:'近30天',quarter:'近一季',year:'近一年'}[insScope];}
function insDays(){ // 洞察当前维度的天数组（week=周一起，其它=截至锚点的滚动窗口）
 if(insScope==='week'){const ws=weekStart(curDay());return Array.from({length:7},(_,i)=>addDays(ws,i));}
 const N=INS_WIN[insScope],a=curDay();return Array.from({length:N},(_,i)=>addDays(a,-(N-1-i)));}
function curDay(){return addDays(TBASE,off);}

function vClock(){
 const d=curDay(),ds=dateStr(d),evs=genDay(ds),ou=OURA_DATA[ds];
 const m=catMins(evs),work=WORK.reduce((s,k)=>s+(m[k]||0),0),logged=Object.values(m).reduce((a,b)=>a+b,0);
 const isToday=ds===dateStr(today());
 let ctr;
 if(isToday){const now=new Date(),nh=now.getHours()+now.getMinutes()/60,rem=(24-nh)*60;
   ctr=`<div class="rg">${h2t(nh)}–24:00</div><div class="lb">今日剩余</div><div class="big">${fmtDur(rem)}</div>`;}
 else ctr=`<div class="rg">${ds.slice(5)} · ${WKD[d.getDay()]}</div><div class="lb">已记录</div><div class="big">${fmtDur(logged)}</div>`;
 window._evs=evs;
 // 时间线：事件行 + 可点的"空白补录"行
 let list='';
 if(!evs.length){list='<div class="gap" data-s="9" data-e="10">＋ 这天还没有记录 · 点此补录</div>';}
 else{let prev=null;
  evs.forEach((e,i)=>{
   if(prev!=null && e.start-prev>=0.5 && prev>=6 && e.start<=23.5)
     list+=`<div class="gap" data-s="${prev}" data-e="${e.start}">＋ ${h2t(prev)}–${h2t(e.start)} 空白 · 点此补录</div>`;
   const c=CM[e.cat];
   list+=`<div class="tli" data-i="${i}"><div class="tm">${h2t(e.start)}<br>${h2t(e.end)}</div>
    <span class="dot" style="background:${c.color}"></span><span class="nm">${e.cat!=='sleep'?`<b class="catpx" style="color:${c.color}">【${c.label}】</b>`:''}${esc(e.title)}${e.man?' <span class="mtag">手动</span>':''}</span>
    <span class="du">${fmtShort((e.end-e.start)*60)}</span><span class="ch">›</span></div>`;
   prev=Math.max(prev==null?0:prev,e.end);});
  const isT=ds===dateStr(today()),nowH=new Date().getHours()+new Date().getMinutes()/60,lim=isT?nowH:24;
  if(prev!=null && lim-prev>=0.5 && prev>=6 && prev<23.5)
   list+=`<div class="gap" data-s="${prev}" data-e="${Math.min(lim,prev+1).toFixed(2)}">＋ ${h2t(prev)} 起 · 点此补录</div>`;}
 // 健康 + 双角色概览（爱时间没有，你的数据独有）
 const fam=(m.family||0)+(m.self||0), rec=(ou&&ou.rec>0)?ou.rec:null, sh=(ou&&ou.hrs>0)?ou.hrs:null;   // hrs/rec=0 表示 WHOOP 尚未定稿（只有起止时刻）→ 显示 -- 而非红色 0
 const GRN='#5E9C6B',AMB='#E0922A',RED='#D2553A';
 const sleepC=sh==null?'#C2B8A6':sh>=8?GRN:sh<5?RED:'#1D1D1D';      // 睡眠：≥8绿 <5红 中间黑
 const recC=rec==null?'#C2B8A6':rec>=67?GRN:rec>=34?AMB:RED;        // 恢复分：≥67绿 34-66黄 <34红
 const ov=`<div class="ov">
   <div class="ovi"><b style="color:${sleepC}">${sh!=null?sh+'<i>h</i>':'--'}</b><span>睡眠</span></div>
   <div class="ovi"><b style="color:${recC}">${rec!=null?rec:'--'}</b><span>恢复分</span></div>
   <div class="ovi"><b>${fmtU(work)||'0<i>m</i>'}</b><span>工作</span></div>
   <div class="ovi"><b>${fmtU(fam)||'0<i>m</i>'}</b><span>家庭·自我</span></div>
 </div>`;
 // 角色体检：一开 App（时钟页）就看清本周——战略被挤压？家庭够不够？（全用已流逝口径）
 const _ws=weekStart(today()),_wd=Array.from({length:7},(_,i)=>addDays(_ws,i));
 let _wk=0,_st=0,_fa=0;_wd.forEach(dd=>{const mm=catMinsElapsed(dateStr(dd));WORK.forEach(k=>_wk+=(mm[k]||0));_st+=(mm.strategy||0)+(mm.global||0);_fa+=(mm.family||0);});
 const _stP=_wk?Math.round(_st/_wk*100):0,_faH=_fa/60;
 const _fg=goals().find(x=>x.key==='family'),_df=_fg?(_fg.period==='每周'?_fg.target/7:_fg.target):3;
 const _ed=_wd.filter(dd=>dateStr(dd)<=dateStr(today())).length||1,_fgoal=_df*_ed;
 let _ai=0;_wd.forEach(dd=>{_ai+=aiHrsElapsed(dateStr(dd));});
 const _aiP=_wk?Math.round(_ai*60/_wk*100):0;
 const rc=`<div class="rcheck"><span class="rlab">本周体检</span>`
   +`<span class="rc-i">战略 <b class="${_stP<20?'w':'g'}">${_stP}%</b>${_stP<20?'·被挤压':''}</span>`
   +`<span class="rc-i">陪家庭 <b class="${_faH>=_fgoal?'g':'w'}">${_faH.toFixed(1)}h</b>${_faH>=_fgoal?'·✓':'·目标'+_fgoal.toFixed(0)+'h'}</span>`
   +`<span class="rc-i">⚡AI <b class="g">${_aiP}%</b></span></div>`;
 return `<div class="clockwrap"><div class="clock">${clock(evs,d)}<div class="ctr">${ctr}</div></div></div>${ov}${rc}<div class="tl">${list}</div>
  <button class="fab2" id="fabT" title="开始计时">⏱</button><button class="fab" id="fab">＋</button>`;
}

// 单日已流逝分钟：过去=1440，今天=到此刻，未来=0（分母只算真实发生过的时间）
function elapsedMin(ds){
 const tds=dateStr(today());
 if(ds<tds)return 1440;
 if(ds>tds)return 0;
 const n=new Date();return Math.round((n.getHours()*60+n.getMinutes()));
}
// 该日「到此刻」的边界（小时）：过去=24，今天=当前时刻，未来=0。
// 事件只在 [start, min(end, 边界)] 范围内算作已发生，绝不把未来排程当既成事实。
function nowBound(ds){const tds=dateStr(today());if(ds<tds)return 24;if(ds>tds)return 0;const n=new Date();return n.getHours()+n.getMinutes()/60;}
// 只计已发生部分的 catMins：把每条事件截到「到此刻」边界内（诚实口径，与统计页一致）
function catMinsElapsed(ds){const b=nowBound(ds),m={};if(b<=0)return m;
 genDay(ds).forEach(e=>{const s=Math.min(e.start,b),en=Math.min(e.end,b);if(en>s)m[e.cat]=(m[e.cat]||0)+(en-s)*60;});return m;}
// 只计已发生部分的孩子陪伴时长（截到「到此刻」）
function kidHrsElapsed(ds,key){const b=nowBound(ds);if(b<=0)return 0;let t=0;
 genDay(ds).forEach(e=>{if((e.tags||[]).includes(key)){const s=Math.min(e.start,b),en=Math.min(e.end,b);if(en>s)t+=en-s;}});return t;}
// 某日 AI 标签的工作时长(小时,已流逝口径)——AI 渗透率的分子
function aiHrsElapsed(ds){const b=nowBound(ds);if(b<=0)return 0;let t=0;
 genDay(ds).forEach(e=>{if(WORK.includes(e.cat)&&(e.tags||[]).includes('AI')){const s0=Math.min(e.start,b),e0=Math.min(e.end,b);if(e0>s0)t+=e0-s0;}});return t;}
// 窗口是否含「今天或未来」——用于给标题打「截至此刻」标记
function winPartial(days){const tds=dateStr(today());return days.some(d=>dateStr(d)>=tds);}
function aggregate(scope){
 const d=curDay();const m={};let totalSpan=0,partial=false;
 // 分子也只算「已发生」部分：事件截到「到此刻」边界，避免今天满额排程 / 未来事件把占比冲到 >100%
 let covered=0;
 const add=ds=>{const x=catMinsElapsed(ds);for(const k in x)m[k]=(m[k]||0)+x[k];
   const el=elapsedMin(ds);totalSpan+=el;if(el<1440)partial=true;
   const b=nowBound(ds);
   const iv=genDay(ds).map(e=>[Math.max(0,e.start),Math.min(e.end,b)]).filter(v=>v[1]>v[0]).sort((a,c)=>a[0]-c[0]);
   let cur=-1;iv.forEach(([a,c])=>{if(a>cur){covered+=(c-a)*60;cur=c;}else if(c>cur){covered+=(c-cur)*60;cur=c;}});};
 if(scope==='day'){add(dateStr(d));}
 else if(scope==='week'){const ws=weekStart(d);for(let i=0;i<7;i++)add(dateStr(addDays(ws,i)));}
 else if(scope==='month'){const dim=new Date(d.getFullYear(),d.getMonth()+1,0).getDate();
   for(let i=1;i<=dim;i++)add(dateStr(new Date(d.getFullYear(),d.getMonth(),i)));}
 else if(scope==='quarter'){const q0=new Date(d.getFullYear(),Math.floor(d.getMonth()/3)*3,1),q1=new Date(q0.getFullYear(),q0.getMonth()+3,0);
   for(let x=new Date(q0);x<=q1;x.setDate(x.getDate()+1))add(dateStr(x));}
 else{const y0=new Date(d.getFullYear(),0,1),y1=new Date(d.getFullYear(),11,31);
   for(let x=new Date(y0);x<=y1;x.setDate(x.getDate()+1))add(dateStr(x));}
 // partial=分母含今天(未走完)或未来天，说明是"截至此刻"口径
 return {m,totalSpan:totalSpan||1,partial,covered};
}
function vStats(){
 const {m,totalSpan,partial,covered}=aggregate(statScope);
 const span=totalSpan; // 已=elapsed 分母，>=1
 const logged=Object.values(m).reduce((a,b)=>a+b,0);
 let unrec=0;scopeDaysList().forEach(gd=>dayGaps(dateStr(gd)).forEach(([a,c])=>unrec+=(c-a)*60));   // 与空白清单同口径:06:00 后 ≥30min 的可补录空档,点进去数字对得上
 const hasData=Object.keys(m).some(k=>m[k]>0);
 const rows=Object.keys(m).filter(k=>m[k]>0).map(k=>({k,v:m[k],c:CM[k]})).sort((a,b)=>b.v-a.v);
 if(unrec>5)rows.push({k:'unrec',v:unrec,c:{label:'未记录',color:'#E2DACB',icon:''}});
 const _d=curDay(),_md=x=>`${x.getMonth()+1}/${x.getDate()}`;
 let scopeTxt;
 if(statScope==='day')scopeTxt=`${_md(_d)} ${WKD[_d.getDay()]}`+(partial?' · 截至此刻':' · 全天');
 else if(statScope==='week'){const ws=weekStart(_d),we=addDays(ws,6),en=partial?today():we;
   scopeTxt=`${_md(ws)}(周一) – ${_md(en)}`+(partial?' · WTD 截至此刻':' · 整周');}
 else if(statScope==='month'){const en=partial?today():new Date(_d.getFullYear(),_d.getMonth()+1,0);
   scopeTxt=`${_d.getMonth()+1}/1 – ${_md(en)}`+(partial?' · MTD 截至此刻':' · 整月');}
 else if(statScope==='quarter'){const q0=new Date(_d.getFullYear(),Math.floor(_d.getMonth()/3)*3,1),q1=new Date(q0.getFullYear(),q0.getMonth()+3,0),en=partial?today():q1;
   scopeTxt=`Q${Math.floor(_d.getMonth()/3)+1} ${_md(q0)} – ${_md(en)}`+(partial?' · QTD 截至此刻':' · 整季');}
 else{const en=partial?today():new Date(_d.getFullYear(),11,31);
   scopeTxt=`1/1 – ${_md(en)}`+(partial?' · YTD 截至此刻':' · 整年');}
 const seg=`<div class="seg2">
   <button data-s="day" class="${statScope==='day'?'on':''}">日</button>
   <button data-s="week" class="${statScope==='week'?'on':''}">周</button>
   <button data-s="month" class="${statScope==='month'?'on':''}">月</button>
   <button data-s="quarter" class="${statScope==='quarter'?'on':''}">季</button>
   <button data-s="year" class="${statScope==='year'?'on':''}">年</button></div>`;
 if(!hasData) return seg+`<div class="tl"><div class="empty" style="padding:48px 24px;line-height:1.7">
   这段还没有任何记录<br><span style="font-size:12.5px;color:var(--mut2)">点右下角 <b style="color:var(--tang)">＋</b> 或时钟页空白段补录</span></div></div>
   <button class="fab" id="fabS">＋</button>`;
 return seg+
  `<div class="sthdr"><span>${scopeTxt}</span><span>已记录 ${fmtShort(logged)} · 覆盖 ${Math.min(100,Math.round((covered||0)/span*100))}%</span></div>
  ${rows.map(r=>{const isU=r.k==='unrec';
   const slp=r.k==='sleep'?' slpdot':'';
   return `<div class="srow${isU?' srow-u':''}"${isU?' data-unrec="1"':` data-cat="${r.k}" style="cursor:pointer"`}><div class="t"><span class="dot${slp}" style="background:${r.c.color}"></span>
   <span class="nm">${r.c.icon?r.c.icon+' ':''}${r.c.label}${isU?' <span class="uadd">＋ 补录</span>':''}</span><span class="du">${fmtShort(r.v)}${(()=>{if(isU)return '';const g=goals().find(x=>x.key===r.k);if(!g)return '';const de=g.period==='每周'?g.target/7:g.target;return ` <em class="tgl">${g.cap?'≤':'目标'}${Math.round(de/24*100)}%</em>`;})()}</span>
   <span class="pc">${Math.round(r.v/span*100)}%</span></div>
   <div class="bar"><i class="${slp.trim()}" style="width:${Math.min(100,r.v/span*100)}%;background:${r.c.color};display:block;height:100%"></i>${(()=>{if(isU)return '';const g=goals().find(x=>x.key===r.k);if(!g)return '';const de=g.period==='每周'?g.target/7:g.target;return `<div class="tgt2" style="left:${Math.min(98,de/24*100).toFixed(1)}%"></div>`;})()}</div></div>`;}).join('')}
  <div class="snote">竖线＝该类的参考目标（按每日目标折算到时间占比，目标页可调）。<b>未记录</b>＝这段时间里没有日历日程、也没有手动补录覆盖的部分${partial?'（分母只算到此刻，未来时间不计）':''}。点「未记录」这一行即可补录。日程撞车/补录重叠时各类相加可能 >100%，「覆盖」和「未记录」按时间轴去重计算。</div>
  <button class="fab" id="fabS">＋</button>`;
}
function vTimer(){
  const t=tGet();
  if(!t)return`<div style="height:100%;display:flex;align-items:center;justify-content:center;color:var(--mut);flex-direction:column;gap:12px;padding:40px 20px"><div style="font-size:14px;color:var(--mut);font-weight:600">还没开始计时</div><button id="timerStart" style="padding:12px 24px;background:var(--tang);color:#fff;border:none;border-radius:12px;cursor:pointer;font-weight:700">开始计时</button></div>`;
  const ms=Date.now()-t.start;
  const h=Math.floor(ms/3600000),m=Math.floor((ms%3600000)/60000),s=Math.floor((ms%60000)/1000);
  const timeStr=`${String(h).padStart(2,'0')}:${String(m).padStart(2,'0')}:${String(s).padStart(2,'0')}`;
  const cat=t.cat?CM[t.cat]:{label:'计时中',color:'#C2B8A6'};
  return`<div style="height:100%;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;padding:40px 20px"><div style="font-size:13px;color:var(--mut);font-weight:600">现在计时中</div><div style="font-size:64px;font-weight:800;font-family:monospace;letter-spacing:8px;color:var(--ink)">${timeStr}</div><div style="font-size:16px;font-weight:700;color:${cat.color}">● ${cat.label}</div><div style="display:flex;gap:12px;margin-top:20px"><button id="timerStop" style="padding:11px 24px;border:1.5px solid var(--tang);background:var(--tang);color:#fff;border-radius:12px;cursor:pointer;font-weight:700;font-size:14px">结束计时</button><button id="timerNew" style="padding:11px 24px;border:1.5px solid var(--line);background:var(--soft);border-radius:12px;cursor:pointer;font-weight:700;font-size:14px">新计时</button></div></div>`;
}

// 目标：可编辑（存 localStorage 'ztGoals'），家庭默认提到 每天3h
const GOAL_DEF=[
 {key:'family',period:'每天',target:3},{key:'sleep',period:'每天',target:7},{key:'self',period:'每天',target:1},
 {key:'strategy',period:'每周',target:10},{key:'growth',period:'每周',target:5},{key:'people',period:'每周',target:6},
 // 上限型(cap)：控制不要超——超了=被运营/会议吃掉
 {key:'operations',period:'每周',target:15,cap:true},{key:'product',period:'每周',target:8,cap:true},
 {key:'external',period:'每周',target:5,cap:true},{key:'travel',period:'每周',target:10,cap:true},
];
const GOV=JSON.parse(localStorage.getItem('ztGoals')||'{}');
function goals(){return GOAL_DEF.map(g=>({...g,...(GOV[g.key]||{})}));}
function saveGoal(key,patch){GOV[key]={...(GOV[key]||{}),...patch};localStorage.setItem('ztGoals',JSON.stringify(GOV));const g=goals().find(x=>x.key===key);if(g)cloud('goal',{key,period:g.period,target:g.target});}
// 目标进度只算「已发生」的时间——未来排程不算达成（诚实口径，与统计/洞察一致）
function goalActual(g,d){if(g.period==='每天')return (catMinsElapsed(dateStr(d))[g.key]||0)/60;
 const ws=weekStart(d);let a=0;for(let i=0;i<7;i++)a+=(catMinsElapsed(dateStr(addDays(ws,i)))[g.key]||0)/60;return a;}
function vGoals(){
 const d=curDay(),isWk=dateStr(d)>=dateStr(weekStart(today()))&&dateStr(d)<=dateStr(addDays(weekStart(today()),6));
 const daysLeft=isWk?Math.max(1,7-((today().getDay()+6)%7)):7;  // 含今天
 return `<div class="goalhint">点任一目标卡可改数值 · 想多陪孩子？把「家庭」目标调高</div>
  <div class="goals">${goals().map(g=>{const c=CM[g.key];
  const act=goalActual(g,d),pct=Math.min(100,Math.round(act/g.target*100)),r=22,cc=2*Math.PI*r;
  const gapH=g.target-act;
  let nudge;
  if(g.cap){ nudge = gapH>=0 ? `额度还剩 ${gapH.toFixed(1)}h · 控制住 👍` : `⚠ 已超上限 ${(-gapH).toFixed(1)}h——警惕被它吃掉`; }
  else if(gapH<=0) nudge=`✓ 已达标，超额 ${(-gapH).toFixed(1)}h`;
  else if(g.period==='每天') nudge=`今天还差 ${gapH.toFixed(1)}h`;
  else nudge=`本周还差 ${gapH.toFixed(1)}h${isWk?` · 剩 ${daysLeft} 天，日均再 ${(gapH/daysLeft).toFixed(1)}h`:''}`;
  const _h=c.color.replace('#','');const _lum=(0.299*parseInt(_h.slice(0,2),16)+0.587*parseInt(_h.slice(2,4),16)+0.114*parseInt(_h.slice(4,6),16))/255;const lite=_lum>0.7;const fg=lite?'#1D1D1D':'#fff',tr=lite?'rgba(29,29,29,.15)':'rgba(255,255,255,.3)';
  return `<div class="gcard" style="background:${c.color};color:${fg};${lite?'border:1.5px solid var(--line);':''}" data-g="${g.key}">
   <div class="gn">${c.icon} ${c.label}</div>
   <div class="gg">${g.period} ${g.cap?'≤':'≥'} ${g.target}小时 ✎${g.cap?' · 上限':''}</div>
   <div class="now">${g.period==='每天'?'今日':'本周'} ${act.toFixed(1)}h · ${nudge}</div>
   <div class="ring"><svg viewBox="0 0 54 54"><circle cx="27" cy="27" r="${r}" fill="none" stroke="${tr}" stroke-width="5"></circle>
    <circle cx="27" cy="27" r="${r}" fill="none" stroke="${fg}" stroke-width="5" stroke-linecap="round" stroke-dasharray="${cc}" stroke-dashoffset="${cc*(1-pct/100)}" transform="rotate(-90 27 27)"></circle></svg>
    <div class="pv">${pct}%</div></div></div>`;}).join('')}</div>`;
}
function openGoalEdit(key){const g=goals().find(x=>x.key===key);if(!g)return;const c=CM[key];
 const mask=document.createElement('div');mask.className='mask';
 const render2=()=>{const gg=goals().find(x=>x.key===key);
  mask.querySelector('.ge-val').textContent=gg.target+' 小时';
  mask.querySelectorAll('.ge-p').forEach(b=>b.classList.toggle('on',b.dataset.p===gg.period));};
 mask.innerHTML=`<div class="sheet"><div class="sh-t">设定目标</div><div class="sh-n">${c.icon} ${c.label}</div>
  <div class="ge-row"><button class="ge-p" data-p="每天">每天</button><button class="ge-p" data-p="每周">每周</button></div>
  <div class="ge-stepper"><button class="ge-m">−</button><div class="ge-val">${g.target} 小时</div><button class="ge-pl">＋</button></div>
  <button class="cancel">完成</button></div>`;
 mask.onclick=ev=>{
  if(ev.target===mask||ev.target.classList.contains('cancel')){mask.remove();render();return;}
  const p=ev.target.closest('.ge-p');if(p){saveGoal(key,{period:p.dataset.p});render2();}
  if(ev.target.classList.contains('ge-pl')){saveGoal(key,{target:Math.min(24,(goals().find(x=>x.key===key).target)+0.5)});render2();}
  if(ev.target.classList.contains('ge-m')){saveGoal(key,{target:Math.max(0.5,(goals().find(x=>x.key===key).target)-0.5)});render2();}};
 document.body.appendChild(mask);render2();}
// 类别详情：近 10 周趋势 + 目标参考线 + 改目标
function openCatDetail(key){const c=CM[key],g=goals().find(x=>x.key===key);
 const thisWS=weekStart(curDay());
 const weeks=[];for(let w=9;w>=0;w--){const ws=addDays(thisWS,-7*w);let t=0;
  for(let i=0;i<7;i++){const dd=addDays(ws,i);if(dd>today())break;t+=(catMinsElapsed(dateStr(dd))[key]||0)/60;}weeks.push({ws,t});}   // 诚实口径：本周只算到今天此刻，未来排程不计（与目标卡/12周图对齐）
 const maxT=Math.max(...weeks.map(w=>w.t),g?(g.period==='每周'?g.target:g.target*7):0,1);
 const wgoal=g?(g.period==='每周'?g.target:g.target*7):null;
 const avg=weeks.reduce((s,w)=>s+w.t,0)/10, cur=weeks[9].t, prev=weeks[8].t;
 const bars=weeks.map(w=>{const hh=w.t/maxT*100,isC=dateStr(w.ws)===dateStr(thisWS);
  return `<div class="tcol"><div class="tval">${w.t>0?w.t.toFixed(0):''}</div><div class="tbar" style="height:${Math.max(2,hh)}%;background:${c.color};opacity:${isC?1:.5}"></div><div class="tlb">${w.ws.getMonth()+1}/${w.ws.getDate()}</div></div>`;}).join('');
 const ov=document.createElement('div');ov.className='detail';
 const dlt=cur-prev;
 ov.innerHTML=`<div class="dhead"><button class="dback">‹ 返回</button><b>${c.icon} ${c.label}</b><button class="dedit">改目标</button></div>
  <div class="dbody">
   <div class="dstat"><div class="ds"><b>${cur.toFixed(1)}h</b><span>本周${(dateStr(thisWS)<=dateStr(today())&&dateStr(addDays(thisWS,6))>=dateStr(today()))?'·至此刻':''}</span></div>
    <div class="ds"><b class="${dlt>=0?'up':'dn'}">${dlt>=0?'↑':'↓'}${Math.abs(dlt).toFixed(1)}h</b><span>较上周</span></div>
    <div class="ds"><b>${avg.toFixed(1)}h</b><span>10周周均</span></div>
    ${g?`<div class="ds"><b>${wgoal}h</b><span>周目标</span></div>`:''}</div>
   <div class="dtt">每周时长趋势 · 近 10 周${wgoal?' · 虚线=目标':''}</div>
   <div class="trend">${wgoal?`<div class="goalline" style="bottom:${Math.min(98,wgoal/maxT*100)}%"></div>`:''}${bars}</div>
   <div class="dnote">${(goals().find(x=>x.key===key)||{}).cap?(cur>avg?'近期高于自己的均值——这是上限型，注意别被它吃掉时间。':'近期压得比均值低，控制得不错。'):(cur>=avg?'近期高于自己的均值，保持。':'近期低于自己的均值，可以多投入。')}</div>
  </div>`;
 ov.onclick=ev=>{if(ev.target.classList.contains('dback')||ev.target===ov){ov.remove();return;}
  if(ev.target.classList.contains('dedit')){ov.remove();openGoalEdit(key);}};
 document.body.appendChild(ov);}
// ── 通用「近30天·每日」趋势下钻（复用 .detail/.trend 全套样式）──
function trendSeries(kind,key){ // 返回 {days,vals,goal|null,title,icon}（vals 复用 valOf 的诚实口径）
 const end=today(),N=30,days=Array.from({length:N},(_,i)=>addDays(end,-(N-1-i)));
 let goal=null,title='',icon='';
 if(kind==='sleep'){goal=7;title='平均睡眠';icon='😴';}
 else if(kind==='kid'){title='陪 '+key;icon='🧒';}
 else if(kind==='bucket'){const b=BUCKETS.find(x=>x.key===key);title=b.label;icon='🎯';}
 else{ // cat（含 family/self）
   const c=CM[key];
   const g=goals().find(x=>x.key===key);
   if(g)goal=g.period==='每周'?g.target/7:g.target;
   title=c?c.label:key;icon=c&&c.icon?c.icon:'';
 }
 const vals=days.map(valOf(kind,key));
 return {days,vals,goal,title,icon};
}
function valOf(kind,key){ // 单日取值函数(小时)·诚实口径：只算已发生（截到 nowBound），今天的未来排程不计，与统计/目标一致
 if(kind==='sleep')return d=>{const h=(OURA_DATA[dateStr(d)]||{}).hrs;return h&&h>0?h:0;};
 if(kind==='kid')return d=>kidHrsElapsed(dateStr(d),key);
 if(kind==='bucket'){const b=BUCKETS.find(x=>x.key===key);return d=>{const m=catMinsElapsed(dateStr(d));return b.cats.reduce((a,k)=>a+(m[k]||0),0)/60;};}
 return d=>(catMinsElapsed(dateStr(d))[key]||0)/60;
}
function fmtBar(v){return v<=0?'':(v>=1?(v>=10?Math.round(v):+v.toFixed(1))+'':Math.round(v*60)+'m');}
// 通用 SVG 柱图:基线严格对齐 + 柱顶数值 + 均值线(灰)/目标线(黑虚线胶囊标)
function svgChart(vals,ticks,color,goal,avgLabel,tag,wknd){
 const N=vals.length,W=340,H=150,pT=16,pB=15,pL=4,pR=4;
 const base=H-pB, span=base-pT;
 const have=vals.filter(v=>v>0), avg=have.length?have.reduce((a,b)=>a+b,0)/have.length:0;
 const maxV=Math.max(...vals,goal||0,avg,0.1)*1.06;
 const bw=Math.min(18,(W-pL-pR)/N*0.62), step=(W-pL-pR)/N;
 const nz=vals.map((v,i)=>v>0?i:-1).filter(i=>i>=0);
 const lab=new Set(nz.length<=14?nz:nz.filter((x,k)=>k%2===0));if(nz.length)lab.add(nz[nz.length-1]);
 let sv='';
 (wknd||[]).forEach(i=>{sv+=`<rect x="${(pL+i*step).toFixed(1)}" y="${pT-6}" width="${step.toFixed(1)}" height="${(base-pT+6).toFixed(1)}" fill="#E7DFCC" opacity="0.5"/>`;});
 vals.forEach((v,i)=>{const x=pL+i*step+step/2,h=v>0?Math.max(2,v/maxV*span):0,y=base-h;
  if(v>0)sv+=`<rect ${tag?`data-tag="${tag}" data-i="${i}" style="cursor:pointer"`:''} x="${(x-bw/2).toFixed(1)}" y="${y.toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" rx="${Math.min(3,bw/3)}" fill="${typeof color==='function'?color(v,i):color}" opacity="${i===N-1?1:.62}"/>`;
  if(lab.has(i))sv+=`<text x="${x.toFixed(1)}" y="${(y-2.5).toFixed(1)}" font-size="7.2" font-weight="700" fill="#6F6A5E" text-anchor="middle">${fmtBar(v)}</text>`;});
 // 均值线:细灰实线 + 灰字(白描边防压柱)
 if(avg>0){const ya=base-avg/maxV*span;
  sv+=`<line x1="${pL}" y1="${ya.toFixed(1)}" x2="${W-pR}" y2="${ya.toFixed(1)}" stroke="#9A937F" stroke-width="1.1"/>`;
  const yg2=goal?base-Math.min(goal,maxV)/maxV*span:-99;
  const below=goal&&yg2<ya&&(ya-yg2)<15;   // 目标线贴在均值线上方 → 标签挪线下
  sv+=`<text x="${pL+1}" y="${(below?ya+9:ya-2.5).toFixed(1)}" font-size="8" font-weight="800" fill="#8A8475" stroke="#FBFAF6" stroke-width="2.6" paint-order="stroke">${avgLabel||'均'} ${avg.toFixed(1)}h</text>`;}
 // 目标线:黑虚线 + 黑底白字胶囊(和均值一眼区分)
 if(goal){const yg=base-Math.min(goal,maxV)/maxV*span;
  sv+=`<line x1="${pL}" y1="${yg.toFixed(1)}" x2="${W-pR}" y2="${yg.toFixed(1)}" stroke="#1D1D1D" stroke-width="1.4" stroke-dasharray="5 4"/>`;
  const gt=`目标 ${goal>=10?Math.round(goal):+goal.toFixed(1)}h`,tw=gt.length*8+10,py=Math.max(1,yg-13);
  sv+=`<rect x="${W-pR-tw}" y="${py.toFixed(1)}" width="${tw}" height="12.5" rx="6.2" fill="#1D1D1D"/><text x="${W-pR-tw/2}" y="${(py+9.2).toFixed(1)}" font-size="8" font-weight="800" fill="#FAFBF9" text-anchor="middle">${gt}</text>`;}
 sv+=`<line x1="${pL}" y1="${base}" x2="${W-pR}" y2="${base}" stroke="#E3DCCB" stroke-width="1"/>`;
 ticks.forEach(([i,t])=>{const x=pL+i*step+step/2;
  sv+=`<text x="${x.toFixed(1)}" y="${H-4}" font-size="7.6" fill="#B4AC98" text-anchor="middle">${t}</text>`;});
 return `<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;display:block">${sv}</svg>`;
}
function openTrend(kind,key){
 const vf=valOf(kind,key);
 const end=today();
 const meta=trendSeries(kind,key), goal=meta.goal, title=meta.title, icon=meta.icon;
 const KIDC={Olivia:'#9678B6',George:'#6E8FA8',Max:'#7FA64B',Donald:'#B8B2A6','父母':'#8C6E45'};
 const color=kind==='sleep'?((v)=>v>=7?'#7FA64B':v>=6?'#E07A3C':'#E0301E'):(kind==='ai'?'#1D1D1D':(kind==='kid'?(KIDC[key]||'#F37434'):(CM[key]?CM[key].color:(kind==='bucket'?(BCOLOR[key]||'#F37434'):'#F37434'))));
 // 近30天每日
 const d30=Array.from({length:30},(_,i)=>addDays(end,-(29-i)));
 const v30=d30.map(vf);
 const t30=d30.map((d,i)=>(i%5===0||i===29)?[i,`${d.getMonth()+1}/${d.getDate()}`]:null).filter(Boolean);
 // 近12周(周一起,含本周)
 const ws0=weekStart(end);
 const wk=Array.from({length:12},(_,k)=>{const ws=addDays(ws0,-(11-k)*7);let t=0;for(let i=0;i<7;i++){const dd=addDays(ws,i);if(dd<=end)t+=vf(dd);}return {ws,t};});
 const vW=wk.map(x=>x.t);
 const tW=wk.map((x,i)=>(i%2===0||i===11)?[i,`${x.ws.getMonth()+1}/${x.ws.getDate()}`]:null).filter(Boolean);
 // 近6个自然月(含本月)
 const mo=Array.from({length:6},(_,k)=>{const m0=new Date(end.getFullYear(),end.getMonth()-(5-k),1),m1=new Date(m0.getFullYear(),m0.getMonth()+1,0);let t=0;for(let d=new Date(m0);d<=m1&&d<=end;d.setDate(d.getDate()+1))t+=vf(new Date(d));return {m0,t};});
 const vM=mo.map(x=>x.t);
 const tM=mo.map((x,i)=>[i,`${x.m0.getMonth()+1}月`]);
 const have=v30.filter(v=>v>0), avg=have.length?have.reduce((a,b)=>a+b,0)/have.length:0;
 const sum=v30.reduce((a,b)=>a+b,0), cur=v30[29], prev=v30[28]||0, dlt=cur-prev;
 const fmtH=v=>v>=10?Math.round(v)+'h':v.toFixed(1)+'h';
 const ov=document.createElement('div');ov.className='detail';
 ov.innerHTML=`<div class="dhead"><button class="dback">‹ 返回</button><b>${icon} ${title}</b><span style="width:44px"></span></div>
  <div class="dbody">
   <div class="dstat">
     <div class="ds"><b>${fmtH(cur)}</b><span>昨日/今日</span></div>
     <div class="ds"><b class="${dlt>=0?'up':'dn'}">${dlt>=0?'↑':'↓'}${Math.abs(dlt).toFixed(1)}h</b><span>较前一天</span></div>
     <div class="ds"><b>${fmtH(avg)}</b><span>30天日均</span></div>
     ${goal?`<div class="ds"><b>${goal.toFixed(goal>=10?0:1)}h</b><span>每日目标</span></div>`:`<div class="ds"><b>${fmtH(sum)}</b><span>30天合计</span></div>`}
   </div>
   <div class="dtt">近 30 天 · 每日<span class="dhint">柱顶=当日时长(h,不足1小时为分钟) · 灰线=日均 · 黑虚线=目标</span></div>
   ${svgChart(v30,t30,color,goal,'均','d',d30.map((d,i)=>(d.getDay()===0||d.getDay()===6)?i:-1).filter(i=>i>=0))}
   <div class="dtt">近 12 周 · 每周合计<span class="dhint">看趋势更稳</span></div>
   ${svgChart(vW,tW,color,goal?goal*7:null,'周均','w')}
   <div class="dtt">近 6 个月 · 每月合计</div>
   ${svgChart(vM,tM,color,null,'月均','m')}
   <div class="dnote">${have.length?((kind==='cat'&&(goals().find(x=>x.key===key)||{}).cap)?(cur>avg?'高于日均——上限型，警惕被它吃掉时间。':'压在日均下，控制得不错。'):(cur>=avg?'昨日高于近30天日均，保持。':'昨日低于近30天日均，可以多投入。')):'近30天暂无该项记录。'}${kind==='kid'?'<br>仅统计日历中点名到该孩子的事件；多数「家庭」时间未点名。':''}</div>
  </div>`;
 // 点柱子 → 这根柱由哪些日程构成
 const match=e=>{
  if(kind==='ai')return WORK.includes(e.cat)&&(e.tags||[]).includes('AI');
  if(kind==='sleep')return e.cat==='sleep';
  if(kind==='kid')return (e.tags||[]).includes(key);
  if(kind==='bucket'){const b=BUCKETS.find(x=>x.key===key);return b.cats.includes(e.cat);}
  return e.cat===key;};
 const showBar=(tag,i)=>{
  let d0,d1,lab;
  if(tag==='d'){d0=d30[i];d1=d30[i];lab=`${d0.getMonth()+1}/${d0.getDate()}`;}
  else if(tag==='w'){d0=addDays(ws0,-(11-i)*7);d1=addDays(d0,6);lab=`${d0.getMonth()+1}/${d0.getDate()} 那周`;}
  else{d0=new Date(end.getFullYear(),end.getMonth()-(5-i),1);d1=new Date(d0.getFullYear(),d0.getMonth()+1,0);lab=`${d0.getMonth()+1}月`;}
  let rows='',tot=0;
  for(let d=new Date(d0);d<=d1&&d<=end;d.setDate(d.getDate()+1)){const ds=dateStr(d),bd=nowBound(ds);if(bd<=0)continue;
   genDay(ds).filter(match).forEach(e=>{if(e.start>=bd)return;const en=Math.min(e.end,bd),du=en-e.start;tot+=du;   // 明细同为诚实口径：截到「到此刻」，与柱值对得上
    rows+=`<div class="bdrow" data-ds="${ds}"><span class="bdd">${d.getMonth()+1}/${d.getDate()}</span><span class="bdt">${h2t(e.start)}–${h2t(en)}</span><span class="bdn">${esc(e.title)}${e.man?' <span class="mtag">手动</span>':''}</span><span class="bdu">${fmtShort(du*60)}</span></div>`;});}
  const m=document.createElement('div');m.className='mask';m.style.zIndex=60;
  m.innerHTML=`<div class="sheet"><div class="sh-t">${lab} · ${title} · 共 ${fmtShort(tot*60)}</div>
   <div class="bdlist">${rows||'<div class="bdempty">这段没有明细记录</div>'}</div>
   <div class="bdhint">点某条可跳到那天的时间线</div><button class="cancel">关闭</button></div>`;
  m.onclick=ev=>{
   if(ev.target===m||ev.target.classList.contains('cancel')){m.remove();return;}
   const r=ev.target.closest('.bdrow');
   if(r){const ds=r.dataset.ds;const t=new Date(ds+'T00:00:00');
    off=Math.round((t-TBASE)/86400000);view='clock';
    document.querySelectorAll('.tabs button').forEach(x=>x.classList.toggle('on',x.dataset.v==='clock'));
    m.remove();ov.remove();render();}};
  document.body.appendChild(m);};
 ov.querySelectorAll('rect[data-tag]').forEach(r=>{r.addEventListener('click',()=>showBar(r.dataset.tag,+r.dataset.i));});
 ov.onclick=ev=>{if(ev.target.classList.contains('dback')||ev.target===ov)ov.remove();};
 document.body.appendChild(ov);
}

/* ---------- 洞察层 ---------- */
const BUCKETS=[
 {key:'strategy',cats:['strategy','global'],label:'战略方向',tgt:35},
 {key:'ops',cats:['operations','product'],label:'运营执行',tgt:25},
 {key:'people',cats:['people'],label:'组织人才',tgt:20},
 {key:'external',cats:['external'],label:'对外关系',tgt:2},
 {key:'growth',cats:['growth'],label:'进修成长',tgt:8},
];
const BCOLOR={strategy:'#F37434',ops:'#D69A3C',people:'#A6C061',external:'#B4643E',growth:'#818A7D'};
function vInsights(){
 const days=insDays();
 const partial=winPartial(days); // 窗口含今天/未来 → 只算到此刻，标题打「截至此刻」
 // 诚实口径：每天只统计「已发生」部分，未来排程不计（与统计页 elapsed 一致）
 const dms=days.map(d=>catMinsElapsed(dateStr(d)));
 const bsum={};let workTot=0;
 BUCKETS.forEach(b=>{bsum[b.key]=dms.reduce((s,m)=>s+b.cats.reduce((a,k)=>a+(m[k]||0),0),0);workTot+=bsum[b.key];});
 const wt=workTot||1;
 const dev=BUCKETS.map(b=>({b,act:bsum[b.key]/wt*100,gap:bsum[b.key]/wt*100-b.tgt}));
 const over=dev.slice().sort((a,b)=>b.gap-a.gap)[0],under=dev.slice().sort((a,b)=>a.gap-b.gap)[0];
 let verdict;
 if(workTot<60) verdict=scopeName()+'记录的工作时间还太少，多记几天配比更准。';
 else verdict=`${scopeName()}时间最偏向 <b>${over.b.label}</b>（${Math.round(over.act)}% vs 目标 ${over.b.tgt}%），而 <b>${under.b.label}</b> 偏少（仅 ${Math.round(under.act)}%）。`+
   (under.b.key==='strategy'?'CEO 最该守住的战略时间被挤压了。':under.b.key==='growth'?'记得给自己留充电时间。':over.b.key==='ops'?'警惕困在运营救火。':'');
 const bars=BUCKETS.map(b=>{const act=bsum[b.key]/wt*100;
  return `<div class="brow" data-bucket="${b.key}" style="cursor:pointer"><div class="bl"><span class="nm">${b.label}</span><span class="vv">${Math.round(act)}%<em>${fmtShort(bsum[b.key])} · 目标${b.tgt}%</em></span></div>
   <div class="tk"><i style="width:${Math.min(100,act)}%;background:${BCOLOR[b.key]}"></i><div class="tgt" style="left:${b.tgt}%"></div></div></div>`;}).join('');
 // 会议负荷（只看工作类；重叠去重；分清"撞车"与"背靠背"）
 let mtg=0,b2b=0,gaps=0,eve=0,longest=0,conflicts=0,mergedMin=0;
 days.forEach(d=>{const ds=dateStr(d),bd=nowBound(ds); // 只看已发生的会议：把事件截到「到此刻」，未来的会不算负荷
  const evs=genDay(ds).filter(e=>WORK.includes(e.cat)&&e.start<bd).map(e=>({...e,end:Math.min(e.end,bd)})).sort((a,b)=>a.start-b.start);
  mtg+=evs.length;let mS=null,mE=null,cs=null,ce=null;
  evs.forEach((e,i)=>{
   if(e.end>19)eve+=(Math.min(e.end,24)-Math.max(e.start,19));
   if(i>0){const g=e.start-evs[i-1].end;
     if(g<-0.001)conflicts++; else {gaps++; if(g<=0.25)b2b++;}}
   if(mE===null){mS=e.start;mE=e.end;}
   else if(e.start<=mE+0.001){mE=Math.max(mE,e.end);}
   else {mergedMin+=(mE-mS)*60;mS=e.start;mE=e.end;}
   if(ce!==null&&e.start-ce<=0.25)ce=Math.max(ce,e.end);
   else {if(ce!==null)longest=Math.max(longest,ce-cs);cs=e.start;ce=e.end;}});
  if(mE!==null)mergedMin+=(mE-mS)*60;
  if(ce!==null)longest=Math.max(longest,ce-cs);});
 const b2bP=gaps?Math.round(b2b/gaps*100):0;
 // 精力 × 时间
 const dayWork=days.map((d,i)=>BUCKETS.reduce((s,b)=>s+b.cats.reduce((a,k)=>a+(dms[i][k]||0),0),0)/60);
 const wr=days.map((d,i)=>({wh:dayWork[i],rec:(OURA_DATA[dateStr(d)]||{}).rec})).filter(x=>x.rec!=null);
 let ec;
 if(wr.length>=4){const so=wr.slice().sort((a,b)=>b.wh-a.wh),half=Math.ceil(so.length/2);
  const avg=a=>Math.round(a.reduce((s,x)=>s+x.rec,0)/a.length);
  const hi=avg(so.slice(0,half)),lo=avg(so.slice(half));
  ec=`<div class="ecorr"><div class="ec"><b class="${hi<lo?'r':'g'}">${hi}</b><span>开会多的日子<br>平均恢复分</span></div>
   <div class="ec"><b class="${lo>=hi?'g':'r'}">${lo}</b><span>开会少的日子<br>平均恢复分</span></div></div>
   <div class="inote">${hi<lo?`开会多的日子恢复分平均低 <b>${lo-hi} 分</b> —— 身体在替你记账。考虑给最满的几天之后留恢复缓冲。`:'本周会议量和恢复分没明显负相关，状态稳。'}</div>`;
 } else ec='<div class="inote">本周 Oura 数据不足（需 ≥4 天）来算精力×时间相关性。</div>';
 // 工作 × 生活平衡（家庭是重点）
 const wkW=workTot/60, famW=dms.reduce((s,m)=>s+(m.family||0),0)/60,
   selfW=dms.reduce((s,m)=>s+(m.self||0),0)/60, sleepW=dms.reduce((s,m)=>s+(m.sleep||0),0)/60;
 // 上一周期做同口径对比：本窗口截到「到此刻」，上一窗口就按对应天数截同一时刻，避免拿满额比已发生
 const N=days.length,pStart=addDays(days[0],-N);let famPrev=0;
 for(let i=0;i<N;i++){const cd=days[i],pd=addDays(pStart,i),cb=nowBound(dateStr(cd));if(cb<=0)continue;
   genDay(dateStr(pd)).forEach(e=>{if(e.cat!=='family')return;const s=Math.min(e.start,cb),en=Math.min(e.end,cb);if(en>s)famPrev+=en-s;});}
 // 目标只按「已发生天数」折算（已过完的天算满、今天算到此刻、未来不算），达标与否只看真实已发生
 let famGoalDays=0;days.forEach(d=>{famGoalDays+=Math.min(1,nowBound(dateStr(d))/24);});
 const fg=goals().find(x=>x.key==='family'),dailyFam=fg?(fg.period==='每周'?fg.target/7:fg.target):3,famGoal=dailyFam*famGoalDays,famD=famW-famPrev;
 const segB=[['工作',wkW,'#F37434',0],['家庭',famW,'#A6C061',1],['自我',selfW,CM.self.color,1],['睡眠',sleepW,(CM.sleep.color.toUpperCase()==='#FFFFFF'?'#EFE9DC':CM.sleep.color),0]];
 const totB=segB.reduce((s,x)=>s+x[1],0)||1;
 let _ac=0; const _stops=segB.filter(x=>x[1]>0.05).map(x=>{const p=x[1]/totB*100,s=`${x[2]} ${_ac.toFixed(2)}% ${(_ac+p).toFixed(2)}%`;_ac+=p;return s;}).join(',');
 const balCard=`<div class="icard"><div class="it">⚖️ 工作 × 生活</div><div class="isub">${scopeName()}时间去向占比 · 家庭是你最在意的</div>
   <div class="balwrap"><div class="donut" style="background:conic-gradient(${_stops||'var(--soft) 0 100%'})"><div class="dhole"><b>${Math.round(wkW/totB*100)}%</b><span>工作</span></div></div>
   <div class="ballist">${segB.map(x=>`<div class="balrow"><em style="background:${x[2]}"></em><span class="bn">${x[0]}</span><span class="bp">${Math.round(x[1]/totB*100)}%</span><span class="bh">${x[1].toFixed(x[3])}h</span></div>`).join('')}</div></div>
   <div class="famnudge">👨‍👩‍👧 陪伴家庭 <b>${famW.toFixed(1)}h</b>${partial?'（截至此刻）':''} · 较上一周期 ${famD>=0?'<span class="up">↑'+famD.toFixed(1)+'h</span>':'<span class="dn">↓'+Math.abs(famD).toFixed(1)+'h</span>'} · ${partial?'进度目标':'目标'} ${famGoal.toFixed(0)}h ${famW>=famGoal?`<span class="up">✓ ${partial?'进度达标':'已达标'}</span>`:`· <span class="dn">还差 ${(famGoal-famW).toFixed(1)}h</span>`}</div></div>`;
 // ---- 本周建议：按真实数据触发，克制取前 5 条 ----
 const N2=days.length;
 // 真实睡眠均值（用 WHOOP hrs，不是 genDay 的睡眠事件）
 const slH=days.map(d=>(OURA_DATA[dateStr(d)]||{}).hrs).filter(h=>h!=null&&h>0);
 const slAvg=slH.length?slH.reduce((a,b)=>a+b,0)/slH.length:null;
 const slBelow=slH.filter(h=>h<7).length;
 const stratDev=dev.find(x=>x.b.key==='strategy');   // {b,act,gap}
 const opsDev=dev.find(x=>x.b.key==='ops');
 const growthDev=dev.find(x=>x.b.key==='growth');
 const S=[];  // {ic,html,pr} pr=优先级(小=靠前)
 // 战略被挤压
 if(workTot>=60 && stratDev && stratDev.act < stratDev.b.tgt-15){
  const wkNeed = insScope==='week' ? (stratDev.b.tgt-stratDev.act)/100*(workTot/60) : null;
  const blk = wkNeed!=null ? Math.max(1,Math.round(wkNeed*2)/2) : 2;
  S.push({ic:'🧭',pr:1,html:`${scopeName()}战略仅 <em>${Math.round(stratDev.act)}%</em>（目标 ${stratDev.b.tgt}%），本周在日历 block 一段 <b>${blk}h</b> 深度战略时间，先占坑再排会。`});}
 // 运营救火
 if(workTot>=60 && opsDev && opsDev.act > opsDev.b.tgt+15){
  S.push({ic:'🪃',pr:2,html:`运营执行占 <em>${Math.round(opsDev.act)}%</em>（目标 ${opsDev.b.tgt}%），像困在执行里——挑 1–2 类高频事务授权出去，把手抽回战略。`});}
 // 睡眠护栏
 if(slAvg!=null && slAvg<7){
  S.push({ic:'😴',pr:1,html:`近期睡眠均 <em>${slAvg.toFixed(1)}h</em>，低于 7h 护栏 <b>${slBelow}</b> 晚；把最满的几天之后留一晚恢复缓冲，别连排。`});}
 // 背靠背
 if(b2bP>=60){
  S.push({ic:'⛓️',pr:2,html:`会议背靠背 <em>${b2bP}%</em>，几乎连轴转——两会之间默认留 <b>15 分钟</b>缓冲，给自己喘息和消化。`});}
 // 家庭低于目标（用已算好的 famW/famGoal）
 if(famGoal>0 && famW < famGoal*0.8){
  const gap=famGoal-famW;
  S.push({ic:'👨‍👩‍👧',pr:2,html:`陪伴家庭 <em>${famW.toFixed(1)}h</em>，距目标 ${famGoal.toFixed(0)}h 还差 <b>${gap.toFixed(1)}h</b>；本周固定 1–2 段亲子时间，写进日历当会议守。`});}
 // 进修成长被挤没
 if(workTot>=60 && growthDev && growthDev.act < growthDev.b.tgt-5){
  S.push({ic:'📚',pr:3,html:`进修成长仅 <em>${Math.round(growthDev.act)}%</em>（目标 ${growthDev.b.tgt}%），给自己留一段充电时间，别让学习永远排在最后。`});}
 // 记录太少
 if(workTot<60){
  S.push({ic:'✍️',pr:1,html:`${scopeName()}只记录了 <em>${fmtShort(workTot)}</em> 工作时间，样本还太少；多记几天，建议才够准。`});}
 S.sort((a,b)=>a.pr-b.pr);
 const top=S.slice(0,5);
 const suggBody = top.length
  ? `<ul>${top.map(s=>`<li><span class="si">${s.ic}</span><span>${s.html}</span></li>`).join('')}</ul>`
  : `<div class="sempty">✓ ${scopeName()}各项都在护栏内——战略在线、睡眠达标、会议不挤、家庭有陪伴。保持节奏就好。</div>`;
 const suggCard=`<div class="sugg"><div class="st">🧩 本周建议</div><div class="ssub">按你的真实数据生成 · 具体、可落地、点到为止</div>${suggBody}</div>`;
 return `<div class="segI">${['week','month','quarter','year'].map(s=>`<button data-i="${s}" class="${insScope===s?'on':''}">${({week:'周',month:'月',quarter:'季',year:'年'})[s]}</button>`).join('')}</div>
 <div class="ins">
  <div class="verdict"><div class="vt">${scopeName()}一句话</div><div class="vc">${verdict}</div></div>
  ${suggCard}
  ${(()=>{let aiH=0;days.forEach(d=>{aiH+=aiHrsElapsed(dateStr(d));});
    const wkH=workTot/60, pen=wkH>0?Math.round(aiH/wkH*100):0;
    const byCat={};days.forEach(d=>genDay(dateStr(d)).forEach(e=>{if(WORK.includes(e.cat)&&(e.tags||[]).includes('AI')){const b=nowBound(dateStr(d));const s0=Math.min(e.start,b),e0=Math.min(e.end,b);if(e0>s0)byCat[e.cat]=(byCat[e.cat]||0)+(e0-s0);}}));
    const top=Object.entries(byCat).sort((a,b)=>b[1]-a[1]).slice(0,4);
    return `<div class="icard" data-ait="1" style="cursor:pointer"><div class="it">⚡ AI 渗透率</div><div class="isub">用 AI 干活的时长占工作时长 · 点卡看30天趋势</div>
     <div style="display:flex;align-items:baseline;gap:12px;margin-bottom:10px"><b style="font-size:34px;font-weight:800">${pen}%</b><span style="color:var(--mut);font-weight:600;font-size:13px">AI ${aiH.toFixed(1)}h / 工作 ${wkH.toFixed(1)}h</span></div>
     ${top.length?`<div class="leg2">${top.map(([k,v])=>`<span><em style="background:${CM[k]?CM[k].color:'#999'}"></em>${CM[k]?CM[k].label:k} ${v.toFixed(1)}h</span>`).join('')}</div>`:'<div class="inote">本窗口还没有 AI 标签的工作——补录/计时时点亮「⚡用了AI」,或点日程标记。</div>'}
    </div>`;})()}
  ${balCard}
  <div class="icard"><div class="it">⚖️ CEO 时间配比</div><div class="isub">工作时间在各方向的占比 · 竖线＝参考目标（可调）</div>${bars}</div>
  <div class="icard"><div class="it">🔋 精力 × 时间</div><div class="isub">把 Oura 恢复分叠到时间分配上 —— 只有你的合并数据能看出</div>${ec}</div>
  <div class="icard"><div class="it">📋 会议负荷体检</div><div class="isub">${scopeName()} · 只看工作类、重叠已去重</div>
   <div class="mgrid">
    <div class="mcell"><b>${mtg}</b><span>工作会议数</span></div>
    <div class="mcell"><b>${fmtShort(mergedMin)}</b><span>实际工作时长</span></div>
    <div class="mcell"><b class="${longest>=4?'warn':''}">${longest?longest.toFixed(1)+'h':'—'}</b><span>最长无歇时段</span></div>
    <div class="mcell"><b class="${b2bP>=60?'warn':''}">${b2bP}%</b><span>会议背靠背</span></div>
    <div class="mcell"><b class="${eve>=5?'warn':''}">${fmtShort(eve*60)}</b><span>19:00 后工作</span></div>
    <div class="mcell" data-clash="1" style="cursor:pointer"><b class="${conflicts>0?'warn':''}">${conflicts}</b><span>日程撞车 ›</span></div>
   </div>
   <div class="inote"><b>最长无歇</b>＝首尾相接、中间没 ≥15分钟休息的最长时段（含工作午餐）。<b>背靠背</b>＝两个会间隔<15分钟就接上的占比，越高越"连轴转"。<b>撞车</b>＝同一时段订了多个日程。</div></div>
 </div>`;
}

/* ---------- 家庭 · 自身 页 ---------- */
function vFamily(){
 const end=today(),N=30,ds=Array.from({length:N},(_,i)=>addDays(end,-(N-1-i)));
 // 睡眠趋势 30 天
 const sl=ds.map(d=>({d,h:(OURA_DATA[dateStr(d)]||{}).hrs}));
 const have=sl.filter(x=>x.h!=null&&x.h>0);
 const avg=have.length?have.reduce((s,x)=>s+x.h,0)/have.length:0;
 const below=have.filter(x=>x.h<7).length;
 const W=328,H=118,pad=10,maxH=Math.max(9,...have.map(x=>x.h));
 const xs=i=>pad+i*((W-2*pad)/(N-1)), ys=h=>H-pad-(h/maxH)*(H-2*pad);
 let path='',dots='',prev=null;
 let wkbg='';const stepW=(W-2*pad)/(N-1);
 ds.forEach((d,i)=>{if(d.getDay()===0||d.getDay()===6)wkbg+=`<rect x="${(xs(i)-stepW/2).toFixed(1)}" y="4" width="${stepW.toFixed(1)}" height="${H-12}" fill="#E7DFCC" opacity="0.5"/>`;});
 sl.forEach((x,i)=>{if(x.h==null||x.h<=0){prev=null;return;}const X=xs(i),Y=ys(x.h);
   path+=(prev===null?`M${X} ${Y}`:` L${X} ${Y}`);prev=X;
   dots+=`<circle cx="${X}" cy="${Y}" r="3.1" fill="${x.h>=7?'#7FA64B':x.h>=6?'#E07A3C':'#E0301E'}"/>`;});
 const gy=ys(7);
 const sleepCard=`<div class="fcard"><div class="fhd"><div class="ft">睡眠 · 30天</div><div class="fbadge ${avg<7?'warn':''}">均 ${avg.toFixed(1)}h${avg<7?' ⚠':''}</div></div>
   <svg viewBox="0 0 ${W} ${H}" class="sleepsvg">${wkbg}<line x1="${pad}" y1="${gy}" x2="${W-pad}" y2="${gy}" stroke="#C9C2B4" stroke-width="1" stroke-dasharray="4 4"/><text x="${pad+2}" y="${gy-5}" text-anchor="start" font-size="10" font-weight="700" fill="#B7AE9C" font-family="inherit">7h 护栏</text><path d="${path}" fill="none" stroke="#6B6257" stroke-width="1.6" stroke-linejoin="round"/>${dots}</svg>
   <div class="fnote">虚线＝7h 睡眠护栏。<b>${below}</b> 晚低于护栏（共 ${have.length} 晚有记录）。睡眠是你最该补的护栏——WHOOP 数据每天 11:00 后更新。</div></div>`;
 // 陪每个孩子（近30天，来自日历点名到具体孩子的事件）
 const kids=[['Olivia','#9678B6'],['George','#6E8FA8'],['Max','#7FA64B'],['Donald','#B8B2A6'],['父母','#8C6E45']];
 const kh=Object.fromEntries(kids.map(([k])=>[k,0]));
 ds.forEach(d=>{const dss=dateStr(d),b=nowBound(dss);if(b<=0)return;genDay(dss).forEach(e=>{if(e.start>=b)return;const du=Math.min(e.end,b)-e.start;(e.tags||[]).forEach(t=>{if(kh[t]!=null)kh[t]+=du;});});});   // 诚实口径：今天只算到此刻
 const kidCards=`<div class="fcard"><div class="ft">陪伴家人（近30天 · 截至此刻）</div>
   <div class="kgrid">${kids.map(([k,c])=>`<div class="kcell" data-kid="${k}" style="cursor:pointer"><div class="kn"><em style="background:${c}"></em>${k}</div><div class="kh">${kh[k]<10?kh[k].toFixed(1):Math.round(kh[k])}<i>h</i></div></div>`).join('')}</div>
   <div class="fnote">仅统计日历中点名到具体孩子的事件；多数「家庭」时间未点名。<b>口径</b>：同一段同时陪 2–3 个孩子时，这段时长会给每个在场孩子各记一遍（不平摊），因此各娃相加可能大于总陪伴时长。想更准：点时间线某条改类，或右下角 + 补录。</div></div>`;
 // 家庭·自身 汇总（近30天）
 let famH=0,selfH=0;ds.forEach(d=>{const m=catMinsElapsed(dateStr(d));famH+=(m.family||0)/60;selfH+=(m.self||0)/60;});   // 诚实口径：今天只算到此刻
 const sumCard=`<div class="fcard"><div class="ft">家庭 · 自身（近30天 · 截至此刻）</div>
   <div class="kgrid">
     <div class="kcell" data-trend="family" style="cursor:pointer"><div class="kn"><em style="background:${CM.family.color}"></em>陪伴家庭</div><div class="kh">${Math.round(famH)}<i>h</i></div></div>
     <div class="kcell" data-trend="self" style="cursor:pointer"><div class="kn"><em style="background:${CM.self.color}"></em>自我时间</div><div class="kh">${Math.round(selfH)}<i>h</i></div></div>
     <div class="kcell" data-trend="sleep" style="cursor:pointer"><div class="kn"><em style="background:${CM.sleep.color}"></em>平均睡眠</div><div class="kh">${avg.toFixed(1)}<i>h</i></div></div>
   </div></div>`;
 return `<div class="fam">${sleepCard}${kidCards}${sumCard}</div>`;
}
/* ---------- 说明 ---------- */
function openAbout(){
 const m=document.createElement('div');m.className='amask';
 m.innerHTML=`<div class="asheet"><div class="ahd"><b>关于「Zoe · 时间」</b><button class="aclose">✕</button></div>
   <div class="abody">
    <div class="asec"><h4>🎯 它在做什么</h4><p>把你的真实时间——飞书日程 + WHOOP 睡眠恢复——自动归类、统计、给出洞察。<b>全部真实数据，零编造填充。</b></p></div>
    <div class="asec"><h4>🧠 怎么归类</h4><p>日程按语义层规则自动分到 10 类（战略 / 运营 / 对外 / 人才 / 深度 / 家庭 / 健康 / 自我 / 差旅 / 睡眠）。规则没命中的用 AI 兜底判断。<b>你改一次，它记住一次——越用越准。</b></p></div>
    <div class="asec"><h4>🔄 多久更新一次</h4>
      <p><b>日程</b>：每天 <b>6:40 / 11:00 / 16:00</b> 三次，自动拉飞书日历、重建并发布。</p>
      <p><b>睡眠 / 恢复（WHOOP）</b>：手环数据由健康归档在 <b>10:30 / 15:30 / 22:30</b> 落盘。所以当天睡眠通常在 <b>11:00</b> 那次刷新后出现，最迟 <b>16:00</b> 补齐；偶尔 WHOOP 云端定稿晚会拖到下午。<b>前一晚的睡眠不会在清晨立刻出现，属正常。</b></p></div>
    <div class="asec"><h4>✍️ 你可以怎么调</h4><p>· 点时间线某条 → 改类别 / 删除（不参加）<br>· 右下角 <b>+</b> → 手动补录一段时间<br>· 目标页 → 改每类目标、点卡片看趋势<br><span class="amut">所有修改实时云同步（多设备/与助理共享），断网时先存本机、恢复后自动补传。</span></p></div>
    <div class="asec"><h4>🧭 背后的原则</h4><p>· 只呈现真实、绝不编造填充<br>· 睡眠是第一护栏，健康优先<br>· 家庭时间是重点守护的指标<br>· CEO 时间对标理想配比（洞察页竖线＝参考目标，可调）</p><p class="amut">睡眠两口径：统计页「睡眠·在床」＝在床区间（时间账本）；概览 / 家庭页的「睡眠」＝WHOOP 实际睡眠时长（扣除清醒段），二者数字不同属正常。概览显示 -- 表示当天 WHOOP 数据尚未定稿。</p></div>
   </div></div>`;
 document.body.appendChild(m);
 m.onclick=e=>{if(e.target===m||e.target.classList.contains('aclose'))m.remove();};
}
// 撞车清理台：列出窗口内所有时段重叠对，逐条可删（人来判断哪条是重复/不参加）
function openClashList(){
 const days=insDays().filter(d=>d<=today());
 const pairs=[];
 days.forEach(d=>{const ds=dateStr(d),evs=genDay(ds).filter(e=>e.cat!=='sleep');
  for(let i=0;i<evs.length;i++)for(let j=i+1;j<evs.length;j++){
   const a=evs[i],b=evs[j],ov=Math.min(a.end,b.end)-Math.max(a.start,b.start);
   if(ov>=0.2)pairs.push({ds,a,b,ov});}});
 const m=document.createElement('div');m.className='mask';m.style.zIndex=60;
 const row=(ds,e)=>`<div class="bdrow"><span class="bdd">${+ds.slice(5,7)}/${+ds.slice(8)}</span><span class="bdt">${h2t(e.start)}–${h2t(e.end)}</span><span class="bdn">【${(CM[e.cat]||{}).label||e.cat}】${esc(e.title)}${e.man?' <span class="mtag">手动</span>':''}</span><button class="bdel">🗑</button></div>`;
 m.innerHTML=`<div class="sheet"><div class="sh-t">日程撞车 · ${scopeName()} · ${pairs.length} 对<br><span style="font-weight:500;color:var(--mut);font-size:11.5px">点条目=改时间(如实际提前结束) · 点🗑=删除 · 穿插的小会是正常的</span></div>
  <div class="bdlist">${pairs.length?pairs.map((p,i)=>`<div style="border:1px solid var(--line);border-radius:12px;margin-bottom:10px;padding:2px 8px" data-pi="${i}">${row(p.ds,p.a)}${row(p.ds,p.b)}</div>`).join(''):'<div class="bdempty">这段没有撞车 👍</div>'}</div>
  <button class="cancel">关闭</button></div>`;
 m.onclick=ev=>{
  if(ev.target===m||ev.target.classList.contains('cancel')){m.remove();return;}
  const box0=ev.target.closest('[data-pi]');if(!box0)return;
  const p=pairs[+box0.dataset.pi];
  const rowEl=ev.target.closest('.bdrow');if(!rowEl)return;
  const isFirst=rowEl===box0.querySelectorAll('.bdrow')[0];
  const e=isFirst?p.a:p.b;
  if(ev.target.closest('.bdel')){                    // 🗑 删除
   if(e.man)delManual(p.ds,e.mi); else saveDel(delKey(p.ds,e.ot,e.os));
   m.remove();render();openClashList();return;}
  m.remove();                                        // 点行 → 改时间,保存后回清单
  openEditEv(e,p.ds,()=>openClashList());};
 document.body.appendChild(m);}
function render(){
 const d=curDay();
 if(view==='insights'){const dd=insDays(),a=dd[0],b=dd[dd.length-1];
   document.getElementById('dlab').textContent=scopeName()+'洞察';
   document.getElementById('dsub').textContent=`${a.getMonth()+1}.${a.getDate()} – ${b.getMonth()+1}.${b.getDate()}`+(winPartial(dd)?' · 截至此刻':'');
 } else if(view==='clock'||view==='stats'){
   document.getElementById('dlab').textContent=off===0?'今天':`${d.getMonth()+1}月${d.getDate()}日`;
   document.getElementById('dsub').textContent=`${dateStr(d)} ${WKD[d.getDay()]}`;
 } else if(view==='family'){document.getElementById('dlab').textContent='家庭 · 自身';document.getElementById('dsub').textContent='睡眠趋势 · 陪伴每个孩子';
 } else {const isT=dateStr(d)===dateStr(today());document.getElementById('dlab').textContent=isT?'目标 · 今天':`目标 · ${d.getMonth()+1}月${d.getDate()}日`;document.getElementById('dsub').textContent=`${dateStr(d)} ${WKD[d.getDay()]} · 每日看当天/每周看所在周 · 点卡片改`;}
 document.getElementById('nextB').style.visibility=off>=0?'hidden':'visible';
 document.getElementById('body').innerHTML = view==='clock'?vClock():view==='stats'?vStats():view==='timer'?vTimer():view==='insights'?vInsights():view==='family'?vFamily():vGoals();
 if(view==='stats'){document.querySelectorAll('.seg2 button').forEach(b=>b.onclick=()=>{statScope=b.dataset.s;render();});
  wireStatsAdd();
  document.querySelectorAll('.srow[data-cat]').forEach(el=>el.onclick=()=>openTrend('cat',el.dataset.cat));}
 if(view==='insights'){document.querySelectorAll('.segI button').forEach(b=>b.onclick=()=>{insScope=b.dataset.i;off=0;render();});
  document.querySelectorAll('.brow[data-bucket]').forEach(el=>el.onclick=()=>openTrend('bucket',el.dataset.bucket));
  const aic=document.querySelector('[data-ait]');if(aic)aic.onclick=()=>openTrend('ai','AI');
  const cl=document.querySelector('[data-clash]');if(cl)cl.onclick=openClashList;}
 if(view==='clock')wireEdit();
 if(view==='family'){
   document.querySelectorAll('.kcell[data-kid]').forEach(el=>el.onclick=()=>openTrend('kid',el.dataset.kid));
   document.querySelectorAll('.kcell[data-trend]').forEach(el=>el.onclick=()=>{const t=el.dataset.trend;openTrend(t==='sleep'?'sleep':'cat',t);});
 }
 if(view==='goals')document.querySelectorAll('.gcard').forEach(el=>el.onclick=()=>openCatDetail(el.dataset.g));
 if(view==='timer'){
  const startBtn=document.getElementById('timerStart');if(startBtn)startBtn.onclick=()=>startTimerFlow();
  const stopBtn=document.getElementById('timerStop');if(stopBtn)stopBtn.onclick=()=>stopTimerSheet();
  const newBtn=document.getElementById('timerNew');if(newBtn)newBtn.onclick=()=>{tSet(null);render();};
 }
}
// 点一条时间线 → 改类别 / 删除（不参加）
function wireEdit(){
 document.querySelectorAll('.tli').forEach(el=>{el.onclick=()=>openPicker(+el.dataset.i);});
 document.querySelectorAll('.gap').forEach(el=>{el.onclick=()=>openAdd(parseFloat(el.dataset.s),parseFloat(el.dataset.e));});
 // 时钟圆环直接点：彩色扇区=编辑该条；空白弧段=补录该空档
 const svg=document.getElementById('clocksvg');
 if(svg)svg.onclick=ev=>{
  const r=svg.getBoundingClientRect();
  const x=(ev.clientX-r.left)/r.width*332-16, y=(ev.clientY-r.top)/r.height*332-16;
  const dx=x-150, dy=y-150, rad=Math.sqrt(dx*dx+dy*dy);
  if(rad<86||rad>140)return;                                   // 只认圆环带,中心/外圈不响应
  const h=((Math.atan2(dx,-dy)/(2*Math.PI)*24)+24)%24;         // 12点方向=0时,顺时针
  const evs=window._evs||[];
  let hit=-1;
  evs.forEach((e,i)=>{const inSeg=(h>=e.start&&h<Math.min(e.end,24))||(e.end>24&&h<e.end-24);if(inSeg)hit=i;});
  // 今天且点在"现在"附近(±0.35h,跨0点取环绕距离)：计时中→计时面板优先；未计时→彩色扇区优先，只有空白弧段才开新计时（正在开的会不再被热区遮蔽）
  const _isT=dateStr(curDay())===dateStr(today());
  if(_isT){const _n=new Date(),_nh=_n.getHours()+_n.getMinutes()/60;
   const _dd=Math.abs(h-_nh),_wd=Math.min(_dd,24-_dd);
   if(_wd<=0.35&&(tGet()||hit<0)){tGet()?stopTimerSheet():startTimerFlow();return;}}
  if(hit>=0){openPicker(hit);return;}
  // 空白:找包住 h 的空档
  let gs=0,ge=24;
  evs.forEach(e=>{const en=Math.min(e.end,24);if(en<=h&&en>gs)gs=en;if(e.start>=h&&e.start<ge)ge=e.start;});
  gs=Math.round(gs*4)/4; ge=Math.round(ge*4)/4;
  if(ge-gs>=0.25)openAdd(gs,ge);
 };
 const fab=document.getElementById('fab');if(fab)fab.onclick=()=>{const n=new Date(),nh=n.getHours()+n.getMinutes()/60;
  const e=Math.min(24,Math.round(nh*2)/2),s=Math.max(0,e-1);openAdd(s,e);};
 const fT=document.getElementById('fabT');if(fT)fT.onclick=()=>{tGet()?stopTimerSheet():startTimerFlow();};
 renderTimerBar();}
// 统计页：点"未记录"行 or FAB → 补录（智能选默认时段）
function suggestGap(){ // 返回当前锚点日一个"最近的空白"[s,e]，无则给近1h
 const ds=dateStr(curDay()),evs=genDay(ds).filter(e=>e.cat!=='sleep').sort((a,b)=>a.start-b.start);
 const isT=ds===dateStr(today()),nowH=new Date().getHours()+new Date().getMinutes()/60,lim=isT?nowH:24;
 let prev=6; // 从早6点起找第一段>=0.5h空白
 for(const e of evs){if(e.start-prev>=0.5&&prev>=6)return[Math.round(prev*4)/4,Math.round(e.start*4)/4];prev=Math.max(prev,e.end);}
 if(lim-prev>=0.5&&prev>=6)return[Math.round(prev*4)/4,Math.round(Math.min(lim,prev+1)*4)/4];
 const e=Math.min(24,Math.round((isT?nowH:12)*2)/2);return[Math.max(0,e-1),e]; // 兜底近1h
}
// 空白清单：当前统计周期内每一天的每段空白，点哪段补哪段
function scopeDaysList(){
 const d=curDay();let ds=[];
 if(statScope==='day')ds=[d];
 else if(statScope==='week'){const ws=weekStart(d);for(let i=0;i<7;i++)ds.push(addDays(ws,i));}
 else if(statScope==='month'){const dim=new Date(d.getFullYear(),d.getMonth()+1,0).getDate();for(let i=1;i<=dim;i++)ds.push(new Date(d.getFullYear(),d.getMonth(),i));}
 else if(statScope==='quarter'){const q0=new Date(d.getFullYear(),Math.floor(d.getMonth()/3)*3,1),q1=new Date(q0.getFullYear(),q0.getMonth()+3,0);for(let x=new Date(q0);x<=q1;x.setDate(x.getDate()+1))ds.push(new Date(x));}
 else{for(let x=new Date(d.getFullYear(),0,1);x<=new Date(d.getFullYear(),11,31);x.setDate(x.getDate()+1))ds.push(new Date(x));}
 return ds.filter(x=>x<=today());
}
function dayGaps(ds){ // 该日 6:00–此刻边界 内未被任何记录覆盖的空档
 const b=nowBound(ds);if(b<=6)return[];
 const iv=genDay(ds).map(e=>[Math.max(0,e.start),Math.min(e.end,b)]).filter(x=>x[1]>x[0]).sort((a,c)=>a[0]-c[0]);
 const gaps=[];let cur=6;
 iv.forEach(([a,c])=>{if(a>cur&&a-cur>=0.5)gaps.push([cur,Math.min(a,b)]);cur=Math.max(cur,c);});
 if(b-cur>=0.5)gaps.push([cur,b]);
 return gaps.filter(([a,c])=>c-a>=0.5);
}
function openGapList(){
 const rows=[];
 scopeDaysList().forEach(d=>{const ds=dateStr(d);
  dayGaps(ds).forEach(([a,c])=>rows.push({ds,d,a,c}));});
 const m=document.createElement('div');m.className='mask';m.style.zIndex=60;
 m.innerHTML=`<div class="sheet"><div class="sh-t">未记录的空白 · ${scopeName()} · 共 ${fmtShort(rows.reduce((s,r)=>s+(r.c-r.a)*60,0))}<br><span style="font-weight:500;color:var(--mut);font-size:11.5px">点一段直接补录（只列 ≥30 分钟、06:00 后的空白）</span></div>
  <div class="bdlist">${rows.length?rows.map((r,i)=>`<div class="bdrow" data-gi="${i}"><span class="bdd">${+r.ds.slice(5,7)}/${+r.ds.slice(8)}</span><span class="bdt">${WKD[r.d.getDay()]}</span><span class="bdn">${h2t(r.a)} – ${h2t(r.c)}</span><span class="bdu">${fmtShort((r.c-r.a)*60)}</span></div>`).join(''):'<div class="bdempty">这段没有 ≥30 分钟的空白 👍</div>'}</div>
  <button class="cancel">关闭</button></div>`;
 m.onclick=ev=>{
  if(ev.target===m||ev.target.classList.contains('cancel')){m.remove();return;}
  const r0=ev.target.closest('.bdrow');
  if(r0){const r=rows[+r0.dataset.gi];m.remove();
   off=Math.round((r.d-TBASE)/86400000);          // 锚到那一天,补录才落对日期
   openAdd(Math.round(r.a*4)/4,Math.round(r.c*4)/4);}};
 document.body.appendChild(m);}
function wireStatsAdd(){
 document.querySelectorAll('.srow-u').forEach(el=>el.onclick=openGapList);
 const fb=document.getElementById('fabS');if(fb)fb.onclick=()=>{const[s,e]=suggestGap();openAdd(s,e);};
}
// 选了带子类的类目后再弹：具体做什么（单选，可跳过）——要加新类目子类,改这张表即可
const SUBMAP={self:['煲剧','冥想','运动','逛街'],growth:['湖畔','AI','阅读'],travel:['by air','by train','by car'],external:['湖畔','YPO','投资人','合作伙伴','其他'],people:['面试','1o1','团建']};
function openSubs(k,done){
 const list=SUBMAP[k]||[];
 const m=document.createElement('div');m.className='mask';
 m.innerHTML=`<div class="sheet"><div class="sh-t">具体做什么？（点一个即选）</div>
  <div class="kidgrid">${list.map(x=>`<button class="kb" data-k="${x}">${x}</button>`).join('')}</div>
  <button class="cancel">跳过（不细分）</button></div>`;
 m.onclick=ev=>{
  if(ev.target===m||ev.target.classList.contains('cancel')){m.remove();done('');return;}
  const b=ev.target.closest('.kb');if(b){m.remove();done(b.dataset.k);}};
 document.body.appendChild(m);}
// 选了「家庭」后再弹：这段陪的是哪个/哪几个孩子（可多选，可跳过）
function openKids(done){
 const KIDS=[['Olivia','#9678B6'],['George','#6E8FA8'],['Max','#7FA64B'],['Donald','#B8B2A6'],['父母','#8C6E45']];
 const m=document.createElement('div');m.className='mask';const sel=new Set();
 m.innerHTML=`<div class="sheet"><div class="sh-t">陪的是谁？（可多选 · 全家就都选上）</div>
  <div class="kidgrid">${KIDS.map(([k,c])=>`<button class="kb" data-k="${k}"><span class="d" style="background:${c}"></span>${k}</button>`).join('')}</div>
  <button class="kok">确定</button><button class="cancel">跳过（不区分）</button></div>`;
 m.onclick=ev=>{
  if(ev.target===m||ev.target.classList.contains('cancel')){m.remove();done([]);return;}
  if(ev.target.classList.contains('kok')){m.remove();done([...sel]);return;}
  const b=ev.target.closest('.kb');if(b){const k=b.dataset.k;sel.has(k)?sel.delete(k):sel.add(k);b.classList.toggle('on',sel.has(k));}};
 document.body.appendChild(m);}
// 改标题/时间：日历事件走 EDITS 覆盖；手动补录直接改 MANUAL
function openEdit(i){const e=window._evs[i];if(!e)return;openEditEv(e,dateStr(curDay()));}
function openEditEv(e,ds,after){
 let s=e.start,en=e.end;
 const m=document.createElement('div');m.className='mask';
 const isSlp=e.cat==='sleep';
 m.innerHTML=`<div class="sheet"><div class="sh-t">${isSlp?'修正睡眠时段（手环偶尔判错起床点）':'改标题 / 调时间'+(e.man?'（手动补录）':'（不影响飞书日历原件）')}</div>
  <input class="anote" id="etitle" value="${esc(e.title||'')}" maxlength="40" ${isSlp?'style="display:none"':''}>
  <div class="addtime">
   <div class="att"><span>开始</span><div class="stp"><button data-a="s-">−</button><input type="time" class="tin" id="es" value="${h2t(s)}"><button data-a="s+">＋</button></div></div>
   <div class="att"><span>结束</span><div class="stp"><button data-a="e-">−</button><input type="time" class="tin" id="ee" value="${h2t(en)}"><button data-a="e+">＋</button></div></div>
  </div>
  <button class="kok">保存</button><button class="cancel">取消</button></div>`;
 const upd=()=>{m.querySelector('#es').value=h2t(s);m.querySelector('#ee').value=h2t(en);};
 m.querySelector('#es').onchange=()=>{const mm=/^(\d{1,2}):(\d{2})$/.exec(m.querySelector('#es').value);if(mm){const nv=Math.min(en-0.25,+mm[1]+ +mm[2]/60);if(Number.isFinite(nv))s=nv;}upd();};   // 清空/半截输入(value='')不再算出 NaN，直接回显原值
 m.querySelector('#ee').onchange=()=>{const mm=/^(\d{1,2}):(\d{2})$/.exec(m.querySelector('#ee').value);if(mm){const nv=Math.max(s+0.25,+mm[1]+ +mm[2]/60);if(Number.isFinite(nv))en=nv;}upd();};
 m.onclick=ev=>{
  if(ev.target===m||ev.target.classList.contains('cancel')){m.remove();return;}
  const st=ev.target.closest('[data-a]');
  if(st){const a=st.dataset.a;
   if(a==='s-')s=Math.max(0,Math.round((s-0.25)*100)/100);
   if(a==='s+')s=Math.min(en-0.25,Math.round((s+0.25)*100)/100);
   if(a==='e-')en=Math.max(s+0.25,Math.round((en-0.25)*100)/100);
   if(a==='e+')en=Math.min(24,Math.round((en+0.25)*100)/100);
   upd();return;}
  if(ev.target.classList.contains('kok')){
   if(!Number.isFinite(+s)||!Number.isFinite(+en)||+en<=+s){toast('时间无效，未保存');return;}   // 兜底：NaN/倒置不写 MANUAL/EDITS
   const nt=(m.querySelector('#etitle').value||'').trim();
   if(e.man){const it=MANUAL[ds][e.mi];if(it){const os0=it.start,oc0=it.cat;it.title=nt||it.title;it.note=nt||it.note;it.start=s;it.end=en;localStorage.setItem('ztManual',JSON.stringify(MANUAL));
    cloud('editManual',{ds,start:os0,cat:oc0,ncat:it.cat,nsub:it.sub||'',nstart:s,nend:en,nnote:it.note||'',nkids:(it.tags||[]).join(',')});}}   // 单请求原子改：告别 delManual→manual 两发无序竞态（丢编辑/复活重复）
   else saveEdit(ds,e.ot,e.os,{title:nt!==e.ot?nt:'',start:s,end:en});   // 敲回原名=撤销标题覆盖：置''让 genDay 的 ed.title||e.title 回落原标题（云端往返同为''，闭环一致）
   m.remove();render();if(typeof after==='function')after();}};   // after：撞车台等场景保存后回到清单
 document.body.appendChild(m);}
function catSheet(title,sub,onpick,extra){
 const cats=CATS.filter(c=>c.key!=='sleep');
 const btns=cats.map(c=>`<button class="cb" data-k="${c.key}"><span class="d" style="background:${c.color}"></span>${c.icon} ${c.label}</button>`).join('');
 const mask=document.createElement('div');mask.className='mask';
 mask.innerHTML=`<div class="sheet"><div class="sh-t">${sub}</div><div class="sh-n">${title}</div><div class="grid">${btns}</div>${extra||''}<button class="cancel">取消</button></div>`;
 mask.onclick=ev=>{
  if(ev.target===mask||ev.target.classList.contains('cancel')){mask.remove();return;}
  if(ev.target.classList.contains('del')){onpick('__del__');mask.remove();render();return;}
  const b=ev.target.closest('.cb');if(b){onpick(b.dataset.k);mask.remove();render();}};
 document.body.appendChild(mask);}
function openPicker(i){const e=window._evs[i];if(!e)return;if(e.cat==='sleep'){openEdit(i);return;}const ds=dateStr(curDay());
 catSheet(esc(e.title), e.man?'手动记录 · 改类别或删除':'改归类（点一下记住，下次自动）', k=>{
  if(k==='__del__'){ if(e.man) delManual(ds,e.mi); else saveDel(delKey(ds,e.ot,e.os)); return; }   // 日历事件必须用原始键(ot/os)：genDay 查 DELETED 只认原键，用编辑后键会永久失效
  const c=CM[k];const fin=(kids,sub)=>{const s2=sub||(c.sub&&c.sub[0])||''; if(e.man){const it=MANUAL[ds][e.mi];if(it){const os0=it.start,oc0=it.cat;it.cat=k;it.sub=s2;it.tags=kids||[];localStorage.setItem('ztManual',JSON.stringify(MANUAL));
    cloud('editManual',{ds,start:os0,cat:oc0,ncat:k,nsub:s2,nstart:it.start,nend:it.end,nnote:it.note||'',nkids:(kids||[]).join(',')});}}   // 原子上云：按旧键定位、单请求就地更新，其他设备可见且不会被 cloudPull 复活成重复条目
   else saveCorr(e.ot,k,s2,kids); render(); };   // CORR 以原始标题为键（genDay/worker/refresh 三端读取方都按原始标题匹配）
  if(k==='family')openKids(kids=>fin(kids,'')); else if(SUBMAP[k])openSubs(k,sub=>fin([],sub)); else fin([],'');
 }, `<button class="edit2 aimk">⚡ ${(e.tags||[]).includes('AI')?'取消 AI 标记':'标记用了 AI'}</button><button class="edit2">✏️ 改标题 / 调时间</button><button class="del">🗑 ${e.man?'删除这条补录':'不参加 · 从记录中删除'}</button>`);
 setTimeout(()=>{
  const bs=document.querySelectorAll('.mask .edit2');
  bs.forEach(b=>{
   if(b.classList.contains('aimk'))b.onclick=ev=>{ev.stopPropagation();document.querySelector('.mask').remove();
    const has=(e.tags||[]).includes('AI');const nt=has?(e.tags||[]).filter(x=>x!=='AI'):[...(e.tags||[]),'AI'];
    if(e.man){const it=MANUAL[dateStr(curDay())][e.mi];if(it){it.tags=nt;localStorage.setItem('ztManual',JSON.stringify(MANUAL));
     cloud('editManual',{ds:dateStr(curDay()),start:it.start,cat:it.cat,ncat:it.cat,nsub:it.sub||'',nstart:it.start,nend:it.end,nnote:it.note||'',nkids:nt.join(',')});}}
    else saveCorr(e.ot,e.cat,e.sub,nt);
    render();};
   else b.onclick=ev=>{ev.stopPropagation();document.querySelector('.mask').remove();openEdit(i);};
  });},0);}
function openAdd(gs,ge){const ds=dateStr(curDay());let s=gs,e=ge;
 const cats=CATS.filter(c=>c.key!=='sleep');
 const btns=cats.map(c=>`<button class="cb" data-k="${c.key}"><span class="d" style="background:${c.color}"></span>${c.icon} ${c.label}</button>`).join('');
 const mask=document.createElement('div');mask.className='mask';
 mask.innerHTML=`<div class="sheet"><div class="sh-t">补录一段时间 · 调好时间点类别保存</div>
  <div class="addtime">
   <div class="att"><span>开始</span><div class="stp"><button data-a="s-">−</button><input type="time" class="tin" id="as" value="${h2t(s)}"><button data-a="s+">＋</button></div></div>
   <div class="att"><span>结束</span><div class="stp"><button data-a="e-">−</button><input type="time" class="tin" id="ae" value="${h2t(e)}"><button data-a="e+">＋</button></div></div>
  </div>
  <input class="anote" id="anote" placeholder="备注几个字：做了什么(可选，会显示在时间线上)" maxlength="30">
  <button class="aitog" id="aitog" type="button">⚡ 用了 AI</button>
  <div class="grid">${btns}</div><button class="cancel">取消</button></div>`;
 const upd=()=>{mask.querySelector('#as').value=h2t(s);mask.querySelector('#ae').value=h2t(e);};
 const tin=id=>mask.querySelector(id);
 tin('#as').onchange=()=>{const mm=/^(\d{1,2}):(\d{2})$/.exec(tin('#as').value);if(mm){const nv=Math.min(e-0.25,+mm[1]+ +mm[2]/60);if(Number.isFinite(nv))s=nv;}upd();};   // 同 openEditEv：空值/坏值回显，不产生 NaN
 tin('#ae').onchange=()=>{const mm=/^(\d{1,2}):(\d{2})$/.exec(tin('#ae').value);if(mm){const nv=Math.max(s+0.25,+mm[1]+ +mm[2]/60);if(Number.isFinite(nv))e=nv;}upd();};
 mask.onclick=ev=>{
  if(ev.target===mask||ev.target.classList.contains('cancel')){mask.remove();return;}
  const st=ev.target.closest('[data-a]');
  if(st){const a=st.dataset.a;
   if(a==='s-')s=Math.max(0,Math.round((s-0.25)*100)/100);
   if(a==='s+')s=Math.min(e-0.25,Math.round((s+0.25)*100)/100);
   if(a==='e-')e=Math.max(s+0.25,Math.round((e-0.25)*100)/100);
   if(a==='e+')e=Math.min(24,Math.round((e+0.25)*100)/100);
   upd();return;}
  if(ev.target.id==='aitog'){ev.target.classList.toggle('on');return;}
  const b=ev.target.closest('.cb');if(b){const k=b.dataset.k,c=CM[k];
   const note=(mask.querySelector('#anote').value||'').trim();
   const aiOn=mask.querySelector('#aitog').classList.contains('on');
   const fin=(kids,sub)=>{const s2=sub||(c.sub&&c.sub[0])||'';const tg=[...(kids||[])];if(aiOn&&!tg.includes('AI'))tg.push('AI');
    saveManual(ds,{cat:k,sub:s2,title:note||sub||c.label,note,tags:tg,start:s,end:e});render();};
   mask.remove(); if(k==='family')openKids(kids=>fin(kids,'')); else if(SUBMAP[k])openSubs(k,sub=>fin([],sub)); else fin([],'');}};
 document.body.appendChild(mask);}
document.querySelectorAll('.tabs button').forEach(b=>b.onclick=()=>{view=b.dataset.v;off=0;
  document.querySelectorAll('.tabs button').forEach(x=>x.classList.toggle('on',x===b));render();});
function insStep(){return view==='insights'?INS_WIN[insScope]:1;}
document.getElementById('prevB').onclick=()=>{off-=insStep();render();};
document.getElementById('nextB').onclick=()=>{const st=insStep();if(off<0){off=Math.min(0,off+st);render();}};
document.getElementById('todayB').onclick=()=>{off=0;render();};
(function(){const dp=document.getElementById('dpick');if(!dp)return;
 dp.onclick=()=>{if(view==='family'||view==='goals')return;openDatePicker();};})();
function openDatePicker(){
 const cur=curDay();let vy=cur.getFullYear(),vm=cur.getMonth();
 const m=document.createElement('div');m.className='mask';m.style.zIndex=70;m.style.alignItems='center';
 const draw=()=>{
  const first=new Date(vy,vm,1),pad=(first.getDay()+6)%7+1,dim=new Date(vy,vm+1,0).getDate();
  const td=dateStr(today());let cells='';
  for(let i=1;i<pad;i++)cells+='<span></span>';
  for(let d=1;d<=dim;d++){const ds=`${vy}-${String(vm+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
   const fut=ds>td,sel=ds===dateStr(cur);
   cells+=`<button class="dpc${sel?' on':''}${fut?' fut':''}" ${fut?'disabled':`data-d="${ds}"`}>${d}</button>`;}
  m.querySelector('.dpgrid').innerHTML=cells;
  m.querySelector('.dphd b').textContent=`${vy} 年 ${vm+1} 月`;};
 m.innerHTML=`<div class="sheet dpsheet"><div class="dphd"><button class="dpnav" data-n="-12">‹‹</button><button class="dpnav" data-n="-1">‹</button><b></b><button class="dpnav" data-n="1">›</button><button class="dpnav" data-n="12">››</button></div>
  <div class="dpwk"><span>一</span><span>二</span><span>三</span><span>四</span><span>五</span><span>六</span><span>日</span></div><div class="dpgrid"></div>
  <button class="dpc-today">回到今天</button></div>`;
 m.onclick=ev=>{
  if(ev.target===m){m.remove();return;}
  const nav=ev.target.closest('.dpnav');
  if(nav){vm+=+nav.dataset.n;while(vm<0){vm+=12;vy--;}while(vm>11){vm-=12;vy++;}draw();return;}
  if(ev.target.classList.contains('dpc-today')){off=0;m.remove();render();return;}
  const c=ev.target.closest('.dpc[data-d]');
  if(c){const t=new Date(c.dataset.d+'T00:00:00');off=Math.round((t-TBASE)/86400000);if(off>0)off=0;m.remove();render();}};
 document.body.appendChild(m);draw();}
document.getElementById('reloadB').onclick=function(){
 this.classList.add('spinning');
 if(navigator.vibrate)navigator.vibrate(60);
 setTimeout(()=>location.reload(),480);
};
document.getElementById('aboutB').onclick=openAbout;
render();
(function(){const h=document.querySelector('.hdr');const f=()=>document.documentElement.style.setProperty('--hdrH',(h?h.offsetHeight:66)+'px');f();window.addEventListener('resize',f);})();
cloudPull();                        // 启动即拉云端（Zoe+助理的共享编辑），合并后自动重渲染
setInterval(cloudPull, 5*60*1000);  // 常开时每 5 分钟拉一次，两人编辑准实时互见
setInterval(()=>{if(view==='timer'&&tGet()){document.getElementById('body').innerHTML=vTimer();
 const stopBtn=document.getElementById('timerStop');if(stopBtn)stopBtn.onclick=()=>stopTimerSheet();
 const newBtn=document.getElementById('timerNew');if(newBtn)newBtn.onclick=()=>{tSet(null);render();};}},1000);
</script></body></html>'''

def render(real_js, oura_js, ver='dev'):
    """供 refresh.py 调用：注入最新数据，返回完整 App HTML。"""
    return (HTML.replace("__FAV__",FAV).replace("__CATS__",CATS)
            .replace("__REAL_EVENTS__",real_js).replace("__OURA_DATA__",oura_js)
            .replace("__VERSION__",ver))

if __name__=="__main__":
    out=render(REAL,OURA,'dev')
    os.makedirs(f"{BASE}/demos",exist_ok=True)
    open(f"{BASE}/demos/itime.html","w",encoding="utf-8").write(out)
    print("wrote demos/itime.html", len(out))

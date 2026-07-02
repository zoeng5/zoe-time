// Zoe 时间 · 云端持久化代理（Cloudflare Worker）
// App ⇄ 这个 Worker（藏飞书密钥）⇄ 飞书多维表格
const APP = 'SWhDb2O44a7rnrskSBRcl177nvg';
const T = { manual:'tblylYDLAard5ZlZ', corr:'tbl2yVHGoZ8jtECk', del:'tblueeOFzLoukVvO', goal:'tblrYVZLzJ06BJyZ' };
const BASE = 'https://open.feishu.cn/open-apis';
const CORS = { 'Access-Control-Allow-Origin':'*', 'Access-Control-Allow-Methods':'GET,POST,OPTIONS', 'Access-Control-Allow-Headers':'Content-Type' };
const txt = v => Array.isArray(v) ? v.map(s => s.text ?? s).join('') : (v ?? '');

async function token(env){
  const r = await fetch(`${BASE}/auth/v3/tenant_access_token/internal`, {
    method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ app_id: env.LARK_APP_ID, app_secret: env.LARK_APP_SECRET }) });
  return (await r.json()).tenant_access_token;
}
async function listAll(tk, table){
  let items=[], pt;
  do{
    const u = new URL(`${BASE}/bitable/v1/apps/${APP}/tables/${table}/records`);
    u.searchParams.set('page_size','500'); if(pt) u.searchParams.set('page_token', pt);
    const j = await (await fetch(u, { headers:{ Authorization:'Bearer '+tk } })).json();
    items = items.concat(j.data?.items || []); pt = j.data?.has_more ? j.data.page_token : null;
  } while(pt);
  return items;
}
const create = (tk,table,fields) => fetch(`${BASE}/bitable/v1/apps/${APP}/tables/${table}/records`,
  { method:'POST', headers:{ Authorization:'Bearer '+tk, 'Content-Type':'application/json' }, body: JSON.stringify({ fields }) });
const update = (tk,table,rid,fields) => fetch(`${BASE}/bitable/v1/apps/${APP}/tables/${table}/records/${rid}`,
  { method:'PUT', headers:{ Authorization:'Bearer '+tk, 'Content-Type':'application/json' }, body: JSON.stringify({ fields }) });
const del = (tk,table,rid) => fetch(`${BASE}/bitable/v1/apps/${APP}/tables/${table}/records/${rid}`,
  { method:'DELETE', headers:{ Authorization:'Bearer '+tk } });
const J = o => new Response(JSON.stringify(o), { headers:{ ...CORS, 'Content-Type':'application/json' } });

export default {
  async fetch(req, env){
    if(req.method==='OPTIONS') return new Response(null,{ headers:CORS });
    const url = new URL(req.url);
    let tk;
    try { tk = await token(env); } catch(e){ return J({ error:'auth' }); }

    if(url.pathname==='/test'){
      const r=await create(tk,T.goal,{'类别':'family','周期':'每天','目标值':3});
      return J({status:r.status, body:await r.json()});
    }
    if(url.pathname==='/sync'){
      const [mn,co,de,go] = await Promise.all([listAll(tk,T.manual),listAll(tk,T.corr),listAll(tk,T.del),listAll(tk,T.goal)]);
      const manual={}; mn.forEach(r=>{const f=r.fields,d=txt(f['日期']);(manual[d]=manual[d]||[]).push({cat:txt(f['类别']),sub:txt(f['子类']),title:txt(f['类别']),start:+f['开始'],end:+f['结束'],_rid:r.record_id});});
      const corrections={}; co.forEach(r=>{const f=r.fields;corrections[txt(f['标题'])]={cat:txt(f['类别']),sub:txt(f['子类'])};});
      const deleted = de.map(r=>txt(r.fields['标识']));
      const goals={}; go.forEach(r=>{const f=r.fields;goals[txt(f['类别'])]={period:txt(f['周期']),target:+f['目标值']};});
      return J({ manual, corrections, deleted, goals });
    }
    if(url.pathname==='/save' && req.method==='POST'){
      const b = await req.json(); const dev = b.device||'';
      if(b.kind==='manual') await create(tk,T.manual,{'日期':b.ds,'类别':b.cat,'子类':b.sub||'','开始':b.start,'结束':b.end,'设备':dev});
      else if(b.kind==='delete') await create(tk,T.del,{'标识':b.key,'日期':b.ds||'','标题':b.title||''});
      else if(b.kind==='correction'){ const hit=(await listAll(tk,T.corr)).find(r=>txt(r.fields['标题'])===b.title); const f={'标题':b.title,'类别':b.cat,'子类':b.sub||'','设备':dev}; hit?await update(tk,T.corr,hit.record_id,f):await create(tk,T.corr,f); }
      else if(b.kind==='goal'){ const hit=(await listAll(tk,T.goal)).find(r=>txt(r.fields['类别'])===b.key); const f={'类别':b.key,'周期':b.period,'目标值':b.target}; hit?await update(tk,T.goal,hit.record_id,f):await create(tk,T.goal,f); }
      else if(b.kind==='undelete'){ const hit=(await listAll(tk,T.del)).find(r=>txt(r.fields['标识'])===b.key); if(hit)await del(tk,T.del,hit.record_id); }
      else if(b.kind==='delManual'){ const hit=(await listAll(tk,T.manual)).find(r=>txt(r.fields['日期'])===b.ds && +r.fields['开始']===+b.start && txt(r.fields['类别'])===b.cat); if(hit)await del(tk,T.manual,hit.record_id); }
      return J({ ok:true });
    }
    return new Response('Zoe time sync worker');
  }
};

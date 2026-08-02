// Cloudflare Pages Function —— GET /api/search?q=<中文名/英文名/代码>
// 名称→代码解析(东方财富 suggest,UTF-8,覆盖 A股/美股)。返回候选 {sym, name, market}。

export async function onRequestGet(context) {
  const { request } = context;
  const q = (new URL(request.url).searchParams.get("q") || "").trim();
  if (!q) return cors(json({ results: [] }));
  const cache = caches.default;
  const ck = new Request(new URL(request.url).origin + "/api/search?q=" + encodeURIComponent(q), { method: "GET" });
  const hit = await cache.match(ck);
  if (hit) return cors(hit);

  let results = [];
  try {
    const url = `https://searchadapter.eastmoney.com/api/suggest/get?input=${encodeURIComponent(q)}&type=14&token=D43BF722C8E33BDC906FB84D85E326E8&count=12`;
    const j = await (await fetch(url)).json();
    const data = (j.QuotationCodeTable && j.QuotationCodeTable.Data) || [];
    for (const x of data) {
      const code = x.Code, mkt = String(x.MktNum), name = x.Name;
      let sym = null, market = null;
      if (mkt === "1") { sym = code + ".SS"; market = "CN"; }
      else if (mkt === "0") { sym = code + ((code[0] === "8" || code[0] === "4") ? ".BJ" : ".SZ"); market = "CN"; }
      else if (mkt === "105" || mkt === "106" || mkt === "107") { sym = String(code).toUpperCase(); market = "US"; }
      if (sym) results.push({ sym, name, market });
    }
  } catch (e) {
    return cors(json({ results: [], error: String(e) }));
  }
  const resp = json({ results }, 200, 300);
  context.waitUntil(cache.put(ck, resp.clone()));
  return cors(resp);
}
export async function onRequestOptions() { return cors(new Response(null, { status: 204 })); }

function json(obj, status = 200, ttl = 0) {
  const h = { "Content-Type": "application/json; charset=utf-8" };
  if (ttl) h["Cache-Control"] = `public, max-age=${ttl}`;
  return new Response(JSON.stringify(obj), { status, headers: h });
}
function cors(resp) {
  const r = new Response(resp.body, resp);
  r.headers.set("Access-Control-Allow-Origin", "*");
  r.headers.set("Access-Control-Allow-Methods", "GET, OPTIONS");
  return r;
}

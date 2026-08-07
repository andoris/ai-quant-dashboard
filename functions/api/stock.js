// Cloudflare Pages Function —— GET /api/stock?sym=TSLA  或  ?sym=600519.SS
// 现场拉取"库里没有"的任意个股:历史 OHLC(约130日)+ 最新价,供前端用同一套详情页模板渲染。
// 环境变量:TIINGO_TOKEN(美股)。A股走腾讯免费接口。约 30 秒边缘缓存。

export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  let sym = normSym((url.searchParams.get("sym") || "").trim());
  if (!sym) return cors(json({ error: "missing sym" }, 400));

  const cache = caches.default;
  const ck = new Request(url.origin + "/api/stock?sym=" + encodeURIComponent(sym), { method: "GET" });
  const hit = await cache.match(ck);
  if (hit) return cors(hit);

  let payload;
  try {
    payload = /\.(SS|SZ|BJ)$/.test(sym) ? await cnStock(sym) : await usStock(sym, env);
  } catch (e) {
    return cors(json({ error: String(e), sym }, 200, 0));
  }
  const resp = json(payload, 200, 30);
  context.waitUntil(cache.put(ck, resp.clone()));
  return cors(resp);
}
export async function onRequestOptions() { return cors(new Response(null, { status: 204 })); }

function normSym(s) {
  if (!s) return "";
  if (/^\d{6}$/.test(s)) {
    const f = s[0];
    const sfx = (f === "5" || f === "6" || f === "9") ? ".SS" : (f >= "0" && f <= "3") ? ".SZ" : ".BJ";
    return s + sfx;
  }
  return s.toUpperCase();
}

// 美股:雅虎 chart 日线历史 + 现价(免费,无需 key)
async function usStock(sym) {
  const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodeURIComponent(sym)}?range=6mo&interval=1d`;
  const r = await fetch(url, { headers: { "User-Agent": "Mozilla/5.0", "Accept": "application/json" } });
  const j = await r.json();
  const res = j && j.chart && j.chart.result && j.chart.result[0];
  if (!res || !res.timestamp || !res.indicators || !res.indicators.quote) throw "无历史数据";
  const q = res.indicators.quote[0], ts = res.timestamp;
  const H = { d: [], o: [], h: [], l: [], c: [], v: [] };
  for (let i = 0; i < ts.length; i++) {
    if (q.close[i] == null) continue;
    const dt = new Date(ts[i] * 1000);
    H.d.push(String(dt.getMonth() + 1).padStart(2, "0") + "-" + String(dt.getDate()).padStart(2, "0"));
    H.o.push(r2(q.open[i])); H.h.push(r2(q.high[i])); H.l.push(r2(q.low[i]));
    H.c.push(r2(q.close[i])); H.v.push(Math.round(q.volume[i] || 0));
  }
  if (H.c.length < 2) throw "无历史数据";
  const n = H.c.length;
  const meta = res.meta || {};
  const last = r2(meta.regularMarketPrice != null ? meta.regularMarketPrice : H.c[n - 1]);
  const prev = r2(meta.chartPreviousClose != null ? meta.chartPreviousClose : (meta.previousClose != null ? meta.previousClose : H.c[n - 2]));
  return { sym, market: "US", name: meta.shortName || sym, price: last, prev, pct: pct(last, prev), history: H };
}

// A股:腾讯前复权日线(web.ifzq.gtimg.cn,Cloudflare 可达)。中文名以搜索结果为准。
async function cnStock(sym) {
  const m = sym.match(/^(\d{6})\.(SS|SZ|BJ)$/);
  const tc = (m[2] === "SS" ? "sh" : m[2] === "SZ" ? "sz" : "bj") + m[1];
  const j = await (await fetch(`https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param=${tc},day,,,130,qfq`)).json();
  const node = (j.data && j.data[tc]) || {};
  const arr = node.qfqday || node.day || [];
  if (!arr.length) throw "无历史数据";
  const H = { d: [], o: [], h: [], l: [], c: [], v: [] };
  for (const x of arr.slice(-130)) {
    H.d.push(String(x[0]).slice(5)); H.o.push(+x[1]); H.c.push(+x[2]);
    H.h.push(+x[3]); H.l.push(+x[4]); H.v.push(+x[5] || 0);
  }
  const last = H.c[H.c.length - 1], prev = H.c[H.c.length - 2];
  let name = sym;
  try { if (node.qt && node.qt[tc]) name = node.qt[tc][1]; } catch (e) {}
  return { sym, market: "CN", name, price: last, prev, pct: pct(last, prev), history: H };
}

function pct(a, b) { return b ? Math.round(((a - b) / b) * 10000) / 100 : null; }
function r2(x) { return x == null ? null : Math.round(x * 100) / 100; }
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

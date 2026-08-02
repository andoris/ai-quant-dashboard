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

// 美股:Tiingo 日线历史 + IEX 最新价
async function usStock(sym, env) {
  const token = env.TIINGO_TOKEN;
  if (!token) throw "TIINGO_TOKEN 未配置";
  const start = new Date(Date.now() - 200 * 864e5).toISOString().slice(0, 10);
  const r = await fetch(`https://api.tiingo.com/tiingo/daily/${sym}/prices?startDate=${start}&token=${token}`,
    { headers: { "Content-Type": "application/json" } });
  const arr = await r.json();
  if (!Array.isArray(arr) || !arr.length) throw "无历史数据";
  const rows = arr.slice(-130);
  const H = { d: [], o: [], h: [], l: [], c: [], v: [] };
  for (const x of rows) {
    H.d.push(String(x.date).slice(5, 10)); H.o.push(r2(x.open)); H.h.push(r2(x.high));
    H.l.push(r2(x.low)); H.c.push(r2(x.close)); H.v.push(Math.round(x.volume || 0));
  }
  let last = H.c[H.c.length - 1], prev = H.c[H.c.length - 2];
  try {
    const q = await (await fetch(`https://api.tiingo.com/iex/?tickers=${sym}&token=${token}`)).json();
    if (q && q[0] && q[0].last != null) { last = r2(q[0].last); prev = r2(q[0].prevClose != null ? q[0].prevClose : prev); }
  } catch (e) {}
  return { sym, market: "US", name: sym, price: last, prev, pct: pct(last, prev), history: H };
}

// A股:东方财富前复权日线(UTF-8,中文名不乱码)
async function cnStock(sym) {
  const m = sym.match(/^(\d{6})\.(SS|SZ|BJ)$/);
  const secid = (m[2] === "SS" ? "1" : "0") + "." + m[1];
  const url = `https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=${secid}&klt=101&fqt=1&lmt=130&fields1=f1&fields2=f51,f52,f53,f54,f55,f56`;
  const j = await (await fetch(url)).json();
  const dd = j.data;
  if (!dd || !dd.klines || !dd.klines.length) throw "无历史数据";
  const H = { d: [], o: [], h: [], l: [], c: [], v: [] };
  for (const k of dd.klines.slice(-130)) {
    const p = k.split(",");
    H.d.push(p[0].slice(5)); H.o.push(+p[1]); H.c.push(+p[2]);
    H.h.push(+p[3]); H.l.push(+p[4]); H.v.push(+p[5] || 0);
  }
  const last = H.c[H.c.length - 1], prev = H.c[H.c.length - 2];
  return { sym, market: "CN", name: dd.name || sym, price: last, prev, pct: pct(last, prev), history: H };
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

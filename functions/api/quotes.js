// Cloudflare Pages Function —— GET /api/quotes
// 按需实时报价:用户打开/轮询时才调用;边缘缓存 ~20 秒(多人同看也只打数据源几次)。
//
// 环境变量(Cloudflare Pages → Settings → Environment variables 里加):
//   TIINGO_TOKEN   —— 美股实时(Tiingo IEX),必填才有美股实时
//   (A股走腾讯免费行情接口,无需 key)
//   SYMBOLS_URL    —— 可选,标的清单来源,默认同源 /data.json
//
// 返回: { ts, count, quotes: { "<yf>": {price, prev, pct} , ... } }

const EDGE_TTL = 20; // 秒:边缘缓存时长 = "实时"刷新粒度

export async function onRequestGet(context) {
  const { request, env } = context;
  const cache = caches.default;
  const cacheKey = new Request(new URL("/api/quotes", request.url).toString(), { method: "GET" });

  const hit = await cache.match(cacheKey);
  if (hit) return cors(hit);

  let payload;
  try {
    payload = await buildQuotes(request, env);
  } catch (e) {
    return cors(jsonResp({ error: String(e), ts: Date.now(), quotes: {} }, 200, 0));
  }
  const resp = jsonResp(payload, 200, EDGE_TTL);
  context.waitUntil(cache.put(cacheKey, resp.clone()));
  return cors(resp);
}

// CORS 预检
export async function onRequestOptions() {
  return cors(new Response(null, { status: 204 }));
}

async function buildQuotes(request, env) {
  const { us, cn } = await getUniverse(request, env);
  const quotes = {};
  await Promise.all([fetchTiingo(us, env, quotes), fetchTencentCN(cn, quotes)]);
  return { ts: Date.now(), count: Object.keys(quotes).length, quotes };
}

// 从已部署的 data.json 读取标的清单(缓存 1 小时)
async function getUniverse(request, env) {
  const origin = new URL(request.url).origin;
  const url = env.SYMBOLS_URL || `${origin}/data.json`;
  const r = await fetch(url, { cf: { cacheTtl: 3600, cacheEverything: true } });
  const d = await r.json();
  const us = [], cn = [], seen = new Set();
  for (const x of (d.universe || [])) {
    if (x.kind !== "stock" && x.kind !== "etf") continue;
    if (seen.has(x.yf)) continue;
    seen.add(x.yf);
    if (x.market === "US") us.push(x.yf);
    else if (x.market === "CN") cn.push(x.yf);
  }
  return { us, cn };
}

// 美股 / 美股ETF —— Tiingo IEX 批量(一次多只)
async function fetchTiingo(syms, env, out) {
  const token = env.TIINGO_TOKEN;
  if (!token || !syms.length) return;
  const CH = 90;
  const jobs = [];
  for (let i = 0; i < syms.length; i += CH) {
    const batch = syms.slice(i, i + CH);
    const url = `https://api.tiingo.com/iex/?tickers=${batch.join(",")}&token=${token}`;
    jobs.push(
      fetch(url, { headers: { "Content-Type": "application/json" } })
        .then((r) => (r.ok ? r.json() : []))
        .then((arr) => {
          for (const q of arr || []) {
            const last = q.last ?? q.tngoLast ?? q.lastSalePrice;
            const prev = q.prevClose;
            if (last == null || prev == null || !q.ticker) continue;
            out[q.ticker.toUpperCase()] = { price: r2(last), prev: r2(prev), pct: pct(last, prev) };
          }
        })
        .catch(() => {})
    );
  }
  await Promise.all(jobs);
}

// A股 / A股ETF —— 腾讯行情批量(qt.gtimg.cn)。yf 形如 600519.SS / 000001.SZ / 8xxxxx.BJ
async function fetchTencentCN(syms, out) {
  if (!syms.length) return;
  const map = {}, codes = [];
  for (const yf of syms) {
    const m = yf.match(/^(\d{6})\.(SS|SZ|BJ)$/);
    if (!m) continue;
    const pfx = m[2] === "SS" ? "sh" : m[2] === "SZ" ? "sz" : "bj";
    const tc = pfx + m[1];
    map[tc] = yf;
    codes.push(tc);
  }
  const CH = 60;
  const jobs = [];
  for (let i = 0; i < codes.length; i += CH) {
    const batch = codes.slice(i, i + CH);
    const url = `https://qt.gtimg.cn/q=${batch.join(",")}`;
    jobs.push(
      fetch(url)
        .then((r) => r.text()) // 数字字段为 ASCII,GBK 中文乱码不影响解析
        .then((txt) => {
          for (const line of txt.split("\n")) {
            const mm = line.match(/v_(\w+)="([^"]*)"/);
            if (!mm) continue;
            const yf = map[mm[1]];
            if (!yf) continue;
            const f = mm[2].split("~");
            const last = parseFloat(f[3]), prev = parseFloat(f[4]);
            if (!isFinite(last) || !isFinite(prev) || prev === 0) continue;
            out[yf] = { price: r2(last), prev: r2(prev), pct: pct(last, prev) };
          }
        })
        .catch(() => {})
    );
  }
  await Promise.all(jobs);
}

function pct(a, b) { return b ? Math.round(((a - b) / b) * 10000) / 100 : null; }
function r2(x) { return Math.round(x * 100) / 100; }
function jsonResp(obj, status = 200, ttl = 0) {
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

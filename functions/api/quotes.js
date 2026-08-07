// Cloudflare Pages Function —— GET /api/quotes?symbols=NVDA,600519.SS,...
// 单文件架构:标的清单由前端(index.html)传入,后端不再依赖 data.json。
// 按需实时报价;边缘缓存 ~20 秒(多人同看/轮询也只打数据源几次)。
//   美股/美股ETF → 雅虎行情(免费);A股/A股ETF → 腾讯行情(免费)。
// 返回: { ts, count, quotes: { "<yf>": {price, prev, pct} , ... } }

const EDGE_TTL = 20;

export async function onRequestGet(context) {
  const { request } = context;
  const url = new URL(request.url);
  const raw = (url.searchParams.get("symbols") || "").trim();
  if (!raw) return cors(jsonResp({ ts: Date.now(), count: 0, quotes: {} }, 200, 0));

  const cache = caches.default;
  const cacheKey = new Request(url.origin + "/api/quotes?symbols=" + encodeURIComponent(raw), { method: "GET" });
  const hit = await cache.match(cacheKey);
  if (hit) return cors(hit);

  let payload;
  try {
    payload = await buildQuotes(raw);
  } catch (e) {
    return cors(jsonResp({ error: String(e), ts: Date.now(), quotes: {} }, 200, 0));
  }
  const resp = jsonResp(payload, 200, EDGE_TTL);
  context.waitUntil(cache.put(cacheKey, resp.clone()));
  return cors(resp);
}

export async function onRequestOptions() {
  return cors(new Response(null, { status: 204 }));
}

async function buildQuotes(raw) {
  const syms = raw.split(",").map((s) => s.trim()).filter(Boolean);
  const us = [], cn = [], seen = new Set();
  for (const s of syms) {
    if (seen.has(s)) continue;
    seen.add(s);
    if (/\.(SS|SZ|BJ)$/.test(s)) cn.push(s);
    else us.push(s);
  }
  const quotes = {};
  await Promise.all([fetchYahooUS(us, quotes), fetchTencentCN(cn, quotes)]);
  return { ts: Date.now(), count: Object.keys(quotes).length, quotes };
}

// 美股 / 美股ETF —— 雅虎行情批量(免费,无需 key;一次多只)
async function fetchYahooUS(syms, out) {
  if (!syms.length) return;
  const CH = 50;
  const jobs = [];
  for (let i = 0; i < syms.length; i += CH) {
    const batch = syms.slice(i, i + CH);
    const url = `https://query1.finance.yahoo.com/v7/finance/quote?symbols=${batch.join(",")}`;
    jobs.push(
      fetch(url, { headers: { "User-Agent": "Mozilla/5.0", "Accept": "application/json" } })
        .then((r) => (r.ok ? r.json() : null))
        .then((j) => {
          const arr = (j && j.quoteResponse && j.quoteResponse.result) || [];
          for (const q of arr) {
            const last = q.regularMarketPrice, prev = q.regularMarketPreviousClose;
            if (last == null || prev == null || !q.symbol) continue;
            out[String(q.symbol).toUpperCase()] = { price: r2(last), prev: r2(prev), pct: pct(last, prev) };
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
        .then((r) => r.text())
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

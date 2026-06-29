# -*- coding: utf-8 -*-
"""抓取行情 + 计算涨跌幅/排名 + 生成盘前前瞻/盘后总结简报,写入 docs/data.json。

用法:
  python fetch.py --market cn --mode preview     # A股盘前前瞻
  python fetch.py --market cn --mode summary      # A股盘后总结
  python fetch.py --market us --mode preview      # 美股盘前前瞻
  python fetch.py --market us --mode summary       # 美股盘后总结
  python fetch.py --market both --mode summary      # 两个盘都刷新

数据源: yfinance(雅虎财经,免费,覆盖美股/A股/ETF/指数)。为日级/延迟数据,非逐笔实时。
"""
import argparse
import json
import os
from datetime import datetime, timezone, timedelta

import yfinance as yf

from universe import INDICES, TRACKS, build_records

DOCS = os.path.join(os.path.dirname(__file__), "docs")
DATA_PATH = os.path.join(DOCS, "data.json")
CN_TZ = timezone(timedelta(hours=8))
US_TZ = timezone(timedelta(hours=-5))


def download_closes(symbols):
    """返回 {symbol: (last_close, prev_close)},取最近两个有效交易日收盘。"""
    out = {}
    if not symbols:
        return out
    try:
        df = yf.download(symbols, period="7d", interval="1d",
                         group_by="column", auto_adjust=False,
                         progress=False, threads=True)
    except Exception as e:
        print("download error:", e)
        return out
    if df is None or len(df) == 0:
        return out
    close = df["Close"] if "Close" in df else df
    # 单标的时 close 是 Series
    if hasattr(close, "columns"):
        cols = list(close.columns)
        for sym in cols:
            series = close[sym].dropna()
            if len(series) >= 2:
                out[sym] = (float(series.iloc[-1]), float(series.iloc[-2]))
            elif len(series) == 1:
                out[sym] = (float(series.iloc[-1]), float(series.iloc[-1]))
    else:
        series = close.dropna()
        if len(series) >= 2:
            out[symbols[0]] = (float(series.iloc[-1]), float(series.iloc[-2]))
        elif len(series) == 1:
            out[symbols[0]] = (float(series.iloc[-1]), float(series.iloc[-1]))
    return out


def pct(last, prev):
    if prev in (None, 0):
        return None
    return round((last - prev) / prev * 100, 2)


def load_existing():
    if os.path.exists(DATA_PATH):
        try:
            with open(DATA_PATH, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"tickers": {}, "indices": {}, "universe": [], "meta": {}, "briefs": {}}


def build_universe_struct():
    """静态结构(给前端渲染表格用)。"""
    recs = build_records()
    return recs


def make_brief(market, mode, quotes_by_yf, records, idx_quotes):
    """生成中文简报(数据驱动,简报粒度)。"""
    mkt_recs = [r for r in records if r["market"] == market and r["kind"] == "stock"]
    rows = []          # 领涨/领跌/宽度: 同一只票去重(按代码)
    seen_codes = set()
    for r in mkt_recs:
        if r["code"] in seen_codes:
            continue
        q = quotes_by_yf.get(r["yf"])
        if q and q.get("pct") is not None:
            seen_codes.add(r["code"])
            rows.append((r["name"], r["track"], q["pct"]))
    # 赛道平均仍按"出现在该赛道"统计(允许跨赛道计入)
    track_rows = [(r["name"], r["track"], quotes_by_yf[r["yf"]]["pct"])
                  for r in mkt_recs
                  if quotes_by_yf.get(r["yf"]) and quotes_by_yf[r["yf"]].get("pct") is not None]
    rows_sorted = sorted(rows, key=lambda x: x[2], reverse=True)
    up = sum(1 for _, _, p in rows if p > 0)
    down = sum(1 for _, _, p in rows if p < 0)
    flat = len(rows) - up - down

    # 赛道平均涨跌幅
    track_avg = {}
    for name, track, p in track_rows:
        track_avg.setdefault(track, []).append(p)
    track_rank = sorted(((t, round(sum(v) / len(v), 2)) for t, v in track_avg.items()),
                        key=lambda x: x[1], reverse=True)

    # 指数
    idx_list = INDICES.get(market, [])
    idx_lines = []
    for sym, nm in idx_list:
        q = idx_quotes.get(sym)
        if q and q.get("pct") is not None:
            idx_lines.append(f"{nm} {q['pct']:+.2f}%")

    mkt_cn = "A股" if market == "CN" else "美股"
    title_mode = "盘前前瞻" if mode == "preview" else "盘后总结"
    now = datetime.now(CN_TZ if market == "CN" else US_TZ)

    bullets = []
    if idx_lines:
        bullets.append("大盘:" + " · ".join(idx_lines))
    if rows:
        bullets.append(f"观察池涨跌:{up} 涨 / {down} 跌 / {flat} 平(共 {len(rows)} 只有数据)")
    if track_rank:
        best = track_rank[0]; worst = track_rank[-1]
        bullets.append(f"最强赛道:{best[0]} ({best[1]:+.2f}%);最弱:{worst[0]} ({worst[1]:+.2f}%)")
    if rows_sorted:
        tops = "、".join(f"{n}{p:+.1f}%" for n, _, p in rows_sorted[:5])
        bots = "、".join(f"{n}{p:+.1f}%" for n, _, p in rows_sorted[-5:][::-1])
        bullets.append("领涨:" + tops)
        bullets.append("领跌:" + bots)

    if mode == "preview":
        # 盘前: 用另一市场隔夜表现做提示
        other = "US" if market == "CN" else "CN"
        other_idx = INDICES.get(other, [])
        cues = []
        for sym, nm in other_idx:
            q = idx_quotes.get(sym)
            if q and q.get("pct") is not None:
                cues.append(f"{nm} {q['pct']:+.2f}%")
        if cues:
            bullets.insert(0, ("隔夜美股:" if market == "CN" else "今日A股:") + " · ".join(cues))
        headline = f"{mkt_cn}{title_mode} · 今日关注上一交易日强弱延续与隔夜外盘指引。"
    else:
        headline = f"{mkt_cn}{title_mode} · 收盘强弱与赛道轮动一览。"

    return {
        "market": market, "mode": mode,
        "title": f"{mkt_cn}{title_mode}",
        "stamp": now.strftime("%Y-%m-%d %H:%M ") + ("北京时间" if market == "CN" else "美东时间"),
        "headline": headline,
        "bullets": bullets,
        "track_rank": track_rank,
    }


def run(market, mode):
    data = load_existing()
    data["universe"] = build_universe_struct()
    records = data["universe"]

    markets = ["CN", "US"] if market == "both" else [market.upper()]

    # 抓取个股/ETF
    target_syms = sorted({r["yf"] for r in records if r["market"] in markets})
    # 盘前也抓另一市场指数做隔夜提示
    idx_markets = set(markets)
    if mode == "preview":
        idx_markets |= {"US", "CN"}
    idx_syms = sorted({s for m in idx_markets for s, _ in INDICES.get(m, [])})

    print(f"抓取 {len(target_syms)} 个标的 + {len(idx_syms)} 个指数 ...")
    closes = download_closes(target_syms)
    idx_closes = download_closes(idx_syms)

    now_iso = datetime.now(timezone.utc).isoformat()
    for r in records:
        if r["market"] not in markets:
            continue
        c = closes.get(r["yf"])
        if not c:
            continue
        last, prev = c
        data["tickers"][r["yf"]] = {
            "code": r["code"], "name": r["name"], "market": r["market"],
            "kind": r["kind"], "price": round(last, 2), "prev": round(prev, 2),
            "pct": pct(last, prev), "ts": now_iso,
        }

    idx_quotes = {}
    for m in idx_markets:
        for sym, nm in INDICES.get(m, []):
            c = idx_closes.get(sym)
            if not c:
                continue
            last, prev = c
            rec = {"name": nm, "market": m, "price": round(last, 2),
                   "prev": round(prev, 2), "pct": pct(last, prev), "ts": now_iso}
            data["indices"][sym] = rec
            idx_quotes[sym] = rec

    # 简报(只为请求的市场生成,both 则两个都生成)
    quotes_by_yf = data["tickers"]
    for m in markets:
        brief = make_brief(m, mode, quotes_by_yf, records, idx_quotes)
        data["briefs"][f"{m.lower()}_{mode}"] = brief
        data["meta"][f"updated_{m.lower()}"] = now_iso
        data["meta"][f"last_{m.lower()}_mode"] = mode

    data["meta"]["updated_at"] = now_iso

    os.makedirs(DOCS, exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    got = sum(1 for r in records if r["market"] in markets and r["yf"] in data["tickers"])
    print(f"完成。写入 {DATA_PATH}。本轮市场 {markets} 命中 {got} 只。")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--market", choices=["cn", "us", "both"], default="both")
    ap.add_argument("--mode", choices=["preview", "summary"], default="summary")
    args = ap.parse_args()
    run(args.market, args.mode)

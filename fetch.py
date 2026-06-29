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
import math
import os
from datetime import datetime, timezone, timedelta

import pandas as pd
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


def fetch_history(symbols, period="3mo", keep=60):
    """抓指数历史 OHLCV,返回 {sym: {d,o,h,l,c,v}}(供 K 线/走势图)。"""
    out = {}
    if not symbols:
        return out
    try:
        df = yf.download(symbols, period=period, interval="1d", group_by="ticker",
                         auto_adjust=False, progress=False, threads=True)
    except Exception as e:
        print("history error:", e)
        return out
    if df is None or len(df) == 0:
        return out

    def grab(sub, sym):
        sub = sub.dropna(subset=["Close"])
        if len(sub) == 0:
            return
        tail = sub.tail(keep)
        def col(name):
            return [None if (v is None or (isinstance(v, float) and math.isnan(v))) else round(float(v), 2)
                    for v in tail[name]]
        vol = []
        for v in tail["Volume"]:
            try:
                vol.append(0 if math.isnan(v) else int(v))
            except Exception:
                vol.append(0)
        out[sym] = {
            "d": [str(d)[5:10] for d in tail.index],
            "o": col("Open"), "h": col("High"), "l": col("Low"),
            "c": col("Close"), "v": vol,
        }

    if isinstance(df.columns, pd.MultiIndex):
        lvl0 = set(df.columns.get_level_values(0))
        for sym in symbols:
            if sym in lvl0:
                grab(df[sym], sym)
    else:
        grab(df, symbols[0])
    return out


def make_brief(market, mode, quotes_by_yf, records, idx_quotes):
    """生成文章式中文简报:开篇综述 + 多个分段(每段多要点)。数据驱动。"""
    mkt_recs = [r for r in records if r["market"] == market and r["kind"] == "stock"]
    # 去重(按代码)用于宽度/领涨领跌
    rows, seen_codes = [], set()
    for r in mkt_recs:
        if r["code"] in seen_codes:
            continue
        q = quotes_by_yf.get(r["yf"])
        if q and q.get("pct") is not None:
            seen_codes.add(r["code"])
            rows.append((r["name"], r["track"], q["pct"]))
    # 赛道均值(允许同一票计入多条赛道)
    track_rows = [(r["name"], r["track"], quotes_by_yf[r["yf"]]["pct"])
                  for r in mkt_recs
                  if quotes_by_yf.get(r["yf"]) and quotes_by_yf[r["yf"]].get("pct") is not None]
    rows_sorted = sorted(rows, key=lambda x: x[2], reverse=True)
    up = sum(1 for *_, p in rows if p > 0)
    down = sum(1 for *_, p in rows if p < 0)
    flat = len(rows) - up - down

    track_avg = {}
    for _n, track, p in track_rows:
        track_avg.setdefault(track, []).append(p)
    track_rank = sorted(((t, round(sum(v) / len(v), 2)) for t, v in track_avg.items()),
                        key=lambda x: x[1], reverse=True)

    def idx_str(m, with_price=False):
        out = []
        for sym, nm in INDICES.get(m, []):
            q = idx_quotes.get(sym)
            if q and q.get("pct") is not None:
                if with_price and q.get("price") is not None:
                    out.append(f"{nm} {q['price']:,} ({q['pct']:+.2f}%)")
                else:
                    out.append(f"{nm} {q['pct']:+.2f}%")
        return out

    mkt_cn = "A股" if market == "CN" else "美股"
    title_mode = "盘前前瞻" if mode == "preview" else "盘后总结"
    now = datetime.now(CN_TZ if market == "CN" else US_TZ)
    main_idx = idx_str(market)
    best = track_rank[0] if track_rank else None
    worst = track_rank[-1] if track_rank else None

    # —— 开篇综述 ——
    parts = []
    if main_idx:
        parts.append(f"{mkt_cn}{'今日' if mode=='summary' else '上一交易日'}{main_idx[0]}")
    if rows:
        ratio = (up / max(down, 1))
        tone = "普涨" if up > down * 1.6 else ("普跌" if down > up * 1.6 else "涨跌互现")
        parts.append(f"AI 算力链观察池{tone},{up} 涨 / {down} 跌(共 {len(rows)} 只)")
    if best and worst:
        parts.append(f"{best[0]}({best[1]:+.2f}%)最强、{worst[0]}({worst[1]:+.2f}%)最弱")
    if rows_sorted:
        parts.append(f"个股看,{rows_sorted[0][0]}领涨 {rows_sorted[0][2]:+.1f}%、{rows_sorted[-1][0]}领跌 {rows_sorted[-1][2]:+.1f}%")
    intro = ";".join(parts) + "。" if parts else ""

    sections = []

    # 1) 大盘与宽度
    s1 = []
    for line in idx_str(market, with_price=True):
        s1.append(line)
    if rows:
        s1.append(f"观察池宽度:{up} 涨 / {down} 跌 / {flat} 平,涨跌比 {up}:{down}。")
        adv = round(up / len(rows) * 100, 1) if rows else 0
        mood = "情绪偏强" if adv >= 60 else ("情绪偏弱" if adv <= 40 else "情绪中性")
        s1.append(f"上涨占比 {adv}%,{mood}。")
    if s1:
        sections.append({"h": "大盘与宽度", "items": s1})

    # 2) 赛道轮动
    s2 = []
    for t, a in track_rank[:3]:
        s2.append(f"领涨赛道 · {t}:平均 {a:+.2f}%")
    for t, a in track_rank[-3:][::-1]:
        s2.append(f"走弱赛道 · {t}:平均 {a:+.2f}%")
    if best and worst:
        s2.append(f"赛道强弱分化(最强-最弱):{best[1] - worst[1]:.2f} 个百分点。")
    if s2:
        sections.append({"h": "赛道轮动", "items": s2})

    # 3) 个股看点
    s3 = []
    if rows_sorted:
        tops = "、".join(f"{n} {p:+.1f}%" for n, _t, p in rows_sorted[:8])
        bots = "、".join(f"{n} {p:+.1f}%" for n, _t, p in rows_sorted[-8:][::-1])
        s3.append("领涨 TOP8:" + tops)
        s3.append("领跌 TOP8:" + bots)
        big_up = [f"{n} {p:+.1f}%" for n, _t, p in rows_sorted if p >= 9][:6]
        big_dn = [f"{n} {p:+.1f}%" for n, _t, p in rows_sorted if p <= -9][:6]
        if big_up:
            s3.append("强势异动(≥+9%):" + "、".join(big_up))
        if big_dn:
            s3.append("大幅回调(≤-9%):" + "、".join(big_dn))
    if s3:
        sections.append({"h": "个股看点", "items": s3})

    # 4) 跨市场 / 隔夜联动
    other = "US" if market == "CN" else "CN"
    other_idx = idx_str(other)
    if other_idx:
        label = "隔夜美股" if market == "CN" else "同期 A股"
        sections.append({"h": "跨市场联动", "items": [label + ":" + " · ".join(other_idx),
                          ("外盘指引偏多" if any('+' in x for x in other_idx[:1]) else "外盘指引偏空") + ",留意开盘情绪传导。"]})

    # 5) 关注 / 风险
    if mode == "preview":
        watch = []
        if best:
            watch.append(f"延续性:关注上一交易日最强的 {best[0]} 能否持续。")
        watch.append("注意高开回落与放量滞涨;以分时与量能验证强弱。")
        sections.append({"h": "今日关注", "items": watch})
        headline = "盘前前瞻 · 上一交易日强弱与隔夜外盘指引"
    else:
        risk = []
        if rows and down > up:
            risk.append("今日下跌家数居多,留意赛道补跌与情绪退潮风险。")
        else:
            risk.append("情绪偏暖,但需防普涨后的获利了结与高位分化。")
        risk.append("本简报为数据驱动的事实汇总,非投资建议;数据为日级/延迟。")
        sections.append({"h": "风险与提示", "items": risk})
        headline = "盘后总结 · 收盘强弱与赛道轮动一览"

    return {
        "market": market, "mode": mode,
        "title": f"{mkt_cn}{title_mode}",
        "stamp": now.strftime("%Y-%m-%d %H:%M ") + ("北京时间" if market == "CN" else "美东时间"),
        "headline": headline,
        "intro": intro,
        "sections": sections,
        "track_rank": track_rank,
    }


def run(market, mode):
    data = load_existing()
    data["universe"] = build_universe_struct()
    records = data["universe"]

    markets = ["CN", "US"] if market == "both" else [market.upper()]

    # 抓取个股/ETF
    target_syms = sorted({r["yf"] for r in records if r["market"] in markets})
    # 指数:始终抓全部 8 个(两市场),供图表与跨市场简报
    all_idx = [(s, nm, m) for m in ("CN", "US") for s, nm in INDICES.get(m, [])]
    idx_syms = sorted({s for s, _, _ in all_idx})

    print(f"抓取 {len(target_syms)} 个标的 + {len(idx_syms)} 个指数(含历史)...")
    closes = download_closes(target_syms)
    hist = fetch_history(idx_syms, period="3mo", keep=60)

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

    # 指数行情(由历史末两日收盘推出涨跌幅) + 历史序列
    data["history"] = {}
    idx_quotes = {}
    for sym, nm, m in all_idx:
        h = hist.get(sym)
        if not h or not h.get("c") or len(h["c"]) < 2:
            continue
        data["history"][sym] = h
        last, prev = h["c"][-1], h["c"][-2]
        rec = {"name": nm, "market": m, "price": last, "prev": prev,
               "pct": pct(last, prev), "ts": now_iso}
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

# -*- coding: utf-8 -*-
"""AI 算力链 12 赛道选股池 + 大盘指数。
每个标的: (代码, 名称)。市场由所在列表决定。
A股/ETF 代码会在 fetch.py 里按规则转成 yfinance 符号(.SS/.SZ/.BJ)。
你可以随时增删标的——改这里即可,流水线会自动跟进。
"""

# 大盘指数 (yfinance 符号)
INDICES = {
    "CN": [
        ("000001.SS", "上证指数"),
        ("399001.SZ", "深证成指"),
        ("399006.SZ", "创业板指"),
        ("000300.SS", "沪深300"),
    ],
    "US": [
        ("^GSPC", "标普500"),
        ("^IXIC", "纳斯达克"),
        ("^SOX", "费城半导体"),
        ("^DJI", "道琼斯"),
    ],
}

# 12 赛道。每条: name, layer, stars, us[], cn[], etf[]
TRACKS = [
 {"n": "AI 算力芯片", "layer": "上游·GPU/ASIC", "stars": 5,
  "us": [("NVDA","英伟达"),("AVGO","博通"),("AMD","超威"),("MRVL","美满"),("ARM","Arm"),("QCOM","高通"),("INTC","英特尔"),("ALAB","Astera Labs"),("CRDO","Credo"),("AMBA","安霸")],
  "cn": [("688256","寒武纪"),("688041","海光信息"),("688047","龙芯中科"),("300474","景嘉微"),("688008","澜起科技"),("688521","芯原股份"),("688385","复旦微电"),("002049","紫光国微"),("688107","安路科技"),("688262","国芯科技")],
  "etf": [("SMH","VanEck半导体ETF"),("SOXX","iShares半导体ETF"),("SOXQ","Invesco半导体ETF"),("AIQ","Global X AI ETF"),("159995","芯片ETF")]},

 {"n": "存储 HBM/DRAM/NAND", "layer": "上游·存储", "stars": 5,
  "us": [("MU","美光"),("SNDK","SanDisk"),("WDC","西部数据"),("STX","希捷"),("RMBS","Rambus"),("SIMO","慧荣科技"),("PSTG","Pure Storage"),("NTAP","NetApp"),("NLST","Netlist"),("SGH","Penguin Solutions")],
  "cn": [("603986","兆易创新"),("301308","江波龙"),("300223","北京君正"),("688525","佰维存储"),("688110","东芯股份"),("688766","普冉股份"),("001309","德明利"),("000021","深科技"),("300475","香农芯创"),("300302","同有科技")],
  "etf": [("DRAM","Roundhill存储ETF"),("SMH","VanEck半导体ETF"),("SOXX","iShares半导体ETF"),("SOXQ","Invesco半导体ETF"),("512480","半导体ETF")]},

 {"n": "光通信/CPO/光模块", "layer": "中游·光互联", "stars": 5,
  "us": [("COHR","Coherent"),("LITE","Lumentum"),("FN","Fabrinet"),("AAOI","应用光电"),("CIEN","Ciena"),("MTSI","MACOM"),("POET","POET Tech"),("MRVL","美满"),("AVGO","博通"),("GLW","康宁")],
  "cn": [("300308","中际旭创"),("300502","新易盛"),("300394","天孚通信"),("002281","光迅科技"),("000988","华工科技"),("300570","太辰光"),("688498","源杰科技"),("603083","剑桥科技"),("688313","仕佳光子"),("300548","博创科技")],
  "etf": [("SMH","VanEck半导体ETF"),("SOXX","iShares半导体ETF"),("AIQ","Global X AI ETF"),("515880","通信ETF"),("560660","通信设备ETF")]},

 {"n": "网络交换/互联", "layer": "中游·网络", "stars": 4,
  "us": [("ANET","Arista"),("AVGO","博通"),("NVDA","英伟达"),("MRVL","美满"),("ALAB","Astera Labs"),("CRDO","Credo"),("CSCO","思科"),("CLS","Celestica"),("CIEN","Ciena"),("JNPR","瞻博")],
  "cn": [("688702","盛科通信"),("000938","紫光股份"),("301165","锐捷网络"),("002475","立讯精密"),("002130","沃尔核材"),("300913","兆龙互连"),("301191","菲菱科思"),("688668","鼎通科技"),("300563","神宇股份"),("603118","共进股份")],
  "etf": [("SMH","VanEck半导体ETF"),("SOXX","iShares半导体ETF"),("AIQ","Global X AI ETF"),("515880","通信ETF"),("FIVG","Defiance 5G ETF")]},

 {"n": "EDA/IP", "layer": "上游·设计工具", "stars": 4,
  "us": [("SNPS","新思"),("CDNS","Cadence"),("ARM","Arm"),("ANSS","Ansys"),("KEYS","是德科技"),("CEVA","CEVA"),("RMBS","Rambus"),("LSCC","莱迪思"),("SLAB","芯科科技"),("SITM","SiTime")],
  "cn": [("301269","华大九天"),("688206","概伦电子"),("301095","广立微"),("688521","芯原股份"),("688691","灿芯股份"),("688220","翱捷科技"),("688262","国芯科技"),("002049","紫光国微"),("688385","复旦微电"),("688047","龙芯中科")],
  "etf": [("SMH","VanEck半导体ETF"),("SOXX","iShares半导体ETF"),("IGV","iShares软件ETF"),("AIQ","Global X AI ETF"),("159995","芯片ETF")]},

 {"n": "半导体设备(含光刻)", "layer": "上游·设备", "stars": 5,
  "us": [("ASML","阿斯麦"),("AMAT","应用材料"),("LRCX","泛林"),("KLAC","科磊"),("TER","泰瑞达"),("ONTO","Onto"),("ACLS","Axcelis"),("KLIC","库力索法"),("CAMT","Camtek"),("FORM","FormFactor")],
  "cn": [("002371","北方华创"),("688012","中微公司"),("688072","拓荆科技"),("688082","盛美上海"),("688120","华海清科"),("688037","芯源微"),("688361","中科飞测"),("300567","精测电子"),("300604","长川科技"),("688147","微导纳米")],
  "etf": [("SMH","VanEck半导体ETF"),("SOXX","iShares半导体ETF"),("SOXQ","Invesco半导体ETF"),("159516","半导体设备ETF"),("159995","芯片ETF")]},

 {"n": "半导体材料", "layer": "上游·材料", "stars": 4,
  "us": [("ENTG","Entegris"),("MKSI","MKS Instruments"),("LIN","林德"),("APD","空气产品"),("DD","杜邦"),("MTRN","Materion"),("AVTR","Avantor"),("IOSP","Innospec"),("KWR","Quaker Houghton"),("FUL","HB Fuller")],
  "cn": [("688126","沪硅产业"),("688019","安集科技"),("300054","鼎龙股份"),("002409","雅克科技"),("688268","华特气体"),("300666","江丰电子"),("300346","南大光电"),("605358","立昂微"),("603650","彤程新材"),("688233","神工股份")],
  "etf": [("SMH","VanEck半导体ETF"),("SOXX","iShares半导体ETF"),("516020","半导体材料ETF"),("159995","芯片ETF"),("512480","半导体ETF")]},

 {"n": "晶圆代工", "layer": "上游·制造", "stars": 4,
  "us": [("TSM","台积电"),("INTC","英特尔"),("GFS","GlobalFoundries"),("UMC","联电"),("TSEM","Tower"),("STM","意法半导体"),("ON","安森美"),("TXN","德州仪器"),("ADI","亚德诺"),("MCHP","微芯")],
  "cn": [("688981","中芯国际"),("688347","华虹公司"),("688249","晶合集成"),("688469","芯联集成"),("688172","燕东微"),("600460","士兰微"),("688396","华润微"),("688187","时代电气"),("600745","闻泰科技"),("300373","扬杰科技")],
  "etf": [("SMH","VanEck半导体ETF"),("SOXX","iShares半导体ETF"),("SOXQ","Invesco半导体ETF"),("EWT","iShares台湾ETF"),("159995","芯片ETF")]},

 {"n": "先进封装/封测", "layer": "上游·封测", "stars": 4,
  "us": [("AMKR","Amkor"),("ASX","日月光"),("ONTO","Onto"),("KLIC","库力索法"),("COHU","Cohu"),("FORM","FormFactor"),("CAMT","Camtek"),("TER","泰瑞达"),("NVMI","Nova"),("AEHR","Aehr")],
  "cn": [("600584","长电科技"),("002156","通富微电"),("002185","华天科技"),("688362","甬矽电子"),("603005","晶方科技"),("688372","伟测科技"),("688135","利扬芯片"),("688352","颀中科技"),("688175","气派科技"),("000021","深科技")],
  "etf": [("SMH","VanEck半导体ETF"),("SOXX","iShares半导体ETF"),("SOXQ","Invesco半导体ETF"),("159995","芯片ETF"),("512480","半导体ETF")]},

 {"n": "服务器/整机ODM", "layer": "中游·整机", "stars": 5,
  "us": [("DELL","戴尔"),("SMCI","超微电脑"),("HPE","慧与"),("CLS","Celestica"),("SANM","Sanmina"),("FLEX","Flex"),("SGH","Penguin Solutions"),("PSTG","Pure Storage"),("NTAP","NetApp"),("IBM","IBM")],
  "cn": [("601138","工业富联"),("000977","浪潮信息"),("603019","中科曙光"),("000938","紫光股份"),("000034","神州数码"),("603296","华勤技术"),("002261","拓维信息"),("301236","软通动力"),("600100","同方股份"),("688256","寒武纪")],
  "etf": [("AIQ","Global X AI ETF"),("SMH","VanEck半导体ETF"),("QQQ","Invesco纳指100"),("159890","云计算ETF"),("IGV","iShares软件ETF")]},

 {"n": "数据中心/IDC/液冷", "layer": "中游·基建", "stars": 5,
  "us": [("VRT","Vertiv"),("EQIX","Equinix"),("DLR","Digital Realty"),("ETN","伊顿"),("GEV","GE Vernova"),("MPWR","Monolithic Power"),("NVT","nVent"),("CRWV","CoreWeave"),("IRM","Iron Mountain"),("PWR","Quanta")],
  "cn": [("002837","英维克"),("300442","润泽科技"),("002335","科华数据"),("872808","曙光数创"),("301018","申菱环境"),("300383","光环新网"),("603881","数据港"),("300738","奥飞数据"),("600845","宝信软件"),("300499","高澜股份")],
  "etf": [("DTCR","Global X数据中心REIT"),("AIPO","AI+电力基建ETF"),("SRVR","Pacer数据基建ETF"),("AIQ","Global X AI ETF"),("GRID","First Trust电网ETF")]},

 {"n": "PCB/高速覆铜板", "layer": "中游·载板", "stars": 4,
  "us": [("TTMI","TTM Technologies"),("ROG","Rogers"),("DD","杜邦"),("CLS","Celestica"),("FLEX","Flex"),("JBL","Jabil"),("SANM","Sanmina"),("PLXS","Plexus"),("MTRN","Materion"),("BHE","Benchmark")],
  "cn": [("002463","沪电股份"),("600183","生益科技"),("002916","深南电路"),("300476","胜宏科技"),("002436","兴森科技"),("603228","景旺电子"),("688519","南亚新材"),("603920","世运电路"),("002636","金安国纪"),("688020","方邦股份")],
  "etf": [("SMH","VanEck半导体ETF"),("AIQ","Global X AI ETF"),("515260","电子ETF"),("515880","通信ETF"),("159995","芯片ETF")]},
]


def yf_symbol(code: str, market: str) -> str:
    """把代码转成 yfinance 符号。market: 'US' / 'CN'."""
    code = str(code).strip()
    if market == "US":
        return code  # 美股 / 美股ETF / 指数(^) 原样
    if code.startswith("^") or "." in code:
        return code
    if not code.isdigit():
        return code
    first = code[0]
    if first in ("5", "6", "9"):
        return code + ".SS"   # 上交所(含5开头ETF)
    if first in ("0", "1", "2", "3"):
        return code + ".SZ"   # 深交所(含1开头ETF)
    if first in ("4", "8"):
        return code + ".BJ"   # 北交所
    return code + ".SS"


def is_cn_etf(code: str) -> bool:
    return str(code).isdigit()


def build_records():
    """展开成扁平列表: 每条 {code, name, market, kind, track, yf}.
    同一标的可能出现在多条赛道; 抓数时按 yf 去重。"""
    records = []
    for t in TRACKS:
        for code, name in t["us"]:
            records.append({"code": code, "name": name, "market": "US",
                            "kind": "stock", "track": t["n"], "yf": yf_symbol(code, "US")})
        for code, name in t["cn"]:
            records.append({"code": code, "name": name, "market": "CN",
                            "kind": "stock", "track": t["n"], "yf": yf_symbol(code, "CN")})
        for code, name in t["etf"]:
            mkt = "CN" if is_cn_etf(code) else "US"
            records.append({"code": code, "name": name, "market": mkt,
                            "kind": "etf", "track": t["n"], "yf": yf_symbol(code, mkt)})
    return records


if __name__ == "__main__":
    recs = build_records()
    syms = sorted({r["yf"] for r in recs})
    print(f"赛道数: {len(TRACKS)}  记录数: {len(recs)}  去重符号: {len(syms)}")

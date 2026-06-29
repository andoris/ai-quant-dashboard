# -*- coding: utf-8 -*-
"""AI 算力链 12 赛道选股池 + 大盘指数。

条目格式:
  美股 / 美股ETF: (代码, 中文名, 英文名)
  A股 / A股ETF:   (代码, 中文名)          # A股保持中文,无英文
  指数:           (yf符号, 中文名, 英文名)

说明:每赛道美股、A股各 15 只(尾部为相邻/低纯度的真实标的,可自行删改);
ETF 各 5 只。A股/ETF 代码会按规则转成 yfinance 符号(.SS/.SZ/.BJ)。
"""

INDICES = {
    "CN": [("000001.SS", "上证指数", "SSE Composite"), ("399001.SZ", "深证成指", "SZSE Component"),
           ("399006.SZ", "创业板指", "ChiNext"), ("000300.SS", "沪深300", "CSI 300")],
    "US": [("^GSPC", "标普500", "S&P 500"), ("^IXIC", "纳斯达克", "Nasdaq"),
           ("^SOX", "费城半导体", "PHLX Semiconductor"), ("^DJI", "道琼斯", "Dow Jones")],
}

TRACKS = [
 {"n":"AI 算力芯片","en":"AI Compute Chips","layer":"上游·GPU/ASIC","stars":5,
  "desc":"AI 训练/推理核心算力,GPU、定制 ASIC 与 IP。成长最猛、分化最大,英伟达 CUDA 生态护城河最深。",
  "us":[("NVDA","英伟达","NVIDIA"),("AVGO","博通","Broadcom"),("AMD","超威","AMD"),("MRVL","美满","Marvell"),("ARM","Arm","Arm Holdings"),("QCOM","高通","Qualcomm"),("INTC","英特尔","Intel"),("ALAB","Astera Labs","Astera Labs"),("CRDO","Credo","Credo Technology"),("AMBA","安霸","Ambarella"),("TSM","台积电","TSMC"),("MU","美光","Micron"),("LSCC","莱迪思","Lattice"),("SLAB","芯科科技","Silicon Labs"),("SITM","SiTime","SiTime")],
  "cn":[("688256","寒武纪"),("688041","海光信息"),("688047","龙芯中科"),("300474","景嘉微"),("688008","澜起科技"),("688521","芯原股份"),("688385","复旦微电"),("002049","紫光国微"),("688107","安路科技"),("688262","国芯科技"),("603893","瑞芯微"),("300458","全志科技"),("688099","晶晨股份"),("688608","恒玄科技"),("300613","富瀚微")],
  "etf":[("SMH","VanEck半导体ETF","VanEck Semiconductor ETF"),("SOXX","iShares半导体ETF","iShares Semiconductor ETF"),("SOXQ","Invesco半导体ETF","Invesco PHLX Semiconductor ETF"),("AIQ","Global X AI ETF","Global X AI & Tech ETF"),("159995","芯片ETF")]},

 {"n":"存储 HBM/DRAM/NAND","en":"Memory (HBM/DRAM/NAND)","layer":"上游·存储","stars":5,
  "desc":"AI 硬瓶颈,HBM 需求爆发。真正的 HBM 王者是 SK海力士/三星(非美股),Micron 为追赶者。",
  "us":[("MU","美光","Micron"),("SNDK","SanDisk","SanDisk"),("WDC","西部数据","Western Digital"),("STX","希捷","Seagate"),("RMBS","Rambus","Rambus"),("SIMO","慧荣科技","Silicon Motion"),("PSTG","Pure Storage","Pure Storage"),("NTAP","NetApp","NetApp"),("NLST","Netlist","Netlist"),("SGH","Penguin Solutions","Penguin Solutions"),("MRVL","美满","Marvell"),("AVGO","博通","Broadcom"),("MCHP","微芯","Microchip"),("SMCI","超微电脑","Super Micro"),("DELL","戴尔","Dell")],
  "cn":[("603986","兆易创新"),("301308","江波龙"),("300223","北京君正"),("688525","佰维存储"),("688110","东芯股份"),("688766","普冉股份"),("001309","德明利"),("000021","深科技"),("300475","香农芯创"),("300302","同有科技"),("688123","聚辰股份"),("300672","国科微"),("300042","朗科科技"),("688416","恒烁股份"),("688332","中科蓝讯")],
  "etf":[("DRAM","Roundhill存储ETF","Roundhill Memory ETF"),("SMH","VanEck半导体ETF","VanEck Semiconductor ETF"),("SOXX","iShares半导体ETF","iShares Semiconductor ETF"),("SOXQ","Invesco半导体ETF","Invesco PHLX Semiconductor ETF"),("512480","半导体ETF")]},

 {"n":"光通信/CPO/光模块","en":"Optical / CPO / Transceivers","layer":"中游·光互联","stars":5,
  "desc":"集群越大,光互联价值占比越高。1.6T 光模块需求跳增,A股中际旭创/新易盛为全球出货龙头。",
  "us":[("COHR","Coherent","Coherent"),("LITE","Lumentum","Lumentum"),("FN","Fabrinet","Fabrinet"),("AAOI","应用光电","Applied Optoelectronics"),("CIEN","Ciena","Ciena"),("MTSI","MACOM","MACOM"),("POET","POET Tech","POET Technologies"),("MRVL","美满","Marvell"),("AVGO","博通","Broadcom"),("GLW","康宁","Corning"),("NVDA","英伟达","NVIDIA"),("ANET","Arista","Arista Networks"),("CSCO","思科","Cisco"),("ALAB","Astera Labs","Astera Labs"),("CRDO","Credo","Credo Technology")],
  "cn":[("300308","中际旭创"),("300502","新易盛"),("300394","天孚通信"),("002281","光迅科技"),("000988","华工科技"),("300570","太辰光"),("688498","源杰科技"),("603083","剑桥科技"),("688313","仕佳光子"),("300548","博创科技"),("688205","德科立"),("301205","联特科技"),("300620","光库科技"),("002902","铭普光磁"),("003031","中瓷电子")],
  "etf":[("SMH","VanEck半导体ETF","VanEck Semiconductor ETF"),("SOXX","iShares半导体ETF","iShares Semiconductor ETF"),("AIQ","Global X AI ETF","Global X AI & Tech ETF"),("515880","通信ETF"),("560660","通信设备ETF")]},

 {"n":"网络交换/互联","en":"Networking / Interconnect","layer":"中游·网络","stars":4,
  "desc":"GPU 间互联瓶颈,交换芯片、网卡、高速铜缆。Arista、博通主导,A股盛科通信为交换芯片龙头。",
  "us":[("ANET","Arista","Arista Networks"),("AVGO","博通","Broadcom"),("NVDA","英伟达","NVIDIA"),("MRVL","美满","Marvell"),("ALAB","Astera Labs","Astera Labs"),("CRDO","Credo","Credo Technology"),("CSCO","思科","Cisco"),("CLS","Celestica","Celestica"),("CIEN","Ciena","Ciena"),("JNPR","瞻博","Juniper Networks"),("COHR","Coherent","Coherent"),("FN","Fabrinet","Fabrinet"),("MTSI","MACOM","MACOM"),("HPE","慧与","HPE"),("JBL","Jabil","Jabil")],
  "cn":[("688702","盛科通信"),("000938","紫光股份"),("301165","锐捷网络"),("002475","立讯精密"),("002130","沃尔核材"),("300913","兆龙互连"),("301191","菲菱科思"),("688668","鼎通科技"),("300563","神宇股份"),("603118","共进股份"),("600498","烽火通信"),("000063","中兴通讯"),("688800","瑞可达"),("300679","电连技术"),("002897","意华股份")],
  "etf":[("SMH","VanEck半导体ETF","VanEck Semiconductor ETF"),("SOXX","iShares半导体ETF","iShares Semiconductor ETF"),("AIQ","Global X AI ETF","Global X AI & Tech ETF"),("515880","通信ETF"),("FIVG","Defiance 5G ETF","Defiance Next Gen 5G ETF")]},

 {"n":"EDA/IP","en":"EDA / IP","layer":"上游·设计工具","stars":4,
  "desc":"芯片设计的卡位生意,高毛利深护城河。Synopsys/Cadence 双寡头 + Arm 的 IP 垄断。",
  "us":[("SNPS","新思","Synopsys"),("CDNS","Cadence","Cadence"),("ARM","Arm","Arm Holdings"),("ANSS","Ansys","Ansys"),("KEYS","是德科技","Keysight"),("CEVA","CEVA","CEVA"),("RMBS","Rambus","Rambus"),("LSCC","莱迪思","Lattice"),("SLAB","芯科科技","Silicon Labs"),("SITM","SiTime","SiTime"),("QCOM","高通","Qualcomm"),("ALAB","Astera Labs","Astera Labs"),("CRDO","Credo","Credo Technology"),("TER","泰瑞达","Teradyne"),("FORM","FormFactor","FormFactor")],
  "cn":[("301269","华大九天"),("688206","概伦电子"),("301095","广立微"),("688521","芯原股份"),("688691","灿芯股份"),("688220","翱捷科技"),("688262","国芯科技"),("002049","紫光国微"),("688385","复旦微电"),("688047","龙芯中科"),("688200","华峰测控"),("688135","利扬芯片"),("688372","伟测科技"),("688728","格科微"),("688213","思特威")],
  "etf":[("SMH","VanEck半导体ETF","VanEck Semiconductor ETF"),("SOXX","iShares半导体ETF","iShares Semiconductor ETF"),("IGV","iShares软件ETF","iShares Expanded Tech-Software ETF"),("AIQ","Global X AI ETF","Global X AI & Tech ETF"),("159995","芯片ETF")]},

 {"n":"半导体设备(含光刻)","en":"Semicap (incl. Litho)","layer":"上游·设备","stars":5,
  "desc":"护城河最深、确定性最高的卖铲子赛道。ASML EUV 光刻独家垄断;A股北方华创/中微为国产替代主力。",
  "us":[("ASML","阿斯麦","ASML"),("AMAT","应用材料","Applied Materials"),("LRCX","泛林","Lam Research"),("KLAC","科磊","KLA"),("TER","泰瑞达","Teradyne"),("ONTO","Onto","Onto Innovation"),("ACLS","Axcelis","Axcelis"),("KLIC","库力索法","Kulicke & Soffa"),("CAMT","Camtek","Camtek"),("FORM","FormFactor","FormFactor"),("NVMI","Nova","Nova"),("ICHR","Ichor","Ichor"),("UCTT","Ultra Clean","Ultra Clean"),("ACMR","盛美半导体","ACM Research"),("AEHR","Aehr","Aehr Test Systems")],
  "cn":[("002371","北方华创"),("688012","中微公司"),("688072","拓荆科技"),("688082","盛美上海"),("688120","华海清科"),("688037","芯源微"),("688361","中科飞测"),("300567","精测电子"),("300604","长川科技"),("688147","微导纳米"),("600641","万业企业"),("603690","至纯科技"),("688200","华峰测控"),("688409","富创精密"),("300260","新莱应材")],
  "etf":[("SMH","VanEck半导体ETF","VanEck Semiconductor ETF"),("SOXX","iShares半导体ETF","iShares Semiconductor ETF"),("SOXQ","Invesco半导体ETF","Invesco PHLX Semiconductor ETF"),("159516","半导体设备ETF"),("159995","芯片ETF")]},

 {"n":"半导体材料","en":"Semiconductor Materials","layer":"上游·材料","stars":4,
  "desc":"硅片、光刻胶、电子特气、CMP 等耗材。国产替代空间大,A股沪硅产业/安集科技等领跑。",
  "us":[("ENTG","Entegris","Entegris"),("MKSI","MKS Instruments","MKS Instruments"),("LIN","林德","Linde"),("APD","空气产品","Air Products"),("DD","杜邦","DuPont"),("MTRN","Materion","Materion"),("AVTR","Avantor","Avantor"),("IOSP","Innospec","Innospec"),("KWR","Quaker Houghton","Quaker Houghton"),("FUL","HB Fuller","H.B. Fuller"),("ICHR","Ichor","Ichor"),("UCTT","Ultra Clean","Ultra Clean"),("AVNT","Avient","Avient"),("OLN","Olin","Olin"),("ASH","Ashland","Ashland")],
  "cn":[("688126","沪硅产业"),("688019","安集科技"),("300054","鼎龙股份"),("002409","雅克科技"),("688268","华特气体"),("300666","江丰电子"),("300346","南大光电"),("605358","立昂微"),("603650","彤程新材"),("688233","神工股份"),("300655","晶瑞电材"),("300236","上海新阳"),("688106","金宏气体"),("688548","广钢气体"),("600206","有研新材")],
  "etf":[("SMH","VanEck半导体ETF","VanEck Semiconductor ETF"),("SOXX","iShares半导体ETF","iShares Semiconductor ETF"),("516020","半导体材料ETF"),("159995","芯片ETF"),("512480","半导体ETF")]},

 {"n":"晶圆代工","en":"Foundry","layer":"上游·制造","stars":4,
  "desc":"先进制程与 CoWoS 封装命门在台积电。A股中芯/华虹为国产制造旗舰,受制裁压制。",
  "us":[("TSM","台积电","TSMC"),("INTC","英特尔","Intel"),("GFS","GlobalFoundries","GlobalFoundries"),("UMC","联电","UMC"),("TSEM","Tower","Tower Semiconductor"),("STM","意法半导体","STMicroelectronics"),("ON","安森美","Onsemi"),("TXN","德州仪器","Texas Instruments"),("ADI","亚德诺","Analog Devices"),("MCHP","微芯","Microchip"),("NXPI","恩智浦","NXP"),("SWKS","思佳讯","Skyworks"),("QRVO","Qorvo","Qorvo"),("MPWR","Monolithic Power","Monolithic Power"),("DIOD","美台","Diodes")],
  "cn":[("688981","中芯国际"),("688347","华虹公司"),("688249","晶合集成"),("688469","芯联集成"),("688172","燕东微"),("600460","士兰微"),("688396","华润微"),("688187","时代电气"),("600745","闻泰科技"),("300373","扬杰科技"),("600360","华微电子"),("300623","捷捷微电"),("605111","新洁能"),("688689","银河微电"),("688261","东微半导")],
  "etf":[("SMH","VanEck半导体ETF","VanEck Semiconductor ETF"),("SOXX","iShares半导体ETF","iShares Semiconductor ETF"),("SOXQ","Invesco半导体ETF","Invesco PHLX Semiconductor ETF"),("EWT","iShares台湾ETF","iShares MSCI Taiwan ETF"),("159995","芯片ETF")]},

 {"n":"先进封装/封测","en":"Advanced Packaging / OSAT","layer":"上游·封测","stars":4,
  "desc":"CoWoS、Chiplet、2.5D/3D 是 AI 时代真瓶颈。A股长电/通富/华天承接产能转移。",
  "us":[("AMKR","Amkor","Amkor Technology"),("ASX","日月光","ASE Technology"),("ONTO","Onto","Onto Innovation"),("KLIC","库力索法","Kulicke & Soffa"),("COHU","Cohu","Cohu"),("FORM","FormFactor","FormFactor"),("CAMT","Camtek","Camtek"),("TER","泰瑞达","Teradyne"),("NVMI","Nova","Nova"),("AEHR","Aehr","Aehr Test Systems"),("UCTT","Ultra Clean","Ultra Clean"),("ICHR","Ichor","Ichor"),("ACLS","Axcelis","Axcelis"),("KLAC","科磊","KLA"),("LRCX","泛林","Lam Research")],
  "cn":[("600584","长电科技"),("002156","通富微电"),("002185","华天科技"),("688362","甬矽电子"),("603005","晶方科技"),("688372","伟测科技"),("688135","利扬芯片"),("688352","颀中科技"),("688175","气派科技"),("000021","深科技"),("688200","华峰测控"),("300604","长川科技"),("301348","蓝箭电子"),("688403","汇成股份"),("002077","大港股份")],
  "etf":[("SMH","VanEck半导体ETF","VanEck Semiconductor ETF"),("SOXX","iShares半导体ETF","iShares Semiconductor ETF"),("SOXQ","Invesco半导体ETF","Invesco PHLX Semiconductor ETF"),("159995","芯片ETF"),("512480","半导体ETF")]},

 {"n":"服务器/整机ODM","en":"Servers / ODM","layer":"中游·整机","stars":5,
  "desc":"AI 服务器出货高增,订单排到 2027。A股工业富联/浪潮信息为代工与整机龙头。",
  "us":[("DELL","戴尔","Dell"),("SMCI","超微电脑","Super Micro"),("HPE","慧与","HPE"),("CLS","Celestica","Celestica"),("SANM","Sanmina","Sanmina"),("FLEX","Flex","Flex"),("SGH","Penguin Solutions","Penguin Solutions"),("PSTG","Pure Storage","Pure Storage"),("NTAP","NetApp","NetApp"),("IBM","IBM","IBM"),("CRWV","CoreWeave","CoreWeave"),("NVDA","英伟达","NVIDIA"),("AVGO","博通","Broadcom"),("ANET","Arista","Arista Networks"),("JBL","Jabil","Jabil")],
  "cn":[("601138","工业富联"),("000977","浪潮信息"),("603019","中科曙光"),("000938","紫光股份"),("000034","神州数码"),("603296","华勤技术"),("002261","拓维信息"),("301236","软通动力"),("600100","同方股份"),("688256","寒武纪"),("600498","烽火通信"),("600839","四川长虹"),("300002","神州泰岳"),("000628","高新发展"),("002474","榕基软件")],
  "etf":[("AIQ","Global X AI ETF","Global X AI & Tech ETF"),("SMH","VanEck半导体ETF","VanEck Semiconductor ETF"),("QQQ","Invesco纳指100","Invesco QQQ"),("159890","云计算ETF"),("IGV","iShares软件ETF","iShares Expanded Tech-Software ETF")]},

 {"n":"数据中心/IDC/液冷","en":"Data Center / IDC / Cooling","layer":"中游·基建","stars":5,
  "desc":"AI 耗电与散热刚需,电源、液冷、IDC、电力。Vertiv、Equinix 领跑,A股英维克液冷龙头。",
  "us":[("VRT","Vertiv","Vertiv"),("EQIX","Equinix","Equinix"),("DLR","Digital Realty","Digital Realty"),("ETN","伊顿","Eaton"),("GEV","GE Vernova","GE Vernova"),("MPWR","Monolithic Power","Monolithic Power"),("NVT","nVent","nVent Electric"),("CRWV","CoreWeave","CoreWeave"),("IRM","Iron Mountain","Iron Mountain"),("PWR","Quanta","Quanta Services"),("SMCI","超微电脑","Super Micro"),("DELL","戴尔","Dell"),("CEG","星座能源","Constellation Energy"),("VST","Vistra","Vistra"),("ANET","Arista","Arista Networks")],
  "cn":[("002837","英维克"),("300442","润泽科技"),("002335","科华数据"),("872808","曙光数创"),("301018","申菱环境"),("300383","光环新网"),("603881","数据港"),("300738","奥飞数据"),("600845","宝信软件"),("300499","高澜股份"),("300017","网宿科技"),("300249","依米康"),("300990","同飞股份"),("603912","佳力图"),("603887","城地香江")],
  "etf":[("DTCR","Global X数据中心REIT","Global X Data Center REITs ETF"),("AIPO","AI+电力基建ETF","AI Infrastructure & Power ETF"),("SRVR","Pacer数据基建ETF","Pacer Data & Infrastructure ETF"),("AIQ","Global X AI ETF","Global X AI & Tech ETF"),("GRID","First Trust电网ETF","First Trust Clean Edge Grid ETF")]},

 {"n":"PCB/高速覆铜板","en":"PCB / CCL","layer":"中游·载板","stars":4,
  "desc":"AI 服务器高速多层 PCB 与高频覆铜板需求高增。A股沪电股份/生益科技领跑。",
  "us":[("TTMI","TTM Technologies","TTM Technologies"),("ROG","Rogers","Rogers"),("DD","杜邦","DuPont"),("CLS","Celestica","Celestica"),("FLEX","Flex","Flex"),("JBL","Jabil","Jabil"),("SANM","Sanmina","Sanmina"),("PLXS","Plexus","Plexus"),("MTRN","Materion","Materion"),("BHE","Benchmark","Benchmark Electronics"),("APH","安费诺","Amphenol"),("GLW","康宁","Corning"),("COHR","Coherent","Coherent"),("FN","Fabrinet","Fabrinet"),("NVT","nVent","nVent Electric")],
  "cn":[("002463","沪电股份"),("600183","生益科技"),("002916","深南电路"),("300476","胜宏科技"),("002436","兴森科技"),("603228","景旺电子"),("688519","南亚新材"),("603920","世运电路"),("002636","金安国纪"),("688020","方邦股份"),("002384","东山精密"),("002938","鹏鼎控股"),("001389","广合科技"),("002815","崇达技术"),("000823","超声电子")],
  "etf":[("SMH","VanEck半导体ETF","VanEck Semiconductor ETF"),("AIQ","Global X AI ETF","Global X AI & Tech ETF"),("515260","电子ETF"),("515880","通信ETF"),("159995","芯片ETF")]},
]


def yf_symbol(code, market):
    code = str(code).strip()
    if market == "US":
        return code
    if code.startswith("^") or "." in code:
        return code
    if not code.isdigit():
        return code
    first = code[0]
    if first in ("5", "6", "9"):
        return code + ".SS"
    if first in ("0", "1", "2", "3"):
        return code + ".SZ"
    if first in ("4", "8"):
        return code + ".BJ"
    return code + ".SS"


def is_cn_etf(code):
    return str(code).isdigit()


def _unpack(entry):
    return entry[0], entry[1], (entry[2] if len(entry) > 2 else None)


def build_records():
    records = []
    for t in TRACKS:
        common = {"track": t["n"], "track_en": t["en"], "layer": t["layer"], "stars": t["stars"], "desc": t["desc"]}
        for e in t["us"]:
            code, zh, en = _unpack(e)
            records.append({"code": code, "name": zh, "en": en, "market": "US", "kind": "stock", "yf": yf_symbol(code, "US"), **common})
        for e in t["cn"]:
            code, zh, en = _unpack(e)
            records.append({"code": code, "name": zh, "en": None, "market": "CN", "kind": "stock", "yf": yf_symbol(code, "CN"), **common})
        for e in t["etf"]:
            code, zh, en = _unpack(e)
            mkt = "CN" if is_cn_etf(code) else "US"
            records.append({"code": code, "name": zh, "en": en, "market": mkt, "kind": "etf", "yf": yf_symbol(code, mkt), **common})
    return records


if __name__ == "__main__":
    recs = build_records()
    syms = sorted({r["yf"] for r in recs})
    print(f"赛道数: {len(TRACKS)}  记录数: {len(recs)}  去重符号: {len(syms)}")

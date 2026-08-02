# AI 算力链 · 行情看板(自动更新 + 公开分享)

一个**全自动、免费、可公开分享**的行情看板:每天按 A股/美股盘前盘后自动抓取
12 条 AI 算力链赛道、约 300 只标的(美股 + A股 + ETF)的行情,计算涨跌幅与排名,
生成盘前前瞻 / 盘后总结,并发布到一个公开网页链接,朋友点链接即可查看。

引擎跑在 **GitHub Actions**(免费),网页托管在 **GitHub Pages**(免费),无需自备服务器。

---

## 看板包含什么

- **大盘总览**:上证 / 深证 / 创业板 / 沪深300 + 标普 / 纳指 / 费半 / 道指,及观察池市场宽度。
- **涨跌幅排名**:全部标的按涨跌幅排序,可按市场(A股/美股)、类型(个股/ETF)筛选、搜索。
- **全部赛道**:12 赛道 × (美股 + A股),每只标的实时显示当日涨跌幅,带赛道成长星级。
- **盘前/盘后简报**:A股、美股各自的盘前前瞻与盘后总结(数据驱动,简报粒度)。

> 数据源 yfinance(雅虎财经),为**日级 / 延迟数据,非逐笔实时**,仅供研究,**非投资建议**。

---

## 一次性部署(约 15 分钟)

### 1. 注册并登录 GitHub
没有账号就到 https://github.com 免费注册。

### 2. 新建仓库
右上角 **+ → New repository**:
- Repository name:`ai-quant-dashboard`
- 选择 **Public**(公开,这样朋友才能看)
- 点 **Create repository**

### 3. 上传本文件夹的全部内容
在新仓库页面点 **uploading an existing file**,把本文件夹里的文件**保持目录结构**拖进去:
```
universe.py
fetch.py
requirements.txt
README.md
.gitignore
docs/index.html
docs/data.json
.github/workflows/update.yml
```
> 网页拖拽上传时,`.github/workflows/update.yml` 这种带文件夹的路径,直接把整个 `.github`
> 文件夹拖进去即可;若网页不识别隐藏文件夹,改用下面的 git 命令上传(见文末)。
点 **Commit changes** 提交。

### 4. 开启 GitHub Pages(得到公开链接)
仓库 **Settings → Pages**:
- Source 选 **Deploy from a branch**
- Branch 选 **main**,文件夹选 **/docs**,点 **Save**
- 稍等 1 分钟,页面顶部会出现你的公开链接(你的用户名是 andoris):
  `https://andoris.github.io/ai-quant-dashboard/`

### 5. 允许 Actions 提交数据
仓库 **Settings → Actions → General → Workflow permissions**:
- 选 **Read and write permissions** → **Save**
(这样定时任务才能把抓到的行情写回 `docs/data.json`。)

### 6. 手动跑一次,验证
仓库 **Actions** 标签 → 左侧 **Update market data** → 右侧 **Run workflow**:
- market 填 `both`,mode 填 `summary` → **Run workflow**
- 等 1–2 分钟变绿,然后打开第 4 步的公开链接,应能看到行情。

### 7. 分享
把公开链接发给朋友即可。之后**每天自动更新**,无需再操作。

---

## 自动更新时间表

`.github/workflows/update.yml` 里设了 4 个定时(cron 用 UTC):

| 北京时间 | 美东时间 | 触发 |
|---|---|---|
| 08:30 | — | A股盘前前瞻 |
| 15:30 | — | A股盘后总结 |
| — | 08:30 | 美股盘前前瞻 |
| — | 16:30 | 美股盘后总结 |

> 注意:cron 固定按 UTC,上表按美国**夏令时(EDT)**安排;到冬令时(EST)美股相关时间会
> 早 1 小时,如需精确可在 `update.yml` 里把 `12`/`20` 改成 `13`/`21`。
> GitHub 定时任务在高峰期偶有几分钟延迟,属正常。

---

## 想改观察池?
编辑 `universe.py` 里的 `TRACKS`(增删股票/ETF)或 `INDICES`(改指数),提交即可,
流水线会自动跟进。A股/ETF 用 6 位代码即可,脚本会自动转成 yfinance 符号(`.SS/.SZ/.BJ`)。

## 本地试跑(可选)
```bash
pip install -r requirements.txt
python fetch.py --market both --mode summary   # 生成 docs/data.json
# 然后用浏览器打开 docs/index.html(需通过本地服务器,如 python -m http.server)
```

## AI 策略板块

看板新增「AI 策略」标签页,基于当日行情自动生成:市场情绪研判、赛道关注/回避方向、个股关注清单(按技术信号打分,可点进 K 线)。

- **默认免费**:不配任何 key 时用**规则引擎**(市场宽度 + 赛道轮动 + MACD/RSI/MA/BOLL 技术信号),零成本、每次都稳定。
- **可选升级 Claude**:在仓库 **Settings → Secrets and variables → Actions → New repository secret** 添加
  - Name: `ANTHROPIC_API_KEY`,Value: 你的 Anthropic API key
  之后工作流会自动改用 Claude 生成叙事式策略(每次更新约几美分);调用失败或无 key 时自动回退规则引擎。
  - 可选再加变量 `CLAUDE_MODEL`(默认 `claude-sonnet-4-6`)。

> 重要:AI 策略仅为**信息性参考**,**不构成投资建议**,页面已附免责声明。

## 可选升级:更聪明的简报
当前简报是**数据驱动模板**(指数、宽度、领涨领跌、赛道轮动)。若想要 AI 撰写的叙事性点评,
可在 `fetch.py` 的 `make_brief` 后接一个大模型 API(把密钥放进仓库 Settings → Secrets,
在 workflow 里以环境变量传入),我可以再帮你加这一段。

## 用 git 命令上传(替代第 3 步)
```bash
cd ai-quant-dashboard
git init && git add . && git commit -m "init"
git branch -M main
git remote add origin https://github.com/andoris/ai-quant-dashboard.git
git push -u origin main
```

---
**免责声明**:本项目仅用于信息聚合与研究,所有数据可能存在延迟或错误,不构成任何投资建议。

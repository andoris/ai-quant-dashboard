# 升级:按需实时(Cloudflare Pages + 函数)

目标:**没人看就不取数;有人打开/查询时,价格是当下的(秒~分钟级)。**

原理:静态页不能直接调付费 API(会暴露 key)。所以加一个很小的后端函数
`functions/api/quotes.js`,用户打开页面时才调用,**边缘缓存 ~20 秒**(多人同看也只打数据源几次),
key 藏在环境变量里。前端加载后每 30 秒(仅在标签页可见时)轮询合并最新价。

- **美股实时**:Tiingo IEX 批量接口(需 `TIINGO_TOKEN`)。
- **A股实时**:腾讯行情接口(免费、批量,无需 key)。
- **历史K线/简报/AI策略/标的清单**:仍由 GitHub Action 每天生成 `docs/data.json`,
  并作为"无实时函数时"的兜底。

---

## 一次性部署(约 15 分钟)

### 0. 准备
- 仓库里已有 `functions/api/quotes.js` 和 `docs/`(确认都已推到 GitHub)。
- 注册 Tiingo:https://www.tiingo.com → 账号设置里拿 **API Token**。
  (美股实时建议订阅其付费档,免费档调用频次低,几百只每 20 秒会超限。)
- `docs/data.json` 需要已被 GitHub Action 跑过一次、`universe` 非空(函数靠它拿标的清单)。

### 1. 连接到 Cloudflare Pages
1. 登录 https://dash.cloudflare.com → 左侧 **Workers & Pages** → **Create** → **Pages** → **Connect to Git**。
2. 授权并选择你的仓库 `ai-quant-dashboard`。
3. 构建设置:
   - Framework preset: **None**
   - Build command: **留空**
   - Build output directory: **`docs`**
4. **Save and Deploy**。完成后得到地址 `https://<项目名>.pages.dev`。
   - `functions/` 目录会被**自动识别**为后端函数,`/api/quotes` 即生效。

### 2. 配置环境变量(放 API key)
项目 → **Settings → Environment variables → Production** → 添加:
- `TIINGO_TOKEN` = 你的 Tiingo Token
（A股走腾讯免费接口,无需 key;以后要接 Tushare 做历史层再加 `TUSHARE_TOKEN`。）
加完点 **Save**,然后 **Deployments → 最新一次 → Retry deployment**(让变量生效)。

### 3. 验证
- 打开 `https://<项目名>.pages.dev/api/quotes` → 应返回 JSON,`count` 大于 0、`quotes` 里有价格。
- 打开 `https://<项目名>.pages.dev/` → 看板顶部应显示 **● 实时 LIVE 最后更新 …**,价格随刷新跳动。
- 把这个 `.pages.dev` 链接发给朋友(国内访问通常也快)。

### 4. 数据/历史继续自动更新
- GitHub Action 照常每天生成 `docs/data.json`(历史K线、简报、AI策略、标的清单)。
- 你每次 push(含 Action 的数据提交)Cloudflare Pages 会**自动重新部署**。
- 既然实时已由函数负责,**可把 `update.yml` 的 `*/5` 高频定时降回每天 4 次**(盘前盘后),
  减少仓库提交:把两条 `*/5 ...` 换成
  `- cron: "30 7 * * 1-5"` 和 `- cron: "30 20 * * 1-5"` 即可。

---

## 成本与边界(实话)
- **闲时零成本**:没人访问就不调用函数、不打数据源。
- **有人看时**:每 ~20 秒最多向数据源拉一次(边缘缓存合并所有访客),费用随访问量与 Tiingo 档位走。
- **A股实时**用的是腾讯公开接口(免费、稳定但非官方);要更正规可后续接 Tushare/付费源,我改 `functions/api/quotes.js` 的 A股适配器即可。
- **指数(上证/纳指等)**实时这版暂未接(腾讯/Tiingo 取指数另需适配),指数卡片仍用每日值;需要我再补。
- 我无法联网实测这些 API,**首次部署后若某段取不到**(美股空/ A股空),把 `/api/quotes` 返回贴给我,我针对性修适配器。

---

## 旧的 GitHub Pages 还能用吗?
能,但 `github.io` 上没有 `/api/quotes`(纯静态),所以**只有每日数据、没有实时**。
要实时就用 Cloudflare 的 `.pages.dev` 链接。两边可并存。

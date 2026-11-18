# 🎯 Market Radar · 中国互联网商机挖掘与 AI 锐评投研台

> **在线免登录看板（GitHub Pages）**：`https://donghyq.github.io/market-radar/`  
> **本地双击即开入口**：克隆仓库后直接双击根目录 `index.html`（内置全量免登录证据快照弹窗）

---

## 一、信息是怎么抓的？有哪些渠道？抓了多少？有什么限制？（彻底打开黑盒）

本工具拒绝抓取泛科技新闻，只抓取**直接反映真实付费流水与用户具体抱怨**的 4 类中国互联网信号源：

| 渠道名称 | 抓取方式与技术原理 | 当前入库条数 | 存在的问题 / 边界限制 | 怎么新增关键词或扩充 |
| :--- | :--- | :--- | :--- | :--- |
| **1. Apple 中国区 App Store 差评采集** | 调用官方公开接口 `itunes.apple.com/search?country=cn` 检索赛道内高评价数工具 App，再拉取 `customerreviews/id={appId}/sortby=mostrecent/json` RSS 流，自动过滤出 **1~3 星且含『扣费/太贵/不能打印/卡顿/垃圾』** 的付费用户真实差评 | **21 条**<br>（如《试卷宝》16万评、《小白打印》13万评、《说得提词器》4.2万评） | **优点**：100% 免登录、无反爬、全自动；<br>**限制**：仅覆盖已上架苹果商店的 App，看不到微信私域或纯小程序流水 | 打开 `scripts/radar_cli.py`，在 `collect_appstore()` 的 `queries` 列表加一行 `("分类", "关键词")` |
| **2. B 站（Bilibili）高收藏视频与热评采集** | 自动预热访客 Cookie 后调用 `api.bilibili.com/x/web-interface/search/type` 抓取播放量、收藏量、弹幕数，核心计算 **`收藏/播放比`**（收藏率 > 5% 代表强烈需求）；再调用 `x/v2/reply` 拉取评论区高赞吐槽与求工具评论 | **23 条**<br>（含 Remotion 教程 9954 收藏/11.3% 收藏率、Manim 教程 1.6万收藏等） | **限制**：单 IP 极高频连续翻页会触发 B 站风控验证码；当前限制每词精取前 4 条高相关视频及首屏热评，100% 稳定不封 IP | 打开 `scripts/radar_cli.py`，在 `collect_bilibili()` 的 `queries` 列表加一行 `("分类", "关键词")` |
| **3. 微信公众号（搜狗微信）实战拆解采集** | 请求 `weixin.sogou.com/weixin?type=2` 检索最新发布的公众号实战复盘文章，提取标题、核心收益/痛点摘要与来源公众号 | **12 条**<br>（含闲鱼虚拟变现拆解、教培 78% 续费率案例、B站 50万播放仅赚 500元实测） | **限制**：免登录仅返回文章摘要与临时链接，因此脚本在抓取时已将核心摘要完整存入本地快照库，点击看板『📄 本地完整快照』即可免登录阅读 | 打开 `scripts/radar_cli.py`，在 `collect_wechat_sogou()` 的 `queries` 列表添加新词 |
| **4. 蝉妈妈 / 闲鱼 / 小红书导表收件箱 (`inbox/`)** | 针对滑块与设备指纹风控极严的商业平台，采用 **`inbox/*.csv` 投递箱机制**：网页端筛选导出 CSV 放入 `inbox/` 目录，运行脚本即自动去重入库 | **5 条高价值导表信号**<br>（支持无限追加 `.csv` 文件） | **限制**：需市场部同事每周花 5 分钟从网页端导出一次表格放入 `inbox/` | 见下方【二、蝉妈妈/闲鱼怎么导 CSV】 |

### 🔌 程序员同事怎么花 15 行代码新增一个自动采集渠道（如知乎/七麦/V2EX）？
1. 打开 `scripts/radar_cli.py`，仿照 `collect_wechat_sogou(conn)` 写一个函数 `collect_your_channel(conn)`。
2. 在函数内拿到数据后，直接调用内置函数 `insert_signal(conn, channel="渠道名", source_tier="实时API抓取", category="分类", query_term="检索词", title="标题", content="痛点正文", author_or_app="来源", metric_primary="主指标", metric_secondary="副指标", rating_or_price="价格或评分", source_url="链接")`。
3. 在 `main()` 的 `collect` 分支里加上一行你的函数调用即可！

---

## 二、蝉妈妈 / 闲鱼 / 小红书怎么导 CSV 喂给工具？

### 1. 蝉妈妈 3 步导出 CSV 教程
1. 登录蝉妈妈网页版 → 进入 **【视频榜 / 投流视频库 / 商品榜】**，筛选：**『近 7 天』**、**『粉丝数 < 5 万（专门找低粉爆单的纯工具/虚拟品）』**，关键词搜 `工具 / 模板 / 软件 / 教程 / 定制`。
2. 点击右上角 **【导出数据 (Excel/CSV)】**。
3. 对照本仓库 `inbox/chanmama_xianyu_xhs_signals.csv` 的 10 个标准表头字段（`channel, category, query_term, title, content, author_or_app, metric_primary, metric_secondary, rating_or_price, source_url`）粘贴保存为 `.csv` 放入 `inbox/` 文件夹，运行 `python3 scripts/radar_cli.py run-all` 即自动清洗入库。

### 2. 闲鱼 / 小红书人工巡检与快速录入
- **闲鱼看什么**：搜 `代做 / 脚本 / 批量 / 规划表 / 定制`，切到 **【按想要数排序】**，凡是 `想要 > 300人` 且客单价 `9.9~99元` 的人工代做商品，直接录入！
- **小红书看什么**：搜 `求平替 / 太贵了 / 怎么自动`，找评论区超过 30 人刷 `蹲一个 / 求链接` 的帖子，直接录入！

---

## 三、团队成员通过自己人脉找到一个新方向，怎么自动录入并跑 AI 锐评评估？

提供 **网页零代码填表** 和 **命令行一键入库** 两种方式，均会自动运行五维 AI 锐评打分（付费意愿 40% + 获客路径 25% + 研发交付 15% + 竞争缝隙 10% + 48h 测款 10%）并生成反方风险提示与 48 小时测款动作：

### 方式 A：直接在看板网页上填表（市场部同事推荐）
1. 打开看板 `index.html`（或在线链接），点击顶部第 2 个标签页 **【💡 2. 团队人脉/新方向录入与 AI 锐评】**。
2. 填入方向名称、提报人（如：王总人脉）、具体做什么、卖给谁怎么收费、人脉证据，点击 **『⚡ 立即运行 AI 锐评五维打分并加入首屏立项榜』**。
3. 页面会立即算出分数并插入首屏立项榜，同时底部会自动生成一行终端同步命令，复制给研发或自己运行即可永久写入 GitHub 仓库。

### 方式 B：一行命令自动评分并写入 `data/ideas/`（永久入库共享）
```bash
python3 scripts/radar_cli.py submit-idea \
  --title "你的新方向名称" \
  --proposer "你的名字(人脉来源)" \
  --what "一句话说清客户输入什么、系统产出什么" \
  --buyer "卖给谁、定价多少（如：199元/月）" \
  --evidence "人脉验证证据（如：3家熟人客户明确愿付定金）" \
  --channel "首批客户获客渠道" \
  --mvp-days 5

# 同步到 GitHub 与在线看板
python3 scripts/sync_github.py
```

---

## 四、团队多人协作怎么解决 DB 冲突？GitHub 团队开发收费吗？

### 1. GitHub 团队协作 100% 免费（0 元）
- 在 GitHub 的 `Settings -> Collaborators -> Add people` 中邀请团队所有成员加入 `donghyq/market-radar` 仓库，**不限人数、完全免费**。
- 公开仓库的 **GitHub Pages 在线看板托管** 与 **GitHub Actions 每日定时采集任务** 也全部免费。

### 2. 彻底解决多人开发 `radar.db` 二进制冲突的设计
- **原因**：SQLite 的 `radar.db` 是二进制文件，两人同时修改会导致 Git 无法自动合并。
- **本仓库的无冲突架构（JSONL 增量流 + 独立 Idea 文件 + 本地自动重建 DB）**：
  1. `*.db` 已被加入 `.gitignore`，**Git 不再追踪二进制数据库**；
  2. 所有采集到的信号以纯文本按行存储在 `data/signals/signals_master.jsonl`（一行一条 JSON，带 `uid` 唯一哈希指纹），多人新增信号时 Git 可直接按行自动 Merge；
  3. 每个人提报的新项目方向各自生成独立的 JSON 文件存放在 `data/ideas/TEAM-xxxxxx.json`，A 同事和 B 同事同时提报新方向互不碰同一个文件，**100% 零冲突**；
  4. 任何人拉取代码后运行 `python3 scripts/radar_cli.py run-all`，脚本会在 0.1 秒内从 `signals_master.jsonl` 自动重建本地 `radar.db` 并渲染最新看板。

### 3. 团队模块化分工与 Roadmap
- **模块 1（渠道采集插件组 `scripts/radar_cli.py`）**：负责维护和新增知乎、七麦、GitHub Trending 等自动采集函数；
- **模块 2（评估与立项组 `scripts/dashboard_config.json` & `data/ideas/`）**：市场部与产品负责人通过人脉调研、蝉妈妈导表和 `submit-idea` 持续录入并迭代高分立项卡；
- **模块 3（前端看板与自动化组 `scripts/template.html` & `.github/workflows/`）**：负责看板交互升级与飞书 Webhook 每日早报推送。

---

## 五、怎么做例行更新？以前的历史内容怎么保存和兼容？

1. **云端全自动每日例行更新（已配置 `.github/workflows/daily_radar.yml`）**：
   - 每天北京时间 **08:30**，GitHub Actions 会自动拉起云端环境运行 `python3 scripts/radar_cli.py run-all`，抓取最新差评与高收藏视频并自动推送更新在线看板（也可随时在 GitHub 仓库的 `Actions` 页面点击 `Run workflow` 手动立即触发）。
2. **历史内容 100% 永久保存与向前兼容**：
   - **增量去重合并（绝不删老数据）**：每次运行采集时，系统先加载 `data/signals/signals_master.jsonl` 中的全部历史信号，新抓到的信号按 `channel + title + author` 生成唯一 `uid`，已存在的保留首次发现时间 `first_seen` 并更新 `last_seen`，新发现的追加在末尾；
   - **按日历史快照（`data/archives/YYYY-MM-DD.json`）**：每次例行更新都会在 `data/archives/` 下生成当天的统计快照，方便回溯每周新增趋势。

# Market Radar · 中国互联网真实商机挖掘与 AI 锐评立项工作台

面向团队市场调研与快速变现立项的轻量级雷达工具。自动采集 **中国区 App Store 1~3 星付费痛点差评、B 站高收藏率视频与热评、微信公众号一线实战拆解**，并支持导入 **蝉妈妈、闲鱼、小红书** 监测表格，通过硬规则去噪后生成 **AI 锐评立项看板**（内置免登录本地完整证据快照）。

## 一、团队成员怎么直接看看板与数据（零配置）

1. **直接看可视化看板（含免登录证据快照）**：
   - 克隆本仓库后，直接双击根目录下的 `index.html`（或访问仓库开启的 GitHub Pages 在线链接）。
   - 点击看板中任意项目的 `📄 证据 #ID` 或表格中的 `📄 本地完整快照`，即可**无需登录任何外部平台**，直接在弹窗中阅读抓取入库的完整差评原话、视频数据与痛点摘要。
2. **用 Excel / 飞书多维表格查看全量数据**：
   - 直接打开 `exports/signals_full.csv`（UTF-8 with BOM 编码，Excel 双击直开不乱码），或直接将 `exports/signals_full.csv` 导入团队飞书多维表格。

## 二、团队怎么日常更新数据并同步给所有人

```bash
# 1. 如果有从蝉妈妈/闲鱼导出的新 CSV，放入 inbox/ 目录
# 2. 运行一键采集、去噪与看板刷新（纯 Python3 标准库，无需 pip 安装任何依赖）
python3 scripts/radar_cli.py run-all

# 3. 提交并推送到 GitHub，全团队即可看到最新看板与数据
git add .
git commit -m "chore: update market radar signals and dashboard"
git push
```

## 三、目录结构

- `index.html` / `docs/index.html`：交互式 AI 锐评立项看板（内嵌全量本地证据快照，支持 GitHub Pages 直接托管）
- `radar.db`：SQLite 本地数据库（含 `raw_signals` 原始信号表与 `opportunities` 立项评估表）
- `inbox/`：蝉妈妈、闲鱼、小红书等外部导出 CSV 投递收件箱
- `exports/signals_full.csv`：带 BOM 的全量信号 CSV 导出表（可直接拖入飞书多维表格或 Excel）
- `scripts/radar_cli.py`：多渠道实时采集与硬规则清洗引擎
- `scripts/export_dashboard.py` & `scripts/dashboard_config.json`：AI 锐评立项配置与看板渲染器

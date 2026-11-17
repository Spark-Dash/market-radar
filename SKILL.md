---
name: market-radar
description: 中国互联网真实商机挖掘与AI锐评立项评估工具。支持采集 App Store 中国区差评、B 站高收藏视频与热评、微信公众号文章及本地蝉妈妈/闲鱼导表，经硬规则清洗后输出五维立项评分与 48 小时测款方案。
---

# Market Radar (中国互联网商机雷达)

## 快速运行命令
1. **一键拉取线上多渠道数据并清洗入库**：
   `python3 /Users/hanyudong/.codex/skills/market-radar/scripts/radar_cli.py collect && python3 /Users/hanyudong/.codex/skills/market-radar/scripts/radar_cli.py clean`
2. **导出/刷新本地可视化商机决策看板**：
   `python3 /Users/hanyudong/.codex/skills/market-radar/scripts/export_dashboard.py`
3. **数据与看板路径**：
   - 本地交互式看板：`/Users/hanyudong/Desktop/catClaw/market-radar/index.html`
   - SQLite 数据库：`/Users/hanyudong/Desktop/catClaw/market-radar/radar.db`
   - 蝉妈妈/闲鱼 CSV 导入目录：`/Users/hanyudong/Desktop/catClaw/market-radar/inbox/`

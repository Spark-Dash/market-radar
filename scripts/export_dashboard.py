#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import datetime
import html
import json
import pathlib
import shutil
import sqlite3

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "radar.db"
OUT_HTML = BASE_DIR / "index.html"
DOCS_HTML = BASE_DIR / "docs" / "index.html"
CFG_PATH = pathlib.Path(__file__).parent / "dashboard_config.json"


def export_all(conn=None, base_dir=BASE_DIR):
    close_conn = False
    if conn is None:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        close_conn = True

    signals = [dict(r) for r in conn.execute("SELECT * FROM raw_signals ORDER BY is_noise ASC, id ASC").fetchall()]
    sig_map = {s["id"]: s for s in signals}
    valid_cnt = sum(1 for s in signals if not s["is_noise"])
    cfg = json.loads(CFG_PATH.read_text(encoding="utf-8"))

    # 1. 团队既有 4 个方向复盘卡片
    old_cards = []
    for item in cfg["existing_ideas"]:
        old_cards.append(
            f"<div class='old-card'>"
            f"<div class='old-title'>{html.escape(item['name'])}</div>"
            f"<div class='old-row'><b>🎯 当时想做啥：</b>{html.escape(item['original_plan'])}</div>"
            f"<div class='old-row bad'><b>🛑 为什么卡住没赚到钱：</b>{html.escape(item['blocker'])}</div>"
            f"<div class='old-row sharp'><b>🤖 AI 锐评诊断：</b>{html.escape(item['ai_review'])}</div>"
            f"<div class='old-row good'><b>🚀 怎么改造成能收钱的产品：</b>{html.escape(item['pivot_to'])}</div>"
            f"</div>"
        )

    # 2. 5 个大白话落地赚钱方案
    proj_cards = []
    for p in cfg["projects"]:
        steps_html = "".join(f"<li>{html.escape(st)}</li>" for st in p["workflow_steps"])
        ev_Chips = []
        for eid in p.get("evidence_ids", []):
            s = sig_map.get(eid)
            if s:
                ev_Chips.append(
                    f"<button class='ev-btn' onclick='openSnap({eid})'>"
                    f"📄 证据 #{eid}：{html.escape(s['author_or_app'][:14])} ({html.escape(s['metric_primary'])})"
                    f"</button>"
                )
        proj_cards.append(
            f"<div class='proj-card'>"
            f"<div class='proj-head'>"
            f"<div><span class='badge'>{html.escape(p['category_tag'])}</span>"
            f"<h3>{html.escape(p['title'])}</h3></div>"
            f"<div class='score-wrap'><div class='score'>{p['score']}<span>/100</span></div>"
            f"<div class='score-sub'>{html.escape(p['score_detail'])}</div></div>"
            f"</div>"
            f"<div class='plain-box'><b>💡 一句话听懂到底做啥产品：</b>{html.escape(p['plain_what_to_do'])}</div>"
            f"<div class='grid2'>"
            f"<div class='box'><b>🛠️ 具体怎么做（输入 → 处理 → 产出）</b><ul class='step-list'>{steps_html}</ul></div>"
            f"<div class='box good'><b>💰 卖给谁？收多少钱？</b><p>{html.escape(p['who_pays_and_price'])}</p>"
            f"<b style='margin-top:10px;color:#fbbf24;'>🤖 AI 锐评与数据支撑</b><p>{html.escape(p['ai_sharp_review'])}</p></div>"
            f"</div>"
            f"<div class='plan-box'><b>⚡ 48 小时低成本测款动作（市场部/研发明日即可执行）：</b>{html.escape(p['plan_48h'])}</div>"
            f"<div class='ev-bar'><span>📌 点击直接查看本方案的真实数据快照（免登录）：</span>{''.join(ev_Chips)}</div>"
            f"</div>"
        )

    # 3. 61 条原始证据表（主操作为免登录本地快照弹窗）
    rows_html = []
    for s in signals:
        sid = s["id"]
        noise_tag = "<span class='noise-tag'>已过滤噪音</span> " if s["is_noise"] else ""
        url = s["source_url"] or ""
        need_login = any(d in url for d in ["goofish.com", "chanmama.com", "xiaohongshu.com"])
        ext_label = "外部站(需登录)" if need_login else "直达原网页↗"
        rows_html.append(
            f"<tr class='sig-row' data-ch='{html.escape(s['channel'])}' data-q='{html.escape(s['title'] + ' ' + s['content'] + ' ' + s['author_or_app'])}'>"
            f"<td><b>#{sid}</b></td>"
            f"<td><span class='ch-tag'>{html.escape(s['channel'])}</span><br><small>{html.escape(s['category'])}</small></td>"
            f"<td><b>{html.escape(s['author_or_app'])}</b><br><small style='color:#fbbf24'>{html.escape(s['rating_or_price'])}</small></td>"
            f"<td>{noise_tag}<b>{html.escape(s['title'])}</b><br><span style='color:#cbd5e1'>{html.escape(s['content'])}</span></td>"
            f"<td><b style='color:#4ade80'>{html.escape(s['metric_primary'])}</b><br><small>{html.escape(s['metric_secondary'])}</small></td>"
            f"<td><button class='snap-btn' onclick='openSnap({sid})'>📄 本地完整快照</button><br>"
            f"<a class='ext-link' href='{html.escape(url)}' target='_blank'>{ext_label}</a></td>"
            f"</tr>"
        )

    signals_json = json.dumps(sig_map, ensure_ascii=False)

    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Market Radar · 中国互联网商机挖掘与 AI 锐评立项看板</title>
<style>
  :root {{ --bg:#0f172a; --card:#1e293b; --border:#334155; --text:#f8fafc; --muted:#94a3b8; --blue:#38bdf8; --green:#4ade80; --amber:#fbbf24; --red:#f87171; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif; background:var(--bg); color:var(--text); padding:24px 32px; line-height:1.6; }}
  h1 {{ margin:0 0 6px; font-size:24px; }}
  h2 {{ margin:28px 0 14px; font-size:19px; border-left:4px solid var(--blue); padding-left:10px; }}
  h3 {{ margin:6px 0 0; font-size:18px; color:#fff; }}
  .sub {{ color:var(--muted); font-size:13.5px; margin-bottom:20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px; border-bottom:1px solid var(--border); padding-bottom:14px; }}
  .nav-tabs {{ display:flex; gap:10px; margin-bottom:20px; flex-wrap:wrap; }}
  .tab {{ background:var(--card); color:var(--text); border:1px solid var(--border); padding:10px 18px; border-radius:8px; cursor:pointer; font-weight:600; font-size:14px; }}
  .tab.active {{ background:var(--blue); color:#0f172a; border-color:var(--blue); }}
  .old-grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:24px; }}
  .old-card {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:16px; }}
  .old-title {{ font-size:16px; font-weight:700; color:var(--blue); margin-bottom:10px; border-bottom:1px dashed var(--border); padding-bottom:6px; }}
  .old-row {{ font-size:13.5px; margin-bottom:8px; padding:8px 10px; border-radius:6px; background:rgba(15,23,42,0.5); }}
  .old-row.bad b {{ color:var(--red); }}
  .old-row.sharp b {{ color:var(--amber); }}
  .old-row.good b {{ color:var(--green); }}
  .proj-card {{ background:var(--card); border:1px solid var(--border); border-radius:12px; padding:20px; margin-bottom:20px; }}
  .proj-head {{ display:flex; justify-content:space-between; align-items:flex-start; gap:16px; margin-bottom:12px; }}
  .badge {{ background:rgba(56,189,248,0.18); color:var(--blue); border:1px solid rgba(56,189,248,0.4); padding:3px 10px; border-radius:99px; font-size:12px; font-weight:600; }}
  .score-wrap {{ text-align:right; min-width:220px; }}
  .score {{ font-size:28px; font-weight:800; color:var(--green); line-height:1.1; }}
  .score span {{ font-size:13px; color:var(--muted); font-weight:400; }}
  .score-sub {{ font-size:11px; color:var(--muted); margin-top:4px; }}
  .plain-box {{ background:#0284c722; border:1px solid #0284c766; border-radius:8px; padding:12px 14px; font-size:14.5px; margin-bottom:14px; }}
  .plain-box b {{ color:var(--blue); }}
  .grid2 {{ display:grid; grid-template-columns:1.15fr 1fr; gap:14px; margin-bottom:12px; }}
  .box {{ background:#0f172a; border:1px solid var(--border); border-radius:8px; padding:12px 14px; font-size:13.5px; }}
  .box b {{ display:block; margin-bottom:6px; color:var(--amber); }}
  .box.good b {{ color:var(--green); }}
  .box p {{ margin:0 0 6px; }}
  .step-list {{ margin:0; padding-left:18px; }}
  .step-list li {{ margin-bottom:6px; }}
  .plan-box {{ background:rgba(74,222,128,0.08); border:1px solid rgba(74,222,128,0.35); border-radius:8px; padding:10px 14px; font-size:13.5px; margin-bottom:12px; }}
  .plan-box b {{ color:var(--green); }}
  .ev-bar {{ display:flex; align-items:center; flex-wrap:wrap; gap:8px; font-size:12.5px; color:var(--muted); }}
  .ev-btn, .snap-btn {{ background:#334155; color:#fff; border:1px solid #475569; padding:5px 10px; border-radius:6px; cursor:pointer; font-size:12px; }}
  .ev-btn:hover, .snap-btn:hover {{ background:var(--blue); color:#0f172a; border-color:var(--blue); }}
  .filter-bar {{ display:flex; gap:12px; margin-bottom:12px; flex-wrap:wrap; }}
  input, select {{ background:var(--card); color:var(--text); border:1px solid var(--border); padding:8px 12px; border-radius:6px; font-size:13px; }}
  table {{ width:100%; border-collapse:collapse; background:var(--card); font-size:13px; border-radius:10px; overflow:hidden; }}
  th, td {{ padding:10px 12px; border-bottom:1px solid var(--border); text-align:left; vertical-align:top; }}
  th {{ background:#020617; color:var(--muted); }}
  .ch-tag {{ background:#334155; padding:2px 7px; border-radius:4px; font-size:11px; }}
  .noise-tag {{ background:#7f1d1d; color:#fecaca; padding:2px 6px; border-radius:4px; font-size:11px; }}
  .ext-link {{ display:inline-block; margin-top:6px; font-size:11.5px; color:var(--muted); text-decoration:none; }}
  .ext-link:hover {{ color:var(--blue); text-decoration:underline; }}
  /* 模态框免登录快照 */
  .modal-mask {{ display:none; position:fixed; inset:0; background:rgba(0,0,0,0.72); z-index:999; align-items:center; justify-content:center; padding:20px; }}
  .modal {{ background:var(--card); border:1px solid var(--blue); border-radius:12px; max-width:680px; width:100%; padding:22px; box-shadow:0 20px 50px rgba(0,0,0,0.6); }}
  .modal h3 {{ margin:0 0 10px; font-size:18px; color:var(--blue); }}
  .modal-meta {{ font-size:12.5px; color:var(--muted); margin-bottom:12px; padding-bottom:10px; border-bottom:1px solid var(--border); }}
  .modal-body {{ background:#0f172a; padding:14px; border-radius:8px; font-size:14px; white-space:pre-wrap; margin-bottom:14px; border:1px solid var(--border); }}
  .close-btn {{ background:var(--blue); color:#0f172a; border:none; padding:8px 16px; border-radius:6px; font-weight:700; cursor:pointer; }}
</style>
</head>
<body>
  <h1>🎯 Market Radar · 中国互联网真实商机挖掘与 AI 锐评立项看板</h1>
  <div class="sub">
    <div>已入库真实信号：<b>{len(signals)} 条</b>（清洗后有效证据 <b>{valid_cnt} 条</b>） · 点击任意证据可直接查看<b>本地免登录完整快照</b></div>
    <div>更新时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}</div>
  </div>

  <div class="nav-tabs">
    <button class="tab active" onclick="switchSec('sec-all', this)">📋 全部视图（既有方向复盘 + 5大落地项目 + 证据库）</button>
    <button class="tab" onclick="switchSec('sec-old', this)">🔍 1. 我们之前的 4 个既有方向复盘</button>
    <button class="tab" onclick="switchSec('sec-proj', this)">🚀 2. 具体做什么产品能赚钱（5大详细方案）</button>
    <button class="tab" onclick="switchSec('sec-sig', this)">📡 3. 本地免登录证据库 ({len(signals)}条)</button>
  </div>

  <div id="sec-old">
    <h2>一、我们团队之前的 4 个既有方向是什么？为什么卡住？AI 锐评怎么改？</h2>
    <div class="old-grid">{''.join(old_cards)}</div>
  </div>

  <div id="sec-proj">
    <h2>二、具体做哪 5 个产品能赚到钱？（大白话拆解：做什么 → 怎么做 → 卖给谁 → 48h测款）</h2>
    {''.join(proj_cards)}
  </div>

  <div id="sec-sig">
    <h2>三、本轮采集入库的 {len(signals)} 条真实渠道证据（点击【本地完整快照】无需登录直接看全文）</h2>
    <div class="filter-bar">
      <input type="text" id="qInput" placeholder="搜索关键词（如：Remotion、差评、扣费、教培、闲鱼、提词器）..." style="width:360px;" oninput="filterRows()">
      <select id="chSelect" onchange="filterRows()">
        <option value="">全部采集渠道</option>
        <option value="AppStore">AppStore中国区差评(实时API)</option>
        <option value="B站">B站视频与评论(实时API)</option>
        <option value="微信">微信公众号检索(实时抓取)</option>
        <option value="导表">蝉妈妈/闲鱼/小红书(导表)</option>
      </select>
    </div>
    <table>
      <thead>
        <tr>
          <th width="50">编号</th>
          <th width="165">采集渠道 / 分类</th>
          <th width="165">真实对象 / 来源</th>
          <th>完整标题与用户真实痛点内容（已保存在本地库）</th>
          <th width="165">量化热度 / 价格指标</th>
          <th width="125">免登录查看</th>
        </tr>
      </thead>
      <tbody>{''.join(rows_html)}</tbody>
    </table>
  </div>

  <div class="modal-mask" id="snapModal" onclick="if(event.target===this)closeSnap()">
    <div class="modal">
      <h3 id="mTitle">证据快照</h3>
      <div class="modal-meta" id="mMeta"></div>
      <div class="modal-body" id="mBody"></div>
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <a id="mLink" href="#" target="_blank" style="color:var(--blue);font-size:13px;">前往原始外部链接（部分平台如闲鱼/小红书需登录）↗</a>
        <button class="close-btn" onclick="closeSnap()">关闭窗口</button>
      </div>
    </div>
  </div>

<script>
const SIGNALS = {signals_json};
function openSnap(id) {{
  const s = SIGNALS[id];
  if (!s) return;
  document.getElementById('mTitle').innerText = `[证据 #${{s.id}}] ${{s.title}}`;
  document.getElementById('mMeta').innerHTML = `<b>采集渠道：</b>${{s.channel}} (${{s.source_tier}}) &nbsp;|&nbsp; <b>对象/来源：</b>${{s.author_or_app}} &nbsp;|&nbsp; <b>量化指标：</b>${{s.metric_primary}} / ${{s.metric_secondary}} &nbsp;|&nbsp; <b>采集时间：</b>${{s.collected_at}}`;
  document.getElementById('mBody').innerText = `【核心痛点与完整抓取内容】\n${{s.content}}\n\n【分类与检索词】\n分类：${{s.category}} | 检索词：${{s.query_term}} | 价格/评分属性：${{s.rating_or_price}}\n标签：${{s.pain_tags}}`;
  document.getElementById('mLink').href = s.source_url || '#';
  document.getElementById('snapModal').style.display = 'flex';
}}
function closeSnap() {{
  document.getElementById('snapModal').style.display = 'none';
}}
function switchSec(sec, btn) {{
  document.querySelectorAll('.tab').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  ['sec-old', 'sec-proj', 'sec-sig'].forEach(id => {{
    document.getElementById(id).style.display = (sec === 'sec-all' || sec === id) ? 'block' : 'none';
  }});
}}
function filterRows() {{
  const q = document.getElementById('qInput').value.toLowerCase();
  const ch = document.getElementById('chSelect').value;
  document.querySelectorAll('.sig-row').forEach(row => {{
    const mq = !q || row.dataset.q.toLowerCase().includes(q);
    const mch = !ch || row.dataset.ch.includes(ch);
    row.style.display = (mq && mch) ? '' : 'none';
  }});
}}
</script>
</body>
</html>
"""
    OUT_HTML.write_text(page, encoding="utf-8")
    DOCS_HTML.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUT_HTML, DOCS_HTML)
    if close_conn:
        conn.close()
    return OUT_HTML


if __name__ == "__main__":
    p = export_all()
    print("Updated dashboard:", p, p.stat().st_size)

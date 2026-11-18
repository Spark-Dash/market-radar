const SIG_MAP = {};
(DATA.signals || []).forEach(s => { SIG_MAP[s.id] = s; });

function esc(s) {
  return String(s || '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function getAllProjects() {
  let local = [];
  try { local = JSON.parse(localStorage.getItem('mr_custom_ideas') || '[]'); } catch(e) {}
  const all = [...local, ...(DATA.projects || [])];
  all.sort((a,b) => (b.score || 0) - (a.score || 0));
  return all;
}

function renderProjects() {
  const list = getAllProjects();
  document.getElementById('kpiProjects').innerText = list.length;
  const html = list.map((p, idx) => {
    const steps = (p.workflow_steps || []).map((st, i) =>
      `<div class="step-item"><span class="step-idx">${i+1}</span><div>${esc(st)}</div></div>`
    ).join('');
    const chips = (p.evidence_ids || []).map(eid => {
      const s = SIG_MAP[eid];
      if (!s) return '';
      return `<button class="chip-btn" onclick="openSnap(${eid})">📄 证据 #${eid} · ${esc(s.author_or_app.slice(0,12))} (${esc(s.metric_primary)})</button>`;
    }).join('');
    return `
      <div class="p-card">
        <div class="p-top">
          <div>
            <span class="tag-pill">NO.${idx+1} · ${esc(p.category_tag)}</span>
            <h2 class="p-title">${esc(p.title)}</h2>
          </div>
          <div class="score-panel">
            <div class="score-num">${p.score} <small>/ 100分 (AI 锐评)</small></div>
            <div class="score-detail">${esc(p.score_detail)}</div>
          </div>
        </div>
        <div class="what-banner"><b>💡 一句话听懂到底做什么产品：</b>${esc(p.plain_what_to_do)}</div>
        <div class="cols-2">
          <div class="panel">
            <span class="panel-title">🛠️ 具体怎么做（输入 → 处理 → 产出三步走）</span>
            ${steps}
          </div>
          <div class="panel">
            <span class="panel-title green">💰 卖给谁？收多少钱？</span>
            <div style="margin-bottom:10px;">${esc(p.who_pays_and_price)}</div>
            <span class="panel-title">🤖 AI 锐评（数据依据与避坑指南）</span>
            <div>${esc(p.ai_sharp_review)}</div>
          </div>
        </div>
        <div class="act-bar"><b>⚡ 48 小时低成本测款动作（明日即可执行）：</b>${esc(p.plan_48h)}</div>
        ${chips ? `<div class="ev-chips"><span>📌 点击免登录查看本方案关联的真实数据快照：</span>${chips}</div>` : ''}
      </div>
    `;
  }).join('');
  document.getElementById('tab-projects').innerHTML = html;
}

function renderSubmitTab() {
  document.getElementById('tab-submit').innerHTML = `
    <div class="p-card">
      <span class="tag-pill">🤝 团队人脉 / 内部新商机自动评估通道</span>
      <h2 class="p-title" style="margin-bottom:8px;">有同事通过自己的人脉找到了新方向？直接填表自动跑 AI 锐评并加入看板</h2>
      <p style="color:var(--sub);font-size:13.5px;margin-top:0;">填完下方 6 项后点击按钮，系统会自动按五维漏斗（付费证据40% + 获客路径25% + 交付周期15% + 竞争缝隙10% + 48h测款10%）算出分数、生成 AI 锐评风险诊断，并立即插入首屏【赚钱项目立项榜】，同时生成可提交到 GitHub 共享给全员的命令与 JSON 文件。</p>
      <div class="form-grid" style="margin-top:16px;">
        <div class="field"><label>1. 新项目方向名称 *</label><input id="fTitle" placeholder="例如：跨境独立站 TikTok 达人寄样自动催片脚本"></div>
        <div class="field"><label>2. 提报人 / 人脉来源 *</label><input id="fProposer" placeholder="例如：王总（深圳跨境卖家圈人脉）"></div>
        <div class="field" style="grid-column:span 2;"><label>3. 大白话说明具体做个什么产品（客户输入什么 → 自动产出什么）*</label><input id="fWhat" placeholder="例如：输入达人寄样单号与WhatsApp号，物流签收满3天自动发多语种语音+文案催达人交挂车视频的小工具"></div>
        <div class="field"><label>4. 卖给谁？准备怎么收费？*</label><input id="fBuyer" placeholder="例如：日寄样20+单的TK中小卖家，收 199元/月 或 999元/年"></div>
        <div class="field"><label>5. 首批 50 个客户去哪找（获客渠道）*</label><input id="fChannel" placeholder="例如：提报人手头的 3 个深圳卖家微信群 + 小红书TK寄样痛点帖截流"></div>
        <div class="field"><label>6. 人脉验证证据（对方现在怎么解决？有多痛？）*</label><input id="fEvidence" placeholder="例如：人脉认识的 3 家坂田卖家每月被白嫖样品亏上万，明确表示做出来立刻买"></div>
        <div class="field">
          <label>7. 研发周期与付费确定性</label>
          <div style="display:flex;gap:10px;">
            <select id="fDays"><option value="5">预计 3~7 天内可出 MVP (+14分)</option><option value="12">预计 1~2 周出 MVP (+11分)</option><option value="25">需 2 周以上重度开发 (+7分)</option></select>
            <select id="fPaid"><option value="1">客户已明确愿付定金/已在花钱找人工 (+36分)</option><option value="0">仅口头说不错，尚未谈钱 (+24分)</option></select>
          </div>
        </div>
      </div>
      <div style="margin-top:18px;display:flex;gap:12px;align-items:center;flex-wrap:wrap;">
        <button class="btn-primary" onclick="submitNewIdea()">⚡ 立即运行 AI 锐评五维打分并加入首屏立项榜</button>
        <span id="submitMsg" style="color:var(--green);font-size:13.5px;font-weight:600;"></span>
      </div>
      <div id="cliBox" style="display:none;margin-top:16px;" class="panel">
        <span class="panel-title green">✅ 已加入当前看板！如需永久写入 GitHub 仓库共享给全团队，在终端复制运行下方命令（自动生成独立无冲突 JSON）：</span>
        <code id="cliCmd" style="display:block;padding:10px;white-space:pre-wrap;word-break:break-all;"></code>
      </div>
    </div>
  `;
}

function submitNewIdea() {
  const title = document.getElementById('fTitle').value.trim();
  const proposer = document.getElementById('fProposer').value.trim() || '团队成员';
  const what = document.getElementById('fWhat').value.trim();
  const buyer = document.getElementById('fBuyer').value.trim() || '待定（建议99~299元测款）';
  const channel = document.getElementById('fChannel').value.trim() || '人脉私域+小红书/闲鱼';
  const evidence = document.getElementById('fEvidence').value.trim() || '内部人脉一线痛点反馈';
  const days = parseInt(document.getElementById('fDays').value, 10);
  const paid = document.getElementById('fPaid').value === '1';
  if (!title || !what) { alert('请至少填写【方向名称】和【具体做什么产品】！'); return; }

  const sPay = paid ? 36 : 24;
  const sAcq = /(群|人脉|老客|小红书|闲鱼|评论)/.test(channel) ? 22 : 16;
  const sDel = days <= 7 ? 14 : (days <= 14 ? 11 : 7);
  const sComp = 8;
  const sVal = paid ? 9 : 6;
  const total = sPay + sAcq + sDel + sComp + sVal;

  const risks = [];
  if (!paid) risks.push('当前仅有人脉口头意向，尚未见真金白银，务必先收定金防伪需求。');
  if (days > 10) risks.push('研发周期超10天，切忌闭门造车，前3单必须用脚本+人工半自动交付。');
  if (/(B端|机构|企业)/.test(buyer)) risks.push('面向B端客户极易陷入定制化与拖欠尾款泥潭，必须坚持标准年卡/预付费。');
  if (!risks.length) risks.push('人脉痛点扎实且研发极轻，下一步重点验证能否从熟人关系复制到公域陌生买家。');

  const newObj = {
    code: 'TEAM-' + Date.now().toString().slice(-4),
    category_tag: `🤝 团队人脉提报 · 提报人：${proposer}`,
    title: `【人脉新方向】${title}`,
    score: total,
    score_detail: `付费意愿 ${sPay}/40 · 获客截流 ${sAcq}/25 · 研发交付 ${sDel}/15 · 竞争缝隙 ${sComp}/10 · 48h测款 ${sVal}/10`,
    plain_what_to_do: what,
    workflow_steps: [
      `【人脉一手痛点】${evidence}`,
      `【最小MVP处理】控制在 ${days} 天内用现有脚本/模板搭出半自动流水线交付核心结果`,
      `【商业变现闭环】通过 ${channel} 触达首批客户，按『${buyer}』先收款后交付`
    ],
    who_pays_and_price: buyer,
    ai_sharp_review: '【AI 锐评自动诊断】' + risks.join(' '),
    plan_48h: `由 ${proposer} 在 48 小时内向该人脉客户发去一份手工/半自动跑出的样品 Demo，要求对方先预付 99~299 元测试定金，收到钱当天启动开发。`,
    evidence_ids: []
  };

  let local = [];
  try { local = JSON.parse(localStorage.getItem('mr_custom_ideas') || '[]'); } catch(e) {}
  local.unshift(newObj);
  localStorage.setItem('mr_custom_ideas', JSON.stringify(local));
  renderProjects();

  document.getElementById('submitMsg').innerText = `🎉 评估完成！AI 锐评得分：${total}/100 分，已插入【1. 赚钱项目立项榜】！`;
  document.getElementById('cliBox').style.display = 'block';
  document.getElementById('cliCmd').innerText =
    `python3 scripts/radar_cli.py submit-idea --title "${title}" --proposer "${proposer}" --what "${what}" --buyer "${buyer}" --evidence "${evidence}" --channel "${channel}" --mvp-days ${days}` + (paid ? '' : ' --unpaid') + ` && python3 scripts/sync_github.py`;
}

function renderWhitepaper() {
  const wp = DATA.whitepaper || {};
  const chHtml = (wp.channels || []).map(c => `
    <div class="panel" style="margin-bottom:12px;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <b style="color:var(--blue);font-size:15px;">${esc(c.name)}</b>
        <span class="tag-pill">${esc(c.type)}</span>
      </div>
      <div style="color:var(--green);font-size:12.5px;margin-bottom:6px;">📊 <b>抓取战果：</b>${esc(c.count_info)}</div>
      <div style="margin-bottom:6px;">🔍 <b>怎么抓的（透明原理）：</b>${esc(c.how_it_works)}</div>
      <div style="color:var(--amber);margin-bottom:6px;">⚠️ <b>已知问题与边界：</b>${esc(c.limitations)}</div>
      <div style="color:var(--sub);">🛠️ <b>怎么扩充关键词/新分类：</b><code>${esc(c.how_to_extend)}</code></div>
    </div>
  `).join('');

  const guideHtml = (wp.csv_guides || []).map(g => `
    <div class="panel" style="margin-bottom:12px;">
      <span class="panel-title green" style="font-size:15px;">${esc(g.platform)}</span>
      ${(g.steps || []).map(st => `<div style="margin-bottom:6px;">${esc(st)}</div>`).join('')}
    </div>
  `).join('');

  document.getElementById('tab-whitepaper').innerHTML = `
    <div class="p-card">
      <h2 class="p-title" style="margin-top:0;margin-bottom:14px;">📡 一、当前 4 大采集渠道透明白皮书（怎么抓的、抓了多少、有什么问题）</h2>
      ${chHtml}
      <h2 class="p-title" style="margin-top:24px;margin-bottom:14px;">📥 二、蝉妈妈 / 闲鱼怎么导 CSV？程序员怎么花 15 行代码加新渠道？</h2>
      ${guideHtml}
    </div>
  `;
}

function renderSignals() {
  const sigs = DATA.signals || [];
  document.getElementById('lblSigCnt').innerText = sigs.length;
  document.getElementById('kpiValid').innerText = sigs.filter(s => !s.is_noise).length;
  const rows = sigs.map(s => {
    const needLogin = /(goofish|chanmama|xiaohongshu)/.test(s.source_url || '');
    return `
      <tr class="sig-row" data-ch="${esc(s.channel)}" data-q="${esc(s.title + ' ' + s.content + ' ' + s.author_or_app)}">
        <td><b>#${s.id}</b><br><small style="color:var(--sub)">${esc((s.collected_at||'').slice(0,10))}</small></td>
        <td><span class="tag-pill" style="font-size:11px;">${esc(s.channel)}</span><br><small style="color:var(--sub)">${esc(s.category)}</small></td>
        <td><b>${esc(s.author_or_app)}</b><br><small style="color:var(--amber)">${esc(s.rating_or_price)}</small></td>
        <td>${s.is_noise ? '<span style="background:#7f1d1d;color:#fecaca;padding:2px 6px;border-radius:4px;font-size:11px;">已拦截噪音</span> ' : ''}<b>${esc(s.title)}</b><br><span style="color:#cbd5e1">${esc(s.content)}</span></td>
        <td><b style="color:var(--green)">${esc(s.metric_primary)}</b><br><small style="color:var(--sub)">${esc(s.metric_secondary)}</small></td>
        <td>
          <button class="chip-btn" onclick="openSnap(${s.id})">📄 本地完整快照</button><br>
          <a href="${esc(s.source_url)}" target="_blank" style="font-size:11.5px;color:var(--sub);display:inline-block;margin-top:6px;">${needLogin ? '外部站(需登录)↗' : '直达原网页↗'}</a>
        </td>
      </tr>
    `;
  }).join('');

  document.getElementById('tab-signals').innerHTML = `
    <div style="display:flex;gap:12px;margin-bottom:14px;flex-wrap:wrap;">
      <input id="qInput" placeholder="输入关键词过滤（如：Remotion、差评、扣费、教培、闲鱼、提词器）..." style="width:380px;background:var(--card);color:var(--text);border:1px solid var(--border);padding:9px 12px;border-radius:8px;" oninput="filterRows()">
      <select id="chSelect" onchange="filterRows()" style="background:var(--card);color:var(--text);border:1px solid var(--border);padding:9px 12px;border-radius:8px;">
        <option value="">全部采集渠道 (${sigs.length}条)</option>
        <option value="AppStore">AppStore中国区差评 (21条)</option>
        <option value="B站">B站视频与热评 (23条)</option>
        <option value="微信">微信公众号拆解 (12条)</option>
        <option value="导表">蝉妈妈/闲鱼/小红书导表 (5条)</option>
      </select>
    </div>
    <table>
      <thead><tr><th width="65">编号/日期</th><th width="170">渠道/分类</th><th width="165">对象/来源</th><th>完整标题与痛点内容（已存本地库）</th><th width="165">核心量化指标</th><th width="130">免登录查看</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
  `;
}

function renderRoadmapAndArchive() {
  const wp = DATA.whitepaper || {};
  const rmHtml = (wp.roadmap || []).map(r => `
    <div class="panel" style="margin-bottom:12px;">
      <div style="display:flex;justify-content:space-between;"><b style="color:var(--green)">${esc(r.phase)} · ${esc(r.title)}</b><span style="color:var(--blue);font-size:12px;">分工：${esc(r.owner)}</span></div>
      <div style="margin-top:6px;white-space:pre-line;color:#cbd5e1;">${esc(r.details)}</div>
    </div>
  `).join('');

  const oldHtml = (DATA.existing_ideas || []).map(o => `
    <div class="panel" style="margin-bottom:12px;">
      <b style="color:var(--blue);font-size:15px;">${esc(o.name)}</b>
      <div style="margin-top:6px;">🎯 <b>原设想：</b>${esc(o.original_plan)}</div>
      <div style="color:var(--red);margin-top:4px;">🛑 <b>当时卡点：</b>${esc(o.blocker)}</div>
      <div style="color:var(--amber);margin-top:4px;">🤖 <b>AI 锐评：</b>${esc(o.ai_review)}</div>
      <div style="color:var(--green);margin-top:4px;">🚀 <b>改造去向：</b>${esc(o.pivot_to)}</div>
    </div>
  `).join('');

  document.getElementById('tab-roadmap').innerHTML = `
    <div class="p-card">
      <h2 class="p-title" style="margin-top:0;margin-bottom:12px;">🗺️ 一、多人无冲突协作架构与迭代 Roadmap（GitHub 团队协作 100% 免费）</h2>
      <div class="what-banner">
        <b>💡 为什么现在多人同时开发不会再发生数据库冲突？</b><br>
        我们已将二进制的 <code>radar.db</code> 加入 <code>.gitignore</code>，Git 仓库只追踪纯文本的 <code>data/signals/signals_master.jsonl</code>（按行追加，Git 自动合并）和 <code>data/ideas/*.json</code>（每人提报的方向各自独立成一个 JSON 文件，零冲突）以及 <code>data/archives/YYYY-MM-DD.json</code>（按日历史归档，老数据永久保留）。
      </div>
      ${rmHtml}
      <h2 class="p-title" style="margin-top:24px;margin-bottom:12px;">🧭 二、团队既有 4 个方向复盘归档（为什么卡住 & 怎么改造）</h2>
      ${oldHtml}
    </div>
  `;
}

function openSnap(id) {
  const s = SIG_MAP[id];
  if (!s) return;
  document.getElementById('mTitle').innerText = `[证据 #${s.id}] ${s.title}`;
  document.getElementById('mMeta').innerText = `渠道：${s.channel} | 来源：${s.author_or_app} | 指标：${s.metric_primary} (${s.metric_secondary}) | 入库时间：${s.collected_at}`;
  document.getElementById('mBody').innerText = `【本地完整正文快照（免登录）】\n${s.content}\n\n【分类与检索词】\n分类：${s.category} | 检索词：${s.query_term} | 价格/评分：${s.rating_or_price}\n痛点标签：${s.pain_tags || '已验证信号'}`;
  document.getElementById('mLink').href = s.source_url || '#';
  document.getElementById('snapModal').style.display = 'flex';
}

function switchTab(id, btn) {
  ['tab-projects','tab-submit','tab-whitepaper','tab-signals','tab-roadmap'].forEach(t => {
    document.getElementById(t).style.display = (t === id) ? 'block' : 'none';
  });
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}

function filterRows() {
  const q = (document.getElementById('qInput').value || '').toLowerCase();
  const ch = document.getElementById('chSelect').value || '';
  document.querySelectorAll('.sig-row').forEach(r => {
    const mq = !q || r.dataset.q.toLowerCase().includes(q);
    const mch = !ch || r.dataset.ch.includes(ch);
    r.style.display = (mq && mch) ? '' : 'none';
  });
}

(function init() {
  document.getElementById('lblUpdated').innerText = DATA.updated_at || '';
  const archs = DATA.archives || [];
  document.getElementById('kpiArchives').innerText = `${archs.length || 1} 期`;
  document.getElementById('lblBatches').innerText = archs.map(a => a.date).join(', ') || '2026-11-18';
  renderProjects();
  renderSubmitTab();
  renderWhitepaper();
  renderSignals();
  renderRoadmapAndArchive();
})();

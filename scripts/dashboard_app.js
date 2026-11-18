const SIG_MAP = {};
(DATA.signals || []).forEach(s => { SIG_MAP[s.id] = s; });

let SELECTED_IDX = 0;
let EXPAND_ALL = false;

function cleanText(s) {
  if (!s) return '';
  // Strip decorative emojis for a clean, institutional terminal look
  return String(s).replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}\u{FE0F}]/gu, '').replace(/\s+/g, ' ').trim();
}

function esc(s) {
  return cleanText(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function getAllProjects() {
  let local = [];
  try { local = JSON.parse(localStorage.getItem('mr_custom_ideas') || '[]'); } catch(e) {}
  const all = [...local, ...(DATA.projects || [])];
  all.sort((a,b) => (b.score || 0) - (a.score || 0));
  return all;
}

function renderDetailCard(p, idx) {
  const steps = (p.workflow_steps || []).map((st, i) =>
    `<div class="step-row"><span class="step-no">0${i+1}</span><div>${esc(st)}</div></div>`
  ).join('');

  const comp = p.compounding || {
    tier: "A级复利 · 标准化产品资产",
    snowball: "初期通过轻量服务验证需求，中期沉淀行业模板与自动化流水线转为订阅制SaaS。",
    skill_gain: "沉淀领域工作流编排与高转化产品工程能力。"
  };

  const b = p.biz_eval || {
    cost: "初期成本 <100元", profit: "毛利率 90%+", time: "MVP 5~7天",
    team: "1~2人", landing: "48h测款 -> 自动化交付 -> 订阅SaaS", compliance: "遵守平台与数据脱敏规范"
  };

  const chips = (p.evidence_ids || []).map(eid => {
    const s = SIG_MAP[eid];
    if (!s) return '';
    return `<button class="btn" onclick="openSnap(${eid})">证据 #${eid} · ${esc(s.author_or_app.slice(0,14))} (${esc(s.metric_primary)})</button>`;
  }).join(' ');

  return `
    <div class="inspector">
      <div class="ins-head">
        <div>
          <div style="display:flex;gap:8px;align-items:center;">
            <span class="pill pill-s">RANK 0${idx+1} · ${esc(comp.tier)}</span>
            <span class="pill">${esc(p.category_tag)}</span>
          </div>
          <h2 class="ins-title">${esc(p.title)}</h2>
        </div>
        <div class="ins-score-box">
          <div class="ins-score-big">${p.score}<span style="font-size:13px;color:var(--text-muted);font-weight:400;"> / 100</span></div>
          <div class="ins-score-sub">${esc(p.score_detail)}</div>
        </div>
      </div>

      <span class="sec-label">01 / 产品定位与一句话定义</span>
      <div class="summary-lead">${esc(p.plain_what_to_do)}</div>

      <div class="grid-2">
        <div class="card-cell">
          <span class="cell-k">运转流程（输入 → 处理 → 产出）</span>
          <div class="cell-v">${steps}</div>
        </div>
        <div class="card-cell">
          <span class="cell-k">目标客群、定价策略与 AI 锐评依据</span>
          <div class="cell-v" style="margin-bottom:10px;"><strong style="color:var(--text);">定价与客群：</strong>${esc(p.who_pays_and_price)}</div>
          <div class="cell-v"><strong style="color:var(--text);">AI 锐评依据：</strong>${esc(p.ai_sharp_review)}</div>
        </div>
      </div>

      <span class="sec-label">02 / 复利滚雪球路径与团队能力沉淀（拒绝纯苦力外包）</span>
      <div class="grid-2">
        <div class="card-cell" style="border-left:2px solid var(--accent);">
          <span class="cell-k" style="color:var(--text);">长期复利与护城河（为什么能滚雪球）</span>
          <div class="cell-v">${esc(comp.snowball)}</div>
        </div>
        <div class="card-cell" style="border-left:2px solid var(--pos);">
          <span class="cell-k" style="color:var(--text);">对团队成员的技术与业务成长价值</span>
          <div class="cell-v">${esc(comp.skill_gain)}</div>
        </div>
      </div>

      <span class="sec-label">03 / 市场部立项六维商业与合规核算表</span>
      <div class="grid-3">
        <div class="card-cell"><span class="cell-k">1. 初步资金成本预估</span><div class="cell-v">${esc(b.cost)}</div></div>
        <div class="card-cell"><span class="cell-k">2. 利润预估与多元收入来源</span><div class="cell-v">${esc(b.profit)}</div></div>
        <div class="card-cell"><span class="cell-k">3. 时间成本（研发与回本周期）</span><div class="cell-v">${esc(b.time)}</div></div>
        <div class="card-cell"><span class="cell-k">4. 需要人数与角色配置</span><div class="cell-v">${esc(b.team)}</div></div>
        <div class="card-cell"><span class="cell-k">5. 三阶段落地推进路径</span><div class="cell-v">${esc(b.landing)}</div></div>
        <div class="card-cell"><span class="cell-k">6. 国内法律与平台合规边界</span><div class="cell-v">${esc(b.compliance)}</div></div>
      </div>

      <span class="sec-label">04 / 48 小时低成本测款探针与关联一手证据快照</span>
      <div class="card-cell" style="margin-bottom:12px;">
        <span class="cell-k" style="color:var(--text);">明日可执行 48 小时测款动作（仅作需求验证探针，验证通过后转自动化产品）</span>
        <div class="cell-v">${esc(p.plan_48h)}</div>
      </div>
      ${chips ? `<div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;"><span style="font-size:12px;color:var(--text-muted);">点击查看本地免登录证据快照：</span>${chips}</div>` : ''}
    </div>
  `;
}

function renderProjects() {
  const list = getAllProjects();
  document.getElementById('kpiProjects').innerText = list.length;
  if (SELECTED_IDX >= list.length) SELECTED_IDX = 0;

  const rows = list.map((p, i) => {
    const compTier = (p.compounding && p.compounding.tier) ? p.compounding.tier : 'A级复利';
    const b = p.biz_eval || {};
    const isSel = (!EXPAND_ALL && i === SELECTED_IDX) ? 'selected' : '';
    return `
      <tr class="row-item ${isSel}" onclick="selectProject(${i})">
        <td width="55" style="font-family:monospace;color:var(--text-muted);">0${i+1}</td>
        <td><strong style="color:var(--text);font-weight:500;">${esc(p.title)}</strong></td>
        <td width="175"><span class="pill ${compTier.startsWith('S') ? 'pill-s' : ''}">${esc(compTier)}</span></td>
        <td width="160" style="color:var(--text-secondary);">${esc(p.category_tag.split('·')[0])}</td>
        <td width="145" style="color:var(--text-secondary);">${esc((b.team || '1~2人').split('（')[0])} / ${esc((b.time || '5天').split('；')[0])}</td>
        <td width="85"><span class="num-score">${p.score}</span> <small style="color:var(--text-muted)">/100</small></td>
        <td width="90"><button class="btn" onclick="event.stopPropagation();selectProject(${i})">查看档案</button></td>
      </tr>
    `;
  }).join('');

  const detailHtml = EXPAND_ALL
    ? list.map((p, i) => renderDetailCard(p, i)).join('')
    : renderDetailCard(list[SELECTED_IDX], SELECTED_IDX);

  document.getElementById('tab-projects').innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;">
      <span class="sec-label" style="margin:0;">候选立项总览矩阵（点击任意行在下方切换查看该项目的完整深度评估档案）</span>
      <button class="btn" onclick="toggleExpandAll()">${EXPAND_ALL ? '切换为单项目聚焦模式' : '展开全部 9 个项目完整档案'}</button>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>排名</th>
            <th>项目方向名称</th>
            <th>复利与成长评级</th>
            <th>来源通道</th>
            <th>人数与研发周期</th>
            <th>AI 锐评总分</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
    <div id="inspectorAnchor">${detailHtml}</div>
  `;
}

function selectProject(idx) {
  SELECTED_IDX = idx;
  EXPAND_ALL = false;
  renderProjects();
}

function toggleExpandAll() {
  EXPAND_ALL = !EXPAND_ALL;
  renderProjects();
}

function renderSignals() {
  const sigs = DATA.signals || [];
  document.getElementById('lblSigCnt').innerText = sigs.length;
  document.getElementById('kpiValid').innerText = sigs.filter(s => !s.is_noise).length;
  const rows = sigs.map(s => {
    const needLogin = /(goofish|chanmama|xiaohongshu)/.test(s.source_url || '');
    return `
      <tr class="sig-row" data-ch="${esc(s.channel)}" data-q="${esc(s.title + ' ' + s.content + ' ' + s.author_or_app)}">
        <td style="font-family:monospace;color:var(--text-muted);">#${s.id}<br><small>${esc((s.collected_at||'').slice(0,10))}</small></td>
        <td><span class="pill">${esc(s.channel)}</span><br><small style="color:var(--text-muted)">${esc(s.category)}</small></td>
        <td><strong style="color:var(--text);font-weight:500;">${esc(s.author_or_app)}</strong><br><small style="color:var(--text-muted)">${esc(s.rating_or_price)}</small></td>
        <td>${s.is_noise ? '<span class="pill" style="color:#f87171;">已过滤噪音</span> ' : ''}<strong style="color:var(--text);font-weight:500;">${esc(s.title)}</strong><br><span style="color:var(--text-secondary)">${esc(s.content)}</span></td>
        <td style="color:var(--text-secondary);">${esc(s.metric_primary)}<br><small style="color:var(--text-muted)">${esc(s.metric_secondary)}</small></td>
        <td>
          <button class="btn" onclick="openSnap(${s.id})">本地快照</button><br>
          <a href="${esc(s.source_url)}" target="_blank" style="font-size:11.5px;color:var(--text-muted);display:inline-block;margin-top:6px;text-decoration:none;">${needLogin ? '原站(需登录)↗' : '原网页↗'}</a>
        </td>
      </tr>
    `;
  }).join('');

  document.getElementById('tab-signals').innerHTML = `
    <div style="display:flex;gap:12px;margin-bottom:14px;">
      <input id="qInput" placeholder="搜索关键词（如：Remotion、标书、报价单、差评、扣费、教培、闲鱼）..." style="max-width:420px;" oninput="filterRows()">
      <select id="chSelect" onchange="filterRows()" style="max-width:240px;">
        <option value="">全部渠道 (${sigs.length}条)</option>
        <option value="AppStore">AppStore中国区差评</option>
        <option value="B站">B站高收藏视频与热评</option>
        <option value="微信">微信公众号实战拆解</option>
        <option value="V2EX">V2EX开发者社区</option>
        <option value="导表">蝉妈妈/闲鱼/小红书</option>
      </select>
    </div>
    <div class="table-wrap">
      <table>
        <thead><tr><th width="75">编号</th><th width="175">渠道与分类</th><th width="165">来源对象</th><th>标题与本地保存的正文摘要</th><th width="160">量化指标</th><th width="105">操作</th></tr></thead>
        <tbody>${rows}</tbody>
      </table>
    </div>
  `;
}

function renderSubmitTab() {
  document.getElementById('tab-submit').innerHTML = `
    <div class="inspector">
      <div class="ins-head">
        <div>
          <span class="sec-label">内部人脉与新商机提报通道</span>
          <h2 class="ins-title">录入新市场方向并自动执行五维 AI 锐评与六维商业核算</h2>
        </div>
      </div>
      <div class="grid-2">
        <div><label class="field-lbl">1. 新项目方向名称 *</label><input id="fTitle" placeholder="例如：跨境独立站 TikTok 达人寄样自动催片工具"></div>
        <div><label class="field-lbl">2. 提报人 / 人脉来源 *</label><input id="fProposer" placeholder="例如：王总（深圳跨境卖家圈人脉）"></div>
        <div style="grid-column:span 2;"><label class="field-lbl">3. 产品一句话定义（输入什么 → 处理什么 → 产出什么）*</label><input id="fWhat" placeholder="例如：输入达人寄样单号，签收满3天自动发多语种消息催达人交挂车视频"></div>
        <div><label class="field-lbl">4. 目标客户与收费模式 *</label><input id="fBuyer" placeholder="例如：日寄样20+单的TK中小卖家，199元/月"></div>
        <div><label class="field-lbl">5. 首批客户获客渠道 *</label><input id="fChannel" placeholder="例如：深圳卖家微信群 + 小红书评论区截流"></div>
        <div><label class="field-lbl">6. 真实痛点与付费证据 *</label><input id="fEvidence" placeholder="例如：3家熟人卖家每月被白嫖样品亏上万，愿预付定金"></div>
        <div style="display:flex;gap:10px;">
          <div style="flex:1;"><label class="field-lbl">预计 MVP 工期</label><select id="fDays"><option value="5">3~7 天内</option><option value="12">1~2 周</option><option value="25">2 周以上</option></select></div>
          <div style="flex:1;"><label class="field-lbl">付费确定性</label><select id="fPaid"><option value="1">已确认愿付定金/已在付费</option><option value="0">仅口头意向</option></select></div>
        </div>
      </div>
      <div style="display:flex;gap:12px;align-items:center;">
        <button class="btn btn-primary" onclick="submitNewIdea()">计算评分并加入立项矩阵</button>
        <span id="submitMsg" style="color:var(--pos);font-size:13px;"></span>
      </div>
      <div id="cliBox" style="display:none;margin-top:16px;" class="card-cell">
        <span class="cell-k">永久同步至团队 GitHub 仓库的终端命令：</span>
        <code id="cliCmd" style="display:block;padding:10px;white-space:pre-wrap;word-break:break-all;"></code>
      </div>
    </div>
  `;
}

function submitNewIdea() {
  const title = document.getElementById('fTitle').value.trim();
  const proposer = document.getElementById('fProposer').value.trim() || '团队成员';
  const what = document.getElementById('fWhat').value.trim();
  const buyer = document.getElementById('fBuyer').value.trim() || '待定定价';
  const channel = document.getElementById('fChannel').value.trim() || '人脉私域';
  const evidence = document.getElementById('fEvidence').value.trim() || '人脉一线反馈';
  const days = parseInt(document.getElementById('fDays').value, 10);
  const paid = document.getElementById('fPaid').value === '1';
  if (!title || !what) { alert('请填写方向名称与产品定义'); return; }

  const sPay = paid ? 36 : 24;
  const sAcq = /(群|人脉|老客|小红书|闲鱼|评论)/.test(channel) ? 22 : 16;
  const sDel = days <= 7 ? 14 : (days <= 14 ? 11 : 7);
  const sComp = 8;
  const sVal = paid ? 9 : 6;
  const total = sPay + sAcq + sDel + sComp + sVal;

  const newObj = {
    code: 'TEAM-' + Date.now().toString().slice(-4),
    category_tag: `团队人脉提报 · ${proposer}`,
    title: `【人脉提报】${title}`,
    score: total,
    score_detail: `付费意愿 ${sPay}/40 · 获客截流 ${sAcq}/25 · 研发交付 ${sDel}/15 · 竞争缝隙 ${sComp}/10 · 48h测款 ${sVal}/10`,
    plain_what_to_do: what,
    workflow_steps: [`输入与痛点：${evidence}`, `处理逻辑：${days}天内基于现有脚本搭建最小闭环`, `交付变现：通过 ${channel} 按 ${buyer} 收款`],
    who_pays_and_price: buyer,
    ai_sharp_review: paid ? '人脉痛点明确且有付费意愿，重点验证能否从单点熟人复制至公域标准品。' : '当前仅口头意向，必须先收定金验证真伪。',
    plan_48h: `48小时内由 ${proposer} 向客户发去半自动样品 Demo 并收取 99~299 元测试定金。`,
    compounding: { tier: "A级复利 · 垂直SaaS沉淀", snowball: "从熟人定制切入，提炼通用行业规则后转为按月订阅制工具。", skill_gain: "沉淀垂直行业工作流与自动化交付能力。" },
    biz_eval: { cost: "初期成本 <100元", profit: `按 ${buyer} 测算，毛利率 90%+`, time: `MVP ${days} 天`, team: "1.5人", landing: "熟人首单验证 -> 半自动脚本 -> 标准化SaaS", compliance: "注意数据脱敏与平台合规" },
    evidence_ids: []
  };

  let local = [];
  try { local = JSON.parse(localStorage.getItem('mr_custom_ideas') || '[]'); } catch(e) {}
  local.unshift(newObj);
  localStorage.setItem('mr_custom_ideas', JSON.stringify(local));
  SELECTED_IDX = 0;
  renderProjects();
  document.getElementById('submitMsg').innerText = `已生成评估档案（得分 ${total}/100），已置顶加入 01 立项评估矩阵。`;
  document.getElementById('cliBox').style.display = 'block';
  document.getElementById('cliCmd').innerText =
    `python3 scripts/radar_cli.py submit-idea --title "${title}" --proposer "${proposer}" --what "${what}" --buyer "${buyer}" --evidence "${evidence}" --channel "${channel}" --mvp-days ${days}` + (paid ? '' : ' --unpaid') + ` && python3 scripts/sync_github.py`;
}

function renderWhitepaper() {
  const wp = DATA.whitepaper || {};
  const chHtml = (wp.channels || []).map(c => `
    <div class="card-cell" style="margin-bottom:12px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
        <strong style="color:var(--text);">${esc(c.name)}</strong>
        <span class="pill">${esc(c.type)}</span>
      </div>
      <div class="cell-v" style="margin-bottom:4px;"><strong style="color:var(--text-secondary);">采集量：</strong>${esc(c.count_info)}</div>
      <div class="cell-v" style="margin-bottom:4px;"><strong style="color:var(--text-secondary);">实现机制：</strong>${esc(c.how_it_works)}</div>
      <div class="cell-v" style="margin-bottom:4px;"><strong style="color:var(--text-secondary);">边界限制：</strong>${esc(c.limitations)}</div>
      <div class="cell-v"><strong style="color:var(--text-secondary);">扩展方式：</strong><code>${esc(c.how_to_extend)}</code></div>
    </div>
  `).join('');

  const guideHtml = (wp.csv_guides || []).map(g => `
    <div class="card-cell" style="margin-bottom:12px;">
      <span class="cell-k" style="color:var(--text);">${esc(g.platform)}</span>
      ${(g.steps || []).map(st => `<div class="cell-v" style="margin-bottom:4px;">${esc(st)}</div>`).join('')}
    </div>
  `).join('');

  document.getElementById('tab-whitepaper').innerHTML = `
    <div class="inspector">
      <span class="sec-label">数据采集透明说明</span>
      ${chHtml}
      <span class="sec-label" style="margin-top:24px;">外部平台自动化抓包与导表操作指南</span>
      ${guideHtml}
    </div>
  `;
}

function renderRoadmapAndArchive() {
  const wp = DATA.whitepaper || {};
  const rmHtml = (wp.roadmap || []).map(r => `
    <div class="card-cell" style="margin-bottom:12px;">
      <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
        <strong style="color:var(--text);">${esc(r.phase)} — ${esc(r.title)}</strong>
        <span class="pill">${esc(r.owner)}</span>
      </div>
      <div class="cell-v" style="white-space:pre-line;">${esc(r.details)}</div>
    </div>
  `).join('');

  const oldHtml = (DATA.existing_ideas || []).map(o => `
    <div class="card-cell" style="margin-bottom:12px;">
      <strong style="color:var(--text);display:block;margin-bottom:6px;">${esc(o.name)}</strong>
      <div class="cell-v" style="margin-bottom:4px;"><strong>原设想：</strong>${esc(o.original_plan)}</div>
      <div class="cell-v" style="margin-bottom:4px;"><strong>受阻原因：</strong>${esc(o.blocker)}</div>
      <div class="cell-v" style="margin-bottom:4px;"><strong>AI 锐评：</strong>${esc(o.ai_review)}</div>
      <div class="cell-v"><strong>改造方向：</strong>${esc(o.pivot_to)}</div>
    </div>
  `).join('');

  document.getElementById('tab-roadmap').innerHTML = `
    <div class="inspector">
      <span class="sec-label">系统演进 Roadmap（广谱发现 / 可信度分级 / 平台化与鉴权防攻击 / 合规护栏）</span>
      ${rmHtml}
      <span class="sec-label" style="margin-top:24px;">团队早期 4 个既有想法的复盘归档</span>
      ${oldHtml}
    </div>
  `;
}

function openSnap(id) {
  const s = SIG_MAP[id];
  if (!s) return;
  document.getElementById('mTitle').innerText = `证据 #${s.id} — ${cleanText(s.title)}`;
  document.getElementById('mMeta').innerText = `渠道：${cleanText(s.channel)} | 来源：${cleanText(s.author_or_app)} | 指标：${cleanText(s.metric_primary)} (${cleanText(s.metric_secondary)}) | 时间：${s.collected_at}`;
  document.getElementById('mBody').innerText = `[本地完整正文快照]\n${cleanText(s.content)}\n\n[分类与检索词]\n分类：${cleanText(s.category)} | 检索词：${cleanText(s.query_term)} | 价格/评分：${cleanText(s.rating_or_price)}\n标签：${cleanText(s.pain_tags || '有效信号')}`;
  document.getElementById('mLink').href = s.source_url || '#';
  document.getElementById('snapModal').style.display = 'flex';
}

function switchTab(id, btn) {
  ['tab-projects','tab-signals','tab-submit','tab-whitepaper','tab-roadmap'].forEach(t => {
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
  document.getElementById('kpiArchives').innerText = `${archs.length || 1}`;
  document.getElementById('lblBatches').innerText = archs.map(a => a.date).join(', ') || '2026-11-18';
  renderProjects();
  renderSignals();
  renderSubmitTab();
  renderWhitepaper();
  renderRoadmapAndArchive();
})();

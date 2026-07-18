import { useMemo, useState } from "react";
import {
  ArrowLeftIcon,
  ArrowRightIcon,
  ArrowsClockwiseIcon,
  CalendarBlankIcon,
  CaretDoubleLeftIcon,
  ChartLineUpIcon,
  CheckCircleIcon,
  ClipboardTextIcon,
  DatabaseIcon,
  ExportIcon,
  FileTextIcon,
  FunnelSimpleIcon,
  GearSixIcon,
  InfoIcon,
  LinkSimpleIcon,
  ListChecksIcon,
  MagnifyingGlassIcon,
  MicrophoneStageIcon,
  PackageIcon,
  SlidersHorizontalIcon,
  SparkleIcon,
  TagIcon,
  UserCircleIcon,
  UsersThreeIcon,
  WarningIcon,
  XIcon,
} from "@phosphor-icons/react";
import {
  consumerTaskChains,
  micEvidence,
  micMetrics,
  micSellingPoint,
  selectMicEvidence,
  selectTaskChainEvidence,
} from "./mic-analysis-data.js";

const navItems = [
  [UsersThreeIcon, "洞察工作台", true],
  [MagnifyingGlassIcon, "洞察探索"],
  [ListChecksIcon, "任务中心", false, "12"],
  [FileTextIcon, "文案任务"],
  [TagIcon, "标签管理"],
  [DatabaseIcon, "数据源"],
  [GearSixIcon, "设置"],
];

const roles = [
  ["all", "全部角色", UsersThreeIcon],
  ["operator", "亚马逊运营", UserCircleIcon],
  ["designer", "设计师", UserCircleIcon],
  ["product", "产品经理", UserCircleIcon],
];

const riskRows = [
  {
    id: "microphone-risk",
    priority: "P0",
    title: "麦克风连接不稳定",
    description: "连接、充电或延迟会破坏多人演唱任务。",
    evidence: "16 / 558",
    evidenceLabel: "真实复核 / 去重评论",
    outcome: "9条阻断或需恢复；5条明确退货或更换。",
    strength: "中",
    basis: "21条候选逐条复核，版本未知",
    owners: ["product", "operator", "designer"],
    ownerLabel: "产品经理 · 运营 · 设计",
    link: "microphone",
    realData: true,
  },
  {
    id: "tv-delay",
    priority: "P0",
    title: "电视连接音频延迟",
    description: "需额外设备，预期落空导致不满。",
    evidence: "14 / 100",
    evidenceLabel: "示意 / 电视连接音频",
    outcome: "需外接设备或回音壁才能获得更好音质，具体场景多。",
    strength: "强",
    basis: "内容/详情页描述明确",
    owners: ["product", "operator", "designer"],
    ownerLabel: "产品经理 · 内容/详情页",
  },
  {
    id: "setup-friction",
    priority: "P1",
    title: "首次使用设置阻力",
    description: "配对与充电不直观，影响初体验。",
    evidence: "12 / 100",
    evidenceLabel: "示意 / 首次使用问题",
    outcome: "找不到充电插口、不会配对，准备时间长，不同表达多。",
    strength: "中",
    basis: "用户体验场景分散",
    owners: ["product", "operator", "designer"],
    ownerLabel: "产品经理",
  },
  {
    id: "song-guide",
    priority: "P1",
    title: "缺少来宾引导",
    description: "来宾不知道如何使用，影响体验连贯性。",
    evidence: "9 / 100",
    evidenceLabel: "示意 / 来宾使用不清晰",
    outcome: "来宾不会操作，需要反复教学，打断娱乐氛围。",
    strength: "中",
    basis: "多用户提及，非核心问题",
    owners: ["operator", "designer"],
    ownerLabel: "亚马逊运营 · 内容/详情页",
  },
  {
    id: "battery-state",
    priority: "P2",
    title: "电量状态不清晰",
    description: "无法判断电量，导致中途断电。",
    evidence: "6 / 100",
    evidenceLabel: "示意 / 电量状态问题",
    outcome: "无法直观判断电量，担心中途断电，造成体验焦虑。",
    strength: "弱",
    basis: "提及较少，场景有限",
    owners: ["designer", "product"],
    ownerLabel: "设计师 · 产品经理",
  },
];

const opportunityRows = [
  {
    id: "dock-charge",
    priority: "P0",
    title: "双麦归位充电",
    description: "收纳盒即充电位，随取随用。",
    evidence: "11 / 100",
    evidenceLabel: "示意 / 双麦归位充电",
    outcome: "收纳盒即充电位，随取随用，减少准备压力。",
    strength: "强",
    basis: "高频正向提及，场景明确",
    owners: ["operator", "product"],
    ownerLabel: "亚马逊运营 · 产品经理",
    link: "microphone",
  },
  {
    id: "family-duet",
    priority: "P0",
    title: "家庭双人合唱价值",
    description: "双麦让家人与朋友不必等待，直接共同演唱。",
    evidence: "11 / 558",
    evidenceLabel: "真实复核 / 共同娱乐显性证据",
    outcome: "母女同唱、家庭娱乐、朋友聚会与二重唱均有原声证据。",
    strength: "中",
    basis: "16条候选逐条复核，11条成立",
    owners: ["operator", "designer"],
    ownerLabel: "亚马逊运营 · 内容/详情页",
    link: "microphone",
    realData: true,
  },
  {
    id: "instant-sing",
    priority: "P1",
    title: "来宾无需教学即可参与",
    description: "操作直观，来宾快速上手参与。",
    evidence: "8 / 100",
    evidenceLabel: "示意 / 来宾快速上手",
    outcome: "无需复杂设置，来宾也能快速参与，提升体验连贯性。",
    strength: "中",
    basis: "多场景正向提及，覆盖稳定",
    owners: ["operator"],
    ownerLabel: "亚马逊运营 · 用户体验",
  },
  {
    id: "connect-flexibility",
    priority: "P1",
    title: "轻松连接电视/音箱",
    description: "连接方式简单，使用更灵活。",
    evidence: "7 / 100",
    evidenceLabel: "示意 / 电视音箱连接便捷",
    outcome: "连接电视或蓝牙音箱都很简单，适配多种使用场景。",
    strength: "中",
    basis: "正向提及较多，表达分散",
    owners: ["product", "designer"],
    ownerLabel: "产品经理 · 内容/详情页",
  },
  {
    id: "sound-layer",
    priority: "P2",
    title: "音质清晰有层次",
    description: "声音清晰，演唱更有氛围感。",
    evidence: "6 / 100",
    evidenceLabel: "示意 / 音质表现优秀",
    outcome: "声音清晰、层次感好，提升演唱沉浸感与娱乐体验。",
    strength: "弱",
    basis: "正向提及较少，非主导主题",
    owners: ["designer"],
    ownerLabel: "设计师 · 内容/详情页",
  },
];

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand"><ChartLineUpIcon size={34} weight="duotone" /><div><strong>Review Insight</strong><span>Workbench</span></div></div>
      <nav aria-label="主导航">
        {navItems.map(([Icon, label, active, count]) => (
          <button className={`nav-item ${active ? "active" : ""}`} key={label} type="button">
            <Icon size={19} weight={active ? "duotone" : "regular"} /><span>{label}</span>{count && <em>{count}</em>}
          </button>
        ))}
      </nav>
      <button className="collapse-button" type="button"><CaretDoubleLeftIcon size={18} />收起侧栏</button>
    </aside>
  );
}

function ScopeBar({ onCoverage, coverageText = "麦克风主题已接入真实试点；其余主题仍为结构示意。评论版本无法可靠判断。" }) {
  return (
    <>
      <section className="scope-bar" aria-label="分析范围">
        <div><span>当前范围</span><b>自有 ASIN&nbsp; B0CR1R7FKP</b></div>
        <i />
        <div><span>🇺🇸</span><b>美国站（US）</b></div>
        <i />
        <div><span>时间范围</span><b>全量历史（评论截至 2026-07-08）</b></div>
        <i />
        <div><span>执行日期</span><b>2026-07-18</b></div>
        <button type="button" onClick={onCoverage}><SlidersHorizontalIcon size={17} />范围设置</button>
      </section>
      <button className="coverage-alert" type="button" onClick={onCoverage}>
        <WarningIcon size={20} weight="fill" />
        <span><b>数据覆盖：</b>{coverageText}</span>
        <em>查看数据覆盖详情 <ExportIcon size={15} /></em>
      </button>
    </>
  );
}

function RoleTabs({ role, setRole }) {
  return (
    <section className="role-tabs">
      <strong>角色视图</strong>
      <div role="tablist" aria-label="角色视图">
        {roles.map(([id, label, Icon]) => (
          <button key={id} role="tab" aria-selected={role === id} className={role === id ? "selected" : ""} type="button" onClick={() => setRole(id)}>
            <Icon size={18} />{label}
          </button>
        ))}
      </div>
      <span>切换角色将重新排序与高亮，但不改变洞察内容 <InfoIcon size={15} /></span>
    </section>
  );
}

const taskChainIcons = {
  role: UsersThreeIcon,
  scene: CalendarBlankIcon,
  job: MicrophoneStageIcon,
  motivation: PackageIcon,
  outcome: SparkleIcon,
  "unmet-need": WarningIcon,
};

function AnalysisStageNav({ active, onConsumer, onDiagnosis, onDecision }) {
  const stages = [
    ["consumer", "01", "消费者洞察", "谁、何时、为什么使用", UsersThreeIcon, onConsumer],
    ["diagnosis", "02", "体验诊断", "什么促进或阻碍任务", MagnifyingGlassIcon, onDiagnosis],
    ["decision", "03", "决策行动", "Listing与产品怎么改", ListChecksIcon, onDecision],
  ];
  return (
    <nav className="analysis-stage-nav" aria-label="评论分析阶段">
      {stages.map(([id, number, label, description, Icon, onClick]) => (
        <button key={id} className={active === id ? "selected" : ""} type="button" aria-current={active === id ? "page" : undefined} onClick={onClick}>
          <span>{number}</span><Icon size={20} weight={active === id ? "duotone" : "regular"} /><strong>{label}</strong><small>{description}</small>
        </button>
      ))}
    </nav>
  );
}

function ConsumerEvidenceModal({ node, rows, onClose }) {
  return (
    <div className="modal-backdrop evidence-modal-backdrop" role="presentation" onKeyDown={event => event.key === "Escape" && onClose()} onMouseDown={event => event.target === event.currentTarget && onClose()}>
      <section className="evidence-modal consumer-evidence-modal" role="dialog" aria-modal="true" aria-label={`${node.label}证据`}>
        <button autoFocus className="modal-close" type="button" aria-label="关闭" onClick={onClose}><XIcon size={20} /></button>
        <span className="modal-kicker">{node.evidenceMode} · {node.evidenceLabel}</span>
        <h2>{node.label}：{node.claim}</h2>
        <p>{node.boundary}</p>
        <EvidenceTable rows={rows} />
      </section>
    </div>
  );
}

function ConsumerOverview({ onCoverage, onDiagnosis, onDecision }) {
  const [activeChainId, setActiveChainId] = useState(consumerTaskChains[0].id);
  const [selectedNode, setSelectedNode] = useState(null);
  const activeChain = consumerTaskChains.find(chain => chain.id === activeChainId) || consumerTaskChains[0];
  const openNode = node => setSelectedNode({ node, rows: selectTaskChainEvidence(activeChain.id, node.id) });
  const openDiagnosis = () => {
    if (activeChain.id !== "family-shared-entertainment") {
      openNode(activeChain.nodes.find(node => node.id === "unmet-need"));
      return;
    }
    onDiagnosis();
  };
  return (
    <>
      <main className="main-content consumer-page">
        <header className="page-header">
          <div><h1>评论洞察工作台 <span>| 消费者理解总览</span> <InfoIcon size={17} /></h1><p>先理解谁在什么情况下想完成什么，再判断体验问题与行动优先级</p></div>
          <div className="date-meta">2026-07-18 <i /> 美国站 <i /> 全量历史分析 <CalendarBlankIcon size={18} /></div>
        </header>
        <AnalysisStageNav active="consumer" onConsumer={() => {}} onDiagnosis={onDiagnosis} onDecision={onDecision} />
        <ScopeBar onCoverage={onCoverage} coverageText="已完成家庭共同娱乐、礼物共享、聚会启动、跨场所移动与一体化升级五条真实任务链；证据数是保守下界，不是消费者占比，评论版本无法可靠判断。" />

        <section className="task-chain-tabs" aria-label="已验证消费者任务链">
          <div><span>当前洞察问题</span><strong>选择一条任务链查看六维证据</strong></div>
          <div role="tablist" aria-label="消费者任务链切换">
            {consumerTaskChains.map(chain => (
              <button key={chain.id} role="tab" aria-selected={activeChain.id === chain.id} className={activeChain.id === chain.id ? "selected" : ""} type="button" onClick={() => { setActiveChainId(chain.id); setSelectedNode(null); }}>
                <span>{chain.title}</span><small>{chain.validated}条人工确认</small>
              </button>
            ))}
          </div>
        </section>

        <section className="consumer-hero">
          <div>
            <span className="consumer-kicker">基于{activeChain.denominator}条历史评论 · {activeChain.validated}条人工确认显性证据（保守下界）</span>
            <h2>消费者不是一组标签，而是一条任务链</h2>
            <p>{activeChain.summary}</p>
          </div>
          <div className="consumer-scope-stats" aria-label="任务链证据范围">
            {activeChain.heroStats.map(stat => <div key={stat.label}><b>{stat.value}</b><span>{stat.label}</span></div>)}
          </div>
        </section>

        <section className="consumer-chain-section">
          <div className="section-heading">
            <div><span>01</span><h2>{activeChain.title}任务链</h2></div>
            <p>点击任一维度查看原文与译文；证据性质单独标注</p>
          </div>
          <div className="consumer-chain" role="group" aria-label={`${activeChain.title}六维任务链`}>
            {activeChain.nodes.map((node, index) => {
              const Icon = taskChainIcons[node.id];
              return (
                <button className={`chain-node ${node.id === "unmet-need" ? "risk-node" : ""}`} key={node.id} type="button" onClick={() => openNode(node)}>
                  <span className="chain-index">{String(index + 1).padStart(2, "0")}</span>
                  <Icon size={24} weight="duotone" />
                  <small>{node.label}</small>
                  <strong>{node.claim}</strong>
                  <span className="evidence-mode">{node.evidenceMode}</span>
                  <em>{node.evidenceLabel} <ArrowRightIcon size={13} /></em>
                </button>
              );
            })}
          </div>
          <p className="chain-scope-note"><InfoIcon size={16} />{activeChain.scopeNote}</p>
        </section>

        <section className="consumer-decision-section">
          <div className="section-heading">
            <div><span>02</span><h2>这条任务链如何进入后续决策</h2></div>
            <p>消费者理解、体验诊断与行动建议使用同一组评论证据</p>
          </div>
          <div className="decision-bridge-grid">
            <article><span>消费者价值</span><strong>{activeChain.bridge.valueTitle}</strong><p>{activeChain.bridge.valueBody}</p><small>{activeChain.bridge.valueEvidence}</small></article>
            <article className="bridge-risk"><span>体验诊断</span><strong>{activeChain.bridge.diagnosisTitle}</strong><p>{activeChain.bridge.diagnosisBody}</p><button type="button" onClick={openDiagnosis}>{activeChain.bridge.diagnosisAction} <ArrowRightIcon size={14} /></button></article>
            <article><span>决策行动</span><strong>{activeChain.bridge.actionTitle}</strong><p>{activeChain.bridge.actionBody}</p><button type="button" onClick={onDecision}>进入风险与机会 <ArrowRightIcon size={14} /></button></article>
          </div>
        </section>

        <section className="consumer-boundary">
          <div><WarningIcon size={20} weight="fill" /><span><b>当前不能回答</b>{activeChain.cannotAnswer}</span></div>
          <div><CheckCircleIcon size={20} weight="fill" /><span><b>当前可以回答</b>{activeChain.canAnswer}</span></div>
        </section>
        <footer className="data-footer"><span>数据来源：Lingxing 558条 · Sorftime交叉验证66条</span><span>执行日期：2026-07-18</span><ArrowsClockwiseIcon size={18} /></footer>
      </main>
      {selectedNode && <ConsumerEvidenceModal node={selectedNode.node} rows={selectedNode.rows} onClose={() => setSelectedNode(null)} />}
    </>
  );
}

function InsightRow({ item, activeRole, tone, onOpen }) {
  const matched = activeRole === "all" || item.owners.includes(activeRole);
  return (
    <article className={`insight-row ${matched ? "role-match" : "role-dim"}`}>
      <div className={`priority ${item.priority.toLowerCase()}`}>{item.priority}</div>
      <div className="insight-title"><strong>{item.title}</strong><span>{item.description}</span></div>
      <div className="evidence"><b>{item.evidence}</b><span>{item.evidenceLabel}</span></div>
      <div className="outcome">{item.outcome}</div>
      <div className="strength"><b>{item.strength}</b><span>{item.basis}</span></div>
      <div className="owners">{item.ownerLabel}</div>
      <button className={`open-insight ${tone}`} type="button" onClick={() => onOpen(item)}>查看洞察 <ArrowRightIcon size={15} /></button>
      {item.link && <span className="linked-theme"><LinkSimpleIcon size={14} />同一证据主题</span>}
    </article>
  );
}

function Lane({ title, subtitle, tone, icon: Icon, rows, role, onOpen }) {
  const ordered = useMemo(() => [...rows].sort((a, b) => {
    if (role === "all") return 0;
    return Number(b.owners.includes(role)) - Number(a.owners.includes(role));
  }), [rows, role]);
  return (
    <section className={`lane ${tone}`}>
      <header className="lane-header">
        <div className="lane-symbol"><Icon size={36} weight="duotone" /></div>
        <div><h2>{title}</h2><p>{subtitle}</p></div>
        <span>按影响与证据强度排序</span>
      </header>
      <div className="lane-columns"><span>优先级</span><span>洞察主题</span><span>证据量<br />（命中/总量）</span><span>消费者结果 / 价值</span><span>证据强度<br />（依据）</span><span>接收角色</span><span>操作</span></div>
      <div className="lane-rows">
        {ordered.map(item => <InsightRow key={item.id} item={item} activeRole={role} tone={tone} onOpen={onOpen} />)}
      </div>
      <footer>共 {rows.length} 条{title === "风险修正" ? "风险洞察" : "机会洞察"}（已按影响与证据强度排序）</footer>
    </section>
  );
}

function Overview({ onConsumer, onDetail }) {
  const [role, setRole] = useState("all");
  const [modal, setModal] = useState(null);
  const openInsight = item => item.id === "microphone-risk" || item.id === "family-duet" ? onDetail() : setModal({ type: "insight", item });
  return (
    <>
      <main className="main-content">
        <header className="page-header">
          <div><h1>评论洞察工作台 <span>| 决策行动</span> <InfoIcon size={17} /></h1><p>同一份评论证据，驱动两条决策路径：降低错误预期、退货与差评 ↔ 强化有证据的卖点与文案</p></div>
          <div className="date-meta">2026-07-18 <i /> 美国站 <i /> 全量历史分析 <CalendarBlankIcon size={18} /></div>
        </header>
        <AnalysisStageNav active="decision" onConsumer={onConsumer} onDiagnosis={onDetail} onDecision={() => {}} />
        <ScopeBar onCoverage={() => setModal({ type: "coverage" })} />
        <RoleTabs role={role} setRole={setRole} />
        <div className="lane-grid">
          <Lane title="风险修正" subtitle="降低错误预期、退货与差评风险" tone="risk" icon={WarningIcon} rows={riskRows} role={role} onOpen={openInsight} />
          <div className="bridge-stack" role="img" aria-label="五组洞察共享双轨证据主题">
            {["麦克风主题", "连接主题", "首次体验主题", "来宾使用主题", "音质与电量主题"].map(label => (
              <span className="bridge-dot" key={label} aria-hidden="true"><LinkSimpleIcon size={17} /></span>
            ))}
          </div>
          <Lane title="卖点强化" subtitle="放大正向体验，强化卖点与文案" tone="opportunity" icon={ChartLineUpIcon} rows={opportunityRows} role={role} onOpen={openInsight} />
        </div>
        <footer className="data-footer"><span>数据来源：Lingxing 558条 · Sorftime交叉验证66条</span><span>执行日期：2026-07-18</span><ArrowsClockwiseIcon size={18} /></footer>
      </main>
      {modal && <OverviewModal modal={modal} onClose={() => setModal(null)} />}
    </>
  );
}

function OverviewModal({ modal, onClose }) {
  return (
    <div className="modal-backdrop" role="presentation" onMouseDown={event => event.target === event.currentTarget && onClose()}>
      <section className="modal-card" role="dialog" aria-modal="true" aria-label={modal.type === "coverage" ? "数据覆盖详情" : "洞察说明"}>
        <button className="modal-close" type="button" aria-label="关闭" onClick={onClose}><XIcon size={20} /></button>
        {modal.type === "coverage" ? (
          <><span className="modal-kicker">数据覆盖</span><h2>当前试点使用严格子ASIN真实口径</h2><div className="coverage-grid"><div><b>严格评论分母</b><span>领星导出并按子ASIN确认558条历史评论，review_id无重复。</span></div><div><b>跨源校验</b><span>Sorftime 100条中有66条与领星目标评论匹配；其余不进入严格分母。</span></div><div><b>版本判断</b><span>评论没有可靠购买时版本字段；A版64GB与D版32GB均不强行归因。</span></div></div><p className="modal-note">消费者总览中的五条任务链均已接入人工复核评论；决策行动页仍保留部分示意主题，并继续明确标注。</p></>
        ) : (
          <><span className="modal-kicker">{modal.item.priority} · {modal.item.realData ? "真实洞察" : "示意洞察"}</span><h2>{modal.item.title}</h2><p className="modal-lead">{modal.item.outcome}</p><div className="coverage-grid"><div><b>证据量</b><span>{modal.item.evidence} · {modal.item.evidenceLabel}</span></div><div><b>证据强度</b><span>{modal.item.strength} · {modal.item.basis}</span></div><div><b>接收角色</b><span>{modal.item.ownerLabel}</span></div></div><p className="modal-note">{modal.item.realData ? "该洞察已接入真实评论证据。" : "该洞察尚未接入真实评论详情；当前只保留信息架构位置。"}</p></>
        )}
      </section>
    </div>
  );
}

function MetricCard({ value, label, note, onClick }) {
  return <button className="metric-card" type="button" onClick={onClick}><b>{value}</b><strong>{label}</strong><span>{note}</span><em>查看构成证据 <ArrowRightIcon size={14} /></em></button>;
}

function EvidenceTable({ rows }) {
  return (
    <div className="table-wrap">
      <table>
        <thead><tr><th>消费者表达</th><th>结果</th><th>用户评论原文</th><th>用户评论译文</th><th>星级</th><th>日期</th><th>来源</th><th>评论对象</th><th>版本判断</th></tr></thead>
        <tbody>{rows.map(row => <tr key={row.reviewId}>
          <td>{row.expression}</td><td className={row.sentiment}>{row.result}</td><td className="quote">{row.original}</td><td>{row.translation}</td><td>{row.rating}★</td><td>{row.date}</td><td>{row.source}</td><td>{row.object}</td><td>{row.version}</td>
        </tr>)}</tbody>
      </table>
    </div>
  );
}

function Detail({ onBack, backLabel, onConsumer, onDecision }) {
  const [evidenceModal, setEvidenceModal] = useState(null);
  const representativeEvidence = micEvidence.filter(row => row.representative);
  const filters = {
    all: selectMicEvidence("all"),
    blocking: selectMicEvidence("blocking"),
    commerce: selectMicEvidence("commerce"),
  };
  const openEvidence = (key, title) => setEvidenceModal({ title, rows: filters[key] });
  return (
    <main className="main-content detail-page">
      <button className="back-button" type="button" onClick={onBack}><ArrowLeftIcon size={17} />{backLabel}</button>
      <AnalysisStageNav active="diagnosis" onConsumer={onConsumer} onDiagnosis={() => {}} onDecision={onDecision} />
      <header className="detail-header"><div><span>产品可靠性 · P0</span><h1>麦克风问题会直接破坏多人娱乐任务</h1><p>双麦是家庭聚会和合唱任务的核心组成；单支失效、连接不稳或充电异常，即使主机可用也会让整次活动失败。</p></div><div className="severity"><WarningIcon size={23} weight="fill" />高严重度体验</div></header>
      <div className="sample-banner"><InfoIcon size={18} />真实试点口径：558条严格子ASIN历史评论；16条为人工确认的保守证据下界，不等于产品故障率；购买时版本均未知。</div>

      <section className="detail-section">
        <div className="section-heading"><div><span>01</span><h2>数据化证据</h2></div><p>21条规则候选逐条复核，确认16条；下方默认展示10条代表性证据</p></div>
        <div className="metric-grid">
          <MetricCard value={`${micMetrics.all.numerator} / ${micMetrics.all.denominator}`} label="已确认麦克风问题" note="人工复核证据 / 全部去重评论" onClick={() => openEvidence("all", "全部16条已确认麦克风问题证据")} />
          <MetricCard value={`${micMetrics.blocking.numerator} / ${micMetrics.blocking.denominator}`} label="任务阻断或需要恢复" note="无法唱、需重启/重置或进入售后" onClick={() => openEvidence("blocking", "9条任务阻断或需要恢复的证据")} />
          <MetricCard value={`${micMetrics.commerce.numerator} / ${micMetrics.commerce.denominator}`} label="明确退货或更换" note="退货3条；更换麦克风或整机2条" onClick={() => openEvidence("commerce", "5条明确退货或更换的证据")} />
        </div>
      </section>

      <section className="detail-section expression-section">
        <div className="section-heading"><div><span>02</span><h2>卖点提炼与文案表达</h2></div><p>同一组证据同时约束“能说什么”与“不能夸大什么”</p></div>
        <div className="expression-grid">
          <div><span>消费者价值</span><p>两支麦克风让母女、家人和朋友不必轮流等待，可以直接共同演唱。</p></div>
          <div><span>消费者原声</span><p className="english">“she even let her mom sing along” · “two microphones for duets” · “my family had a blast”</p></div>
          <div className="copy-block"><span>英文候选文案 · {micSellingPoint.validated}/{micSellingPoint.denominator}条显性证据</span><strong>{micSellingPoint.headline}</strong><span>辅助文案</span><p>{micSellingPoint.body}</p></div>
          <div className="boundary-block"><WarningIcon size={19} /><span><b>表达边界</b>共同娱乐价值有真实证据支持，但连接、充电和延迟存在反证；不得写 “always ready”“instant connection” 或 “lag-free”。</span></div>
        </div>
      </section>

      <section className="detail-section">
        <div className="section-heading"><div><span>03</span><h2>行动建议</h2></div><p>按接收角色分配，不把同一洞察复制成三份</p></div>
        <div className="action-grid">
          <div><b>亚马逊运营</b><strong>修正绝对承诺</strong><p>在当前D版延迟测试结果明确前，暂停使用绝对化的“Lag-Free”，并补充首次开机、更新后无声时的恢复入口。</p><small>Listing 只能管理预期与减少排查摩擦，不能替代产品改进。</small></div>
          <div><b>设计师</b><strong>双轨表达</strong><p>一张图放大“双麦共同参与”的卖点，另一张图给出充电、连接、重启或重置的简明排障路径。</p><small>指示灯、按键和步骤必须与当前D版实机一致。</small></div>
          <div><b>产品经理</b><strong>建立回归门槛</strong><p>覆盖冷启动、系统更新、连续取放、双麦并用、充电寿命和端到端人声延迟测试。</p><small>评论版本未知，历史趋势不能直接归因于D版改善。</small></div>
        </div>
      </section>

      <section className="detail-section evidence-section">
        <div className="section-heading"><div><span>04</span><h2>证据下钻</h2></div><p>10 条代表性证据 · 原文与译文并列 · 对象与版本判断分开</p></div>
        <EvidenceTable rows={representativeEvidence} />
      </section>
      {evidenceModal && <div className="modal-backdrop evidence-modal-backdrop" role="presentation" onKeyDown={event => event.key === "Escape" && setEvidenceModal(null)} onMouseDown={event => event.target === event.currentTarget && setEvidenceModal(null)}><section className="evidence-modal" role="dialog" aria-modal="true" aria-label={evidenceModal.title}><button autoFocus className="modal-close" type="button" aria-label="关闭" onClick={() => setEvidenceModal(null)}><XIcon size={20} /></button><span className="modal-kicker">证据构成</span><h2>{evidenceModal.title}</h2><p>点击指标后只过滤证据，不改变原始口径。</p><EvidenceTable rows={evidenceModal.rows} /></section></div>}
    </main>
  );
}

export function App() {
  const [view, setView] = useState("consumer");
  const [detailOrigin, setDetailOrigin] = useState("consumer");
  const openDetail = origin => {
    setDetailOrigin(origin);
    setView("detail");
  };
  return <div className="app-shell"><Sidebar />{
    view === "consumer"
      ? <ConsumerOverview onCoverage={() => setView("consumer-coverage")} onDiagnosis={() => openDetail("consumer")} onDecision={() => setView("decision")} />
      : view === "decision"
        ? <Overview onConsumer={() => setView("consumer")} onDetail={() => openDetail("decision")} />
        : view === "consumer-coverage"
          ? <><ConsumerOverview onCoverage={() => {}} onDiagnosis={() => openDetail("consumer")} onDecision={() => setView("decision")} /><OverviewModal modal={{ type: "coverage" }} onClose={() => setView("consumer")} /></>
          : <Detail onBack={() => setView(detailOrigin)} backLabel={detailOrigin === "decision" ? "返回决策行动" : "返回消费者洞察"} onConsumer={() => setView("consumer")} onDecision={() => setView("decision")} />
  }</div>;
}

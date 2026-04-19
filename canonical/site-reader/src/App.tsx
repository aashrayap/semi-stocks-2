import { useMemo, useState } from "react";
import { siteData, type Company, type GraphNode, type Signal } from "./data";

type View = "companies" | "signals" | "graph" | "reports";

const numberFormat = new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 });
const moneyFormat = new Intl.NumberFormat("en-US", {
  notation: "compact",
  maximumFractionDigits: 1,
  style: "currency",
  currency: "USD"
});

const signalKindLabels: Record<string, string> = {
  company_thesis_signal: "Company",
  semianalysis_signal: "SemiAnalysis",
  thesis_stage_signal: "Thesis",
  thesis_proposal_signal: "Proposal"
};

export function App() {
  const [view, setView] = useState<View>("companies");
  const [query, setQuery] = useState("");
  const [bottleneck, setBottleneck] = useState("all");
  const [signalKind, setSignalKind] = useState("all");
  const [direction, setDirection] = useState("all");
  const [selectedTicker, setSelectedTicker] = useState(
    siteData.companies.find((company) => company.ticker === "NVDA")?.ticker ||
      siteData.companies[0]?.ticker ||
      ""
  );

  const bottlenecks = useMemo(() => {
    const values = new Set<string>();
    siteData.companies.forEach((company) => company.bottleneck && values.add(company.bottleneck));
    siteData.signals.forEach((signal) => signal.bottleneck && values.add(signal.bottleneck));
    siteData.thesis.cascade.forEach((stage) => stage.name && values.add(stage.name));
    return [...values].sort();
  }, []);

  const selectedCompany = useMemo(
    () => siteData.companies.find((company) => company.ticker === selectedTicker) || siteData.companies[0],
    [selectedTicker]
  );

  const filteredCompanies = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return siteData.companies.filter((company) => {
      const matchesQuery =
        !needle ||
        company.ticker.toLowerCase().includes(needle) ||
        company.name.toLowerCase().includes(needle) ||
        (company.bottleneck || "").toLowerCase().includes(needle);
      const matchesBottleneck = matchesBottleneckFilter(company.bottleneck, bottleneck);
      return matchesQuery && matchesBottleneck;
    });
  }, [bottleneck, query]);

  const filteredSignals = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return siteData.signals.filter((signal) => {
      const tickers = [signal.ticker, ...(signal.tickers || [])].filter(Boolean).join(" ");
      const matchesQuery =
        !needle ||
        signal.evidence.toLowerCase().includes(needle) ||
        (signal.title || "").toLowerCase().includes(needle) ||
        tickers.toLowerCase().includes(needle);
      const matchesBottleneck = matchesBottleneckFilter(signal.bottleneck, bottleneck);
      const matchesKind = signalKind === "all" || signal.kind === signalKind;
      const matchesDirection = direction === "all" || signal.direction === direction;
      return matchesQuery && matchesBottleneck && matchesKind && matchesDirection;
    });
  }, [bottleneck, direction, query, signalKind]);

  const selectedSignals = useMemo(() => signalsForTicker(selectedTicker), [selectedTicker]);
  const selectedClaims = useMemo(
    () => siteData.claims.filter((claim) => claim.ticker === selectedTicker),
    [selectedTicker]
  );
  const filteredSignalsCount = filteredSignals.length;

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">semi-stocks</p>
          <h1>Site Data Reader</h1>
        </div>
        <div className="build-meta">
          <span>{siteData.build.generator}</span>
          <span>{siteData.build.artifact_counts.companies} companies</span>
          <span>{siteData.build.artifact_counts.signals} signals</span>
        </div>
      </header>

      <section className="toolbar" aria-label="Reader filters">
        <div className="view-tabs" role="tablist" aria-label="Views">
          {(["companies", "signals", "graph", "reports"] as View[]).map((item) => (
            <button
              className={view === item ? "active" : ""}
              key={item}
              onClick={() => setView(item)}
              role="tab"
              type="button"
            >
              {title(item)}
            </button>
          ))}
        </div>
        <label>
          <span>Search</span>
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Ticker, source, signal" />
        </label>
        <label>
          <span>Bottleneck</span>
          <select value={bottleneck} onChange={(event) => setBottleneck(event.target.value)}>
            <option value="all">All</option>
            {bottlenecks.map((item) => (
              <option key={item} value={item}>
                {title(item)}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Signal</span>
          <select value={signalKind} onChange={(event) => setSignalKind(event.target.value)}>
            <option value="all">All</option>
            {[...new Set(siteData.signals.map((signal) => signal.kind))].sort().map((item) => (
              <option key={item} value={item}>
                {signalKindLabels[item] || title(item)}
              </option>
            ))}
          </select>
        </label>
        <label>
          <span>Direction</span>
          <select value={direction} onChange={(event) => setDirection(event.target.value)}>
            <option value="all">All</option>
            {[...new Set(siteData.signals.map((signal) => signal.direction).filter(Boolean))].sort().map((item) => (
              <option key={item} value={item}>
                {title(item || "")}
              </option>
            ))}
          </select>
        </label>
      </section>

      <section className="stats-grid" aria-label="Site data counts">
        <Stat label="Companies" value={siteData.companies.length} />
        <Stat label="Signals" value={filteredSignalsCount} />
        <Stat label="Claims" value={siteData.claims.length} />
        <Stat label="Edges" value={siteData.edges.length} />
        <Stat label="Report sections" value={siteData.reports[0]?.sections.length || 0} />
      </section>

      <section className="workspace">
        <div className="primary-pane">
          {view === "companies" && (
            <CompanyTable
              companies={filteredCompanies}
              selectedTicker={selectedTicker}
              onSelect={setSelectedTicker}
            />
          )}
          {view === "signals" && <SignalTable signals={filteredSignals} onSelectTicker={setSelectedTicker} />}
          {view === "graph" && <GraphPanel selectedTicker={selectedTicker} onSelectTicker={setSelectedTicker} />}
          {view === "reports" && <ReportsPanel />}
        </div>
        <CompanyDetail company={selectedCompany} claims={selectedClaims} signals={selectedSignals} />
      </section>
    </main>
  );
}

function CompanyTable({
  companies,
  selectedTicker,
  onSelect
}: {
  companies: Company[];
  selectedTicker: string;
  onSelect: (ticker: string) => void;
}) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Company</th>
            <th>Bottleneck</th>
            <th>Signals</th>
            <th>Claims</th>
            <th>Next</th>
          </tr>
        </thead>
        <tbody>
          {companies.map((company) => (
            <tr
              className={company.ticker === selectedTicker ? "selected" : ""}
              key={company.id}
              onClick={() => onSelect(company.ticker)}
            >
              <td className="ticker">{company.ticker}</td>
              <td>{company.name}</td>
              <td>{title(company.bottleneck || "unmapped")}</td>
              <td>{(company.signal_counts?.confirms || 0) + (company.signal_counts?.contradicts || 0) + (company.signal_counts?.semi || 0)}</td>
              <td>{company.claim_counts?.pending || 0} pending</td>
              <td>{company.next_earnings || "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SignalTable({
  signals,
  onSelectTicker
}: {
  signals: Signal[];
  onSelectTicker: (ticker: string) => void;
}) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Source</th>
            <th>Ticker</th>
            <th>Bottleneck</th>
            <th>Direction</th>
            <th>Evidence</th>
          </tr>
        </thead>
        <tbody>
          {signals.map((signal) => {
            const ticker = signal.ticker || signal.tickers?.[0] || "";
            return (
              <tr key={signal.id} onClick={() => ticker && onSelectTicker(ticker)}>
                <td>{signalKindLabels[signal.kind] || title(signal.kind)}</td>
                <td className="ticker">{ticker || "—"}</td>
                <td>{title(signal.bottleneck || "unmapped")}</td>
                <td>{title(signal.direction || "signal")}</td>
                <td className="evidence">{signal.evidence}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function GraphPanel({
  selectedTicker,
  onSelectTicker
}: {
  selectedTicker: string;
  onSelectTicker: (ticker: string) => void;
}) {
  const visible = useMemo(() => graphForTicker(selectedTicker), [selectedTicker]);
  const width = 920;
  const height = 560;
  const positioned = positionNodes(visible.nodes, width, height);

  return (
    <div className="graph-panel">
      <div className="graph-header">
        <strong>{selectedTicker} relationship graph</strong>
        <span>{visible.nodes.length} nodes / {visible.links.length} links</span>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Filtered site-data graph">
        {visible.links.map((link) => {
          const source = positioned.get(link.source);
          const target = positioned.get(link.target);
          if (!source || !target) return null;
          return (
            <line
              className={`edge edge-${link.type}`}
              key={`${link.source}-${link.target}-${link.type}`}
              x1={source.x}
              x2={target.x}
              y1={source.y}
              y2={target.y}
            />
          );
        })}
        {[...positioned.values()].map((node) => {
          const ticker = node.id.startsWith("company:") ? node.id.split(":")[1] : "";
          return (
            <g key={node.id} onClick={() => ticker && onSelectTicker(ticker)}>
              <circle className={`node node-${node.type.replace(/[:_]/g, "-")}`} cx={node.x} cy={node.y} r={node.r} />
              <text x={node.x} y={node.y + node.r + 15}>{shortLabel(node.label)}</text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

function ReportsPanel() {
  const report = siteData.reports[0];
  return (
    <div className="report-sections">
      {report.sections.map((section) => (
        <section className="section-block" key={section.id}>
          <div className="section-heading">
            <h2>{section.title}</h2>
            <span>{section.kind}</span>
          </div>
          {section.body_html && <p>{plainTextFromHtml(section.body_html)}</p>}
          {section.rows && (
            <p className="muted">{section.rows.length} structured rows available in reports.json.</p>
          )}
        </section>
      ))}
    </div>
  );
}

function CompanyDetail({
  company,
  claims,
  signals
}: {
  company?: Company;
  claims: Array<{ id: string; claim: string; status: string; verify_at?: string }>;
  signals: Signal[];
}) {
  if (!company) return null;
  const exposure = company.positions?.reduce((sum, position) => sum + (position.value || 0), 0) || 0;

  return (
    <aside className="detail-pane">
      <div className="detail-heading">
        <div>
          <p className="eyebrow">Selected company</p>
          <h2>{company.ticker}</h2>
        </div>
        <span className="status-pill">{company.status || "unmapped"}</span>
      </div>
      <h3>{company.name}</h3>
      <p>{company.thesis?.why_now || company.thesis?.bottleneck_role || "No thesis note yet."}</p>
      <div className="detail-metrics">
        <Stat label="Exposure" value={exposure ? moneyFormat.format(exposure) : "—"} />
        <Stat label="Signals" value={signals.length} />
        <Stat label="Claims" value={claims.length} />
      </div>
      <section>
        <h4>Positions</h4>
        {(company.positions || []).slice(0, 4).map((position) => (
          <div className="compact-row" key={`${position.source}-${position.type}`}>
            <strong>{title(position.source)}</strong>
            <span>{position.value ? moneyFormat.format(position.value) : "—"} / {position.type || "common"}</span>
          </div>
        ))}
      </section>
      <section>
        <h4>Signals</h4>
        {signals.slice(0, 5).map((signal) => (
          <p className="detail-item" key={signal.id}>{signal.evidence}</p>
        ))}
      </section>
      <section>
        <h4>Claims</h4>
        {claims.slice(0, 4).map((claim) => (
          <p className="detail-item" key={claim.id}>
            <strong>{title(claim.status)}</strong> {claim.claim}
          </p>
        ))}
      </section>
    </aside>
  );
}

function Stat({ label, value }: { label: string; value: number | string }) {
  const display = typeof value === "number" ? numberFormat.format(value) : value;
  return (
    <div className="stat">
      <span>{label}</span>
      <strong>{display}</strong>
    </div>
  );
}

function signalsForTicker(ticker: string) {
  return siteData.signals.filter((signal) => {
    const tickers = [signal.ticker, ...(signal.tickers || [])].filter(Boolean);
    return tickers.includes(ticker);
  });
}

function graphForTicker(ticker: string) {
  const companyId = `company:${ticker}`;
  const related = new Set([companyId]);
  siteData.graph.links.forEach((link) => {
    if (link.source === companyId) related.add(link.target);
    if (link.target === companyId) related.add(link.source);
  });
  siteData.graph.links.forEach((link) => {
    if (related.has(link.source) || related.has(link.target)) {
      related.add(link.source);
      related.add(link.target);
    }
  });
  const nodes = siteData.graph.nodes.filter((node) => related.has(node.id)).slice(0, 44);
  const nodeIds = new Set(nodes.map((node) => node.id));
  const links = siteData.graph.links.filter((link) => nodeIds.has(link.source) && nodeIds.has(link.target)).slice(0, 90);
  return { nodes, links };
}

function positionNodes(nodes: GraphNode[], width: number, height: number) {
  const centerX = width / 2;
  const centerY = height / 2;
  const radius = Math.min(width, height) * 0.36;
  const positioned = new Map<string, GraphNode & { x: number; y: number; r: number }>();
  nodes.forEach((node, index) => {
    const angle = (Math.PI * 2 * index) / Math.max(nodes.length, 1) - Math.PI / 2;
    const nodeRadius = Math.max(7, Math.min(18, 6 + (node.val || 1)));
    const isCompany = node.id.startsWith("company:");
    positioned.set(node.id, {
      ...node,
      x: isCompany ? centerX : centerX + Math.cos(angle) * radius,
      y: isCompany ? centerY : centerY + Math.sin(angle) * radius,
      r: isCompany ? 22 : nodeRadius
    });
  });
  return positioned;
}

function title(value: string) {
  return value.replace(/[_-]/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function slug(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

function matchesBottleneckFilter(value: string | undefined, selected: string) {
  if (selected === "all") return true;
  if (!value) return false;
  const valueSlug = slug(value);
  const selectedSlug = slug(selected);
  return (
    value === selected ||
    valueSlug === selectedSlug ||
    selectedSlug.includes(valueSlug) ||
    valueSlug.includes(selectedSlug)
  );
}

function plainTextFromHtml(value: string) {
  return value.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();
}

function shortLabel(value: string) {
  return value.length > 18 ? `${value.slice(0, 15)}...` : value;
}

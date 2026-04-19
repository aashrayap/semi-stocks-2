import { useMemo, useState } from "react";
import { siteData, type Claim, type Company, type Signal, type ThesisStage } from "./data";

type View = "categories" | "companies" | "signals";

type Category = {
  id: string;
  key: string;
  label: string;
  status?: string;
  period?: string;
  cyclePhase?: string;
  tickers: string[];
  thesisSignals: string[];
  companies: Company[];
  signals: Signal[];
  claims: Claim[];
  reviewCount: number;
  predictionCount: number;
};

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

const categoryAliases: Record<string, string> = {
  copper_signal_integrity: "co-packaged-optics-cpo-scale-up",
  cpo_next: "co-packaged-optics-cpo-scale-up",
  euv: "euv-tools",
  memory: "memory-supercycle",
  n3_logic: "n3-logic-wafers",
  optical: "pluggable-optics-scale-out",
  pluggable_optics: "pluggable-optics-scale-out",
  power: "power-dc-buildout"
};

export function App() {
  const categories = useMemo(() => buildCategories(), []);
  const [view, setView] = useState<View>("categories");
  const [query, setQuery] = useState("");
  const [categoryKey, setCategoryKey] = useState("all");
  const [signalKind, setSignalKind] = useState("all");
  const [direction, setDirection] = useState("all");
  const [selectedTicker, setSelectedTicker] = useState(
    siteData.companies.find((company) => company.ticker === "NVDA")?.ticker ||
      siteData.companies[0]?.ticker ||
      ""
  );

  const selectedCategory = useMemo(
    () => categories.find((category) => category.key === categoryKey),
    [categories, categoryKey]
  );
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
        (company.bottleneck || "").toLowerCase().includes(needle) ||
        (company.thesis?.why_now || "").toLowerCase().includes(needle);
      const matchesCategory = categoryKey === "all" || selectedCategory?.companies.some((item) => item.id === company.id);
      return matchesQuery && matchesCategory;
    });
  }, [categoryKey, query, selectedCategory]);

  const filteredSignals = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return siteData.signals.filter((signal) => {
      const tickers = [signal.ticker, ...(signal.tickers || [])].filter(Boolean).join(" ");
      const matchesQuery =
        !needle ||
        signal.evidence.toLowerCase().includes(needle) ||
        (signal.title || "").toLowerCase().includes(needle) ||
        tickers.toLowerCase().includes(needle) ||
        (signal.bottleneck || "").toLowerCase().includes(needle);
      const matchesCategory = categoryKey === "all" || selectedCategory?.signals.some((item) => item.id === signal.id);
      const matchesKind = signalKind === "all" || signal.kind === signalKind;
      const matchesDirection = direction === "all" || signal.direction === direction;
      return matchesQuery && matchesCategory && matchesKind && matchesDirection;
    });
  }, [categoryKey, direction, query, selectedCategory, signalKind]);

  const filteredCategories = useMemo(() => {
    const needle = query.trim().toLowerCase();
    return categories.filter((category) => {
      const matchesQuery =
        !needle ||
        category.label.toLowerCase().includes(needle) ||
        category.tickers.join(" ").toLowerCase().includes(needle) ||
        category.thesisSignals.join(" ").toLowerCase().includes(needle);
      return matchesQuery;
    });
  }, [categories, query]);

  const selectedSignals = useMemo(() => signalsForTicker(selectedTicker), [selectedTicker]);
  const selectedClaims = useMemo(
    () => siteData.claims.filter((claim) => claim.ticker === selectedTicker),
    [selectedTicker]
  );

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">semi-stocks</p>
          <h1>Signal Desk</h1>
        </div>
        <div className="build-meta">
          <span>{siteData.build.generator}</span>
          <span>{siteData.build.artifact_counts.companies} companies</span>
          <span>{siteData.build.artifact_counts.signals} signals</span>
        </div>
      </header>

      <section className="toolbar" aria-label="Reader filters">
        <div className="view-tabs" role="tablist" aria-label="Views">
          {(["categories", "companies", "signals"] as View[]).map((item) => (
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
          <input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Ticker, category, signal" />
        </label>
        <label>
          <span>Category</span>
          <select value={categoryKey} onChange={(event) => setCategoryKey(event.target.value)}>
            <option value="all">All</option>
            {categories.map((category) => (
              <option key={category.key} value={category.key}>
                {category.label}
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
        <Stat label="Categories" value={categories.length} />
        <Stat label="Companies" value={filteredCompanies.length} />
        <Stat label="Signals" value={filteredSignals.length} />
        <Stat label="Reviews" value={sumCategories(categories, "reviewCount")} />
        <Stat label="Predictions" value={sumCategories(categories, "predictionCount")} />
      </section>

      <section className="workspace">
        <div className="primary-pane">
          {view === "categories" && (
            <CategoryTable
              categories={filteredCategories}
              selectedKey={categoryKey}
              onSelectCategory={setCategoryKey}
              onSelectTicker={setSelectedTicker}
            />
          )}
          {view === "companies" && (
            <CompanyTable
              companies={filteredCompanies}
              selectedTicker={selectedTicker}
              onSelect={setSelectedTicker}
            />
          )}
          {view === "signals" && <SignalTable signals={filteredSignals} onSelectTicker={setSelectedTicker} />}
        </div>
        <InsightDetail
          category={selectedCategory}
          company={selectedCompany}
          claims={selectedClaims}
          signals={selectedSignals}
        />
      </section>
    </main>
  );
}

function CategoryTable({
  categories,
  selectedKey,
  onSelectCategory,
  onSelectTicker
}: {
  categories: Category[];
  selectedKey: string;
  onSelectCategory: (key: string) => void;
  onSelectTicker: (ticker: string) => void;
}) {
  const companyTickers = new Set(siteData.companies.map((company) => company.ticker));

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Category</th>
            <th>Status</th>
            <th>Companies</th>
            <th>Signals</th>
            <th>Reviews</th>
            <th>Predictions</th>
            <th>Tickers</th>
          </tr>
        </thead>
        <tbody>
          {categories.map((category) => (
            <tr
              className={category.key === selectedKey ? "selected" : ""}
              key={category.id}
              onClick={() => onSelectCategory(category.key)}
            >
              <td>
                <strong>{category.label}</strong>
                <span className="subtext">{category.period || category.cyclePhase || "mapped category"}</span>
              </td>
              <td>{title(category.status || "unmapped")}</td>
              <td>{category.companies.length}</td>
              <td>{category.signals.length}</td>
              <td>{category.reviewCount}</td>
              <td>{category.predictionCount}</td>
              <td>
                <div className="ticker-strip">
                  {category.tickers.slice(0, 8).map((ticker) => (
                    <button
                      disabled={!companyTickers.has(ticker)}
                      key={ticker}
                      onClick={(event) => {
                        event.stopPropagation();
                        if (companyTickers.has(ticker)) onSelectTicker(ticker);
                      }}
                      type="button"
                    >
                      {ticker}
                    </button>
                  ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
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
            <th>Category</th>
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
              <td>
                {(company.signal_counts?.confirms || 0) +
                  (company.signal_counts?.contradicts || 0) +
                  (company.signal_counts?.semi || 0)}
              </td>
              <td>{company.claim_counts?.pending || 0} pending</td>
              <td>{company.next_earnings || "-"}</td>
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
            <th>Category</th>
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
                <td className="ticker">{ticker || "-"}</td>
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

function InsightDetail({
  category,
  company,
  claims,
  signals
}: {
  category?: Category;
  company?: Company;
  claims: Claim[];
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
        <Stat label="Exposure" value={exposure ? moneyFormat.format(exposure) : "-"} />
        <Stat label="Signals" value={signals.length} />
        <Stat label="Claims" value={claims.length} />
      </div>
      {category && (
        <section>
          <h4>{category.label}</h4>
          <div className="compact-row">
            <strong>Status</strong>
            <span>{title(category.status || "unmapped")}</span>
          </div>
          <div className="compact-row">
            <strong>Flow</strong>
            <span>{category.reviewCount} reviews / {category.predictionCount} predictions</span>
          </div>
          {category.thesisSignals.slice(0, 3).map((signal) => (
            <p className="detail-item" key={signal}>{signal}</p>
          ))}
        </section>
      )}
      <section>
        <h4>Positions</h4>
        {(company.positions || []).slice(0, 4).map((position) => (
          <div className="compact-row" key={`${position.source}-${position.type}`}>
            <strong>{title(position.source)}</strong>
            <span>{position.value ? moneyFormat.format(position.value) : "-"} / {position.type || "common"}</span>
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

function buildCategories() {
  const categories = new Map<string, Category>();

  const put = (stage: Partial<ThesisStage> & { name: string }) => {
    const key = categoryKey(stage.name);
    if (!categories.has(key)) {
      categories.set(key, {
        id: `category:${key}`,
        key,
        label: stage.name,
        status: stage.status,
        period: stage.period,
        cyclePhase: stage.cycle_phase,
        tickers: dedupe(stage.tickers || []),
        thesisSignals: stage.signals || [],
        companies: [],
        signals: [],
        claims: [],
        reviewCount: 0,
        predictionCount: 0
      });
    }
    return categories.get(key)!;
  };

  siteData.thesis.cascade.forEach((stage) => put(stage));

  siteData.companies.forEach((company) => {
    const category = findCategoryForValue(categories, company.bottleneck) || put({ name: company.bottleneck || "Unmapped" });
    category.companies = pushUnique(category.companies, company, (item) => item.id);
    category.tickers = dedupe([...category.tickers, company.ticker]);
  });

  siteData.signals.forEach((signal) => {
    const category = findCategoryForValue(categories, signal.bottleneck) || put({ name: signal.bottleneck || "Unmapped" });
    category.signals = pushUnique(category.signals, signal, (item) => item.id);
    const tickers = [signal.ticker, ...(signal.tickers || [])].filter(Boolean) as string[];
    category.tickers = dedupe([...category.tickers, ...tickers]);
  });

  siteData.claims.forEach((claim) => {
    const company = siteData.companies.find((item) => item.ticker === claim.ticker);
    const category = findCategoryForValue(categories, company?.bottleneck) || categories.get("unmapped");
    if (category) category.claims = pushUnique(category.claims, claim, (item) => item.id);
  });

  return [...categories.values()]
    .map((category) => ({
      ...category,
      companies: category.companies.sort((a, b) => a.ticker.localeCompare(b.ticker)),
      signals: category.signals.sort((a, b) => a.id.localeCompare(b.id)),
      claims: category.claims.sort((a, b) => a.id.localeCompare(b.id)),
      tickers: dedupe(category.tickers).sort(),
      reviewCount: category.signals.filter((signal) => signal.kind !== "thesis_proposal_signal").length,
      predictionCount:
        category.claims.length +
        category.signals.filter((signal) => signal.kind === "thesis_proposal_signal" || signal.direction === "proposed").length
    }))
    .sort((a, b) => categorySort(a) - categorySort(b) || a.label.localeCompare(b.label));
}

function findCategoryForValue(categories: Map<string, Category>, value?: string) {
  if (!value) return undefined;
  const direct = categories.get(categoryKey(value));
  if (direct) return direct;
  return [...categories.values()].find((category) => matchesCategory(value, category.label) || matchesCategory(value, category.key));
}

function categorySort(category: Category) {
  const statusOrder: Record<string, number> = { active: 0, next: 1, played_out: 2, unmapped: 3 };
  return statusOrder[category.status || "unmapped"] ?? 4;
}

function sumCategories(categories: Category[], key: "reviewCount" | "predictionCount") {
  return categories.reduce((sum, category) => sum + category[key], 0);
}

function signalsForTicker(ticker: string) {
  return siteData.signals.filter((signal) => {
    const tickers = [signal.ticker, ...(signal.tickers || [])].filter(Boolean);
    return tickers.includes(ticker);
  });
}

function pushUnique<T>(items: T[], next: T, idFor: (item: T) => string) {
  return items.some((item) => idFor(item) === idFor(next)) ? items : [...items, next];
}

function dedupe(values: string[]) {
  return [...new Set(values.filter(Boolean))];
}

function title(value: string) {
  return value.replace(/[_-]/g, " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function slug(value: string) {
  return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

function categoryKey(value: string) {
  const key = slug(value || "unmapped");
  return categoryAliases[key.replace(/-/g, "_")] || categoryAliases[key] || key;
}

function matchesCategory(value: string | undefined, selected: string) {
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

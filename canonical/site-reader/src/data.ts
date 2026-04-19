import build from "../../site-data/build.json";
import claims from "../../site-data/claims.json";
import companies from "../../site-data/companies.json";
import edges from "../../site-data/edges.json";
import graph from "../../site-data/graph.json";
import reports from "../../site-data/reports.json";
import search from "../../site-data/search.json";
import signals from "../../site-data/signals.json";
import thesis from "../../site-data/thesis.json";

export type Company = {
  id: string;
  ticker: string;
  name: string;
  bottleneck?: string;
  status?: string;
  next_earnings?: string;
  source_page?: string;
  positions?: Array<{
    source: string;
    value?: number;
    pct_portfolio?: number;
    type?: string;
    change_vs_prior?: string;
    notes?: string;
  }>;
  signal_counts?: {
    confirms?: number;
    contradicts?: number;
    semi?: number;
  };
  claim_counts?: {
    pending?: number;
    confirmed?: number;
    missed?: number;
    due_next?: number;
  };
  metrics?: {
    quarter?: string;
    revenue_label?: string;
    revenue_value?: number | string;
    margin_label?: string;
    margin_value?: number | string;
    guidance_period?: string;
  };
  thesis?: {
    bottleneck_role?: string;
    why_now?: string;
    confirms_next?: string[];
    break_conditions?: string[];
  };
};

export type Signal = {
  id: string;
  kind: string;
  ticker?: string;
  tickers?: string[];
  title?: string;
  date?: string;
  bottleneck?: string;
  bottleneck_id?: string;
  direction?: string;
  evidence: string;
  source?: string;
  source_page?: string;
  source_path?: string;
};

export type Edge = {
  id: string;
  type: string;
  source: string;
  target: string;
  ticker?: string;
};

export type Claim = {
  id: string;
  ticker: string;
  claim: string;
  status: string;
  verify_at?: string;
  source_page?: string;
};

export type Report = {
  id: string;
  title: string;
  path: string;
  sections: Array<{
    id: string;
    title: string;
    kind: string;
    body_html?: string;
    rows?: unknown[];
  }>;
};

export type GraphNode = {
  id: string;
  label: string;
  type: string;
  val?: number;
};

export type GraphLink = {
  source: string;
  target: string;
  type: string;
};

export type ThesisStage = {
  id: string;
  name: string;
  status?: string;
  period?: string;
  cycle_phase?: string;
  tickers?: string[];
  signals?: string[];
};

export const siteData = {
  build,
  claims: claims as Claim[],
  companies: companies as Company[],
  edges: edges as Edge[],
  graph: graph as { nodes: GraphNode[]; links: GraphLink[] },
  reports: reports as Report[],
  search,
  signals: signals as Signal[],
  thesis: thesis as { cascade: ThesisStage[] }
};

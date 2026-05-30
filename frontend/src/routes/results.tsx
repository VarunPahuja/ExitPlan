import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { Share2, ArrowRight, Sparkles, SlidersHorizontal } from "lucide-react";
import { toast } from "sonner";
import { Disclaimer } from "@/components/Disclaimer";

export const Route = createFileRoute("/results")({
  component: Results,
});

const INDIGO = "#5B4FE8";
const ORANGE = "#FF6B35";

const FLAGS: Record<string, string> = {
  GB: "🇬🇧", CA: "🇨🇦", DE: "🇩🇪", AU: "🇦🇺", NL: "🇳🇱",
  PT: "🇵🇹", IE: "🇮🇪", AE: "🇦🇪", NZ: "🇳🇿", SG: "🇸🇬",
};

const FACTOR_LABELS: { key: string; label: string }[] = [
  { key: "job_market", label: "Job Market" },
  { key: "pr_timeline", label: "PR Timeline" },
  { key: "visa_ease", label: "Visa Ease" },
  { key: "salary_cost_ratio", label: "Salary vs Cost" },
  { key: "language", label: "Language" },
];

type Tier = "great" | "good" | "moderate" | "low";
type RankedCountry = {
  rank: number;
  country_code: string;
  country_name: string;
  total_score: number;
  scores: Record<string, number>;
  verdict: string;
  tier: Tier;
  visa_types: string[];
  pr_timeline_years: number;
  last_updated: string;
};
type GraphNode = { id: string; label: string; total_score: number; tier: Tier };
type GraphEdge = { source: string; target: string; similarity: number; reason: string };
type Results = {
  ranked_countries: RankedCountry[];
  graph_data: { nodes: GraphNode[]; edges: GraphEdge[] };
  profile_hash?: string;
  shareable_url?: string;
};

const TIER_META: Record<Tier, { label: string; bg: string; text: string; color: string }> = {
  great: { label: "Great match", bg: "#DCFCE7", text: "#166534", color: "#22C55E" },
  good: { label: "Good match", bg: "#E0E7FF", text: "#3730A3", color: "#5B4FE8" },
  moderate: { label: "Moderate", bg: "#FEF3C7", text: "#92400E", color: "#F59E0B" },
  low: { label: "Low", bg: "#F1F5F9", text: "#475569", color: "#9CA3AF" },
};

function barColor(s: number) {
  if (s >= 75) return "#22C55E";
  if (s >= 50) return "#F59E0B";
  return "#EF4444";
}

function Results() {
  const [data, setData] = useState<Results | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    try {
      const raw = localStorage.getItem("exitplan_results");
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed?.ranked_countries) setData(parsed);
      }
    } catch {
      // ignore
    }
    setLoaded(true);
  }, []);

  const handleShare = async () => {
    try {
      const url = data?.shareable_url || window.location.href;
      await navigator.clipboard.writeText(url);
      toast.success("Copied!");
    } catch {
      toast.error("Couldn't copy");
    }
  };

  if (!loaded) return null;

  if (!data || data.ranked_countries.length === 0) {
    return (
      <div className="flex min-h-[70vh] items-center justify-center bg-[#FAFAF8] px-6">
        <div className="text-center">
          <h1 className="font-[Plus_Jakarta_Sans] text-3xl font-extrabold text-black/80">
            No results yet
          </h1>
          <p className="mt-2 text-black/50">Tell us about you and we'll rank your countries.</p>
          <Link
            to="/profile"
            className="mt-6 inline-flex items-center gap-2 rounded-full px-6 py-3 text-sm font-semibold text-white shadow-[0_10px_30px_-10px_rgba(255,107,53,0.6)] transition hover:translate-y-[-1px]"
            style={{ background: ORANGE }}
          >
            Build your profile <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAFAF8] text-[#0A0A0A]">
      <div className="mx-auto max-w-7xl px-6 py-10 sm:py-14">
        {/* Header */}
        <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.25em]" style={{ color: ORANGE }}>
              Your Exit Plan
            </p>
            <h1 className="mt-2 font-[Plus_Jakarta_Sans] text-3xl font-extrabold tracking-tight sm:text-4xl">
              Your top countries, ranked.
            </h1>
          </div>
          <div className="flex items-center gap-3">
            <Link
              to="/profile"
              className="inline-flex items-center gap-2 rounded-full border border-black/15 bg-white px-4 py-2 text-sm font-semibold text-black/80 hover:border-black/40"
            >
              <SlidersHorizontal className="h-4 w-4" /> Adjust priorities
            </Link>
            <button
              onClick={handleShare}
              className="inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-semibold text-white"
              style={{ background: INDIGO }}
            >
              <Share2 className="h-4 w-4" /> Share
            </button>
          </div>
        </div>

        <Disclaimer />

        {/* Two-column */}
        <div className="grid gap-8 lg:grid-cols-[45%_55%]">
          <div className="space-y-5">
            {data.ranked_countries.map((c, i) => (
              <CountryCard key={c.country_code} country={c} index={i} />
            ))}
          </div>
          <div className="lg:sticky lg:top-20 lg:h-[calc(100vh-6rem)]">
            <KnowledgeMap graph={data.graph_data} />
          </div>
        </div>
      </div>
    </div>
  );
}

function useAnimatedNumber(target: number, duration = 1000, delay = 0) {
  const [val, setVal] = useState(0);
  useEffect(() => {
    let raf = 0;
    let start = 0;
    const tStart = performance.now() + delay;
    const tick = (now: number) => {
      if (now < tStart) {
        raf = requestAnimationFrame(tick);
        return;
      }
      if (!start) start = now;
      const p = Math.min(1, (now - tStart) / duration);
      const eased = 1 - Math.pow(1 - p, 3);
      setVal(target * eased);
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, duration, delay]);
  return val;
}

function CountryCard({ country, index }: { country: RankedCountry; index: number }) {
  const delay = index * 80;
  const score = useAnimatedNumber(country.total_score, 1000, delay);
  const tier = TIER_META[country.tier] ?? TIER_META.moderate;
  const isTop = country.rank === 1;

  return (
    <article
      id={`country-${country.country_code}`}
      className={`relative overflow-hidden rounded-3xl border bg-white p-6 transition-shadow ${
        isTop ? "border-l-4 shadow-[0_20px_50px_-30px_rgba(91,79,232,0.5)]" : "border-black/10"
      }`}
      style={
        isTop
          ? { borderLeftColor: INDIGO, background: "linear-gradient(180deg, #F4F2FF 0%, #FFFFFF 60%)" }
          : undefined
      }
    >
      {isTop && (
        <span
          className="absolute right-5 top-5 inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-bold text-white"
          style={{ background: ORANGE }}
        >
          Best match ✦
        </span>
      )}

      <div className="flex items-start gap-4">
        <div className="text-5xl leading-none">{FLAGS[country.country_code] ?? "🌍"}</div>
        <div className="flex-1">
          <div className="flex items-center gap-2 text-xs font-semibold text-black/40">
            #{country.rank}
          </div>
          <h2 className="font-[Plus_Jakarta_Sans] text-2xl font-extrabold tracking-tight">
            {country.country_name}
          </h2>
          <div className="mt-1 flex items-center gap-3">
            <span
              className="rounded-full px-2.5 py-0.5 text-xs font-semibold"
              style={{ background: tier.bg, color: tier.text }}
            >
              {tier.label}
            </span>
            <span className="text-xs text-black/45">PR in ~{country.pr_timeline_years} years</span>
          </div>
        </div>
        <div className="text-right">
          <div className="font-[Plus_Jakarta_Sans] text-4xl font-extrabold tabular-nums" style={{ color: INDIGO }}>
            {score.toFixed(1)}
          </div>
          <div className="text-[10px] font-semibold uppercase tracking-widest text-black/40">Score</div>
        </div>
      </div>

      <div className="mt-5 space-y-2.5">
        {FACTOR_LABELS.map((f) => {
          const v = country.scores[f.key] ?? 0;
          return (
            <div key={f.key} className="flex items-center gap-3">
              <span className="w-32 shrink-0 text-xs font-medium text-black/60">{f.label}</span>
              <div className="relative h-2 flex-1 overflow-hidden rounded-full bg-black/[0.06]">
                <div
                  className="h-full rounded-full transition-[width] duration-700"
                  style={{ width: `${v}%`, background: barColor(v) }}
                />
              </div>
              <span className="w-8 text-right text-xs font-semibold tabular-nums text-black/70">{v}</span>
            </div>
          );
        })}
      </div>

      <p className="mt-5 text-sm italic leading-relaxed text-black/70">{country.verdict}</p>

      {country.visa_types?.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-1.5">
          {country.visa_types.map((v) => (
            <span
              key={v}
              className="rounded-full border border-black/10 bg-black/[0.03] px-2.5 py-1 text-[11px] font-medium text-black/70"
            >
              {v}
            </span>
          ))}
        </div>
      )}

      <div className="mt-6 flex gap-2">
        <Link
          to="/country/$code"
          params={{ code: country.country_code }}
          className="inline-flex flex-1 items-center justify-center gap-2 rounded-full px-4 py-2.5 text-sm font-semibold text-white transition hover:translate-y-[-1px]"
          style={{ background: INDIGO }}
        >
          Explore <ArrowRight className="h-4 w-4" />
        </Link>
        <Link
          to="/country/$code"
          params={{ code: country.country_code }}
          className="inline-flex items-center gap-2 rounded-full border border-black/15 bg-white px-4 py-2.5 text-sm font-semibold text-black/80 hover:border-black/40"
        >
          <Sparkles className="h-4 w-4" /> Ask AI
        </Link>
      </div>
    </article>
  );
}

// --------- Knowledge Map (D3) ---------
declare global {
  interface Window { d3?: any }
}

function KnowledgeMap({ graph }: { graph: { nodes: GraphNode[]; edges: GraphEdge[] } }) {
  const ref = useRef<HTMLDivElement>(null);
  const [ready, setReady] = useState(typeof window !== "undefined" && !!window.d3);

  useEffect(() => {
    if (typeof window === "undefined") return;
    if (window.d3) { setReady(true); return; }
    const existing = document.querySelector<HTMLScriptElement>("script[data-d3]");
    if (existing) {
      existing.addEventListener("load", () => setReady(true));
      return;
    }
    const s = document.createElement("script");
    s.src = "https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js";
    s.async = true;
    s.dataset.d3 = "1";
    s.onload = () => setReady(true);
    document.head.appendChild(s);
  }, []);

  useEffect(() => {
    if (!ready || !ref.current) return;
    const d3 = window.d3;
    if (!d3 || !graph?.nodes?.length) return;

    const container = ref.current;
    container.innerHTML = "";
    const width = container.clientWidth;
    const height = Math.max(500, container.clientHeight || 500);

    const svg = d3
      .select(container)
      .append("svg")
      .attr("width", "100%")
      .attr("height", height)
      .attr("viewBox", `0 0 ${width} ${height}`);

    const tooltip = d3
      .select(container)
      .append("div")
      .style("position", "absolute")
      .style("pointer-events", "none")
      .style("background", "#0A0A0A")
      .style("color", "white")
      .style("padding", "6px 10px")
      .style("border-radius", "8px")
      .style("font-size", "12px")
      .style("opacity", 0)
      .style("transition", "opacity 0.15s");

    const colorScale = d3.scaleLinear()
      .domain([55, 70, 80, 90])
      .range(["#F59E0B", "#5B4FE8", "#22C55E", "#059669"])
      .clamp(true);

    const r = d3.scaleLinear().domain([55, 90]).range([18, 42]).clamp(true);

    const nodes = graph.nodes.map((n) => ({ ...n }));
    const links = (graph.edges || []).map((e) => ({ ...e }));

    const sim = d3
      .forceSimulation(nodes)
      .force("link", d3.forceLink(links).id((d: any) => d.id).distance(120))
      .force("charge", d3.forceManyBody().strength(-200))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collide", d3.forceCollide().radius(50));

    const link = svg
      .append("g")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke", "#CBD5E1")
      .attr("stroke-width", 1.5)
      .attr("stroke-opacity", (d: any) => 0.3 + d.similarity * 0.5);

    const node = svg
      .append("g")
      .selectAll("g")
      .data(nodes)
      .join("g")
      .style("cursor", "pointer")
      .call(
        d3
          .drag()
          .on("start", (event: any, d: any) => {
            if (!event.active) sim.alphaTarget(0.3).restart();
            d.fx = d.x; d.fy = d.y;
          })
          .on("drag", (event: any, d: any) => { d.fx = event.x; d.fy = event.y; })
          .on("end", (event: any, d: any) => {
            if (!event.active) sim.alphaTarget(0);
            d.fx = null; d.fy = null;
          }),
      );

    node
      .append("circle")
      .attr("r", (d: any) => r(d.total_score))
      .attr("fill", (d: any) => colorScale(d.total_score))
      .attr("stroke", "white")
      .attr("stroke-width", 3);

    node
      .append("text")
      .text((d: any) => d.label)
      .attr("text-anchor", "middle")
      .attr("dy", (d: any) => r(d.total_score) + 16)
      .attr("font-size", 12)
      .attr("font-weight", 600)
      .attr("fill", "#0A0A0A");

    node
      .on("mouseenter", (event: MouseEvent, d: any) => {
        tooltip
          .style("opacity", 1)
          .html(`<strong>${d.label}</strong> · ${d.total_score.toFixed(1)}`);
      })
      .on("mousemove", (event: MouseEvent) => {
        const rect = container.getBoundingClientRect();
        tooltip
          .style("left", `${event.clientX - rect.left + 12}px`)
          .style("top", `${event.clientY - rect.top + 12}px`);
      })
      .on("mouseleave", () => tooltip.style("opacity", 0))
      .on("click", (_event: MouseEvent, d: any) => {
        const card = document.getElementById(`country-${d.id}`);
        if (card) {
          card.scrollIntoView({ behavior: "smooth", block: "center" });
          card.animate(
            [
              { boxShadow: "0 0 0 0 rgba(91,79,232,0.6)" },
              { boxShadow: "0 0 0 14px rgba(91,79,232,0)" },
            ],
            { duration: 900, iterations: 2 },
          );
        }
      });

    sim.on("tick", () => {
      link
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);
      node.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
    });

    return () => {
      sim.stop();
      container.innerHTML = "";
    };
  }, [ready, graph]);

  return (
    <div
      ref={ref}
      className="relative h-full min-h-[500px] w-full overflow-hidden rounded-3xl border border-black/10"
      style={{ background: "#F8FAFC" }}
    >
      {!ready && (
        <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 border-2 border-dashed border-black/15 rounded-3xl">
          <p className="font-[Plus_Jakarta_Sans] text-lg font-bold text-black/70">Knowledge Map</p>
          <p className="text-sm text-black/45">Generating your map…</p>
        </div>
      )}
      <div className="absolute bottom-4 left-4 flex items-center gap-4 text-xs font-semibold text-black/60 pointer-events-none">
        <span className="flex items-center gap-1"><span style={{ color: "#059669" }}>●</span> Top match</span>
        <span className="flex items-center gap-1"><span style={{ color: "#22C55E" }}>●</span> Good</span>
        <span className="flex items-center gap-1"><span style={{ color: "#F59E0B" }}>●</span> Moderate</span>
      </div>
    </div>
  );
}

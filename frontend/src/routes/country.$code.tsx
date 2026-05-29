import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { ArrowLeft, Send, Loader2, ExternalLink, RefreshCw } from "lucide-react";
import { COUNTRIES, type Country } from "@/lib/countries";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/country/$code")({
  component: CountryDetail,
});

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000";

const FLAGS: Record<string, string> = {
  GB: "🇬🇧", CA: "🇨🇦", DE: "🇩🇪", AU: "🇦🇺", NL: "🇳🇱",
  PT: "🇵🇹", IE: "🇮🇪", AE: "🇦🇪", NZ: "🇳🇿", SG: "🇸🇬",
};

const TABS = ["Overview", "Visa Types", "PR Pathway", "Job Market", "Recent Changes"] as const;
type Tab = (typeof TABS)[number];

// ——— Types ———

type CountryDetail = {
  code: string;
  name: string;
  scores: {
    pr_timeline: number;
    visa_ease: number;
    salary_cost_ratio: number;
    language: number;
  };
  visa_types: string[];
  pr_timeline_years: number;
  recent_changes: Array<{
    id: string;
    visa_type: string;
    change_summary: string;
    detected_at: string;
    old_value?: string;
    new_value?: string;
  }>;
  key_facts: Array<{ content: string; visa_type: string; source_url: string }>;
};

type RankedCountry = {
  rank: number;
  country_code: string;
  country_name: string;
  total_score: number;
  scores: Record<string, number>;
  verdict: string;
  tier: "great" | "good" | "moderate" | "low";
};

// ——— Helpers ———

function barColor(s: number) {
  if (s >= 75) return "#22C55E";
  if (s >= 50) return "#F59E0B";
  return "#EF4444";
}

function formatDate(iso: string) {
  try {
    return new Date(iso).toLocaleDateString("en-US", {
      year: "numeric", month: "long", day: "numeric",
    });
  } catch {
    return iso;
  }
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center gap-3">
      <span className="w-36 shrink-0 text-sm font-medium text-foreground/60">{label}</span>
      <div className="relative h-2 flex-1 overflow-hidden rounded-full bg-black/[0.06]">
        <div
          className="h-full rounded-full transition-[width] duration-700"
          style={{ width: `${value}%`, background: barColor(value) }}
        />
      </div>
      <span className="w-8 text-right text-xs font-semibold tabular-nums text-foreground/70">{value}</span>
    </div>
  );
}

// ——— Page component ———

function CountryDetail() {
  const { code } = Route.useParams();
  const upperCode = code.toUpperCase();

  const staticCountry = COUNTRIES.find((c) => c.code === upperCode);
  const flag = FLAGS[upperCode] ?? "🌍";

  const [tab, setTab] = useState<Tab>("Overview");
  const [detail, setDetail] = useState<CountryDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [localCountry, setLocalCountry] = useState<RankedCountry | null>(null);

  const fetchDetail = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${BACKEND_URL}/country/${upperCode}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      setDetail(await res.json());
    } catch {
      setError("Couldn't load country data. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetail();
    try {
      const raw = localStorage.getItem("exitplan_results");
      if (raw) {
        const parsed = JSON.parse(raw);
        const found = parsed?.ranked_countries?.find(
          (c: RankedCountry) => c.country_code === upperCode,
        );
        if (found) setLocalCountry(found);
      }
    } catch {
      // ignore
    }
  }, [upperCode]);

  const displayName = detail?.name ?? staticCountry?.name ?? upperCode;

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <Link
        to="/results"
        className="inline-flex items-center gap-1 text-sm font-medium text-muted-foreground hover:text-primary"
      >
        <ArrowLeft className="h-4 w-4" /> Back to results
      </Link>

      <div className="mt-6 grid gap-8 lg:grid-cols-5">
        <div className="lg:col-span-3">
          {/* Header */}
          <div className="flex items-center gap-4">
            <span className="text-5xl">{flag}</span>
            <h1 className="font-display text-4xl font-extrabold sm:text-5xl">{displayName}</h1>
          </div>

          {/* Tab nav */}
          <div className="mt-8 flex flex-wrap gap-1 border-b border-border">
            {TABS.map((t) => (
              <button
                key={t}
                onClick={() => setTab(t)}
                className={cn(
                  "px-4 py-3 font-display text-sm font-semibold transition-colors",
                  tab === t
                    ? "border-b-2 border-primary text-primary"
                    : "text-muted-foreground hover:text-foreground",
                )}
              >
                {t}
              </button>
            ))}
          </div>

          {/* Tab content */}
          {loading ? (
            <div className="mt-6 flex items-center justify-center rounded-2xl border border-border bg-card p-12">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
              <span className="ml-3 text-muted-foreground">Loading country data…</span>
            </div>
          ) : error ? (
            <div className="mt-6 rounded-2xl border border-border bg-card p-8 text-center">
              <p className="text-sm text-destructive">{error}</p>
              <button
                onClick={fetchDetail}
                className="mt-4 inline-flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm font-semibold hover:border-primary"
              >
                <RefreshCw className="h-4 w-4" /> Retry
              </button>
            </div>
          ) : detail ? (
            <div key={tab} className="mt-6 animate-fade-in-up rounded-2xl border border-border bg-card p-6">
              <TabContent
                tab={tab}
                detail={detail}
                staticCountry={staticCountry}
                localCountry={localCountry}
              />
            </div>
          ) : null}

          {/* Key facts — always visible once loaded */}
          {!loading && !error && detail && detail.key_facts.length > 0 && (
            <KeyFacts facts={detail.key_facts} />
          )}
        </div>

        <div className="lg:col-span-2">
          <ChatPanel countryName={displayName} countryCode={code} />
        </div>
      </div>
    </div>
  );
}

// ——— Tab router ———

function TabContent({
  tab,
  detail,
  staticCountry,
  localCountry,
}: {
  tab: Tab;
  detail: CountryDetail;
  staticCountry: Country | undefined;
  localCountry: RankedCountry | null;
}) {
  switch (tab) {
    case "Overview":
      return <OverviewTab detail={detail} staticCountry={staticCountry} />;
    case "Visa Types":
      return <VisaTypesTab detail={detail} />;
    case "PR Pathway":
      return <PRPathwayTab detail={detail} />;
    case "Job Market":
      return <JobMarketTab detail={detail} localCountry={localCountry} />;
    case "Recent Changes":
      return <RecentChangesTab detail={detail} />;
  }
}

// ——— Individual tabs ———

function OverviewTab({
  detail,
  staticCountry,
}: {
  detail: CountryDetail;
  staticCountry: Country | undefined;
}) {
  return (
    <div>
      <h2 className="font-display text-xl font-bold">Overview</h2>
      <div className="mt-4 space-y-3">
        <ScoreBar label="PR Timeline" value={detail.scores.pr_timeline} />
        <ScoreBar label="Visa Ease" value={detail.scores.visa_ease} />
        <ScoreBar label="Salary vs Cost" value={detail.scores.salary_cost_ratio} />
        <ScoreBar label="Language" value={detail.scores.language} />
      </div>
      <div className="mt-5">
        <span className="rounded-full bg-primary/10 px-4 py-1.5 text-sm font-semibold text-primary">
          PR in ~{detail.pr_timeline_years} year{detail.pr_timeline_years !== 1 ? "s" : ""}
        </span>
      </div>
      {staticCountry?.verdict && (
        <p className="mt-5 text-sm italic leading-relaxed text-foreground/70">
          {staticCountry.verdict}
        </p>
      )}
      <p className="mt-4 text-xs text-muted-foreground">
        Sourced from official government data · Updated weekly
      </p>
    </div>
  );
}

function VisaTypesTab({ detail }: { detail: CountryDetail }) {
  return (
    <div>
      <h2 className="font-display text-xl font-bold">Visa Types</h2>
      <div className="mt-4 space-y-3">
        {detail.visa_types.map((v) => (
          <div key={v} className="rounded-xl border border-border bg-background p-4">
            <div className="font-display text-sm font-semibold">{v}</div>
            <p className="mt-1 text-sm text-muted-foreground">
              Available for skilled workers and international graduates. Check eligibility criteria on the official government site.
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}

function PRPathwayTab({ detail }: { detail: CountryDetail }) {
  const years = detail.pr_timeline_years;
  const mid = Math.ceil(years / 2);

  const milestones = [
    { label: "Year 0", desc: "Arrive on work visa · begin employment" },
    { label: `Year ${mid}`, desc: "Mid-point check · maintain continuous employment and residency" },
    { label: `Year ${years}`, desc: "PR eligible · apply for permanent residence" },
  ];

  return (
    <div>
      <h2 className="font-display text-xl font-bold">PR Pathway</h2>
      <div className="mt-2">
        <span className="inline-flex items-center rounded-full bg-primary/10 px-4 py-1.5 text-sm font-semibold text-primary">
          ~{years} year{years !== 1 ? "s" : ""} to PR
        </span>
      </div>
      <div className="relative mt-8 pl-7">
        <div className="absolute left-2.5 top-2 bottom-2 w-0.5 bg-border" />
        {milestones.map((m, i) => (
          <div key={i} className="relative mb-8">
            <div className="absolute -left-[22px] top-0.5 h-4 w-4 rounded-full border-2 border-primary bg-background" />
            <p className="font-display text-sm font-bold">{m.label}</p>
            <p className="mt-1 text-sm text-muted-foreground">{m.desc}</p>
          </div>
        ))}
      </div>
      <p className="mt-2 text-xs italic text-muted-foreground">
        Timeline based on continuous employment and uninterrupted residency. Individual circumstances vary.
      </p>
    </div>
  );
}

const FACTOR_LABELS = [
  { key: "job_market", label: "Job Market" },
  { key: "pr_timeline", label: "PR Timeline" },
  { key: "visa_ease", label: "Visa Ease" },
  { key: "salary_cost_ratio", label: "Salary vs Cost" },
  { key: "language", label: "Language" },
];

function JobMarketTab({
  localCountry,
}: {
  detail: CountryDetail;
  localCountry: RankedCountry | null;
}) {
  if (!localCountry) {
    return (
      <div>
        <h2 className="font-display text-xl font-bold">Job Market</h2>
        <p className="mt-4 text-sm text-muted-foreground">
          Build your profile to see personalised job market scores for your field in this country.
        </p>
        <Link
          to="/profile"
          className="mt-4 inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground"
        >
          Build profile <ArrowLeft className="h-4 w-4 rotate-180" />
        </Link>
      </div>
    );
  }

  return (
    <div>
      <h2 className="font-display text-xl font-bold">Job Market</h2>
      <p className="mt-1 text-xs text-muted-foreground">
        Ranked #{localCountry.rank} for your profile · overall score {localCountry.total_score.toFixed(1)}
      </p>
      <div className="mt-5 space-y-3">
        {FACTOR_LABELS.map((f) => (
          <ScoreBar key={f.key} label={f.label} value={localCountry.scores[f.key] ?? 0} />
        ))}
      </div>
      {localCountry.verdict && (
        <p className="mt-5 text-sm italic leading-relaxed text-foreground/70">
          {localCountry.verdict}
        </p>
      )}
    </div>
  );
}

function RecentChangesTab({ detail }: { detail: CountryDetail }) {
  if (detail.recent_changes.length === 0) {
    return (
      <div>
        <h2 className="font-display text-xl font-bold">Recent Changes</h2>
        <p className="mt-4 text-sm text-muted-foreground">
          No recent policy changes detected for this country.
        </p>
      </div>
    );
  }

  return (
    <div>
      <h2 className="font-display text-xl font-bold">Recent Changes</h2>
      <div className="mt-4 space-y-4">
        {detail.recent_changes.map((c) => (
          <div key={c.id} className="rounded-xl border border-border bg-background p-4">
            <div className="flex items-center justify-between gap-2 flex-wrap">
              <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-semibold text-amber-800">
                {c.visa_type}
              </span>
              <span className="text-xs text-muted-foreground">{formatDate(c.detected_at)}</span>
            </div>
            <p className="mt-2 text-sm font-medium leading-relaxed">{c.change_summary}</p>
            {(c.old_value || c.new_value) && (
              <div className="mt-3 grid grid-cols-2 gap-2">
                {c.old_value && (
                  <div className="rounded-lg bg-red-50 p-2 text-xs text-red-800">
                    <div className="mb-1 font-semibold">Before</div>
                    {c.old_value.slice(0, 150)}{c.old_value.length > 150 ? "…" : ""}
                  </div>
                )}
                {c.new_value && (
                  <div className="rounded-lg bg-green-50 p-2 text-xs text-green-800">
                    <div className="mb-1 font-semibold">After</div>
                    {c.new_value.slice(0, 150)}{c.new_value.length > 150 ? "…" : ""}
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}

// ——— Key facts section ———

function KeyFacts({ facts }: { facts: CountryDetail["key_facts"] }) {
  const [expanded, setExpanded] = useState<Record<number, boolean>>({});

  return (
    <div className="mt-6">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
        From official sources
      </h3>
      <div className="mt-3 space-y-3">
        {facts.slice(0, 3).map((f, i) => {
          const isExp = !!expanded[i];
          const truncated = f.content.length > 200;
          const text = isExp || !truncated ? f.content : f.content.slice(0, 200);
          return (
            <div key={i} className="rounded-xl border-l-4 border-primary/40 bg-card py-3 pl-4 pr-4">
              {f.visa_type && (
                <span className="text-[11px] font-semibold uppercase tracking-wider text-primary/60">
                  {f.visa_type}
                </span>
              )}
              <p className="mt-1 text-sm leading-relaxed text-foreground/80">
                {text}{truncated && !isExp ? "…" : ""}
              </p>
              <div className="mt-2 flex items-center gap-3">
                {truncated && (
                  <button
                    onClick={() => setExpanded((p) => ({ ...p, [i]: !p[i] }))}
                    className="text-xs font-semibold text-primary hover:underline"
                  >
                    {isExp ? "Show less" : "Read more"}
                  </button>
                )}
                {f.source_url && (
                  <a
                    href={f.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-primary"
                  >
                    <ExternalLink className="h-3 w-3" /> Source
                  </a>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ——— Chat panel (unchanged from original) ———

type Msg = { role: "user" | "assistant"; text: string };

function ChatPanel({ countryName, countryCode }: { countryName: string; countryCode: string }) {
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const [msgs, setMsgs] = useState<Msg[]>([
    { role: "assistant", text: `Hi! Ask me anything about living and working in ${countryName}. I'll answer based on official sources.` },
  ]);
  const bottomRef = useRef<HTMLDivElement>(null);

  const appendToLast = (chunk: string) => {
    setMsgs((m) => {
      const updated = [...m];
      updated[updated.length - 1] = {
        ...updated[updated.length - 1],
        text: updated[updated.length - 1].text + chunk,
      };
      return updated;
    });
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const send = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || streaming) return;
    const q = input.trim();
    setInput("");
    setMsgs((m) => [...m, { role: "user", text: q }, { role: "assistant", text: "" }]);
    setStreaming(true);

    try {
      const res = await fetch(`${BACKEND_URL}/ask/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q, country_code: countryCode, user_profile: {} }),
      });

      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`);

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const text = decoder.decode(value);
        for (const line of text.split("\n")) {
          if (!line.startsWith("data: ")) continue;
          try {
            const data = JSON.parse(line.slice(6));
            if (!data.done && data.chunk) appendToLast(data.chunk);
            if (data.done && data.citations?.length) {
              const sources = (data.citations as { source_url: string }[])
                .map((c) => c.source_url)
                .filter(Boolean)
                .join(" · ");
              if (sources) appendToLast(`\n\nSources: ${sources}`);
            }
          } catch {
            // skip malformed SSE line
          }
        }
      }
    } catch {
      appendToLast("Sorry, couldn't reach the backend. Make sure it's running on port 8000.");
    } finally {
      setStreaming(false);
    }
  };

  return (
    <div className="sticky top-20 flex h-[calc(100vh-7rem)] flex-col overflow-hidden rounded-2xl border border-border bg-card shadow-sm">
      <div className="border-b border-border bg-background/50 px-5 py-4">
        <h3 className="font-display text-base font-semibold">Ask AI about {countryName}</h3>
      </div>
      <div className="flex-1 space-y-3 overflow-y-auto p-5">
        {msgs.map((m, i) => (
          <div
            key={i}
            className={cn(
              "max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap",
              m.role === "assistant"
                ? "bg-accent text-accent-foreground"
                : "ml-auto bg-primary text-primary-foreground",
            )}
          >
            {m.text}
            {streaming && i === msgs.length - 1 && m.role === "assistant" && !m.text && (
              <span className="inline-flex items-center gap-1 text-xs opacity-60">
                <Loader2 className="h-3 w-3 animate-spin" /> Thinking…
              </span>
            )}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>
      <form onSubmit={send} className="flex items-center gap-2 border-t border-border bg-background p-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask anything about visas, jobs, PR..."
          disabled={streaming}
          className="flex-1 rounded-lg border border-border bg-card px-3 py-2 text-sm outline-none focus:border-primary disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={streaming || !input.trim()}
          className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground transition-colors hover:bg-primary/90 disabled:opacity-50"
          aria-label="Send"
        >
          {streaming ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
        </button>
      </form>
    </div>
  );
}

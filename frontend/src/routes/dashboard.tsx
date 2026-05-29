import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { Bell, ArrowRight, Loader2, CheckCheck } from "lucide-react";

export const Route = createFileRoute("/dashboard")({
  component: Dashboard,
});

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000";

const FLAGS: Record<string, string> = {
  GB: "🇬🇧", CA: "🇨🇦", DE: "🇩🇪", AU: "🇦🇺", NL: "🇳🇱",
  PT: "🇵🇹", IE: "🇮🇪", AE: "🇦🇪", NZ: "🇳🇿", SG: "🇸🇬",
};

// ——— Types ———

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

type Results = {
  ranked_countries: RankedCountry[];
  profile_hash?: string;
  shareable_url?: string;
};

type Alert = {
  id: string;
  country_id?: string;
  alert_type: string;
  message: string;
  plain_english?: string;
  sent_at?: string;
  read_at?: string | null;
  source_url?: string;
};

type Outcome = {
  id?: string;
  field: string;
  destination_country: string;
  visa_type: string;
  summary: string;
  months_to_job?: number;
  year?: number;
  verified?: boolean;
};

// ——— Helpers ———

function getSupabaseToken(): string | null {
  try {
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.endsWith("-auth-token")) {
        const val = JSON.parse(localStorage.getItem(key) ?? "");
        return val?.access_token ?? null;
      }
    }
  } catch {
    // ignore
  }
  return null;
}

function formatDate(iso: string | undefined) {
  if (!iso) return "";
  try {
    return new Date(iso).toLocaleDateString("en-US", {
      year: "numeric", month: "long", day: "numeric",
    });
  } catch {
    return iso;
  }
}

const TIER_META: Record<Tier, { label: string; bg: string; text: string }> = {
  great:    { label: "Great match", bg: "#DCFCE7", text: "#166534" },
  good:     { label: "Good match",  bg: "#E0E7FF", text: "#3730A3" },
  moderate: { label: "Moderate",    bg: "#FEF3C7", text: "#92400E" },
  low:      { label: "Low",         bg: "#F1F5F9", text: "#475569" },
};

// ——— Main component ———

function Dashboard() {
  const [results, setResults] = useState<Results | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [alertsLoading, setAlertsLoading] = useState(true);
  const [token, setToken] = useState<string | null>(null);
  const [outcomes, setOutcomes] = useState<Outcome[]>([]);

  useEffect(() => {
    // Profile from localStorage
    try {
      const raw = localStorage.getItem("exitplan_results");
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed?.ranked_countries) setResults(parsed);
      }
    } catch {
      // ignore
    }

    // Auth token
    const tok = getSupabaseToken();
    setToken(tok);

    // Alerts — auth required
    if (tok) {
      fetch(`${BACKEND_URL}/alerts/`, {
        headers: { Authorization: `Bearer ${tok}` },
      })
        .then((r) => (r.ok ? r.json() : []))
        .then((data) => setAlerts(Array.isArray(data) ? data : []))
        .catch(() => {})
        .finally(() => setAlertsLoading(false));
    } else {
      setAlertsLoading(false);
    }

    // Outcome stories — public
    fetch(`${BACKEND_URL}/outcomes/?limit=4`)
      .then((r) => (r.ok ? r.json() : []))
      .then((data) => setOutcomes(Array.isArray(data) ? data : []))
      .catch(() => {});
  }, []);

  const markRead = async (id: string) => {
    if (!token) return;
    try {
      await fetch(`${BACKEND_URL}/alerts/mark-read/${id}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      });
      setAlerts((prev) =>
        prev.map((a) => (a.id === id ? { ...a, read_at: new Date().toISOString() } : a)),
      );
    } catch {
      // ignore
    }
  };

  const top3 = results?.ranked_countries?.slice(0, 3) ?? [];
  const lastUpdated = top3[0]?.last_updated ? formatDate(top3[0].last_updated) : null;

  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="font-display text-3xl font-bold sm:text-4xl">Your Exit Plan</h1>
        <Link
          to="/profile"
          className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-4 py-2 font-display text-sm font-semibold text-foreground transition-colors hover:border-primary hover:text-primary"
        >
          Adjust priorities <ArrowRight className="h-4 w-4" />
        </Link>
      </div>

      {/* Section 1 — Profile summary */}
      <section className="mt-8">
        <h2 className="mb-3 font-display text-sm font-semibold uppercase tracking-wider text-muted-foreground">
          Top ranked countries
        </h2>
        {top3.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-border bg-card p-8 text-center">
            <p className="text-sm text-muted-foreground">No profile yet.</p>
            <Link
              to="/profile"
              className="mt-4 inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground"
            >
              Build your profile <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        ) : (
          <>
            <div className="grid gap-3 sm:grid-cols-3">
              {top3.map((c) => {
                const tier = TIER_META[c.tier] ?? TIER_META.moderate;
                return (
                  <Link
                    key={c.country_code}
                    to="/country/$code"
                    params={{ code: c.country_code }}
                    className="group rounded-2xl border border-border bg-card p-5 transition-colors hover:border-primary/40"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{FLAGS[c.country_code] ?? "🌍"}</span>
                      <div>
                        <div className="font-display text-sm font-semibold group-hover:text-primary">
                          #{c.rank} {c.country_name}
                        </div>
                        <span
                          className="mt-0.5 inline-block rounded-full px-2 py-0.5 text-[11px] font-semibold"
                          style={{ background: tier.bg, color: tier.text }}
                        >
                          {tier.label}
                        </span>
                      </div>
                    </div>
                    <div className="mt-3 font-display text-2xl font-extrabold tabular-nums text-primary">
                      {c.total_score.toFixed(1)}
                    </div>
                    <div className="mt-1 text-xs text-muted-foreground">
                      PR in ~{c.pr_timeline_years}y
                    </div>
                  </Link>
                );
              })}
            </div>
            {lastUpdated && (
              <p className="mt-2 text-xs text-muted-foreground">Last updated: {lastUpdated}</p>
            )}
          </>
        )}
      </section>

      {/* Sections 2 + 3 — side by side */}
      <div className="mt-10 grid gap-8 lg:grid-cols-2">
        {/* Section 2 — Alerts */}
        <section>
          <h2 className="mb-3 flex items-center gap-2 font-display text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            <Bell className="h-4 w-4" /> Recent alerts
          </h2>

          {!token ? (
            <div className="rounded-2xl border border-dashed border-border bg-card p-6 text-center">
              <p className="text-sm text-muted-foreground">Sign in to see your personalised alerts.</p>
              <Link
                to="/signin"
                className="mt-3 inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground"
              >
                Sign in <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          ) : alertsLoading ? (
            <div className="flex items-center gap-2 rounded-2xl border border-border bg-card p-6 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" /> Loading alerts…
            </div>
          ) : alerts.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-border bg-card p-6 text-center text-sm text-muted-foreground">
              No alerts yet. Save countries to get notified when policies change.
            </div>
          ) : (
            <div className="space-y-3">
              {alerts.map((a) => (
                <div
                  key={a.id}
                  className={`rounded-2xl border bg-card p-5 transition-opacity ${a.read_at ? "opacity-60" : ""}`}
                  style={{ borderColor: a.read_at ? undefined : "var(--border)" }}
                >
                  <div className="flex items-center justify-between gap-3 flex-wrap">
                    <span className="rounded-full bg-amber-100 px-2.5 py-0.5 font-display text-[11px] font-semibold uppercase tracking-wide text-amber-800">
                      {a.alert_type.replace("_", " ")}
                    </span>
                    <span className="text-xs text-muted-foreground">{formatDate(a.sent_at)}</span>
                  </div>
                  <p className="mt-3 text-sm leading-relaxed text-foreground/80">{a.message}</p>
                  {a.plain_english && a.plain_english !== a.message && (
                    <p className="mt-1 text-xs text-muted-foreground">{a.plain_english}</p>
                  )}
                  <div className="mt-3 flex items-center justify-between text-xs">
                    {a.source_url ? (
                      <a
                        href={a.source_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="font-semibold text-primary hover:underline"
                      >
                        Read more →
                      </a>
                    ) : (
                      <span />
                    )}
                    {!a.read_at && (
                      <button
                        onClick={() => markRead(a.id)}
                        className="inline-flex items-center gap-1 text-muted-foreground hover:text-foreground"
                      >
                        <CheckCheck className="h-3.5 w-3.5" /> Mark read
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        {/* Section 3 — Outcomes */}
        <section>
          <h2 className="mb-3 font-display text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Community stories
          </h2>
          {outcomes.length === 0 ? (
            <div className="rounded-2xl border border-dashed border-border bg-card p-6 text-center text-sm text-muted-foreground">
              No stories yet.
            </div>
          ) : (
            <div className="space-y-3">
              {outcomes.map((o, i) => (
                <div key={o.id ?? i} className="rounded-2xl border border-border bg-card p-5">
                  <div className="flex items-start justify-between gap-3 flex-wrap">
                    <div className="flex items-center gap-2">
                      <span className="text-xl">{FLAGS[o.destination_country] ?? "🌍"}</span>
                      <div>
                        <div className="font-display text-sm font-semibold">
                          {o.field} → {o.destination_country}
                        </div>
                        <div className="text-xs text-muted-foreground">{o.visa_type}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 flex-wrap">
                      {o.verified && (
                        <span className="rounded-full bg-green-100 px-2.5 py-0.5 text-[11px] font-semibold text-green-800">
                          Verified ✓
                        </span>
                      )}
                      {o.year && (
                        <span className="text-xs text-muted-foreground">{o.year}</span>
                      )}
                    </div>
                  </div>
                  <p className="mt-3 text-sm leading-relaxed text-foreground/80">{o.summary}</p>
                  {o.months_to_job != null && (
                    <p className="mt-2 text-xs text-muted-foreground">
                      Job found in {o.months_to_job} month{o.months_to_job !== 1 ? "s" : ""}
                    </p>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { LogOut, ArrowRight } from "lucide-react";
import { toast } from "sonner";
import { supabase } from "@/lib/supabase";

export const Route = createFileRoute("/account")({
  component: Account,
});

const FLAGS: Record<string, string> = {
  GB: "🇬🇧", CA: "🇨🇦", DE: "🇩🇪", AU: "🇦🇺", NL: "🇳🇱",
  PT: "🇵🇹", IE: "🇮🇪", AE: "🇦🇪", NZ: "🇳🇿", SG: "🇸🇬",
};

const ALL_COUNTRIES = [
  { code: "CA", name: "Canada" },
  { code: "DE", name: "Germany" },
  { code: "GB", name: "United Kingdom" },
  { code: "AU", name: "Australia" },
  { code: "NL", name: "Netherlands" },
  { code: "IE", name: "Ireland" },
  { code: "SG", name: "Singapore" },
  { code: "NZ", name: "New Zealand" },
  { code: "AE", name: "UAE" },
  { code: "PT", name: "Portugal" },
];

type Tier = "great" | "good" | "moderate" | "low";

type RankedCountry = {
  rank: number;
  country_code: string;
  country_name: string;
  total_score: number;
  tier: Tier;
  pr_timeline_years: number;
};

type Results = {
  ranked_countries: RankedCountry[];
};

const TIER_META: Record<Tier, { label: string; bg: string; text: string }> = {
  great:    { label: "Great match", bg: "#DCFCE7", text: "#166534" },
  good:     { label: "Good match",  bg: "#E0E7FF", text: "#3730A3" },
  moderate: { label: "Moderate",    bg: "#FEF3C7", text: "#92400E" },
  low:      { label: "Low",         bg: "#F1F5F9", text: "#475569" },
};

function Account() {
  const navigate = useNavigate();
  const [email, setEmail] = useState<string | null>(null);
  const [results, setResults] = useState<Results | null>(null);
  const [watched, setWatched] = useState<string[]>([]);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (session?.user?.email) setEmail(session.user.email);
    });

    try {
      const raw = localStorage.getItem("exitplan_results");
      if (raw) {
        const parsed = JSON.parse(raw);
        if (parsed?.ranked_countries) setResults(parsed);
      }
    } catch {
      // ignore
    }
  }, []);

  const signOut = async () => {
    await supabase.auth.signOut();
    navigate({ to: "/" });
  };

  const toggleCountry = (code: string, checked: boolean) => {
    setWatched((prev) =>
      checked ? [...prev, code] : prev.filter((c) => c !== code),
    );
  };

  const savePrefs = () => {
    toast.success("Preferences saved!");
  };

  const top3 = results?.ranked_countries?.slice(0, 3) ?? [];

  return (
    <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      <h1 className="font-display text-3xl font-bold">Your Account</h1>

      {/* ── Section 1: Account info ── */}
      <section className="mt-8 rounded-2xl border border-border bg-card p-6">
        <h2 className="font-display text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Account
        </h2>
        <div className="mt-4 flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="font-display text-lg font-semibold">{email ?? "—"}</div>
            <span className="mt-1 inline-flex items-center gap-1.5 rounded-full bg-blue-100 px-2.5 py-0.5 text-xs font-semibold text-blue-800">
              Signed in with Google
            </span>
          </div>
          <button
            onClick={signOut}
            className="inline-flex items-center gap-2 rounded-lg border border-border px-4 py-2 text-sm font-semibold text-foreground/70 transition-colors hover:border-destructive hover:text-destructive"
          >
            <LogOut className="h-4 w-4" /> Sign out
          </button>
        </div>
      </section>

      {/* ── Section 2: Exit Plan results ── */}
      <section className="mt-6">
        <h2 className="font-display text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Your Exit Plan
        </h2>

        {top3.length === 0 ? (
          <div className="mt-3 rounded-2xl border border-dashed border-border bg-card p-6 text-center">
            <p className="text-sm text-muted-foreground">You haven't built your profile yet.</p>
            <Link
              to="/profile"
              className="mt-4 inline-flex items-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground"
            >
              Build profile <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        ) : (
          <>
            <div className="mt-3 grid gap-3 sm:grid-cols-3">
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
            <div className="mt-4 flex flex-wrap gap-3">
              <Link
                to="/profile"
                className="inline-flex items-center gap-2 rounded-lg border border-border bg-background px-4 py-2 text-sm font-semibold text-foreground/70 hover:border-primary hover:text-primary"
              >
                Rebuild profile
              </Link>
              <Link
                to="/results"
                className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground"
              >
                View full results <ArrowRight className="h-4 w-4" />
              </Link>
            </div>
          </>
        )}
      </section>

      {/* ── Section 3: Alert preferences ── */}
      <section className="mt-6">
        <h2 className="font-display text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Alert preferences
        </h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Watch these countries for policy changes:
        </p>
        <div className="mt-4 grid gap-2 sm:grid-cols-2">
          {ALL_COUNTRIES.map((c) => (
            <label
              key={c.code}
              className="flex cursor-pointer items-center gap-3 rounded-xl border border-border bg-card px-4 py-3 transition-colors hover:border-primary/40"
            >
              <input
                type="checkbox"
                checked={watched.includes(c.code)}
                onChange={(e) => toggleCountry(c.code, e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 accent-primary"
              />
              <span className="text-sm font-medium">
                {FLAGS[c.code]} {c.name}
              </span>
            </label>
          ))}
        </div>
        <button
          onClick={savePrefs}
          className="mt-4 inline-flex items-center rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground transition-opacity hover:opacity-90"
        >
          Save preferences
        </button>
      </section>
    </div>
  );
}

import { createFileRoute, Link } from "@tanstack/react-router";
import { Plus, Bell } from "lucide-react";

export const Route = createFileRoute("/dashboard")({
  component: Dashboard,
});

const PROFILES = [
  { id: 1, nationality: "India", field: "Computer Science", top: ["🇩🇪 Germany", "🇳🇱 Netherlands", "🇨🇦 Canada"], updated: "Updated 2 days ago" },
  { id: 2, nationality: "India", field: "Data Science", top: ["🇨🇦 Canada", "🇩🇪 Germany", "🇦🇺 Australia"], updated: "Updated 1 week ago" },
];

const ALERTS = [
  { flag: "🇬🇧", country: "United Kingdom", type: "Policy Change", msg: "Skilled Worker visa salary threshold rising to £38,700 from April.", date: "May 18, 2026" },
  { flag: "🇨🇦", country: "Canada", type: "Policy Change", msg: "Express Entry category-based draw now prioritizing healthcare and STEM.", date: "May 14, 2026" },
  { flag: "🇩🇪", country: "Germany", type: "Policy Change", msg: "Chancenkarte (Opportunity Card) points system expanded for IT roles.", date: "May 10, 2026" },
];

function Dashboard() {
  return (
    <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="font-display text-3xl font-bold sm:text-4xl">Your Exit Plans</h1>
        <button className="inline-flex items-center gap-2 rounded-lg border-2 border-primary bg-background px-4 py-2 font-display text-sm font-semibold text-primary transition-colors hover:bg-primary hover:text-primary-foreground">
          <Plus className="h-4 w-4" /> Add new profile
        </button>
      </div>

      <div className="mt-8 grid gap-6 lg:grid-cols-2">
        <section>
          <h2 className="mb-3 font-display text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            Saved profiles
          </h2>
          <div className="space-y-3">
            {PROFILES.map((p) => (
              <div key={p.id} className="rounded-2xl border border-border bg-card p-5 transition-colors hover:border-primary/40">
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="font-display text-lg font-semibold">
                      {p.nationality} · {p.field}
                    </div>
                    <div className="mt-1 text-xs text-muted-foreground">{p.updated}</div>
                  </div>
                  <Link to="/results" className="text-sm font-semibold text-primary hover:underline">
                    Open →
                  </Link>
                </div>
                <div className="mt-4 flex flex-wrap gap-2">
                  {p.top.map((c, i) => (
                    <span key={c} className={`rounded-full border px-3 py-1 text-xs font-medium ${i === 0 ? "border-primary/40 bg-primary/5 text-primary" : "border-border bg-background text-foreground/70"}`}>
                      {i === 0 && "🏆 "}{c}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2 className="mb-3 flex items-center gap-2 font-display text-sm font-semibold uppercase tracking-wider text-muted-foreground">
            <Bell className="h-4 w-4" /> Alert feed
          </h2>
          <div className="space-y-3">
            {ALERTS.map((a, i) => (
              <div key={i} className="rounded-2xl border border-border bg-card p-5">
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">{a.flag}</span>
                    <span className="font-display text-base font-semibold">{a.country}</span>
                  </div>
                  <span className="rounded-full bg-warning/15 px-2.5 py-1 font-display text-[11px] font-semibold uppercase tracking-wide text-warning">
                    {a.type}
                  </span>
                </div>
                <p className="mt-3 text-sm leading-relaxed text-foreground/80">{a.msg}</p>
                <div className="mt-3 flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">{a.date}</span>
                  <a className="font-semibold text-primary hover:underline" href="#">Read more →</a>
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}

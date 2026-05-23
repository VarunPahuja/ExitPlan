import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { ArrowLeft, Send } from "lucide-react";
import { COUNTRIES } from "@/lib/countries";
import { cn } from "@/lib/utils";

export const Route = createFileRoute("/country/$code")({
  component: CountryDetail,
});

const TABS = ["Overview", "Visa Types", "PR Pathway", "Job Market", "Recent Changes"] as const;
type Tab = (typeof TABS)[number];

function CountryDetail() {
  const { code } = Route.useParams();
  const country = COUNTRIES.find((c) => c.code === code) ?? COUNTRIES[0];
  const [tab, setTab] = useState<Tab>("Overview");

  return (
    <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
      <Link to="/results" className="inline-flex items-center gap-1 text-sm font-medium text-muted-foreground hover:text-primary">
        <ArrowLeft className="h-4 w-4" /> Back to results
      </Link>

      <div className="mt-6 grid gap-8 lg:grid-cols-5">
        <div className="lg:col-span-3">
          <div className="flex items-center gap-4">
            <span className="text-5xl">{country.flag}</span>
            <h1 className="font-display text-4xl font-extrabold sm:text-5xl">{country.name}</h1>
          </div>

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

          <div key={tab} className="mt-6 animate-fade-in-up rounded-2xl border border-border bg-card p-6">
            <h2 className="font-display text-xl font-bold">{tab}</h2>
            <p className="mt-3 leading-relaxed text-foreground/80">
              {tabCopy(tab, country.name)}
            </p>
            <ul className="mt-5 space-y-2 text-sm text-muted-foreground">
              <li>• Sourced from official government data — updated weekly.</li>
              <li>• Cross-referenced with LinkedIn job postings for {country.name}.</li>
              <li>• Last refreshed 2 days ago.</li>
            </ul>
          </div>
        </div>

        <div className="lg:col-span-2">
          <ChatPanel countryName={country.name} />
        </div>
      </div>
    </div>
  );
}

function tabCopy(tab: Tab, name: string) {
  switch (tab) {
    case "Overview": return `${name} at a glance — population, language(s), cost of living and the overall vibe for international students.`;
    case "Visa Types": return `The main visa categories that apply to students and post-study workers in ${name}, with eligibility, duration, and switching paths.`;
    case "PR Pathway": return `Step-by-step route to permanent residency in ${name}, typical timelines, and the trade-offs at each stage.`;
    case "Job Market": return `Hiring trends in ${name} for your field, average salaries, and which cities are pulling ahead.`;
    case "Recent Changes": return `Policy updates from the last 90 days in ${name} that might affect your plan.`;
  }
}

function ChatPanel({ countryName }: { countryName: string }) {
  const [input, setInput] = useState("");
  const [msgs, setMsgs] = useState<{ role: "user" | "assistant"; text: string }[]>([
    { role: "assistant", text: `Hi! Ask me anything about living and working in ${countryName}. I'll answer based on official sources.` },
  ]);

  const send = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    const q = input.trim();
    setInput("");
    setMsgs((m) => [...m, { role: "user", text: q }]);
    setTimeout(() => {
      setMsgs((m) => [...m, { role: "assistant", text: `Here's what I found about "${q}" for ${countryName}. (Connect an AI provider to get real answers.)` }]);
    }, 600);
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
              "max-w-[85%] rounded-2xl px-4 py-2.5 text-sm leading-relaxed",
              m.role === "assistant"
                ? "bg-accent text-accent-foreground"
                : "ml-auto bg-primary text-primary-foreground",
            )}
          >
            {m.text}
          </div>
        ))}
      </div>
      <form onSubmit={send} className="flex items-center gap-2 border-t border-border bg-background p-3">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask anything about visas, jobs, PR..."
          className="flex-1 rounded-lg border border-border bg-card px-3 py-2 text-sm outline-none focus:border-primary"
        />
        <button
          type="submit"
          className="inline-flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground transition-colors hover:bg-primary/90"
          aria-label="Send"
        >
          <Send className="h-4 w-4" />
        </button>
      </form>
    </div>
  );
}

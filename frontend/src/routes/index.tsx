import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, X } from "lucide-react";

export const Route = createFileRoute("/")({
  component: Landing,
});

const HERO_IMG =
  "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=1800&q=80&auto=format&fit=crop";


function DottedPath({ className = "" }: { className?: string }) {
  return (
    <svg
      aria-hidden
      viewBox="0 0 200 1200"
      preserveAspectRatio="none"
      className={className}
      fill="none"
    >
      <path
        d="M100 0 C 20 200, 180 400, 80 600 S 20 1000, 120 1200"
        stroke="#FF6B35"
        strokeWidth="2.5"
        strokeDasharray="2 10"
        strokeLinecap="round"
      />
    </svg>
  );
}

function Landing() {
  return (
    <div className="bg-[#FAFAF8] text-[#0A0A0A]">
      {/* ============ HERO ============ */}
      <section className="relative min-h-screen w-full overflow-hidden bg-[#0A0A0A] text-white">
        <img
          src={HERO_IMG}
          alt="Aerial view from a plane window"
          className="absolute inset-0 h-full w-full object-cover"
          loading="eager"
        />
        <div className="absolute inset-0 bg-[#0A0A0A]/60" />

        {/* Wordmark */}
        <div className="absolute left-6 top-6 z-10 sm:left-10 sm:top-8">
          <span className="font-sans text-[11px] font-semibold uppercase tracking-[0.3em] text-white">
            Exit Plan
          </span>
        </div>

        {/* Center content */}
        <div className="relative z-10 mx-auto flex min-h-screen max-w-[1200px] flex-col justify-center px-6 py-32 text-center sm:px-10">
          <h1 className="font-serif text-[56px] font-black leading-[0.95] tracking-[-0.02em] sm:text-[64px] md:text-[72px]">
            <span className="block">FIND YOUR</span>
            <span className="block text-[#FF6B35]">EXIT PLAN</span>
          </h1>
          <p className="mt-8 max-w-xl font-display text-base font-medium leading-relaxed text-white/60 sm:text-lg mx-auto">
            Real-time country rankings, personalized to you.
            <br />
            Not Reddit. Not a consultant. Your actual next move.
          </p>
          <div className="mt-10 flex flex-col items-center gap-3">
            <Link
              to="/profile"
              className="group inline-flex items-center gap-3 rounded-full bg-[#FF6B35] px-8 py-4 font-display text-base font-semibold text-white shadow-xl shadow-[#FF6B35]/20 transition-all hover:-translate-y-0.5 hover:bg-[#FF7d4d]"
            >
              Find my country
              <ArrowRight className="h-5 w-5 transition-transform group-hover:translate-x-1" />
            </Link>
            <p className="font-sans text-xs uppercase tracking-[0.2em] text-white/40">
              No signup required
            </p>
          </div>
        </div>

      </section>

      {/* ============ SECTION 2 — PROBLEM ============ */}
      <section className="relative bg-[#FAFAF8] px-6 py-24 sm:px-10 sm:py-32">
        <DottedPath className="pointer-events-none absolute -right-4 top-0 hidden h-full w-32 md:block" />
        <div className="mx-auto grid max-w-[1200px] gap-16 md:grid-cols-2 md:gap-20">
          <div>
            <h2 className="font-serif text-[40px] font-black leading-[1.05] tracking-[-0.02em] text-[#0A0A0A] sm:text-[56px] md:text-[72px]">
              You're making a life-changing decision with the worst possible information.
            </h2>
            <p className="mt-10 font-serif text-2xl italic text-[#FF6B35] sm:text-3xl">
              There's a better way.
            </p>
          </div>
          <div className="flex flex-col gap-4 md:pt-6">
            {[
              "Reddit threads from 2019",
              "Consultants charging ₹1,50,000",
              "Generic visa sites with no personalization",
            ].map((t) => (
              <div
                key={t}
                className="flex items-start gap-4 rounded-2xl bg-[#F1F0EC] p-6"
              >
                <span className="mt-0.5 flex h-8 w-8 flex-none items-center justify-center rounded-full bg-red-100 text-red-600">
                  <X className="h-4 w-4" strokeWidth={3} />
                </span>
                <p className="font-display text-lg font-semibold text-[#0A0A0A]">
                  {t}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============ SECTION 3 — HOW IT WORKS ============ */}
      <section className="relative overflow-hidden bg-[#F5F4F0] px-6 py-24 sm:px-10 sm:py-32">
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <span className="select-none font-serif text-[280px] font-black leading-none text-[#EBEBEB] sm:text-[400px] md:text-[560px]">
            HOW
          </span>
        </div>
        <DottedPath className="pointer-events-none absolute -left-4 top-0 hidden h-full w-32 md:block" />

        <div className="relative mx-auto max-w-[1200px]">
          <h2 className="text-center font-serif text-[40px] font-black leading-[1.05] tracking-[-0.02em] text-[#0A0A0A] sm:text-[56px] md:text-[64px]">
            Three steps to your exit plan
          </h2>

          <div className="relative mt-20 grid gap-12 md:grid-cols-3 md:gap-8">
            {/* dotted connector */}
            <svg
              aria-hidden
              className="pointer-events-none absolute left-[16%] right-[16%] top-12 hidden h-2 md:block"
              viewBox="0 0 800 8"
              preserveAspectRatio="none"
            >
              <line
                x1="0"
                y1="4"
                x2="800"
                y2="4"
                stroke="#FF6B35"
                strokeWidth="2.5"
                strokeDasharray="2 10"
                strokeLinecap="round"
              />
            </svg>

            {[
              { n: "01", t: "Tell us who you are", b: "Nationality, field, finances." },
              { n: "02", t: "Set your priorities", b: "Drag to rank what matters most." },
              { n: "03", t: "Get your map", b: "Ranked countries + knowledge graph." },
            ].map((s) => (
              <div key={s.n} className="relative text-center">
                <div className="relative inline-block">
                  <span className="font-display text-[120px] font-extrabold leading-none text-[#FF6B35]/15">
                    {s.n}
                  </span>
                  <span className="absolute inset-0 flex items-center justify-center font-display text-sm font-bold uppercase tracking-[0.2em] text-[#FF6B35]">
                    Step {s.n}
                  </span>
                </div>
                <h3 className="mt-2 font-serif text-2xl font-bold text-[#0A0A0A] sm:text-3xl">
                  {s.t}
                </h3>
                <p className="mt-3 font-sans text-base text-[#8B8B8B]">{s.b}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ============ SECTION 4 — COLOR BLOCK ============ */}
      <section className="relative overflow-hidden bg-[#FF6B35] px-6 py-28 text-white sm:px-10 sm:py-36">
        <DottedPath className="pointer-events-none absolute -right-4 top-0 hidden h-full w-32 opacity-40 md:block" />
        <div className="mx-auto max-w-[1200px] text-center">
          <ul className="space-y-2 font-serif text-[44px] font-black uppercase leading-[1.05] tracking-[-0.02em] sm:text-[72px] md:text-[96px]">
            <li>Real-time data</li>
            <li className="italic font-normal">Your priorities</li>
            <li>10 countries</li>
            <li className="italic font-normal">AI-powered</li>
            <li>Always updated</li>
          </ul>
          <p className="mt-14 font-display text-base font-medium text-white/80 sm:text-lg">
            Everything a consultant charges ₹1,50,000 for. Free.
          </p>
        </div>
      </section>

      {/* ============ SECTION 5 — TRUST ============ */}
      <section className="bg-[#FAFAF8] px-6 py-24 sm:px-10 sm:py-32">
        <div className="mx-auto max-w-[1200px] text-center">
          <p className="font-sans text-xs font-semibold uppercase tracking-[0.3em] text-[#8B8B8B]">
            Data Sources
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            {["UKVI", "IRCC", "BAMF", "DHA", "LinkedIn", "Indeed"].map((s) => (
              <span
                key={s}
                className="rounded-full border border-[#5B4FE8]/20 bg-[#5B4FE8]/5 px-5 py-2 font-display text-sm font-semibold text-[#5B4FE8]"
              >
                {s}
              </span>
            ))}
          </div>
          <p className="mx-auto mt-12 max-w-3xl font-serif text-3xl italic leading-snug text-[#0A0A0A] sm:text-4xl md:text-5xl">
            Built on official government sources, not forums.
          </p>
        </div>
      </section>

      {/* ============ FOOTER ============ */}
      <footer className="bg-[#0A0A0A] px-6 py-20 text-white sm:px-10">
        <div className="mx-auto max-w-[1200px]">
          <div className="flex flex-col items-start justify-between gap-8 sm:flex-row sm:items-end">
            <span className="font-display text-4xl font-extrabold tracking-tight sm:text-5xl">
              EXIT PLAN
            </span>
            <span className="font-serif text-2xl italic text-[#FF6B35] sm:text-3xl">
              Your move. Your rules.
            </span>
          </div>
          <div className="mt-16 border-t border-white/10 pt-8 text-center">
            <p className="font-sans text-xs uppercase tracking-[0.25em] text-white/40">
              Made for the ones who are going places.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

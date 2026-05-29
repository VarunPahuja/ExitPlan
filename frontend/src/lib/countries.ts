import type { Priority } from "./profile-store";

export type Country = {
  code: string;
  name: string;
  flag: string;
  scores: Record<Priority, number>;
  verdict: string;
};

export const COUNTRIES: Country[] = [
  {
    code: "DE", name: "Germany", flag: "🇩🇪",
    scores: { job: 88, pr: 78, visa: 82, salary: 74, language: 55 },
    verdict: "Strong job market, fast PR if you stick around — language helps a lot.",
  },
  {
    code: "CA", name: "Canada", flag: "🇨🇦",
    scores: { job: 70, pr: 85, visa: 80, salary: 62, language: 92 },
    verdict: "Clearest PR pathway in the world, but jobs are tighter than they were.",
  },
  {
    code: "GB", name: "United Kingdom", flag: "🇬🇧",
    scores: { job: 72, pr: 55, visa: 65, salary: 70, language: 95 },
    verdict: "Great salaries in your field; PR takes patience and paperwork.",
  },
  {
    code: "AU", name: "Australia", flag: "🇦🇺",
    scores: { job: 78, pr: 72, visa: 68, salary: 80, language: 94 },
    verdict: "High pay, high cost of living — points-based system rewards your profile.",
  },
  {
    code: "NL", name: "Netherlands", flag: "🇳🇱",
    scores: { job: 82, pr: 68, visa: 88, salary: 76, language: 78 },
    verdict: "Highly skilled migrant visa is one of the smoothest in Europe.",
  },
  {
    code: "PT", name: "Portugal", flag: "🇵🇹",
    scores: { job: 60, pr: 65, visa: 75, salary: 55, language: 62 },
    verdict: "NHR tax regime and EU access make it a favourite for remote workers.",
  },
  {
    code: "IE", name: "Ireland", flag: "🇮🇪",
    scores: { job: 78, pr: 70, visa: 72, salary: 72, language: 95 },
    verdict: "Tech hub of Europe with a clear English-speaking PR pathway.",
  },
  {
    code: "AE", name: "United Arab Emirates", flag: "🇦🇪",
    scores: { job: 75, pr: 40, visa: 80, salary: 85, language: 70 },
    verdict: "Tax-free salaries but no clear path to permanent residency.",
  },
  {
    code: "NZ", name: "New Zealand", flag: "🇳🇿",
    scores: { job: 65, pr: 75, visa: 70, salary: 68, language: 93 },
    verdict: "Relaxed points-based system, but the job market is smaller than Australia's.",
  },
  {
    code: "SG", name: "Singapore", flag: "🇸🇬",
    scores: { job: 82, pr: 62, visa: 78, salary: 88, language: 90 },
    verdict: "Asia's tech gateway — high salaries, competitive PR, and low taxes.",
  },
];

const WEIGHTS = [35, 25, 20, 12, 8];

export function rankCountries(priorities: Priority[]) {
  return [...COUNTRIES]
    .map((c) => {
      const total = priorities.reduce(
        (sum, p, i) => sum + (c.scores[p] * WEIGHTS[i]) / 100,
        0,
      );
      return { ...c, total: Math.round(total) };
    })
    .sort((a, b) => b.total - a.total);
}

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
    code: "de", name: "Germany", flag: "🇩🇪",
    scores: { job: 88, pr: 78, visa: 82, salary: 74, language: 55 },
    verdict: "Strong job market, fast PR if you stick around — language helps a lot.",
  },
  {
    code: "ca", name: "Canada", flag: "🇨🇦",
    scores: { job: 70, pr: 85, visa: 80, salary: 62, language: 92 },
    verdict: "Clearest PR pathway in the world, but jobs are tighter than they were.",
  },
  {
    code: "uk", name: "United Kingdom", flag: "🇬🇧",
    scores: { job: 72, pr: 55, visa: 65, salary: 70, language: 95 },
    verdict: "Great salaries in your field; PR takes patience and paperwork.",
  },
  {
    code: "au", name: "Australia", flag: "🇦🇺",
    scores: { job: 78, pr: 72, visa: 68, salary: 80, language: 94 },
    verdict: "High pay, high cost of living — points-based system rewards your profile.",
  },
  {
    code: "nl", name: "Netherlands", flag: "🇳🇱",
    scores: { job: 82, pr: 68, visa: 88, salary: 76, language: 78 },
    verdict: "Highly skilled migrant visa is one of the smoothest in Europe.",
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

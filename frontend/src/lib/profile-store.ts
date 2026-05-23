import { useSyncExternalStore } from "react";

export type Priority = "job" | "pr" | "visa" | "salary" | "language";

export const PRIORITY_LABELS: Record<Priority, { title: string; desc: string }> = {
  job: { title: "Job Market", desc: "How easy is it to find work in your field?" },
  pr: { title: "PR Timeline", desc: "How fast can you get permanent residency?" },
  visa: { title: "Visa Ease", desc: "How straightforward is the visa process?" },
  salary: { title: "Salary vs Cost", desc: "Will you actually save money there?" },
  language: { title: "Language", desc: "How much does not knowing the local language hurt?" },
};

export const PRIORITY_WEIGHTS = [35, 25, 20, 12, 8];

export type ProfileState = {
  nationality: string;
  status: string;
  field: string;
  degree: string;
  savings: string;
  goal: string;
  priorities: Priority[];
};

const KEY = "exitplan:profile";

const defaultState: ProfileState = {
  nationality: "India",
  status: "",
  field: "",
  degree: "",
  savings: "",
  goal: "",
  priorities: ["job", "pr", "visa", "salary", "language"],
};

let state: ProfileState = loadInitial();
const listeners = new Set<() => void>();

function loadInitial(): ProfileState {
  if (typeof window === "undefined") return defaultState;
  try {
    const raw = window.sessionStorage.getItem(KEY);
    if (raw) return { ...defaultState, ...JSON.parse(raw) };
  } catch {}
  return defaultState;
}

function persist() {
  if (typeof window !== "undefined") {
    try { window.sessionStorage.setItem(KEY, JSON.stringify(state)); } catch {}
  }
}

export function setProfile(patch: Partial<ProfileState>) {
  state = { ...state, ...patch };
  persist();
  listeners.forEach((l) => l());
}

function subscribe(l: () => void) {
  listeners.add(l);
  return () => listeners.delete(l);
}

export function useProfile() {
  return useSyncExternalStore(subscribe, () => state, () => defaultState);
}

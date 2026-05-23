import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import {
  ArrowLeft,
  ArrowRight,
  Briefcase,
  GraduationCap,
  Hourglass,
  Search,
  GripVertical,
  Loader2,
} from "lucide-react";
import {
  DndContext,
  closestCenter,
  PointerSensor,
  KeyboardSensor,
  useSensor,
  useSensors,
  type DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  arrayMove,
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { toast } from "sonner";

export const Route = createFileRoute("/profile")({
  component: ProfilePage,
});

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL ?? "http://localhost:8000";

// ---------- Data ----------
const COUNTRIES: { code: string; name: string }[] = [
  { code: "IN", name: "India" },
  ...[
    ["AU", "Australia"], ["AT", "Austria"], ["BD", "Bangladesh"], ["BE", "Belgium"],
    ["BR", "Brazil"], ["CA", "Canada"], ["CN", "China"], ["CO", "Colombia"],
    ["DK", "Denmark"], ["EG", "Egypt"], ["FI", "Finland"], ["FR", "France"],
    ["DE", "Germany"], ["GR", "Greece"], ["HK", "Hong Kong"], ["ID", "Indonesia"],
    ["IE", "Ireland"], ["IL", "Israel"], ["IT", "Italy"], ["JP", "Japan"],
    ["KE", "Kenya"], ["MY", "Malaysia"], ["MX", "Mexico"], ["NP", "Nepal"],
    ["NL", "Netherlands"], ["NZ", "New Zealand"], ["NG", "Nigeria"], ["NO", "Norway"],
    ["PK", "Pakistan"], ["PH", "Philippines"], ["PL", "Poland"], ["PT", "Portugal"],
    ["QA", "Qatar"], ["RO", "Romania"], ["RU", "Russia"], ["SA", "Saudi Arabia"],
    ["SG", "Singapore"], ["ZA", "South Africa"], ["KR", "South Korea"], ["ES", "Spain"],
    ["LK", "Sri Lanka"], ["SE", "Sweden"], ["CH", "Switzerland"], ["TW", "Taiwan"],
    ["TH", "Thailand"], ["TR", "Turkey"], ["UA", "Ukraine"], ["AE", "United Arab Emirates"],
    ["GB", "United Kingdom"], ["US", "United States"], ["VN", "Vietnam"],
  ]
    .map(([code, name]) => ({ code, name }))
    .sort((a, b) => a.name.localeCompare(b.name)),
];

const FIELDS = [
  { value: "computer_science", label: "Computer Science" },
  { value: "data_science", label: "Data Science" },
  { value: "engineering", label: "Engineering" },
  { value: "business", label: "Business" },
  { value: "medicine", label: "Medicine" },
  { value: "law", label: "Law" },
  { value: "design", label: "Design" },
  { value: "finance", label: "Finance" },
  { value: "other", label: "Other" },
];

type PriorityKey =
  | "job_market"
  | "pr_timeline"
  | "visa_ease"
  | "salary_cost_ratio"
  | "language";

const PRIORITIES: { key: PriorityKey; title: string; desc: string }[] = [
  { key: "job_market", title: "Job Market", desc: "Find work in your field" },
  { key: "pr_timeline", title: "PR Timeline", desc: "Speed to permanent residency" },
  { key: "visa_ease", title: "Visa Ease", desc: "How hard is the visa process" },
  { key: "salary_cost_ratio", title: "Salary vs Cost", desc: "Will you actually save money" },
  { key: "language", title: "Language", desc: "Barrier of not knowing local language" },
];

const WEIGHTS = [0.35, 0.25, 0.2, 0.12, 0.08];

type FormState = {
  nationality: string;
  current_status: "" | "student" | "post_study" | "employed";
  field: string;
  degree_level: "" | "bachelors" | "masters" | "phd" | "diploma";
  savings_range: "" | "0_5L" | "5_15L" | "15L_plus";
  career_goal: "" | "long_term_pr" | "work_experience" | "return_home";
  priorities: PriorityKey[];
};

const INDIGO = "#5B4FE8";
const ORANGE = "#FF6B35";

// ---------- Page ----------
function ProfilePage() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState<FormState>({
    nationality: "IN",
    current_status: "",
    field: "",
    degree_level: "",
    savings_range: "",
    career_goal: "",
    priorities: PRIORITIES.map((p) => p.key),
  });

  const update = <K extends keyof FormState>(k: K, v: FormState[K]) =>
    setForm((f) => ({ ...f, [k]: v }));

  const canAdvance = useMemo(() => {
    switch (step) {
      case 1: return !!form.nationality && !!form.current_status;
      case 2: return !!form.field && !!form.degree_level;
      case 3: return !!form.savings_range;
      case 4: return !!form.career_goal;
      case 5: return form.priorities.length === 5;
      default: return false;
    }
  }, [step, form]);

  const handleSubmit = async () => {
    const weights = form.priorities.reduce<Record<string, number>>((acc, key, i) => {
      acc[key] = WEIGHTS[i];
      return acc;
    }, {});
    const payload = {
      nationality: form.nationality,
      current_status: form.current_status,
      field: form.field,
      degree_level: form.degree_level,
      savings_range: form.savings_range,
      career_goal: form.career_goal,
      weights,
    };
    setSubmitting(true);
    try {
      const res = await fetch(`${BACKEND_URL}/rank/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("bad status");
      const data = await res.json();
      localStorage.setItem("exitplan_results", JSON.stringify(data));
      navigate({ to: "/results" });
    } catch {
      toast.error("Something went wrong. Make sure the backend is running.");
    } finally {
      setSubmitting(false);
    }
  };

  const next = () => {
    if (!canAdvance) return;
    if (step === 5) return handleSubmit();
    setStep((s) => Math.min(5, s + 1));
  };
  const back = () => setStep((s) => Math.max(1, s - 1));

  return (
    <div className="min-h-screen bg-[#FAFAF8] text-[#0A0A0A]">
      {/* Progress */}
      <div className="sticky top-0 z-20 border-b border-black/5 bg-[#FAFAF8]/90 backdrop-blur">
        <div className="mx-auto flex max-w-3xl items-center gap-4 px-6 py-4">
          <span className="font-[Plus_Jakarta_Sans] text-lg font-extrabold tracking-tight" style={{ color: INDIGO }}>
            Exit Plan
          </span>
          <div className="flex-1">
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-black/10">
              <div
                className="h-full rounded-full transition-[width] duration-500 ease-out"
                style={{ width: `${(step / 5) * 100}%`, background: INDIGO }}
              />
            </div>
          </div>
          <span className="text-sm font-medium tabular-nums text-black/60">
            Step {step} / 5
          </span>
        </div>
      </div>

      {/* Step content */}
      <main className="mx-auto max-w-3xl px-6 py-12 sm:py-20">
        {step === 1 && <Step1 form={form} update={update} />}
        {step === 2 && <Step2 form={form} update={update} />}
        {step === 3 && <Step3 form={form} update={update} />}
        {step === 4 && <Step4 form={form} update={update} />}
        {step === 5 && (
          <Step5
            priorities={form.priorities}
            setPriorities={(p) => update("priorities", p)}
          />
        )}

        {/* Footer buttons */}
        <div className="mt-14 flex items-center justify-between gap-4">
          <button
            type="button"
            onClick={back}
            disabled={step === 1}
            className="inline-flex items-center gap-2 rounded-full border border-black/15 bg-white px-5 py-3 text-sm font-semibold text-black/80 transition hover:border-black/40 disabled:cursor-not-allowed disabled:opacity-30"
          >
            <ArrowLeft className="h-4 w-4" /> Back
          </button>
          <button
            type="button"
            onClick={next}
            disabled={!canAdvance || submitting}
            className="group inline-flex flex-1 items-center justify-center gap-2 rounded-full px-6 py-4 text-base font-semibold text-white shadow-[0_10px_30px_-10px_rgba(255,107,53,0.6)] transition hover:translate-y-[-1px] hover:shadow-[0_14px_36px_-10px_rgba(255,107,53,0.7)] disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:translate-y-0 sm:flex-none sm:min-w-[220px]"
            style={{ background: ORANGE }}
          >
            {submitting ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" /> Finding…
              </>
            ) : step === 5 ? (
              <>Find my countries <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" /></>
            ) : (
              <>Next <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" /></>
            )}
          </button>
        </div>
      </main>
    </div>
  );
}

// ---------- Shared bits ----------
function StepHeading({ eyebrow, title, sub }: { eyebrow: string; title: string; sub?: string }) {
  return (
    <header className="mb-10">
      <p className="mb-3 text-xs font-semibold uppercase tracking-[0.25em]" style={{ color: ORANGE }}>
        {eyebrow}
      </p>
      <h1 className="font-[Plus_Jakarta_Sans] text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl">
        {title}
      </h1>
      {sub && <p className="mt-4 text-base text-black/60">{sub}</p>}
    </header>
  );
}

function CardOption({
  active, onClick, icon, title, desc,
}: {
  active: boolean; onClick: () => void;
  icon?: React.ReactNode; title: string; desc?: string;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`group flex w-full items-center gap-4 rounded-2xl border bg-white p-5 text-left transition ${
        active
          ? "border-[var(--c)] shadow-[0_10px_30px_-12px_var(--c)] ring-2 ring-[var(--c)]/20"
          : "border-black/10 hover:border-black/30 hover:translate-y-[-1px]"
      }`}
      style={{ ["--c" as never]: INDIGO }}
    >
      {icon && (
        <span
          className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-xl transition ${
            active ? "text-white" : "bg-black/[0.04] text-black/70"
          }`}
          style={active ? { background: INDIGO } : undefined}
        >
          {icon}
        </span>
      )}
      <span className="flex-1">
        <span className="block font-[Plus_Jakarta_Sans] text-lg font-bold">{title}</span>
        {desc && <span className="mt-0.5 block text-sm text-black/55">{desc}</span>}
      </span>
    </button>
  );
}

function SearchableSelect({
  value, onChange, options, placeholder,
}: {
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string; sub?: string }[];
  placeholder: string;
}) {
  const [open, setOpen] = useState(false);
  const [q, setQ] = useState("");
  const filtered = useMemo(
    () => options.filter((o) => o.label.toLowerCase().includes(q.toLowerCase())),
    [q, options],
  );
  const selected = options.find((o) => o.value === value);
  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-3 rounded-2xl border border-black/10 bg-white px-5 py-4 text-left transition hover:border-black/30 focus:border-[var(--c)] focus:outline-none focus:ring-2 focus:ring-[var(--c)]/20"
        style={{ ["--c" as never]: INDIGO }}
      >
        <span className={selected ? "font-medium" : "text-black/40"}>
          {selected ? selected.label : placeholder}
        </span>
        <Search className="h-4 w-4 text-black/40" />
      </button>
      {open && (
        <div className="absolute z-30 mt-2 w-full overflow-hidden rounded-2xl border border-black/10 bg-white shadow-xl">
          <div className="border-b border-black/5 p-2">
            <input
              autoFocus
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="Search…"
              className="w-full rounded-lg px-3 py-2 text-sm outline-none"
            />
          </div>
          <ul className="max-h-72 overflow-auto py-1">
            {filtered.length === 0 && (
              <li className="px-4 py-3 text-sm text-black/40">No matches</li>
            )}
            {filtered.map((o) => (
              <li key={o.value}>
                <button
                  type="button"
                  onClick={() => { onChange(o.value); setOpen(false); setQ(""); }}
                  className={`flex w-full items-center justify-between px-4 py-2.5 text-left text-sm transition hover:bg-black/[0.04] ${
                    value === o.value ? "font-semibold" : ""
                  }`}
                  style={value === o.value ? { color: INDIGO } : undefined}
                >
                  <span>{o.label}</span>
                  {o.sub && <span className="text-xs text-black/40">{o.sub}</span>}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

// ---------- Steps ----------
function Step1({ form, update }: { form: FormState; update: <K extends keyof FormState>(k: K, v: FormState[K]) => void }) {
  return (
    <div>
      <StepHeading eyebrow="Step 1 · Background" title="Where are you from?" />
      <div className="space-y-8">
        <div>
          <label className="mb-2 block text-sm font-semibold text-black/70">Nationality</label>
          <SearchableSelect
            value={form.nationality}
            onChange={(v) => update("nationality", v)}
            options={COUNTRIES.map((c) => ({ value: c.code, label: c.name, sub: c.code }))}
            placeholder="Select your nationality"
          />
        </div>
        <div>
          <label className="mb-3 block text-sm font-semibold text-black/70">Current status</label>
          <div className="grid gap-3">
            <CardOption
              active={form.current_status === "student"}
              onClick={() => update("current_status", "student")}
              icon={<GraduationCap className="h-6 w-6" />}
              title="Currently Studying"
              desc="On a student visa abroad right now"
            />
            <CardOption
              active={form.current_status === "post_study"}
              onClick={() => update("current_status", "post_study")}
              icon={<Hourglass className="h-6 w-6" />}
              title="Post-Study Visa"
              desc="Graduated, on a job-search visa"
            />
            <CardOption
              active={form.current_status === "employed"}
              onClick={() => update("current_status", "employed")}
              icon={<Briefcase className="h-6 w-6" />}
              title="Employed Abroad"
              desc="Working on a work visa"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function Step2({ form, update }: { form: FormState; update: <K extends keyof FormState>(k: K, v: FormState[K]) => void }) {
  return (
    <div>
      <StepHeading eyebrow="Step 2 · Education" title="What did you study?" />
      <div className="space-y-8">
        <div>
          <label className="mb-2 block text-sm font-semibold text-black/70">Field of study</label>
          <SearchableSelect
            value={form.field}
            onChange={(v) => update("field", v)}
            options={FIELDS}
            placeholder="Pick your field"
          />
        </div>
        <div>
          <label className="mb-3 block text-sm font-semibold text-black/70">Degree level</label>
          <div className="grid grid-cols-2 gap-3">
            {(["bachelors", "masters", "phd", "diploma"] as const).map((d) => (
              <CardOption
                key={d}
                active={form.degree_level === d}
                onClick={() => update("degree_level", d)}
                title={d === "phd" ? "PhD" : d[0].toUpperCase() + d.slice(1)}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function Step3({ form, update }: { form: FormState; update: <K extends keyof FormState>(k: K, v: FormState[K]) => void }) {
  const opts: { value: FormState["savings_range"]; title: string }[] = [
    { value: "0_5L", title: "Under ₹5 Lakhs (~$6K)" },
    { value: "5_15L", title: "₹5–15 Lakhs ($6K–$18K)" },
    { value: "15L_plus", title: "₹15 Lakhs+ ($18K+)" },
  ];
  return (
    <div>
      <StepHeading eyebrow="Step 3 · Finances" title="What are your savings?" />
      <div className="grid gap-3">
        {opts.map((o) => (
          <CardOption
            key={o.value}
            active={form.savings_range === o.value}
            onClick={() => update("savings_range", o.value)}
            title={o.title}
          />
        ))}
      </div>
      <p className="mt-4 text-sm text-black/50">
        This helps us filter countries by minimum fund requirements.
      </p>
    </div>
  );
}

function Step4({ form, update }: { form: FormState; update: <K extends keyof FormState>(k: K, v: FormState[K]) => void }) {
  const opts: { value: FormState["career_goal"]; title: string; desc: string }[] = [
    { value: "long_term_pr", title: "Permanent Residency", desc: "Stay long term, get PR" },
    { value: "work_experience", title: "Work Experience", desc: "Gain experience, decide later" },
    { value: "return_home", title: "Return Home", desc: "Earn abroad, come back" },
  ];
  return (
    <div>
      <StepHeading eyebrow="Step 4 · Goal" title="What's your end goal?" />
      <div className="grid gap-3">
        {opts.map((o) => (
          <CardOption
            key={o.value}
            active={form.career_goal === o.value}
            onClick={() => update("career_goal", o.value)}
            title={o.title}
            desc={o.desc}
          />
        ))}
      </div>
    </div>
  );
}

// ---- Step 5 with dnd-kit ----
function Step5({
  priorities, setPriorities,
}: { priorities: PriorityKey[]; setPriorities: (p: PriorityKey[]) => void }) {
  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 4 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates }),
  );
  const onDragEnd = (e: DragEndEvent) => {
    const { active, over } = e;
    if (!over || active.id === over.id) return;
    const oldIdx = priorities.indexOf(active.id as PriorityKey);
    const newIdx = priorities.indexOf(over.id as PriorityKey);
    setPriorities(arrayMove(priorities, oldIdx, newIdx));
  };
  return (
    <div>
      <StepHeading
        eyebrow="Step 5 · Priorities"
        title="What matters most to you?"
        sub="Drag to reorder. Your ranking directly changes your results."
      />
      <DndContext sensors={sensors} collisionDetection={closestCenter} onDragEnd={onDragEnd}>
        <SortableContext items={priorities} strategy={verticalListSortingStrategy}>
          <ul className="space-y-3">
            {priorities.map((key, i) => {
              const p = PRIORITIES.find((x) => x.key === key)!;
              return (
                <SortableRow
                  key={key}
                  id={key}
                  rank={i + 1}
                  weight={WEIGHTS[i]}
                  title={p.title}
                  desc={p.desc}
                />
              );
            })}
          </ul>
        </SortableContext>
      </DndContext>
    </div>
  );
}

function SortableRow({
  id, rank, weight, title, desc,
}: { id: string; rank: number; weight: number; title: string; desc: string }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({ id });
  const style: React.CSSProperties = {
    transform: CSS.Transform.toString(transform),
    transition,
  };
  const pct = Math.round(weight * 100);
  return (
    <li
      ref={setNodeRef}
      style={style}
      className={`flex items-center gap-4 rounded-2xl border bg-white p-4 ${
        isDragging
          ? "z-10 border-[#5B4FE8] shadow-[0_18px_40px_-12px_rgba(91,79,232,0.4)]"
          : "border-black/10"
      }`}
    >
      <button
        type="button"
        {...attributes}
        {...listeners}
        className="flex h-10 w-10 cursor-grab items-center justify-center rounded-lg text-black/30 transition hover:bg-black/[0.04] hover:text-black/60 active:cursor-grabbing"
        aria-label="Drag to reorder"
      >
        <GripVertical className="h-5 w-5" />
      </button>
      <span
        className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full text-sm font-bold text-white"
        style={{ background: INDIGO }}
      >
        {rank}
      </span>
      <div className="flex-1">
        <div className="font-[Plus_Jakarta_Sans] text-base font-bold">{title}</div>
        <div className="text-sm text-black/55">{desc}</div>
      </div>
      <div className="flex flex-col items-end">
        <span className="font-[Plus_Jakarta_Sans] text-xl font-extrabold tabular-nums" style={{ color: ORANGE }}>
          {pct}%
        </span>
        <span className="text-[10px] font-semibold uppercase tracking-wider text-black/40">weight</span>
      </div>
    </li>
  );
}

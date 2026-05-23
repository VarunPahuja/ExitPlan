import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";
import { supabase } from "@/lib/supabase";

export const Route = createFileRoute("/signin")({
  component: SignIn,
});

const INDIGO = "#5B4FE8";

function GoogleIcon() {
  return (
    <svg viewBox="0 0 48 48" className="h-5 w-5">
      <path fill="#FFC107" d="M43.6 20.5H42V20H24v8h11.3c-1.6 4.6-6 8-11.3 8-6.6 0-12-5.4-12-12s5.4-12 12-12c3 0 5.8 1.1 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 12.9 4 4 12.9 4 24s8.9 20 20 20 20-8.9 20-20c0-1.3-.1-2.4-.4-3.5z"/>
      <path fill="#FF3D00" d="M6.3 14.7l6.6 4.8C14.6 16 18.9 13 24 13c3 0 5.8 1.1 7.9 3l5.7-5.7C34 6.1 29.3 4 24 4 16.1 4 9.3 8.5 6.3 14.7z"/>
      <path fill="#4CAF50" d="M24 44c5.2 0 9.9-2 13.4-5.2l-6.2-5.2c-2 1.4-4.5 2.4-7.2 2.4-5.3 0-9.7-3.4-11.3-8l-6.5 5C9.2 39.4 16 44 24 44z"/>
      <path fill="#1976D2" d="M43.6 20.5H42V20H24v8h11.3c-.8 2.2-2.2 4.1-4.1 5.5l6.2 5.2C40.9 35.7 44 30.3 44 24c0-1.3-.1-2.4-.4-3.5z"/>
    </svg>
  );
}

function SignIn() {
  const [loading, setLoading] = useState(false);

  const handleGoogle = async () => {
    setLoading(true);
    try {
      const { error } = await supabase.auth.signInWithOAuth({
        provider: "google",
        options: {
          redirectTo: window.location.origin + "/results",
        },
      });
      if (error) throw error;
      // Browser will redirect to Google — loading stays true intentionally
    } catch {
      toast.error("Sign in failed. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-[80vh] items-center justify-center bg-[#FAFAF8] px-6 py-16">
      <div className="w-full max-w-md rounded-3xl border border-black/10 bg-white p-8 shadow-[0_30px_60px_-30px_rgba(0,0,0,0.15)] sm:p-10">
        <Link
          to="/"
          className="font-[Plus_Jakarta_Sans] text-2xl font-extrabold tracking-tight"
          style={{ color: INDIGO }}
        >
          Exit Plan
        </Link>
        <h1 className="mt-8 font-[Plus_Jakarta_Sans] text-3xl font-extrabold tracking-tight">
          Sign in to save your results
        </h1>
        <p className="mt-3 text-sm leading-relaxed text-black/55">
          Save your country rankings and get alerts when immigration policies change.
        </p>

        <button
          onClick={handleGoogle}
          disabled={loading}
          className="mt-8 inline-flex w-full items-center justify-center gap-3 rounded-full px-6 py-3.5 text-sm font-semibold text-white transition hover:translate-y-[-1px] disabled:opacity-60"
          style={{ background: INDIGO }}
        >
          <GoogleIcon />
          {loading ? "Redirecting…" : "Continue with Google"}
        </button>

        <p className="mt-4 text-center text-xs text-black/45">No password needed.</p>
      </div>
    </div>
  );
}

import { Link, useRouterState } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";
import type { Session } from "@supabase/supabase-js";
import { supabase } from "@/lib/supabase";

export function Navbar() {
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const [session, setSession] = useState<Session | null>(null);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, [pathname]);

  const email = session?.user?.email ?? null;
  const initial = email?.[0]?.toUpperCase() ?? null;

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/60 bg-background/80 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <Link to="/" className="font-display text-xl font-bold text-primary tracking-tight">
          Exit Plan
        </Link>
        <nav className="flex items-center gap-3 sm:gap-5">
          <Link
            to="/dashboard"
            className="text-sm font-medium text-foreground/80 hover:text-primary transition-colors"
          >
            Dashboard
          </Link>
          {initial ? (
            <Link
              to="/account"
              title={email ?? ""}
              className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-primary-foreground font-display text-sm font-semibold hover:opacity-90 transition-opacity"
            >
              {initial}
            </Link>
          ) : (
            <Link to="/signin">
              <Button
                variant="outline"
                className="border-primary text-primary hover:bg-primary hover:text-primary-foreground"
              >
                Sign in
              </Button>
            </Link>
          )}
        </nav>
      </div>
    </header>
  );
}

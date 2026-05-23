import { Link, useLocation, useRouterState } from "@tanstack/react-router";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";

function readUser(): { email: string } | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem("exitplan_user");
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function Navbar() {
  const location = useLocation();
  const pathname = useRouterState({ select: (s) => s.location.pathname });
  const onDashboard = location.pathname.startsWith("/dashboard");
  const [user, setUser] = useState<{ email: string } | null>(null);

  useEffect(() => {
    setUser(readUser());
  }, [pathname]);

  const initial = user?.email?.[0]?.toUpperCase() ?? "A";

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
          {user ? (
            <div
              title={user.email}
              className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-primary-foreground font-display text-sm font-semibold"
            >
              {onDashboard ? "AS" : initial}
            </div>
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

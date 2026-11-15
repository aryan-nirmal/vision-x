"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useState, type FormEvent } from "react";
import { supabaseBrowser } from "@/lib/supabase/client";

/** Resolve `next` against this origin and only follow it if it stays here
 * ("//evil.com", "/\\evil.com" and "/\t/evil.com" all resolve elsewhere and fall back to "/"). */
function safeNext(raw: string | null): string {
  if (!raw) return "/";
  try {
    const url = new URL(raw, window.location.origin);
    return url.origin === window.location.origin ? url.pathname + url.search + url.hash : "/";
  } catch {
    return "/";
  }
}

function LoginForm() {
  const router = useRouter();
  const raw = useSearchParams().get("next");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setBusy(true);
    setError(null);
    const { error } = await supabaseBrowser().auth.signInWithPassword({ email, password });
    setBusy(false);
    if (error) {
      setError(error.message === "Invalid login credentials" ? "That email and password don't match." : error.message);
      return;
    }
    router.replace(safeNext(raw));
    router.refresh();
  }

  return (
    <form onSubmit={submit} className="panel w-full max-w-sm space-y-5 p-7 sm:p-8" suppressHydrationWarning>
      <div>
        <h1 className="text-3xl leading-tight font-semibold tracking-tight text-[#002E6E]">Sign in to Vasooli</h1>
        <p className="mt-1 text-muted">Your Paytm merchant ledger & collections on autopilot.</p>
      </div>
      <label className="block space-y-1.5" suppressHydrationWarning>
        <span className="text-sm text-muted">Email</span>
        <input
          className="field"
          type="email"
          name="email"
          autoComplete="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </label>
      <label className="block space-y-1.5" suppressHydrationWarning>
        <span className="text-sm text-muted">Password</span>
        <input
          className="field"
          type="password"
          name="password"
          autoComplete="current-password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </label>
      {error ? (
        <p role="alert" className="text-sm text-rose">
          {error}
        </p>
      ) : null}
      <button type="submit" className="btn btn-primary w-full py-3" disabled={busy}>
        {busy ? "Signing in…" : "Sign in to Console"}
      </button>

      <div className="flex items-center justify-between rounded-xl bg-page p-3 border border-line text-xs text-muted">
        <div>
          <p className="font-semibold text-[#002E6E]">Joshi Supermarket (Pune)</p>
          <p className="text-[11px] font-mono text-faint">demo@paytmvyapaar.in</p>
        </div>
        <button
          type="button"
          onClick={() => {
            setEmail("demo@paytmvyapaar.in");
            setPassword("paytm-demo-2026");
          }}
          className="rounded-lg bg-[#002E6E]/10 px-2.5 py-1 text-xs font-semibold text-[#002E6E] hover:bg-[#002E6E]/20"
        >
          Auto-fill
        </button>
      </div>
    </form>
  );
}

export default function LoginPage() {
  return (
    <main className="grid min-h-dvh place-items-center px-4 py-10 bg-page">
      <div className="flex w-full flex-col items-center gap-8">
        <div className="flex flex-col items-center gap-2">
          <div className="flex items-center gap-2.5">
            <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#002E6E] font-bold text-white text-2xl shadow-sm">
              P
            </span>
            <span className="text-3xl font-bold tracking-tight text-[#002E6E]">
              Paytm <span className="font-semibold text-[#00BAF2]">Vasooli AI</span>
            </span>
          </div>
          <p className="text-sm font-medium text-muted">Merchant Operating System · Track 3 AI Teammate</p>
        </div>
        <Suspense>
          <LoginForm />
        </Suspense>
      </div>
    </main>
  );
}

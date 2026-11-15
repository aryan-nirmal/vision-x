import clsx from "clsx";
import type { ReactNode } from "react";
import { initials } from "@/lib/format";

export function Avatar({ name, size = 44 }: { name: string; size?: number }) {
  return (
    <span
      aria-hidden
      className="inline-flex shrink-0 items-center justify-center rounded-full bg-raised font-medium text-muted shadow-[inset_0_0_0_1px_var(--color-line)]"
      style={{ width: size, height: size, fontSize: Math.round(size * 0.36) }}
    >
      {initials(name)}
    </span>
  );
}

// Each customer category gets a small dot; the label itself stays quiet.
const BADGE_DOTS: Record<string, string> = {
  Regular: "bg-blue",
  Recurring: "bg-mint",
  Lapsed: "bg-amber",
  New: "bg-faint",
};

export function Badge({ label }: { label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-md border border-line px-2 py-0.5 text-sm leading-5 text-muted">
      <span aria-hidden className={clsx("h-1.5 w-1.5 rounded-full", BADGE_DOTS[label] ?? "bg-faint")} />
      {label}
    </span>
  );
}

export function StatTile({
  label,
  value,
  sub,
  delta,
  icon,
}: {
  label: string;
  value: ReactNode;
  sub?: ReactNode;
  delta?: { ratio: number; vs: string } | null;
  icon?: ReactNode;
  total?: boolean;
}) {
  const up = delta && delta.ratio >= 0;
  return (
    <div className="panel relative flex flex-col justify-between p-5 transition-all hover:border-[#00BAF2]/40 hover:shadow-sm">
      <div className="flex items-center justify-between gap-3">
        <span className="text-xs font-semibold uppercase tracking-wider text-muted">{label}</span>
        {icon ? (
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-[#002E6E]/5 text-[#002E6E]">
            {icon}
          </div>
        ) : null}
      </div>
      <div className="mt-3">
        <p className="num text-2xl font-bold tracking-tight text-text sm:text-3xl">
          {value}
        </p>
      </div>
      {delta ? (
        <div className="mt-2.5 flex items-center gap-1.5 text-xs text-muted">
          <span
            className={clsx(
              "num inline-flex items-center gap-0.5 rounded-full px-2 py-0.5 font-semibold text-[11px]",
              up ? "bg-emerald-50 text-emerald-700" : "bg-amber-50 text-amber-700",
            )}
          >
            {up ? "↑ +" : "↓ −"}
            {Math.abs(Math.round(delta.ratio * 100))}%
          </span>
          <span className="truncate">vs {delta.vs}</span>
        </div>
      ) : sub ? (
        <p className="mt-2 text-xs text-muted">{sub}</p>
      ) : null}
    </div>
  );
}

export function SectionTitle({ title, action, sub }: { title: string; sub?: ReactNode; action?: ReactNode }) {
  return (
    <div className="mb-4 flex items-end justify-between gap-3">
      <div className="min-w-0">
        <h2 className="text-lg font-medium text-text">{title}</h2>
        {sub ? <p className="mt-1 text-sm text-muted">{sub}</p> : null}
      </div>
      {action}
    </div>
  );
}

export function Skeleton({ className }: { className?: string }) {
  return <div className={clsx("animate-pulse rounded-xl bg-raised", className)} />;
}

export function ErrorNote({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="panel flex items-center justify-between gap-3 border-rose/30 p-4 text-sm">
      <span className="text-rose">{message}</span>
      {onRetry ? (
        <button className="btn btn-quiet" onClick={onRetry}>
          Try again
        </button>
      ) : null}
    </div>
  );
}

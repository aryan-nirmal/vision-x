"use client";

import clsx from "clsx";
import {
  AlertCircle,
  Building2,
  Clock,
  IndianRupee,
  Receipt,
  TrendingDown,
  Users,
  Volume2,
  Zap,
} from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import {
  COMPARE,
  TrendChart,
  type Grain,
} from "@/components/charts";
import { InvoiceStatusText } from "@/components/invoice-status";
import { PayerSearch } from "@/components/payer-search";
import { PromisedPayments } from "@/components/promised-payments";
import {
  ErrorNote,
  SectionTitle,
  Skeleton,
  StatTile,
} from "@/components/ui";
import { useApi } from "@/lib/api";
import { dateOnly, inr, istDate, istTime, pct } from "@/lib/format";
import type { DashboardSummary, TrendPoint } from "@/lib/types";

const RANGES: {
  key: string;
  label: string;
  days: number;
  grain: Grain;
  now: string;
  before: string;
}[] = [
  {
    key: "7d",
    label: "7 days",
    days: 7,
    grain: "day",
    now: "Last 7 days",
    before: "7 days before",
  },
  {
    key: "30d",
    label: "30 days",
    days: 30,
    grain: "day",
    now: "Last 30 days",
    before: "30 days before",
  },
  {
    key: "90d",
    label: "90 days",
    days: 91,
    grain: "week",
    now: "Last 13 weeks",
    before: "13 weeks before",
  },
];

/** The calendar date `days` before an ISO date, as YYYY-MM-DD. */
function daysBefore(isoDate: string, days: number): string {
  const d = new Date(`${isoDate}T00:00:00Z`);
  d.setUTCDate(d.getUTCDate() - days);
  return d.toISOString().slice(0, 10);
}

function TrendBlock({
  fallback,
  date,
  isToday,
}: {
  fallback: TrendPoint[];
  date: string;
  isToday: boolean;
}) {
  const [range, setRange] = useState(RANGES[0]);
  const { data } = useApi<{ points: TrendPoint[] }>(
    range.key === "7d"
      ? null
      : `/dashboard/trend?days=${range.days}&grain=${range.grain}`,
    { keepPreviousData: true },
  );
  // The same span just before, for the quiet comparison line. `end` goes first so this
  // request never matches a wait on `/dashboard/trend?days=…`.
  const { data: before } = useApi<{ points: TrendPoint[] }>(
    `/dashboard/trend?end=${daysBefore(date, range.days)}&days=${range.days}&grain=${range.grain}`,
    { keepPreviousData: true },
  );
  const points = range.key === "7d" ? fallback : (data?.points ?? fallback);
  return (
    <div>
      <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h2 className="text-base font-medium text-text">
            Collections, last {range.label}
            {range.grain === "week" ? " by week" : ""}
          </h2>
          <p className="mt-1 flex flex-wrap gap-x-4 text-xs text-faint">
            <span className="flex items-center gap-2">
              <span aria-hidden className="h-0.5 w-4 rounded-full bg-blue" />
              {range.now}
            </span>
            {before ? (
              <span className="flex items-center gap-2">
                <span
                  aria-hidden
                  className="h-0.5 w-4 rounded-full"
                  style={{ background: COMPARE }}
                />
                {range.before}
              </span>
            ) : null}
          </p>
        </div>
        <div
          role="group"
          aria-label="Chart range"
          className="flex rounded-lg border border-line bg-page p-0.5"
        >
          {RANGES.map((r) => (
            <button
              key={r.key}
              onClick={() => setRange(r)}
              aria-pressed={r.key === range.key}
              className={clsx(
                "num h-7 rounded-md px-2.5 text-xs transition-colors",
                r.key === range.key
                  ? "bg-card text-text shadow-[inset_0_0_0_1px_var(--color-line)]"
                  : "text-muted hover:text-text",
              )}
            >
              {r.label.replace(" days", "D")}
            </button>
          ))}
        </div>
      </div>
      <TrendChart
        points={points}
        grain={range.grain}
        partialLast={isToday}
        compare={before?.points}
        compareLabel={range.before}
        height={280}
      />
    </div>
  );
}

function SlowDayBanner({
  slow,
}: {
  slow: NonNullable<DashboardSummary["slow_day"]>;
}) {
  return (
    <div
      role="status"
      className="flex items-start gap-3 rounded-xl border border-line bg-card px-5 py-4 shadow-[0_1px_2px_rgb(31_27_22/0.05)]"
    >
      <TrendingDown
        size={16}
        className="mt-[3px] shrink-0 text-amber"
        aria-hidden
      />
      <p className="text-base text-text">
        Slow day: takings are {slow.drop_pct}% below a usual {slow.weekday} so
        far.{" "}
        <span className="text-muted">
          {inr(slow.today_paise)} by {slow.as_of}, against an average of{" "}
          {inr(slow.baseline_paise)} by this time on the last four{" "}
          {slow.weekday}s.
        </span>
      </p>
    </div>
  );
}

export default function DashboardPage() {
  const { data, error, isLoading, mutate } = useApi<DashboardSummary>(
    "/dashboard/summary",
    {
      refreshInterval: 60_000,
    },
  );

  if (error)
    return (
      <ErrorNote
        message={`Couldn't load today's numbers: ${error.message}`}
        onRetry={() => mutate()}
      />
    );
  if (isLoading || !data) return <DashboardSkeleton />;

  const k = data.kpis;
  const compareLabel = `last ${dateOnly(k.compare_day, { weekday: "short" })}`;

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      {/* 1. Executive Store Header */}
      <header className="flex flex-wrap items-center justify-between gap-4 rounded-2xl border border-line bg-card p-5 sm:p-6 shadow-xs">
        <div className="flex items-center gap-3.5 sm:gap-4">
          <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-[#002E6E] text-white shadow-sm font-bold text-xl">
            P
          </div>
          <div>
            <div className="flex flex-wrap items-center gap-2">
              <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#002E6E]">
                Joshi Supermarket
              </h1>
              <span className="rounded-full bg-[#00BAF2]/15 px-2.5 py-0.5 text-xs font-semibold text-[#002E6E]">
                FC Road, Pune
              </span>
              <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 px-2.5 py-0.5 text-xs font-medium text-emerald-700">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Soundbox 4.0 Online
              </span>
            </div>
            <p className="mt-1 text-xs sm:text-sm text-muted">
              {dateOnly(data.date, {
                weekday: "long",
                day: "numeric",
                month: "long",
              })}
              {data.is_today ? ` · Synced as of ${istTime(data.now)}` : ""} · Terminal: <span className="font-mono text-xs font-semibold">PTM00MOCK0000001</span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 sm:gap-3">
          <Link
            href="/collections"
            className="btn btn-quiet text-xs font-medium px-3.5 py-2 shadow-xs"
          >
            <Receipt size={15} /> New Invoice
          </Link>
          <div className="hidden sm:flex items-center gap-2 rounded-xl border border-line bg-page px-3 py-2 text-xs font-medium text-muted">
            <Zap size={14} className="text-amber-500" />
            <span>Instant UPI Settlements</span>
          </div>
        </div>
      </header>

      {data.slow_day?.is_slow ? <SlowDayBanner slow={data.slow_day} /> : null}

      {/* 2. Top 4 Metric Cards Grid */}
      <section aria-label="Today at a glance" className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatTile
          label="Today’s Collection"
          value={inr(k.collected_paise)}
          delta={
            k.change_vs_last_week === null
              ? null
              : { ratio: k.change_vs_last_week, vs: compareLabel }
          }
          icon={<IndianRupee size={18} />}
        />
        <StatTile
          label="Total Transactions"
          value={k.payments.toLocaleString("en-IN")}
          sub={`${k.new_payers} new payer${k.new_payers === 1 ? "" : "s"} today`}
          icon={<Receipt size={18} />}
        />
        <StatTile
          label="Repeat Shoppers"
          value={pct(k.repeat_share)}
          sub="Loyalty & regular volume"
          icon={<Users size={18} />}
        />
        <StatTile
          label="Pending Receivables"
          value={inr(data.outstanding.total_paise)}
          sub={`${data.outstanding.customers} customer${data.outstanding.customers === 1 ? "" : "s"} due`}
          icon={<Clock size={18} />}
        />
      </section>

      {/* 3. Core Operations Split: 7 Cols (Primary Ledger & Charts) & 5 Cols (Live Feeds & Actions) */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        {/* Left Column (7 Cols) */}
        <div className="space-y-6 lg:col-span-7">
          {/* Revenue Velocity Chart Card */}
          <section className="panel p-5 sm:p-6 shadow-xs">
            <TrendBlock
              fallback={data.trend}
              date={data.date}
              isToday={data.is_today}
            />
          </section>

          {/* Customer Khata Directory */}
          <section className="panel p-5 sm:p-6 shadow-xs">
            <SectionTitle
              title="Customer Directory & Khata Lookup"
              sub="Find regulars, search by phone number or UPI handle"
            />
            <PayerSearch limit={5} />
          </section>

          {/* Pending Invoices Table */}
          <section
            className="panel min-w-0 p-5 sm:p-6 shadow-xs"
            aria-labelledby="pending-title"
          >
            <SectionTitle
              title="Pending Invoices"
              sub={
                data.outstanding.invoices.length ? (
                  <>
                    <span className="font-semibold text-text">
                      {inr(data.outstanding.total_paise)}
                    </span>{" "}
                    outstanding across {data.outstanding.customers} customer
                    {data.outstanding.customers === 1 ? "" : "s"}
                  </>
                ) : (
                  "Nothing outstanding"
                )
              }
              action={
                <Link href="/collections" className="text-xs font-semibold text-[#00BAF2] hover:underline">
                  Manage Invoices &rarr;
                </Link>
              }
            />
            <h2 id="pending-title" className="sr-only">
              Pending payments
            </h2>
            {data.outstanding.invoices.length ||
            data.outstanding.recently_paid.length ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                  <thead className="text-xs font-semibold uppercase tracking-wider text-muted border-b border-line">
                    <tr>
                      <th className="py-3 pr-4 font-medium">Customer</th>
                      <th className="py-3 px-4 text-right font-medium">Amount</th>
                      <th className="py-3 pl-4 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-line">
                    {data.outstanding.invoices.map((inv) => (
                      <tr
                        key={inv.id}
                        className="transition-colors hover:bg-page/50"
                      >
                        <td className="py-3 pr-4">
                          <Link
                            href={`/customers/${inv.payer_id}`}
                            className="font-medium text-text transition-colors hover:text-[#00BAF2]"
                          >
                            {inv.payer_name}
                          </Link>
                          <span className="block text-xs font-mono text-faint">
                            {inv.number}
                          </span>
                        </td>
                        <td className="num py-3 px-4 text-right font-semibold text-text">
                          {inr(inv.amount_paise)}
                        </td>
                        <td className="py-3 pl-4">
                          <InvoiceStatusText
                            status={inv.status}
                            dueInDays={-inv.days_overdue}
                            graceDays={inv.grace_days}
                          />
                        </td>
                      </tr>
                    ))}
                    {data.outstanding.recently_paid.length ? (
                      <tr>
                        <td
                          colSpan={3}
                          className="pt-4 pb-2 text-xs font-semibold uppercase tracking-wider text-faint"
                        >
                          Paid Recently
                        </td>
                      </tr>
                    ) : null}
                    {data.outstanding.recently_paid.map((inv) => (
                      <tr key={inv.id} className="transition-colors hover:bg-page/50">
                        <td className="py-3 pr-4">
                          <Link
                            href={`/collections/${inv.id}`}
                            className="font-medium text-text transition-colors hover:text-[#00BAF2]"
                          >
                            {inv.payer_name}
                          </Link>
                          <span className="block text-xs font-mono text-faint">
                            {inv.number}
                          </span>
                        </td>
                        <td className="num py-3 px-4 text-right text-muted">
                          {inr(inv.amount_paise)}
                        </td>
                        <td className="py-3 pl-4">
                          <InvoiceStatusText
                            status="paid"
                            dueInDays={0}
                            markedPaid={inv.marked_paid}
                          />
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="flex flex-wrap items-center gap-3">
                <p className="text-sm text-muted">No unpaid invoices.</p>
                <Link href="/collections" className="btn btn-quiet px-3 py-1.5 text-xs font-medium">
                  Create Invoice
                </Link>
              </div>
            )}
          </section>
        </div>

        {/* Right Column (5 Cols) */}
        <div className="space-y-6 lg:col-span-5">
          {/* Paytm Merchant Growth / Working Capital */}
          <section className="panel p-5 sm:p-6 bg-gradient-to-br from-[#002E6E]/10 via-[#00BAF2]/10 to-transparent border-[#00BAF2]/40 shadow-xs">
            <div className="flex items-start gap-3.5">
              <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-[#002E6E] text-white shadow-xs">
                <Building2 size={22} className="text-[#00BAF2]" />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-[#002E6E]">Paytm Business Growth</span>
                  <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[10px] font-bold text-emerald-800">Pre-Approved</span>
                </div>
                <h3 className="text-lg font-bold text-text mt-1">₹75,000 Working Capital</h3>
                <p className="text-xs text-muted mt-1 leading-relaxed">
                  Calculated automatically from Joshi Supermarket’s 90-day UPI collection score (7,800+ transactions).
                </p>
                <div className="mt-4 flex items-center justify-between rounded-xl bg-card p-3 border border-line">
                  <div>
                    <p className="text-[11px] text-faint">Daily Soundbox Repay</p>
                    <p className="text-sm font-bold num text-[#002E6E]">₹120 / day</p>
                  </div>
                  <button className="btn btn-primary text-xs font-semibold px-3.5 py-1.5 bg-[#002E6E] hover:bg-[#001f4d]">
                    Claim Funds
                  </button>
                </div>
              </div>
            </div>
          </section>

          {/* Soundbox Realtime Live Feed */}
          <section className="panel min-w-0 p-5 sm:p-6 shadow-xs">
            <div className="mb-4 flex items-center justify-between gap-3">
              <div>
                <h2 className="text-base font-semibold text-text flex items-center gap-2">
                  <Volume2 size={16} className="text-[#00BAF2]" /> Soundbox Payment Stream
                </h2>
                <p className="text-xs text-muted mt-0.5">
                  {data.is_today ? "Live payments received today" : `Payments on ${dateOnly(data.date)}`}
                </p>
              </div>
              <span className="inline-flex items-center gap-1 rounded-full bg-emerald-50 px-2 py-0.5 text-[10px] font-semibold text-emerald-700">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
                Live
              </span>
            </div>

            {data.recent.length ? (
              <ul className="divide-y divide-line">
                {data.recent.map((t) => (
                  <li
                    key={t.id}
                    className="flex items-center justify-between gap-3 py-3"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium text-text">
                        {t.payer_id ? (
                          <Link
                            href={`/customers/${t.payer_id}`}
                            className="transition-colors hover:text-[#00BAF2]"
                          >
                            {t.payer_name}
                          </Link>
                        ) : (
                          <span className="text-muted">Walk-in Customer</span>
                        )}
                      </p>
                      <p className="truncate text-xs text-faint mt-0.5">
                        {t.description ?? "UPI Payment"}
                      </p>
                    </div>
                    <div className="shrink-0 text-right">
                      <p className="num text-sm font-bold text-text">
                        {inr(t.amount_paise)}
                      </p>
                      <p className="num text-[11px] text-faint">
                        {istTime(t.paid_at)}
                      </p>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted">
                No payments yet {data.is_today ? "today" : `on ${istDate(data.date)}`}.
              </p>
            )}
          </section>

          {/* Promised Collections */}
          <PromisedPayments />
        </div>
      </div>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div
      className="mx-auto max-w-7xl space-y-6"
      aria-busy="true"
      aria-label="Loading"
    >
      <Skeleton className="h-24 rounded-2xl" />
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Skeleton className="h-32 rounded-2xl" />
        <Skeleton className="h-32 rounded-2xl" />
        <Skeleton className="h-32 rounded-2xl" />
        <Skeleton className="h-32 rounded-2xl" />
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-12">
        <Skeleton className="h-[460px] rounded-2xl lg:col-span-7" />
        <Skeleton className="h-[460px] rounded-2xl lg:col-span-5" />
      </div>
    </div>
  );
}

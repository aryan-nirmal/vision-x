"use client";

import { Users } from "lucide-react";
import { PayerSearch } from "@/components/payer-search";

export default function CustomersPage() {
  return (
    <div className="mx-auto max-w-5xl space-y-6">
      <header className="rounded-2xl border border-line bg-card p-5 sm:p-6 shadow-xs">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#002E6E]/10 text-[#002E6E]">
            <Users size={20} />
          </div>
          <div>
            <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-[#002E6E]">
              Customer Khata Directory
            </h1>
            <p className="mt-0.5 text-xs sm:text-sm text-muted">
              Auto-matched retail & B2B buyers across Paytm UPI VPA, phone numbers, and invoice order IDs.
            </p>
          </div>
        </div>
      </header>
      <PayerSearch limit={50} emptyLimit={200} />
    </div>
  );
}

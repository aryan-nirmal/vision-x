import type { Metadata, Viewport } from "next";
import { IBM_Plex_Mono, Mukta } from "next/font/google";
import "./globals.css";

// Mukta (Ek Type) covers Latin, Devanagari and the ₹ sign, so Hinglish transcripts
// and Hindi replies render in the same face as the rest of the UI.
const mukta = Mukta({
  variable: "--font-mukta",
  subsets: ["latin", "devanagari"],
  weight: ["400", "500", "600", "700"],
});

const plexMono = IBM_Plex_Mono({
  variable: "--font-plex-mono",
  subsets: ["latin"],
  weight: ["400", "500"],
});

export const metadata: Metadata = {
  title: "Paytm Vasooli AI | Autonomous Debt Recovery & Ledger System",
  description: "Autonomous Indic voice assistant & debt recovery engine for Paytm merchants.",
};

export const viewport: Viewport = {
  themeColor: "#002E6E",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${mukta.variable} ${plexMono.variable} antialiased`} suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}

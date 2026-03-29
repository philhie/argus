import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Finance Spezialist — Autonome Buchhaltung | Kengo",
  description:
    "Kengo Finance verarbeitet Eingangsrechnungen, synchronisiert mit DATEV, versendet Mahnungen und überwacht Cash Flow. Ab €0,75 pro Rechnung.",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}

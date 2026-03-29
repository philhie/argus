import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Preise — Transparent, bezahlbar, kein Risiko | Kengo",
  description:
    "KI-Assistent ab €1.999/Monat. Spezialisten ab €0,75 pro Ergebnis. Monatlich kündbar. Keine versteckten Kosten. ROI-Rechner inklusive.",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}

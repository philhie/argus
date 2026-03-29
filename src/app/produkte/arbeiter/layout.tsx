import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "KI-Arbeiter — Dein persönlicher KI-Mitarbeiter | Kengo",
  description:
    "Der KI-Arbeiter ist dein Generalist. Er baut Automatisierungen, beantwortet Fragen, managed dein Büro und verwaltet Unternehmenswissen. Ab €1.999/Monat.",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}

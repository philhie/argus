import type { Metadata } from "next";
export const metadata: Metadata = {
  title: "KI-Abteilung — Dein gesamtes KI-Team, ein Abteilungsleiter | Kengo",
  description: "Der KI-Abteilungsleiter koordiniert alle Agenten, liefert Executive Summaries, überwacht Budgets und onboardet neue Spezialisten automatisch. Individuell.",
};
export default function Layout({ children }: { children: React.ReactNode }) { return children; }

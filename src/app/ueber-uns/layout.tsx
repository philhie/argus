import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Über uns — Wir geben Unternehmen die Kapazität zurück | Kengo",
  description:
    "Kengo gibt jedem Unternehmen die Kapazität, die es auf dem Arbeitsmarkt nicht mehr findet. KI-Mitarbeiter für den europäischen Mittelstand. Gegründet in Deutschland.",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}

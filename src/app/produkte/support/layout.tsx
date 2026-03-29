import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Customer Support Spezialist — Autonomer Kundenservice | Kengo",
  description:
    "Kengo Support beantwortet Kundenanfragen per Email, Chat und Telefon. Löst Standardanfragen autonom. Ab €1,25 pro Ticket.",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}

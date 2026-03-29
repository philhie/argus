import type { Metadata } from "next";
export const metadata: Metadata = {
  title: "Procurement Spezialist — Autonomer Einkauf | Kengo",
  description: "Kengo Procurement vergleicht Lieferantenangebote, erstellt Bestellungen und trackt Lieferungen. Ab €1,50 pro Bestellung.",
};
export default function Layout({ children }: { children: React.ReactNode }) { return children; }

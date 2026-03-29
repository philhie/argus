import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Sicherheit | Kengo",
  description:
    "Enterprise-Sicherheit für den Mittelstand. DSGVO-konform, gehostet in Deutschland, Open-Source-auditierbar. Kengo schützt Ihre Daten auf höchstem Niveau.",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}

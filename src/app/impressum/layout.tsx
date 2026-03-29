import type { Metadata } from "next";
export const metadata: Metadata = {
  title: "Impressum | Kengo",
  description: "Impressum der Kengo GmbH gemäß § 5 TMG.",
};
export default function Layout({ children }: { children: React.ReactNode }) { return children; }

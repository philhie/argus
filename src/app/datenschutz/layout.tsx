import type { Metadata } from "next";
export const metadata: Metadata = {
  title: "Datenschutzerklärung | Kengo",
  description: "Datenschutzerklärung der Kengo GmbH gemäß DSGVO.",
};
export default function Layout({ children }: { children: React.ReactNode }) { return children; }

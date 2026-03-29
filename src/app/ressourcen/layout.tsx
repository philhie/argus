import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Ressourcen | Kengo",
  description:
    "Alles was Sie brauchen, um Kengo in Ihrem Unternehmen einzuführen. Executive Summary, ROI-Rechner, Sicherheitsspezifikationen und mehr.",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}

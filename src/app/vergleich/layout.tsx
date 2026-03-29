import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Vergleich | Kengo",
  description:
    "Kengo vs. ChatGPT, Copilot, Langdock und klassische Sachbearbeiter. Der ehrliche Vergleich — alle Fakten auf einen Blick.",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}

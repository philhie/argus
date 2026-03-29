import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Live Demo | Kengo",
  description:
    "Erlebe deinen KI-Mitarbeiter in Aktion. Gib deinen Firmennamen ein und sieh in 30 Sekunden, was Kengo für dein Unternehmen tun kann.",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}

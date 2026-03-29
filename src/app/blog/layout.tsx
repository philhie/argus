import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Blog — KI-Wissen für den Mittelstand | Kengo",
  description:
    "Artikel über KI-Mitarbeiter, Automatisierung, Fachkräftemangel und digitale Transformation im deutschen Mittelstand.",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}

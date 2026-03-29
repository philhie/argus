import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "HR Spezialist — Autonomes Recruiting | Kengo",
  description:
    "Kengo HR screent Bewerbungen, koordiniert Interviews, versendet Absagen und Einladungen. Ab €2,50 pro gescreente Bewerbung.",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return children;
}

import SpecialistPageTemplate from "@/components/SpecialistPageTemplate";
import SpecialistCascade from "@/components/SpecialistCascade";
import { hrScenarios } from "@/lib/specialist-demos";

export default function HRPage() {
  return (
    <SpecialistPageTemplate
      demo={<SpecialistCascade scenarios={hrScenarios} />}
      badge={
        <span className="badge-live">
          <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-live" />
          LIVE
        </span>
      }
      headline="Dein autonomes Recruiting."
      subline="Vom Eingang bis zum Interview."
      bodyCopy="Screent Bewerbungen, bewertet Kandidaten, koordiniert Interviews, versendet Absagen und Einladungen, erstellt Onboarding-Dokumentation."
      capabilities={[
        {
          icon: "📄",
          title: "Bewerbungs-Screening",
          description:
            "Analysiert eingehende Bewerbungen, gleicht Qualifikationen mit Anforderungen ab und erstellt ein Ranking der besten Kandidaten.",
        },
        {
          icon: "📅",
          title: "Interview-Koordination",
          description:
            "Findet passende Termine, versendet Einladungen, koordiniert mit Hiring Managern und sendet Erinnerungen. Vollautomatisch.",
        },
        {
          icon: "✉️",
          title: "Kommunikation",
          description:
            "Versendet professionelle Absagen, Einladungen und Status-Updates. Jede Nachricht passt zu deiner Employer Brand.",
        },
        {
          icon: "📋",
          title: "Onboarding-Dokumentation",
          description:
            "Erstellt Onboarding-Pläne, sammelt Dokumente ein, richtet Zugänge ein und begleitet neue Mitarbeiter durch die ersten Wochen.",
        },
      ]}
      outcomeMetric="Pro gescreente Bewerbung"
      outcomePrice="€2,50"
      outcomeSaving="vs. €12,50 manuell = 80% Ersparnis"
      comparison={[
        { metric: "Kosten pro Screening", kengo: "€2,50", manual: "€12,50" },
        { metric: "Screening-Zeit", kengo: "< 1 Minute", manual: "15–30 Min." },
        { metric: "Time-to-Interview", kengo: "1–2 Tage", manual: "5–10 Tage" },
        { metric: "Verfügbarkeit", kengo: "24/7", manual: "Bürozeiten" },
        { metric: "Kandidaten-Kommunikation", kengo: "Automatisch", manual: "Manuell" },
      ]}
      ctaLabel="Demo vereinbaren"
      ctaHref="https://cal.eu/philhie/kengo"
    />
  );
}

import SpecialistPageTemplate from "@/components/SpecialistPageTemplate";
import SpecialistCascade from "@/components/SpecialistCascade";
import { salesScenarios } from "@/lib/specialist-demos";

export default function SalesPage() {
  return (
    <SpecialistPageTemplate
      demo={<SpecialistCascade scenarios={salesScenarios} />}
      badge={
        <span className="badge-live">
          <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-live" />
          LIVE
        </span>
      }
      headline="Dein autonomer Vertriebsassistent."
      subline="Qualifiziert Leads während du schläfst."
      bodyCopy="Qualifiziert eingehende Leads, reichert Kontaktdaten an, aktualisiert dein CRM, erstellt Angebote, koordiniert Follow-ups. Dein Vertrieb konzentriert sich auf Abschlüsse."
      capabilities={[
        { icon: "🎯", title: "Lead-Qualifizierung", description: "Bewertet eingehende Leads nach deinen Kriterien. Scoring, Priorisierung und automatische Weiterleitung an den richtigen Vertriebsmitarbeiter." },
        { icon: "🔍", title: "Kontakt-Anreicherung", description: "Reichert Kontaktdaten automatisch an: Firmengröße, Branche, Entscheider, LinkedIn-Profile. Dein CRM ist immer aktuell." },
        { icon: "📝", title: "Angebotserstellung", description: "Erstellt personalisierte Angebote basierend auf dem Kundenprofil, historischen Deals und deiner Preisstruktur." },
        { icon: "🔄", title: "Follow-up Automatisierung", description: "Koordiniert Follow-ups über Email, Telefon und LinkedIn. Kein Lead geht verloren, kein Termin wird vergessen." },
      ]}
      outcomeMetric="Pro qualifizierter Lead"
      outcomePrice="€5,00"
      outcomeSaving="vs. €25–40 manuell = 80–87% Ersparnis"
      comparison={[
        { metric: "Kosten pro Lead", kengo: "€5,00", manual: "€25–40" },
        { metric: "Qualifizierungszeit", kengo: "< 2 Minuten", manual: "30–60 Min." },
        { metric: "CRM-Updates", kengo: "Automatisch", manual: "Manuell" },
        { metric: "Verfügbarkeit", kengo: "24/7", manual: "Bürozeiten" },
        { metric: "Follow-up Rate", kengo: "100%", manual: "~60%" },
      ]}
      ctaLabel="Demo vereinbaren"
      ctaHref="https://cal.eu/philhie/kengo"
    />
  );
}

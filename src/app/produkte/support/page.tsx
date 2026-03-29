import SpecialistPageTemplate from "@/components/SpecialistPageTemplate";
import SpecialistCascade from "@/components/SpecialistCascade";
import { supportScenarios } from "@/lib/specialist-demos";

export default function SupportPage() {
  return (
    <SpecialistPageTemplate
      demo={<SpecialistCascade scenarios={supportScenarios} />}
      badge={
        <span className="badge-live">
          <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-live" />
          LIVE
        </span>
      }
      headline="Dein autonomer Kundenservice."
      subline="Löst Tickets, bevor dein Team aufwacht."
      bodyCopy="Beantwortet Kundenanfragen per Email, Chat und Telefon. Löst Standardanfragen autonom. Eskaliert komplexe Fälle. Pflegt FAQs. Tracked Zufriedenheit."
      capabilities={[
        {
          icon: "💬",
          title: "Multi-Channel Support",
          description:
            "Email, Chat, Telefon — dein KI-Mitarbeiter beantwortet Anfragen auf allen Kanälen. In Deutsch, Englisch und 30+ Sprachen.",
        },
        {
          icon: "⚡",
          title: "Autonome Lösung",
          description:
            "Löst Standardanfragen sofort und autonom. Passwort-Resets, Statusabfragen, Rückgaben, FAQs — ohne menschliches Eingreifen.",
        },
        {
          icon: "🔀",
          title: "Intelligente Eskalation",
          description:
            "Erkennt komplexe oder emotionale Anfragen und eskaliert mit vollem Kontext an dein Team. Kein Informationsverlust.",
        },
        {
          icon: "📈",
          title: "Zufriedenheits-Tracking",
          description:
            "Misst CSAT automatisch, identifiziert wiederkehrende Probleme und schlägt FAQ-Updates und Prozessverbesserungen vor.",
        },
      ]}
      outcomeMetric="Pro gelöstes Ticket"
      outcomePrice="€1,25"
      outcomeSaving="vs. €15–20 manuell = 90%+ Ersparnis"
      comparison={[
        { metric: "Kosten pro Ticket", kengo: "€1,25", manual: "€15–20" },
        { metric: "Antwortzeit", kengo: "< 30 Sekunden", manual: "2–24 Stunden" },
        { metric: "Lösungsrate (autonom)", kengo: "78%", manual: "—" },
        { metric: "Verfügbarkeit", kengo: "24/7", manual: "Bürozeiten" },
        { metric: "Sprachen", kengo: "30+", manual: "1–2" },
      ]}
      ctaLabel="Demo vereinbaren"
      ctaHref="https://cal.eu/philhie/kengo"
    />
  );
}

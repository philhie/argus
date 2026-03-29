import SpecialistPageTemplate from "@/components/SpecialistPageTemplate";
import SpecialistCascade from "@/components/SpecialistCascade";
import { itOpsScenarios } from "@/lib/specialist-demos";

export default function ITOpsPage() {
  return (
    <SpecialistPageTemplate
      demo={<SpecialistCascade scenarios={itOpsScenarios} />}
      badge={
        <span className="badge-live">
          <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-live" />
          LIVE
        </span>
      }
      headline="Dein autonomer IT-Support."
      subline="Löst Tickets, bevor der Admin sie sieht."
      bodyCopy="Löst IT-Tickets autonom: Password-Resets, Zugriffsanfragen, Software-Installationen, System-Monitoring. Eskaliert nur was menschliches Urteil braucht."
      capabilities={[
        { icon: "🎫", title: "Ticket-Triage", description: "Klassifiziert eingehende IT-Tickets automatisch nach Priorität, Kategorie und benötigtem Skill-Level." },
        { icon: "🔑", title: "Autonome Lösung", description: "Löst Standardanfragen sofort: Password-Resets, Zugriffsanfragen, VPN-Probleme, Software-Installationen." },
        { icon: "📡", title: "System-Monitoring", description: "Überwacht Systeme 24/7. Erkennt Anomalien, benachrichtigt bei Ausfällen, startet automatische Incident Response." },
        { icon: "📈", title: "Reporting", description: "Trackt Ticket-Volumen, Lösungszeiten, wiederkehrende Probleme. Identifiziert Ursachen und schlägt Prävention vor." },
      ]}
      outcomeMetric="Pro gelöstes IT-Ticket"
      outcomePrice="€1,00"
      outcomeSaving="vs. €12–18 manuell = 91–94% Ersparnis"
      comparison={[
        { metric: "Kosten pro Ticket", kengo: "€1,00", manual: "€12–18" },
        { metric: "Lösungszeit", kengo: "< 1 Minute", manual: "2–8 Stunden" },
        { metric: "Autonome Lösungsrate", kengo: "72%", manual: "—" },
        { metric: "Verfügbarkeit", kengo: "24/7", manual: "Bürozeiten" },
        { metric: "System-Monitoring", kengo: "Echtzeit", manual: "Stichproben" },
      ]}
      ctaLabel="Demo vereinbaren"
      ctaHref="https://cal.eu/philhie/kengo"
    />
  );
}

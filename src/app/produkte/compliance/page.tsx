import SpecialistPageTemplate from "@/components/SpecialistPageTemplate";
import SpecialistCascade from "@/components/SpecialistCascade";
import { complianceScenarios } from "@/lib/specialist-demos";

export default function CompliancePage() {
  return (
    <SpecialistPageTemplate
      demo={<SpecialistCascade scenarios={complianceScenarios} />}
      badge={
        <span className="badge-live">
          <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-live" />
          LIVE
        </span>
      }
      headline="Dein autonomer Compliance Officer."
      subline="DORA, NIS2, AI Act — automatisch."
      bodyCopy="Trackt regulatorische Anforderungen (DORA, NIS2, AI Act, CSRD, ESG), bereitet Audits vor, überwacht Compliance-Status, erstellt Berichte. Europäische Regulierung als Kompetenz."
      capabilities={[
        { icon: "⚖️", title: "Regulatorisches Tracking", description: "Überwacht DORA, NIS2, AI Act, CSRD und ESG-Anforderungen. Benachrichtigt bei Änderungen und neuen Pflichten." },
        { icon: "📋", title: "Audit-Vorbereitung", description: "Sammelt automatisch alle benötigten Dokumente, erstellt Audit-Trails und bereitet Prüfungsunterlagen vor." },
        { icon: "🛡️", title: "Policy Enforcement", description: "Überwacht die Einhaltung interner Richtlinien. Meldet Verstöße und schlägt Korrekturmaßnahmen vor." },
        { icon: "📊", title: "Compliance-Reporting", description: "Erstellt regelmäßige Compliance-Reports für Geschäftsführung, Aufsichtsrat und externe Prüfer." },
      ]}
      outcomeMetric="Pro Compliance-Report"
      outcomePrice="€25,00"
      outcomeSaving="vs. €500–1.000 manuell = 95–97% Ersparnis"
      comparison={[
        { metric: "Kosten pro Report", kengo: "€25,00", manual: "€500–1.000" },
        { metric: "Regulatorisches Tracking", kengo: "Echtzeit", manual: "Quartalsweise" },
        { metric: "Audit-Vorbereitung", kengo: "Automatisch", manual: "2–4 Wochen" },
        { metric: "Verfügbarkeit", kengo: "24/7", manual: "Bürozeiten" },
        { metric: "Abdeckung", kengo: "DORA, NIS2, AI Act, ESG", manual: "Teilweise" },
      ]}
      ctaLabel="Demo vereinbaren"
      ctaHref="https://cal.eu/philhie/kengo"
    />
  );
}

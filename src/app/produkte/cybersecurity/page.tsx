import SpecialistPageTemplate from "@/components/SpecialistPageTemplate";
import SpecialistCascade from "@/components/SpecialistCascade";
import { cybersecurityScenarios } from "@/lib/specialist-demos";

export default function CybersecurityPage() {
  return (
    <SpecialistPageTemplate
      demo={<SpecialistCascade scenarios={cybersecurityScenarios} />}
      badge={
        <span className="badge-live">
          <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-live" />
          LIVE
        </span>
      }
      headline="Dein autonomes Security Operations Center."
      subline="Threat Detection meets NIS2 Compliance."
      bodyCopy="Threat Detection, Vulnerability Scanning, Security Incident Response, NIS2/DORA Compliance Monitoring. Enterprise-Grade Security für den Mittelstand."
      capabilities={[
        { icon: "🔍", title: "Threat Detection", description: "24/7 Überwachung auf Bedrohungen. Erkennt Anomalien, verdächtige Aktivitäten und potenzielle Angriffe in Echtzeit." },
        { icon: "🛡️", title: "Vulnerability Scanning", description: "Scannt Systeme und Anwendungen auf Schwachstellen. Priorisiert nach Risiko und schlägt Patches vor." },
        { icon: "🚨", title: "Incident Response", description: "Automatisierte Erstreaktion bei Sicherheitsvorfällen. Isolierung, Dokumentation und Eskalation nach Playbook." },
        { icon: "📜", title: "NIS2/DORA Monitoring", description: "Überwacht die Einhaltung von NIS2 und DORA. Erstellt Nachweise und bereitet auf Prüfungen vor." },
      ]}
      outcomeMetric="Pro Sicherheitsvorfall"
      outcomePrice="€50,00"
      outcomeSaving="vs. €2.000–5.000 manuell = 97–99% Ersparnis"
      comparison={[
        { metric: "Kosten pro Vorfall", kengo: "€50,00", manual: "€2.000–5.000" },
        { metric: "Erkennungszeit", kengo: "Sekunden", manual: "Stunden/Tage" },
        { metric: "Threat Monitoring", kengo: "24/7 Echtzeit", manual: "Stichproben" },
        { metric: "Vulnerability Scans", kengo: "Kontinuierlich", manual: "Quartalsweise" },
        { metric: "NIS2/DORA Reporting", kengo: "Automatisch", manual: "Manuell" },
      ]}
      ctaLabel="Demo vereinbaren"
      ctaHref="https://cal.eu/philhie/kengo"
    />
  );
}

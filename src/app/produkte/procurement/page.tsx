import SpecialistPageTemplate from "@/components/SpecialistPageTemplate";
import SpecialistCascade from "@/components/SpecialistCascade";
import { procurementScenarios } from "@/lib/specialist-demos";

export default function ProcurementPage() {
  return (
    <SpecialistPageTemplate
      demo={<SpecialistCascade scenarios={procurementScenarios} />}
      badge={
        <span className="badge-live">
          <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-live" />
          LIVE
        </span>
      }
      headline="Dein autonomer Einkauf."
      subline="Lieferanten, Angebote, Bestellungen."
      bodyCopy="Vergleicht Lieferantenangebote, erstellt Bestellungen, trackt Lieferungen, managed Reklamationen. Spart Zeit und Kosten im gesamten Beschaffungsprozess."
      capabilities={[
        { icon: "📦", title: "Angebotsvergleich", description: "Vergleicht Lieferantenangebote automatisch nach Preis, Qualität, Lieferzeit und Zuverlässigkeit." },
        { icon: "📋", title: "Bestellmanagement", description: "Erstellt Bestellungen, versendet an Lieferanten, trackt Bestätigungen und Liefertermine." },
        { icon: "🚚", title: "Lieferverfolgung", description: "Trackt alle offenen Lieferungen, meldet Verzögerungen und koordiniert mit Lieferanten bei Problemen." },
        { icon: "⚠️", title: "Reklamationsmanagement", description: "Dokumentiert Reklamationen, erstellt Mängelberichte und koordiniert Ersatzlieferungen oder Gutschriften." },
      ]}
      outcomeMetric="Pro verarbeitete Bestellung"
      outcomePrice="€1,50"
      outcomeSaving="vs. €15–25 manuell = 90–94% Ersparnis"
      comparison={[
        { metric: "Kosten pro Bestellung", kengo: "€1,50", manual: "€15–25" },
        { metric: "Verarbeitungszeit", kengo: "< 5 Minuten", manual: "30–60 Min." },
        { metric: "Angebotsvergleich", kengo: "Automatisch", manual: "Manuell" },
        { metric: "Verfügbarkeit", kengo: "24/7", manual: "Bürozeiten" },
        { metric: "Lieferverfolgung", kengo: "Echtzeit", manual: "Bei Bedarf" },
      ]}
      ctaLabel="Demo vereinbaren"
      ctaHref="https://cal.eu/philhie/kengo"
    />
  );
}

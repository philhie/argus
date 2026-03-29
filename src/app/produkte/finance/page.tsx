import SpecialistPageTemplate from "@/components/SpecialistPageTemplate";
import InvoiceDemo from "@/components/InvoiceDemo";

export default function FinancePage() {
  return (
    <SpecialistPageTemplate
      demo={<InvoiceDemo />}
      badge={
        <span className="badge-live">
          <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-live" />
          LIVE
        </span>
      }
      headline="Deine autonome Buchhaltung."
      subline="Rechnungen rein, DATEV raus."
      bodyCopy="Verarbeitet Eingangsrechnungen, synchronisiert mit DATEV, versendet Mahnungen, überwacht Cash Flow, erstellt Monatsberichte. Ab dem ersten Tag."
      capabilities={[
        {
          icon: "📥",
          title: "Rechnungsverarbeitung",
          description:
            "Erkennt Eingangsrechnungen automatisch, extrahiert alle Positionen, gleicht mit Bestellungen ab und erstellt Buchungssätze.",
        },
        {
          icon: "📊",
          title: "DATEV-Synchronisation",
          description:
            "Exportiert Buchungen direkt in DATEV. Konto, Kostenstelle, USt. — alles automatisch zugeordnet und geprüft.",
        },
        {
          icon: "⚠️",
          title: "Mahnwesen",
          description:
            "Überwacht Zahlungseingänge, versendet Zahlungserinnerungen und Mahnstufen automatisch nach deinen Regeln.",
        },
        {
          icon: "💰",
          title: "Cash Flow Monitoring",
          description:
            "Echtzeit-Übersicht über Ein- und Ausgänge. Prognostiziert Liquiditätsengpässe und meldet Anomalien.",
        },
      ]}
      outcomeMetric="Pro verarbeitete Rechnung"
      outcomePrice="€0,75"
      outcomeSaving="vs. €5–8 manuell = 85–91% Ersparnis"
      comparison={[
        { metric: "Kosten pro Rechnung", kengo: "€0,75", manual: "€5–8" },
        { metric: "Verarbeitungszeit", kengo: "8 Sekunden", manual: "15–30 Min." },
        { metric: "Genauigkeit", kengo: "99,2%", manual: "~95%" },
        { metric: "Verfügbarkeit", kengo: "24/7", manual: "Bürozeiten" },
        { metric: "DATEV-Export", kengo: "Automatisch", manual: "Manuell" },
      ]}
      ctaLabel="Demo vereinbaren"
      ctaHref="https://cal.eu/philhie/kengo"
    />
  );
}

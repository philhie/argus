import SpecialistPageTemplate from "@/components/SpecialistPageTemplate";
import SpecialistCascade from "@/components/SpecialistCascade";
import { marketingScenarios } from "@/lib/specialist-demos";

export default function MarketingPage() {
  return (
    <SpecialistPageTemplate
      demo={<SpecialistCascade scenarios={marketingScenarios} />}
      badge={
        <span className="badge-live">
          <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-live" />
          LIVE
        </span>
      }
      headline="Dein autonomes Marketing-Team."
      subline="Von Content bis Campaign."
      bodyCopy="Plant Kampagnen, erstellt Content, scheduled Posts, analysiert Performance, optimiert Budgets. Von Social Media bis Newsletter — autonom und datengetrieben."
      capabilities={[
        { icon: "📣", title: "Kampagnen-Planung", description: "Erstellt datengetriebene Kampagnenpläne mit Zielgruppen, Kanälen, Timing und Budget-Allokation." },
        { icon: "✍️", title: "Content-Erstellung", description: "Schreibt Blog-Artikel, Social-Media-Posts, Newsletter und Landing Pages. In deinem Tone of Voice, für deine Zielgruppe." },
        { icon: "📊", title: "Performance-Analytics", description: "Trackt KPIs über alle Kanäle, identifiziert Top-Performer und generiert automatische Optimierungsvorschläge." },
        { icon: "💰", title: "Budget-Optimierung", description: "Verteilt Marketing-Budget automatisch auf die besten Kanäle. Echtzeit-Anpassung basierend auf Performance-Daten." },
      ]}
      outcomeMetric="Pro durchgeführte Kampagne"
      outcomePrice="€15,00"
      outcomeSaving="vs. €200–500 manuell = 92–97% Ersparnis"
      comparison={[
        { metric: "Kosten pro Kampagne", kengo: "€15,00", manual: "€200–500" },
        { metric: "Content-Erstellung", kengo: "Minuten", manual: "Stunden/Tage" },
        { metric: "Kanalabdeckung", kengo: "Alle gleichzeitig", manual: "1–2 Kanäle" },
        { metric: "Verfügbarkeit", kengo: "24/7", manual: "Bürozeiten" },
        { metric: "Performance-Reports", kengo: "Echtzeit", manual: "Wöchentlich" },
      ]}
      ctaLabel="Demo vereinbaren"
      ctaHref="https://cal.eu/philhie/kengo"
    />
  );
}

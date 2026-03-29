"use client";

import { motion } from "framer-motion";
import { sectionReveal, staggerContainer, staggerItem } from "@/lib/motion";

const tiers = [
  {
    name: "KI-Assistent",
    subtitle: "Für Einzelunternehmer & kleine Teams",
    price: "€1.999",
    period: "/Monat",
    features: [
      "1 KI-Arbeiter (Generalist)",
      "Erste Fachkraft-Kompetenz inklusive",
      "E-Mail, Kalender, Dokumente",
      "Automatisierungen in natürlicher Sprache",
      "5 Tage Einarbeitung",
      "Monatlich kündbar",
    ],
    cta: "Demo vereinbaren",
    ctaStyle: "secondary" as const,
    href: "https://cal.eu/philhie/kengo",
  },
  {
    name: "KI-Fachkraft",
    subtitle: "Für wachsende Unternehmen",
    price: "Individuell",
    period: "",
    highlighted: true,
    features: [
      "Alles aus KI-Assistent",
      "3 Spezialisten-Kompetenzen",
      "Finance, Support, HR — nach Wahl",
      "Ergebnis-basierte Abrechnung",
      "Priority Support",
      "Dedizierter Onboarding-Manager",
    ],
    cta: "Demo vereinbaren",
    ctaStyle: "primary" as const,
    href: "https://cal.eu/philhie/kengo",
  },
  {
    name: "KI-Abteilung",
    subtitle: "Für den gesamten Mittelstand",
    price: "Individuell",
    period: "",
    features: [
      "Alles aus KI-Fachkraft",
      "Unbegrenzte Spezialisten",
      "KI-Abteilungsleiter",
      "Cross-Agent Intelligence",
      "Executive Weekly Summary",
      "Budget-Dashboard & Reporting",
    ],
    cta: "Demo vereinbaren",
    ctaStyle: "secondary" as const,
    href: "https://cal.eu/philhie/kengo",
  },
];

export default function PricingPreview() {
  return (
    <section id="preise" className="section-padding bg-light-bg">
      <div className="max-w-page mx-auto px-6">
        <motion.div
          variants={sectionReveal}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          custom={0}
          className="text-center mb-4"
        >
          <h2 className="text-[32px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.15] text-text-primary-light">
            Transparent. Bezahlbar. Kein Risiko.
          </h2>
        </motion.div>

        <motion.p
          variants={sectionReveal}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          custom={0.1}
          className="text-lg text-text-secondary-light text-center max-w-2xl mx-auto mb-16 leading-relaxed"
        >
          Ein festes Gehalt für deinen Generalisten. Spezialisten zahlen sich nur
          bei Ergebnissen aus. Monatlich kündbar. Keine versteckten Kosten.
        </motion.p>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid md:grid-cols-3 gap-4"
        >
          {tiers.map((tier) => (
            <motion.div
              key={tier.name}
              variants={staggerItem}
              className={`rounded-2xl p-8 flex flex-col relative ${
                tier.highlighted
                  ? "bg-white border-2 border-kengo shadow-lg shadow-kengo/5"
                  : "bg-light-surface border border-light-border"
              }`}
            >
              {tier.highlighted && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="bg-kengo text-white text-[11px] font-semibold uppercase tracking-wider px-3 py-1 rounded-full">
                    Beliebteste Wahl
                  </span>
                </div>
              )}

              <p className="text-xs font-semibold uppercase tracking-wider text-muted mb-1">
                {tier.subtitle}
              </p>
              <h3 className="text-xl font-display font-semibold text-text-primary-light mb-4">
                {tier.name}
              </h3>

              <div className="flex items-baseline gap-1 mb-6">
                <span className="text-[40px] font-mono font-bold text-text-primary-light tracking-tight">
                  {tier.price}
                </span>
                {tier.period && (
                  <span className="text-sm text-text-secondary-light">
                    {tier.period}
                  </span>
                )}
              </div>

              <ul className="space-y-3 mb-8 flex-1">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-2.5 text-sm text-text-secondary-light">
                    <svg className="w-4 h-4 text-kengo flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                    {feature}
                  </li>
                ))}
              </ul>

              <a
                href={tier.href}
                target="_blank"
                rel="noopener noreferrer"
                className={`inline-flex items-center justify-center gap-2 w-full font-semibold px-6 py-3 rounded-xl text-base transition-all duration-150 ${
                  tier.ctaStyle === "primary"
                    ? "bg-kengo text-white hover:bg-kengo-light hover:scale-[1.02]"
                    : "bg-transparent border border-light-border text-text-primary-light hover:border-kengo"
                }`}
              >
                {tier.cta}
              </a>
            </motion.div>
          ))}
        </motion.div>

        <motion.p
          variants={sectionReveal}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          custom={0.25}
          className="text-sm text-text-secondary-light text-center mt-8 mb-4"
        >
          Im Demo-Gespräch erstellen wir dein individuelles Angebot basierend auf deiner Teamgröße.
        </motion.p>

        <motion.div
          variants={sectionReveal}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          custom={0.3}
          className="text-center"
        >
          <a href="/preise" className="text-sm text-kengo hover:text-kengo-light transition-colors font-medium inline-flex items-center gap-1">
            Alle Preise ansehen
            <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </a>
        </motion.div>
      </div>
    </section>
  );
}

"use client";

import { motion } from "framer-motion";
import { sectionReveal, staggerContainer, staggerItem } from "@/lib/motion";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";

interface Capability {
  icon: string;
  title: string;
  description: string;
}

interface ComparisonRow {
  metric: string;
  kengo: string;
  manual: string;
}

interface SpecialistPageProps {
  badge: React.ReactNode;
  headline: string;
  subline: string;
  bodyCopy: string;
  capabilities: Capability[];
  demo?: React.ReactNode;
  outcomeMetric: string;
  outcomePrice: string;
  outcomeSaving: string;
  comparison: ComparisonRow[];
  ctaLabel: string;
  ctaHref: string;
}

export default function SpecialistPageTemplate({
  badge,
  headline,
  subline,
  bodyCopy,
  capabilities,
  demo,
  outcomeMetric,
  outcomePrice,
  outcomeSaving,
  comparison,
  ctaLabel,
  ctaHref,
}: SpecialistPageProps) {
  return (
    <>
      <Navigation />
      <main>
        {/* Hero */}
        <section className="relative pt-32 pb-20 overflow-hidden">
          <div className="absolute inset-0 hero-glow" />
          <div className="absolute inset-0 bg-grid opacity-30" />

          <div className="relative z-10 max-w-page mx-auto px-6">
            {/* Back link */}
            <motion.a
              href="/#specialists"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
              className="inline-flex items-center gap-1.5 text-sm text-text-secondary hover:text-text-primary transition-colors mb-8"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
              </svg>
              Alle Produkte
            </motion.a>

            <motion.div
              variants={sectionReveal}
              initial="hidden"
              animate="visible"
              custom={0}
              className="max-w-3xl"
            >
              <div className="mb-4">{badge}</div>

              <h1 className="text-[36px] sm:text-[48px] md:text-[64px] font-display font-semibold tracking-[-0.03em] leading-[1.05] mb-4">
                {headline}
              </h1>

              <p className="text-lg md:text-xl text-text-secondary leading-[1.6] mb-6 max-w-2xl">
                {subline}
              </p>

              <p className="text-base text-text-secondary leading-relaxed max-w-2xl mb-10">
                {bodyCopy}
              </p>

              <div className="flex flex-col sm:flex-row gap-3">
                <a href={ctaHref} target="_blank" rel="noopener noreferrer" className="btn-primary-lg">
                  {ctaLabel}
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </a>
                <a href="/#preise" className="btn-secondary px-8 py-4">
                  Preise ansehen
                </a>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Optional demo */}
        {demo && (
          <section className="section-padding">
            <div className="max-w-page mx-auto px-6">
              {demo}
            </div>
          </section>
        )}

        {/* Capabilities */}
        <section className="section-padding">
          <div className="max-w-page mx-auto px-6">
            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="grid sm:grid-cols-2 gap-4"
            >
              {capabilities.map((cap) => (
                <motion.div key={cap.title} variants={staggerItem} className="card">
                  <span className="text-2xl mb-4 block">{cap.icon}</span>
                  <h3 className="text-lg font-display font-semibold mb-2">
                    {cap.title}
                  </h3>
                  <p className="text-sm text-text-secondary leading-relaxed">
                    {cap.description}
                  </p>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Outcome Pricing */}
        <section className="section-padding bg-light-bg">
          <div className="max-w-page mx-auto px-6">
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
              custom={0}
              className="text-center mb-16"
            >
              <h2 className="text-[32px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.15] text-text-primary-light">
                Ergebnis-basierte Abrechnung.
              </h2>
              <p className="text-lg text-text-secondary-light mt-4 max-w-xl mx-auto">
                Keine Ergebnisse, keine Kosten.
              </p>
            </motion.div>

            <motion.div
              variants={sectionReveal}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              custom={0.1}
              className="max-w-lg mx-auto"
            >
              <div className="bg-white border-2 border-kengo rounded-2xl p-8 text-center shadow-lg shadow-kengo/5">
                <p className="text-sm font-semibold uppercase tracking-wider text-muted mb-2">
                  {outcomeMetric}
                </p>
                <div className="flex items-baseline justify-center gap-1 mb-2">
                  <span className="text-[56px] font-mono font-bold text-text-primary-light tracking-tight">
                    {outcomePrice}
                  </span>
                </div>
                <p className="text-sm text-success font-medium">
                  {outcomeSaving}
                </p>
              </div>
            </motion.div>

            {/* Comparison table */}
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              custom={0.2}
              className="max-w-2xl mx-auto mt-12"
            >
              <div className="bg-white border border-light-border rounded-2xl overflow-hidden">
                <div className="grid grid-cols-3 text-sm font-semibold border-b border-light-border">
                  <div className="p-4 text-text-secondary-light" />
                  <div className="p-4 text-kengo text-center">Kengo</div>
                  <div className="p-4 text-text-secondary-light text-center">Manuell</div>
                </div>
                {comparison.map((row) => (
                  <div key={row.metric} className="grid grid-cols-3 text-sm border-b border-light-border last:border-0">
                    <div className="p-4 text-text-secondary-light">{row.metric}</div>
                    <div className="p-4 text-text-primary-light font-medium text-center">{row.kengo}</div>
                    <div className="p-4 text-text-secondary-light text-center">{row.manual}</div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </section>

        {/* Bottom CTA */}
        <section className="section-padding">
          <div className="max-w-page mx-auto px-6 text-center">
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
              custom={0}
              className="max-w-2xl mx-auto"
            >
              <h2 className="text-[32px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.15] mb-6">
                Bereit?
              </h2>
              <p className="text-lg text-text-secondary mb-10">
                15 Minuten. Kein Verkaufsdruck. Du siehst deinen KI-Mitarbeiter live.
              </p>
              <a href={ctaHref} target="_blank" rel="noopener noreferrer" className="btn-primary-lg text-lg">
                {ctaLabel}
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </a>
              <p className="text-sm text-muted mt-6">
                Keine Kreditkarte. Kein Vertrag. Monatlich kündbar.
              </p>
            </motion.div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}

"use client";

import { motion } from "framer-motion";
import { sectionReveal, staggerContainer, staggerItem } from "@/lib/motion";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import CascadeDemo from "@/components/CascadeDemo";

const capabilities = [
  {
    icon: "🔄",
    title: "Autonome Automationen",
    description: "Erstellt und verwaltet Workflows in n8n — ohne manuelles Setup.",
  },
  {
    icon: "🧠",
    title: "Generative Intelligenz",
    description: "Nutzt Claude für Textgenerierung, Analyse und Entscheidungshilfe.",
  },
  {
    icon: "📋",
    title: "Office Management",
    description: "E-Mails, Kalender, Dokumente — der digitale Büromanager.",
  },
  {
    icon: "🎯",
    title: "Executive Assistant",
    description: "Briefings, Entscheidungsvorlagen, Terminkoordination für die Geschäftsführung.",
  },
  {
    icon: "📊",
    title: "Chief of Staff Intelligence",
    description: "Unternehmensweite Übersicht, KPI-Tracking, strategische Zusammenfassungen.",
  },
  {
    icon: "💻",
    title: "Vibe Coding",
    description: "Erstellt und modifiziert Code-Lösungen mit Claude Code.",
  },
  {
    icon: "📚",
    title: "Knowledge Management",
    description: "Baut und pflegt das Wissenssystem des Unternehmens. Findet jede Information in Sekunden.",
  },
  {
    icon: "🔍",
    title: "Autonome Recherche",
    description: "Recherchiert Markt, Wettbewerber, Lieferanten, Kandidaten — autonom und gründlich.",
  },
  {
    icon: "📈",
    title: "Autonomes Reporting",
    description: "Erstellt Berichte, Dashboards und Zusammenfassungen — täglich, wöchentlich, monatlich.",
  },
  {
    icon: "💬",
    title: "Communications Hub",
    description: "Zentraler Kommunikationsknoten: E-Mail, Slack, Teams, WhatsApp — alles an einem Ort.",
  },
  {
    icon: "🤝",
    title: "Onboarding Buddy",
    description: "Unterstützt neue Mitarbeiter: beantwortet Fragen, zeigt Prozesse, stellt Kollegen vor.",
  },
  {
    icon: "📌",
    title: "Projektmanagement",
    description: "Verfolgt Aufgaben, Deadlines und Abhängigkeiten. Erinnert proaktiv an offene Punkte.",
  },
];

export default function ArbeiterPage() {
  return (
    <>
      <Navigation />
      <main>
        {/* Hero */}
        <section className="relative pt-32 pb-20 overflow-hidden">
          <div className="absolute inset-0 hero-glow" />
          <div className="absolute inset-0 bg-grid opacity-30" />

          <div className="relative z-10 max-w-page mx-auto px-6">
            <motion.a
              href="/#solution"
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
              <div className="mb-4">
                <span className="badge-live">
                  <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-live" />
                  LIVE
                </span>
              </div>

              <h1 className="text-[36px] sm:text-[48px] md:text-[64px] font-display font-semibold tracking-[-0.03em] leading-[1.05] mb-4">
                Dein persönlicher KI-Mitarbeiter.
              </h1>

              <p className="text-lg md:text-xl text-text-secondary leading-[1.6] mb-8 max-w-2xl">
                Stell dir vor, du hättest jemanden, der neben dir sitzt und alles erledigt.
              </p>

              <p className="text-base text-text-secondary leading-relaxed max-w-2xl mb-10">
                Der KI-Arbeiter ist dein Generalist. Er baut Automatisierungen, beantwortet
                Fragen, managed dein Büro, assistiert bei Strategie, programmiert, und verwaltet
                dein Unternehmenswissen. Alles autonom. 24/7.
              </p>

              <div className="flex flex-col sm:flex-row gap-3">
                <a href="https://cal.eu/philhie/kengo" target="_blank" rel="noopener noreferrer" className="btn-primary-lg">
                  Demo vereinbaren
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

        {/* Pricing callout */}
        <section className="section-padding-sm border-t border-line">
          <div className="max-w-page mx-auto px-6 text-center">
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              custom={0}
            >
              <p className="text-sm text-text-secondary mb-2">Ab</p>
              <p className="text-[48px] font-mono font-bold text-kengo tracking-tight">€1.999</p>
              <p className="text-sm text-text-secondary">/Monat · Monatlich kündbar · Erste Fachkraft-Kompetenz inklusive</p>
            </motion.div>
          </div>
        </section>

        {/* Live demo */}
        <section className="section-padding">
          <div className="max-w-page mx-auto px-6">
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
              custom={0}
              className="text-center mb-12"
            >
              <h2 className="text-[32px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.15]">
                So arbeitet dein KI-Mitarbeiter.
              </h2>
            </motion.div>

            <CascadeDemo />
          </div>
        </section>

        {/* Capabilities */}
        <section className="section-padding">
          <div className="max-w-page mx-auto px-6">
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
              custom={0}
              className="text-center mb-16"
            >
              <h2 className="text-[32px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.15]">
                12 Kompetenzen. Ein Mitarbeiter.
              </h2>
            </motion.div>

            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4"
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

        {/* CTA */}
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
                Dein nächster Mitarbeiter wartet.
              </h2>
              <p className="text-lg text-text-secondary mb-10">
                15 Minuten. Kein Verkaufsdruck. Du siehst deinen KI-Mitarbeiter live.
              </p>
              <a href="https://cal.eu/philhie/kengo" target="_blank" rel="noopener noreferrer" className="btn-primary-lg text-lg">
                Demo vereinbaren
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

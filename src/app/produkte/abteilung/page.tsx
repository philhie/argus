"use client";

import { motion } from "framer-motion";
import { sectionReveal, staggerContainer, staggerItem } from "@/lib/motion";
import { specialists } from "@/lib/specialists";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";

const benefits = [
  {
    icon: "🧠",
    title: "Cross-Agent Intelligence",
    description:
      "Dein Finance-Spezialist weiß, dass Kunde Müller überfällig ist. Dein Support-Spezialist weiß, dass Müller ein offenes Ticket hat. Der Abteilungsleiter koordiniert: Mahnung pausieren bis Ticket gelöst.",
  },
  {
    icon: "📊",
    title: "Executive Weekly Summary",
    description:
      "Jeden Montag 8 Uhr: WhatsApp/Email an den GF. Letzte Woche: 347 Rechnungen, 89 Tickets, 23 Bewerbungen. Top-Issue: Lieferant X hat 3× verspätet. Empfehlung: Gespräch mit Einkauf.",
  },
  {
    icon: "💰",
    title: "Budget-Dashboard",
    description:
      "Gesamtkosten aller Agenten auf einen Blick. Trend-Analyse. Automatische Alerts bei Anomalien. Volle Kostenkontrolle.",
  },
  {
    icon: "⚡",
    title: "Auto-Onboarding",
    description:
      "Neuer Spezialist bekommt automatisch den gesamten Unternehmenskontext vom Master. Setup: 30 Minuten statt 4 Stunden.",
  },
];

export default function AbteilungPage() {
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
                Dein gesamtes KI-Team.
                <br />
                <span className="text-text-secondary">Ein Abteilungsleiter.</span>
              </h1>

              <p className="text-lg md:text-xl text-text-secondary leading-[1.6] mb-6 max-w-2xl">
                Er koordiniert. Er berichtet. Er optimiert. Autonom.
              </p>

              <p className="text-base text-text-secondary leading-relaxed max-w-2xl mb-10">
                Wenn dein KI-Team wächst — ein Arbeiter, drei Spezialisten, fünf
                Spezialisten — brauchst du jemanden, der das Ganze koordiniert.
                Der KI-Abteilungsleiter übernimmt: Cross-Agent Intelligence,
                Executive Weekly Summary, Budget-Dashboard, Performance-Reports,
                Auto-Onboarding neuer Spezialisten.
              </p>

              <div className="flex flex-col sm:flex-row gap-3">
                <a href="https://cal.eu/philhie/kengo" target="_blank" rel="noopener noreferrer" className="btn-primary-lg">
                  Demo vereinbaren
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </a>
                <a href="/preise" className="btn-secondary px-8 py-4">
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
              <p className="text-2xl font-display font-semibold text-kengo">Individuell</p>
              <p className="text-base text-text-secondary mt-2">Basierend auf Teamgröße und Anforderungen</p>
              <p className="text-sm text-text-secondary mt-1">Unbegrenzte Spezialisten · Monatlich kündbar</p>
            </motion.div>
          </div>
        </section>

        {/* 4 Key Benefits */}
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
                Was der Abteilungsleiter kann.
              </h2>
            </motion.div>

            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="grid sm:grid-cols-2 gap-4"
            >
              {benefits.map((b) => (
                <motion.div key={b.title} variants={staggerItem} className="card">
                  <span className="text-2xl mb-4 block">{b.icon}</span>
                  <h3 className="text-lg font-display font-semibold mb-3">
                    {b.title}
                  </h3>
                  <p className="text-sm text-text-secondary leading-relaxed">
                    {b.description}
                  </p>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* All specialists included */}
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
                Alle 9 Spezialisten. Unbegrenzt.
              </h2>
              <p className="text-lg text-text-secondary-light mt-4 max-w-xl mx-auto">
                Im KI-Abteilung-Plan sind alle Spezialisten enthalten — koordiniert
                vom Abteilungsleiter.
              </p>
            </motion.div>

            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="grid sm:grid-cols-2 lg:grid-cols-3 gap-3 max-w-3xl mx-auto"
            >
              {specialists.map((s) => (
                <motion.a
                  key={s.name}
                  variants={staggerItem}
                  href={s.href}
                  className="flex items-center gap-3 bg-white border border-light-border rounded-xl px-5 py-4 hover:border-kengo transition-colors group"
                >
                  <span className="text-xl">{s.icon}</span>
                  <span className="text-sm font-medium text-text-primary-light group-hover:text-kengo transition-colors">
                    {s.name}
                  </span>
                </motion.a>
              ))}
            </motion.div>
          </div>
        </section>

        {/* How it works */}
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
                Wie die KI-Abteilung funktioniert.
              </h2>
            </motion.div>

            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="max-w-2xl mx-auto space-y-6"
            >
              {[
                {
                  step: "01",
                  title: "Spezialisten arbeiten autonom",
                  text: "Jeder Spezialist verarbeitet Rechnungen, löst Tickets, screent Bewerbungen — unabhängig und rund um die Uhr.",
                },
                {
                  step: "02",
                  title: "Abteilungsleiter koordiniert",
                  text: "Erkennt Abhängigkeiten zwischen Agenten. Pausiert Mahnungen bei offenen Tickets. Priorisiert basierend auf Geschäftskontex.",
                },
                {
                  step: "03",
                  title: "Du bekommst den Überblick",
                  text: "Wöchentliche Executive Summary. Budget-Dashboard. Performance-Reports. Alles auf einen Blick — ohne selbst koordinieren zu müssen.",
                },
              ].map((item) => (
                <motion.div
                  key={item.step}
                  variants={staggerItem}
                  className="flex items-start gap-5"
                >
                  <div className="w-12 h-12 rounded-xl bg-surface border border-line flex items-center justify-center flex-shrink-0">
                    <span className="font-mono text-sm font-bold text-kengo">{item.step}</span>
                  </div>
                  <div>
                    <h3 className="text-lg font-display font-semibold mb-1">{item.title}</h3>
                    <p className="text-sm text-text-secondary leading-relaxed">{item.text}</p>
                  </div>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Tech note */}
        <section className="section-padding-sm border-t border-line">
          <div className="max-w-page mx-auto px-6 text-center">
            <motion.p
              variants={sectionReveal}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              custom={0}
              className="text-sm text-text-secondary max-w-2xl mx-auto"
            >
              Built on Paperclip (30K+ GitHub Stars, MIT-licensed). The easiest
              multi-agent orchestration on the planet, autonomous and managed by Kengo.
            </motion.p>
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
                Deine KI-Abteilung wartet.
              </h2>
              <p className="text-lg text-text-secondary mb-10">
                15 Minuten. Kein Verkaufsdruck. Du siehst dein gesamtes KI-Team live.
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

"use client";

import { motion } from "framer-motion";
import { sectionReveal, staggerContainer, staggerItem } from "@/lib/motion";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";

const stats = [
  { value: "391.000", label: "unbesetzte Stellen in Deutschland" },
  { value: "103", label: "Gespräche mit Entscheidern" },
  { value: "32h", label: "pro Monat verschwendet an Admin" },
  { value: "59%", label: "der Aufgaben haben keinen Verantwortlichen" },
];

const journey = [
  {
    date: "2024",
    title: "Die Erkenntnis",
    description:
      "94.000 Tickets analysiert. 103 Gespräche mit IT-Leitern und Geschäftsführern in DACH. Das Muster war überall gleich: Automation-Tools existieren — aber fast nichts ist automatisiert.",
    active: false,
  },
  {
    date: "Q1 2025",
    title: "Die These",
    description:
      "Es muss schneller gehen, etwas für immer zu automatisieren, als es einmal manuell zu erledigen. Nicht Tools verbessern — Mitarbeiter ersetzen, die es nicht mehr gibt.",
    active: false,
  },
  {
    date: "Q1 2026",
    title: "Kengo",
    description:
      "Gründung. Erste KI-Mitarbeiter für Finance, Support und HR. Pilotprojekte mit deutschen Mittelständlern. Ergebnisse ab Tag 5.",
    active: true,
  },
  {
    date: "2027",
    title: "Europa",
    description:
      "Expansion in DACH, Benelux und Nordics. Neue Spezialisten für Legal, Logistics, Quality. Enterprise-Tier mit On-Premises-Deployment.",
    active: false,
  },
  {
    date: "2028+",
    title: "Globale KI-Belegschaft",
    description:
      "Jedes Unternehmen der Welt kann sich eine vollständige Belegschaft leisten. KI-Mitarbeiter als Standard — nicht als Experiment.",
    active: false,
  },
];

const values = [
  {
    title: "Ergebnisse, nicht Features",
    description:
      "Wir messen uns an verarbeiteten Rechnungen, gelösten Tickets, gescreenten Bewerbungen — nicht an Featurelisten.",
  },
  {
    title: "Deutsch zuerst, global von Tag eins",
    description:
      "Wir bauen für den deutschen Mittelstand, aber mit der Ambition, jedes Unternehmen der Welt zu bedienen.",
  },
  {
    title: "Transparenz als Prinzip",
    description:
      "Offene Preise. Offene Technologie. Offene Kommunikation. Unternehmer vertrauen denen, die nichts zu verbergen haben.",
  },
  {
    title: "Autonomie mit Kontrolle",
    description:
      "Unsere KI-Mitarbeiter arbeiten selbstständig — aber du bestimmst die Regeln. Human-in-the-Loop ist kein Kompromiss, sondern Design.",
  },
];

const products = [
  {
    number: "01",
    title: "KI-Arbeiter",
    subtitle: "Der Generalist",
    description:
      "E-Mails, Kalender, Dokumente, Automatisierungen. Dein persönlicher AI Associate, der dein Unternehmen versteht und alles erledigt.",
    href: "/produkte/arbeiter",
  },
  {
    number: "02",
    title: "KI-Fachkräfte",
    subtitle: "Die Spezialisten",
    description:
      "Finance, Sales, HR, IT, Marketing, Support, Procurement, Compliance, Cybersecurity. Bezahlung nur nach Ergebnis.",
    href: "/#specialists",
  },
  {
    number: "03",
    title: "KI-Abteilung",
    subtitle: "Das ganze Team",
    description:
      "Ein Abteilungsleiter koordiniert alle Agenten, berichtet dir, und optimiert die gesamte KI-Belegschaft automatisch.",
    href: "/produkte/abteilung",
  },
];

export default function UeberUnsPage() {
  return (
    <>
      <Navigation />
      <main>
        {/* Hero — Thesis Statement */}
        <section className="relative pt-32 pb-20 overflow-hidden">
          <div className="absolute inset-0 hero-glow" />
          <div className="absolute inset-0 bg-grid opacity-30" />

          <div className="relative z-10 max-w-page mx-auto px-6">
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              animate="visible"
              custom={0}
              className="max-w-4xl"
            >
              <h1 className="text-[32px] sm:text-[44px] md:text-[60px] font-display font-semibold tracking-[-0.03em] leading-[1.1] mb-8">
                Wir glauben, dass jedes Unternehmen{" "}
                <span className="text-kengo">ein vollständiges Team verdient.</span>
              </h1>

              <p className="text-lg md:text-xl text-text-secondary leading-[1.6] max-w-3xl mb-12">
                Wir haben 103 Gespräche mit Entscheidern im DACH-Raum geführt.
                Das Muster war überall gleich: Unternehmen haben Tools — aber
                keine Menschen mehr, die die Arbeit machen. Wir ändern das.
              </p>

              {/* Stats grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {stats.map((stat) => (
                  <div key={stat.label} className="text-center">
                    <div className="text-[28px] md:text-[36px] font-mono font-bold text-kengo tracking-tight">
                      {stat.value}
                    </div>
                    <p className="text-xs text-text-secondary mt-1">
                      {stat.label}
                    </p>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </section>

        {/* The Problem */}
        <section className="section-padding border-t border-line">
          <div className="max-w-page mx-auto px-6">
            <div className="grid md:grid-cols-2 gap-16 items-start">
              <motion.div
                variants={sectionReveal}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: "-100px" }}
                custom={0}
              >
                <p className="text-xs font-semibold uppercase tracking-wider text-kengo mb-4">
                  Das Problem
                </p>
                <h2 className="text-[28px] md:text-[36px] font-display font-semibold tracking-[-0.02em] leading-[1.15] mb-6">
                  Jedes Unternehmen hat Automation-Tools.
                  <br />
                  <span className="text-text-secondary">Fast nichts ist automatisiert.</span>
                </h2>
                <p className="text-base text-text-secondary leading-relaxed mb-6">
                  Der europäische Mittelstand ist das Rückgrat der Wirtschaft.
                  Aber er kämpft mit einem Problem, das kein Tool löst: Es gibt
                  nicht genug Menschen für die Arbeit, die getan werden muss.
                </p>
                <p className="text-base text-text-secondary leading-relaxed">
                  391.000 Stellen sind in Deutschland unbesetzt. Nicht weil die
                  Arbeit unwichtig ist, sondern weil es die Menschen nicht mehr gibt.
                </p>
              </motion.div>

              <motion.div
                variants={sectionReveal}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: "-100px" }}
                custom={0.2}
                className="card"
              >
                <svg className="w-8 h-8 text-kengo/30 mb-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M4.583 17.321C3.553 16.227 3 15 3 13.011c0-3.5 2.457-6.637 6.03-8.188l.893 1.378c-3.335 1.804-3.987 4.145-4.247 5.621.537-.278 1.24-.375 1.929-.311 1.804.167 3.226 1.648 3.226 3.489a3.5 3.5 0 01-3.5 3.5c-1.073 0-2.099-.49-2.748-1.179zm10 0C13.553 16.227 13 15 13 13.011c0-3.5 2.457-6.637 6.03-8.188l.893 1.378c-3.335 1.804-3.987 4.145-4.247 5.621.537-.278 1.24-.375 1.929-.311 1.804.167 3.226 1.648 3.226 3.489a3.5 3.5 0 01-3.5 3.5c-1.073 0-2.099-.49-2.748-1.179z" />
                </svg>
                <blockquote className="text-[15px] text-text-secondary leading-relaxed mb-6 italic">
                  &ldquo;Wir suchen seit 8 Monaten eine Sachbearbeiterin für die
                  Buchhaltung. Wenn ein KI-Mitarbeiter 60% dieser Arbeit
                  übernehmen kann, ist das ein No-Brainer.&rdquo;
                </blockquote>
                <div className="flex items-center gap-3 pt-4 border-t border-line">
                  <div className="w-9 h-9 rounded-full bg-kengo/10 flex items-center justify-center">
                    <span className="text-xs font-bold text-kengo">GF</span>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-text-primary">Geschäftsführer</p>
                    <p className="text-xs text-muted">Fertigungsunternehmen · 85 Mitarbeiter · Baden-Württemberg</p>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </section>

        {/* The Thesis */}
        <section className="section-padding">
          <div className="max-w-page mx-auto px-6">
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
              custom={0}
              className="max-w-3xl mx-auto text-center"
            >
              <p className="text-xs font-semibold uppercase tracking-wider text-kengo mb-6">
                Unsere These
              </p>
              <blockquote className="text-[24px] sm:text-[32px] md:text-[40px] font-display font-semibold tracking-[-0.02em] leading-[1.2] mb-8">
                Hör auf, KI als Tool zu betrachten.
                <br />
                <span className="text-kengo">Fang an, sie als Mitarbeiter einzustellen.</span>
              </blockquote>
              <p className="text-base text-text-secondary leading-relaxed max-w-2xl mx-auto">
                Kengo schließt die Lücke des Arbeitsmarkts — nicht mit Software,
                die Mitarbeiter unterstützt, sondern mit KI-Mitarbeitern, die
                selbstständig arbeiten. Autonom. Zuverlässig. 24/7. Ab Tag eins.
              </p>
            </motion.div>
          </div>
        </section>

        {/* What We Build */}
        <section className="section-padding border-t border-line">
          <div className="max-w-page mx-auto px-6">
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
              custom={0}
              className="mb-12"
            >
              <p className="text-xs font-semibold uppercase tracking-wider text-kengo mb-4">
                Was wir bauen
              </p>
              <h2 className="text-[28px] md:text-[40px] font-display font-semibold tracking-[-0.02em] leading-[1.15]">
                Drei Produkte. Eine autonome Belegschaft.
              </h2>
            </motion.div>

            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="grid md:grid-cols-3 gap-4"
            >
              {products.map((p) => (
                <motion.a
                  key={p.title}
                  variants={staggerItem}
                  href={p.href}
                  className="card-hover group"
                >
                  <span className="text-xs font-mono font-bold text-kengo block mb-4">
                    {p.number}
                  </span>
                  <p className="text-xs font-semibold uppercase tracking-wider text-muted mb-1">
                    {p.subtitle}
                  </p>
                  <h3 className="text-lg font-display font-semibold mb-3">
                    {p.title}
                  </h3>
                  <p className="text-sm text-text-secondary leading-relaxed">
                    {p.description}
                  </p>
                </motion.a>
              ))}
            </motion.div>
          </div>
        </section>

        {/* The Guarantee */}
        <section className="section-padding bg-light-bg">
          <div className="max-w-page mx-auto px-6">
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
              custom={0}
              className="max-w-3xl mx-auto text-center"
            >
              <p className="text-xs font-semibold uppercase tracking-wider text-kengo mb-6">
                Unsere Garantie
              </p>
              <h2 className="text-[28px] md:text-[44px] font-display font-semibold tracking-[-0.02em] leading-[1.15] text-text-primary-light mb-6">
                In 5 Tagen produktiv.
                <br />
                Oder du zahlst nichts.
              </h2>
              <p className="text-base text-text-secondary-light leading-relaxed mb-8 max-w-xl mx-auto">
                Wir verkaufen keine Software. Wir verkaufen Ergebnisse.
                Dein KI-Mitarbeiter wird innerhalb von 5 Tagen eingearbeitet und
                beginnt sofort, echte Arbeit zu erledigen. Monatlich kündbar.
                Keine versteckten Kosten.
              </p>
              <div className="grid grid-cols-3 gap-4 max-w-lg mx-auto">
                <div className="text-center">
                  <div className="text-[28px] font-mono font-bold text-text-primary-light">5</div>
                  <p className="text-xs text-text-secondary-light">Tage Einarbeitung</p>
                </div>
                <div className="text-center">
                  <div className="text-[28px] font-mono font-bold text-text-primary-light">24/7</div>
                  <p className="text-xs text-text-secondary-light">Arbeitszeit</p>
                </div>
                <div className="text-center">
                  <div className="text-[28px] font-mono font-bold text-text-primary-light">0</div>
                  <p className="text-xs text-text-secondary-light">Risiko</p>
                </div>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Founder */}
        <section className="section-padding">
          <div className="max-w-page mx-auto px-6">
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
              custom={0}
              className="max-w-3xl"
            >
              <p className="text-xs font-semibold uppercase tracking-wider text-kengo mb-4">
                Gebaut von Operators, nicht Beobachtern
              </p>

              <div className="flex items-center gap-5 mb-8">
                <div className="w-16 h-16 rounded-2xl bg-kengo/10 flex items-center justify-center">
                  <span className="text-2xl font-display font-semibold text-kengo">PH</span>
                </div>
                <div>
                  <h3 className="text-xl font-display font-semibold">
                    Phil Hie
                  </h3>
                  <p className="text-sm text-text-secondary">
                    Gründer & CEO · Berlin
                  </p>
                </div>
              </div>

              <p className="text-base text-text-secondary leading-relaxed mb-4">
                &ldquo;Ich habe bei Goldman Sachs im Investment Banking gearbeitet
                und als Founders Associate bei Avelios Medical ein KI-natives
                Krankenhaus-OS mitgebaut. Dort habe ich gesehen, wie KI ganze
                Abteilungen transformiert — wenn man sie nicht als Tool behandelt,
                sondern als Mitarbeiter einstellt.&rdquo;
              </p>
              <p className="text-base text-text-secondary leading-relaxed">
                &ldquo;Die 103 Gespräche mit Entscheidern in DACH haben mir
                eines gezeigt: Der Mittelstand erstickt nicht an fehlenden Tools.
                Er erstickt an fehlenden Menschen. Kengo existiert, um diese
                Lücke zu schließen.&rdquo;
              </p>
            </motion.div>
          </div>
        </section>

        {/* Vision Roadmap / Journey */}
        <section className="section-padding border-t border-line">
          <div className="max-w-page mx-auto px-6">
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
              custom={0}
              className="mb-12"
            >
              <p className="text-xs font-semibold uppercase tracking-wider text-kengo mb-4">
                Unsere Reise
              </p>
              <h2 className="text-[28px] md:text-[40px] font-display font-semibold tracking-[-0.02em] leading-[1.15]">
                Vom Mittelstand zur Welt.
              </h2>
            </motion.div>

            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="max-w-2xl relative"
            >
              {/* Vertical line */}
              <div className="absolute left-[23px] top-3 bottom-3 w-px bg-line" />

              {journey.map((m) => (
                <motion.div
                  key={m.title}
                  variants={staggerItem}
                  className="relative pl-14 pb-10 last:pb-0"
                >
                  {/* Dot */}
                  <div
                    className={`absolute left-[16px] top-1.5 w-[15px] h-[15px] rounded-full border-2 ${
                      m.active
                        ? "bg-kengo border-kengo animate-pulse-live"
                        : "bg-surface border-kengo"
                    }`}
                  />

                  <p className="text-xs font-mono font-bold text-kengo uppercase tracking-wider mb-1">
                    {m.date}
                  </p>
                  <h3 className="text-lg font-display font-semibold mb-1">
                    {m.title}
                    {m.active && (
                      <span className="ml-2 text-xs font-mono font-bold text-kengo bg-kengo/10 px-2 py-0.5 rounded-full">
                        JETZT
                      </span>
                    )}
                  </h3>
                  <p className="text-sm text-text-secondary leading-relaxed">
                    {m.description}
                  </p>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Values */}
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
              <h2 className="text-[28px] md:text-[40px] font-display font-semibold tracking-[-0.02em] leading-[1.15] text-text-primary-light">
                Woran wir glauben.
              </h2>
            </motion.div>

            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="grid sm:grid-cols-2 gap-4 max-w-3xl mx-auto"
            >
              {values.map((v) => (
                <motion.div
                  key={v.title}
                  variants={staggerItem}
                  className="bg-white border border-light-border rounded-2xl p-8"
                >
                  <h3 className="text-lg font-display font-semibold text-text-primary-light mb-3">
                    {v.title}
                  </h3>
                  <p className="text-sm text-text-secondary-light leading-relaxed">
                    {v.description}
                  </p>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Final CTA */}
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
              <h2 className="text-[28px] md:text-[44px] font-display font-semibold tracking-[-0.02em] leading-[1.15] mb-6">
                Dein nächster Mitarbeiter wartet.
              </h2>
              <p className="text-lg text-text-secondary mb-10 leading-relaxed">
                15 Minuten. Kein Verkaufsdruck. Du siehst deinen KI-Mitarbeiter live.
              </p>

              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <a
                  href="https://cal.eu/philhie/kengo"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-primary-lg text-lg"
                >
                  Demo vereinbaren
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </a>
                <a
                  href="mailto:hello@kengo.de"
                  className="text-sm text-text-secondary hover:text-kengo transition-colors"
                >
                  hello@kengo.de →
                </a>
              </div>
            </motion.div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}

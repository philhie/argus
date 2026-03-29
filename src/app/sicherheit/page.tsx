"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { sectionReveal, staggerContainer, staggerItem } from "@/lib/motion";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";

/* ─── Data ──────────────────────────────────────────────── */

const badges = [
  {
    icon: "🇩🇪",
    title: "Gehostet in Deutschland",
    description:
      "Alle Daten werden auf Hetzner-Servern in Falkenstein und Nürnberg verarbeitet. ISO 27001-zertifizierte Rechenzentren. Kein Byte verlässt Deutschland.",
  },
  {
    icon: "🔒",
    title: "DSGVO-konform",
    description:
      "Vollständige Einhaltung der EU-Datenschutzgrundverordnung. Auftragsverarbeitungsvertrag (AVV) inklusive. Deine Daten gehören dir.",
  },
  {
    icon: "🛡️",
    title: "Open-Source-auditierbar",
    description:
      "Kengo basiert auf OpenClaw — das größte Open-Source-KI-Projekt der Welt (319K+ GitHub Stars). Jede Zeile Code ist überprüfbar. Kein Black-Box-Problem.",
  },
  {
    icon: "🔐",
    title: "NemoClaw Enterprise Security",
    description:
      "NVIDIA's Enterprise-Sicherheitsschicht: Sandbox-Isolation, Netzwerk-Policies, Syscall-Filtering, Privacy-Routing. Installiert in einem Befehl.",
  },
];

const architectureItems = [
  {
    title: "Striktes Berechtigungsmanagement",
    description:
      "Zugriff auf Daten erfolgt nach dem Least-Privilege-Prinzip. Jeder Agent hat nur Zugriff auf die Systeme, die er braucht — nicht mehr.",
  },
  {
    title: "Sandbox-Isolation",
    description:
      "Jeder KI-Mitarbeiter läuft in einer eigenen, isolierten Umgebung. NVIDIA OpenShell kontrolliert Netzwerkzugriff, Dateisystem und Systemaufrufe.",
  },
  {
    title: "Hybrid Model Routing",
    description:
      "Sensible Daten werden lokal auf Open-Source-Modellen verarbeitet. Nur komplexe Aufgaben werden an Cloud-Modelle weitergeleitet — mit vollständiger Kontrolle.",
  },
  {
    title: "End-to-End-Verschlüsselung",
    description:
      "Alle Daten werden bei Übertragung (TLS 1.3) und im Ruhezustand (AES-256) verschlüsselt.",
  },
  {
    title: "Kein Modelltraining",
    description:
      "Deine Unternehmensdaten werden niemals zum Training von KI-Modellen verwendet. Garantiert.",
  },
  {
    title: "Kontinuierliches Monitoring",
    description:
      "Integrierte Überwachung erkennt und blockiert unautorisierte Zugriffe in Echtzeit.",
  },
];

const deploymentOptions = [
  {
    title: "Managed Cloud",
    description:
      "Gehostet auf Hetzner in Deutschland. Vollständig verwaltet durch Kengo. Zero Maintenance für dich.",
    tag: "Standard",
    highlighted: true,
  },
  {
    title: "Dedicated Instance",
    description:
      "Eigene, dedizierte Instanz auf Hetzner. Physisch getrennt von anderen Kunden.",
    tag: "Ab 100 MA",
    highlighted: false,
  },
  {
    title: "Bring Your Own Cloud",
    description:
      "Bereitstellung in deiner eigenen Cloud-Umgebung (AWS, Azure, GCP).",
    tag: "Enterprise",
    highlighted: false,
  },
  {
    title: "On-Premise",
    description:
      "Hosting auf deinen eigenen Servern. Inklusive Helm-Charts für Kubernetes.",
    tag: "Enterprise",
    highlighted: false,
  },
];

const complianceItems = [
  {
    title: "DSGVO-konform",
    description:
      "Umfassender Schutz der Betroffenenrechte. AVV-Vertrag standardmäßig. Hosting ausschließlich in der EU.",
  },
  {
    title: "Betriebsrat-kompatibel",
    description:
      "Kengo respektiert Mitbestimmungsrechte. Transparente Protokolle für den Betriebsrat. Keine verdeckte Leistungsüberwachung.",
  },
  {
    title: "Revisionssichere Protokolle",
    description:
      "Jede Aktion des KI-Mitarbeiters wird dokumentiert und ist nachvollziehbar. Audit-Trail für Wirtschaftsprüfer.",
  },
  {
    title: "Rollenbasierte Rechte",
    description:
      "Detaillierte Admin-Kontrollen. Wer darf was sehen, freigeben, konfigurieren.",
  },
  {
    title: "Vendor Risk Management",
    description:
      "Alle Subprozessoren werden regelmäßig auditiert. Transparente Lieferantenkette.",
  },
];

const legalDocs = [
  {
    title: "Datenschutzerklärung",
    cta: "Dokument ansehen →",
    href: "/datenschutz",
  },
  {
    title: "Auftragsverarbeitungsvertrag (AVV)",
    cta: "Auf Anfrage",
    href: "https://cal.eu/philhie/kengo",
    target: "_blank",
    rel: "noopener noreferrer",
  },
  {
    title: "Allgemeine Geschäftsbedingungen",
    cta: "Dokument ansehen →",
    href: "/agb",
  },
];

const faqs = [
  {
    q: "Wo werden meine Daten gehostet?",
    a: "Alle Daten werden auf Hetzner-Servern in Falkenstein und Nürnberg (Deutschland) verarbeitet und gespeichert. Die Rechenzentren sind ISO 27001-zertifiziert. Kein Byte verlässt Deutschland.",
  },
  {
    q: "Ist Kengo DSGVO-konform?",
    a: "Ja. Kengo verarbeitet alle Daten strikt gemäß der EU-DSGVO. Ein Auftragsverarbeitungsvertrag (AVV) ist standardmäßig enthalten. Deine Daten gehören dir — wir verarbeiten sie nur in deinem Auftrag.",
  },
  {
    q: "Werden meine Daten zum Training von KI-Modellen verwendet?",
    a: "Nein. Niemals. Deine Unternehmensdaten werden zu keinem Zeitpunkt zum Training, Fine-Tuning oder zur Verbesserung von KI-Modellen verwendet. Das ist vertraglich garantiert.",
  },
  {
    q: "Welche KI-Modelle nutzt Kengo?",
    a: "Kengo ist modellagnostisch. Wir setzen eine Kombination aus Open-Source-Modellen (Nemotron, Llama, Mistral) für Routineaufgaben und Frontier-Modellen (Claude, GPT) für komplexe Aufgaben ein. Sensible Daten werden bevorzugt lokal verarbeitet.",
  },
  {
    q: "Ist der Quellcode einsehbar?",
    a: "Ja. Kengo basiert auf OpenClaw, einem MIT-lizenzierten Open-Source-Projekt mit 319.000+ GitHub Stars. Jede Zeile Code ist öffentlich einsehbar und auditierbar.",
  },
  {
    q: "Wie lange dauert die Einrichtung?",
    a: "5 Arbeitstage. Wir übernehmen die komplette Einrichtung: Discovery-Call, Workflow-Design, Instanz-Konfiguration, Testing und Go-Live-Training. Du musst nichts technisches tun.",
  },
  {
    q: "Was passiert mit meinen Daten, wenn ich kündige?",
    a: "Bei Kündigung werden alle Daten innerhalb von 30 Tagen vollständig gelöscht. Auf Wunsch stellen wir einen Datenexport bereit. Die Löschung wird schriftlich bestätigt.",
  },
  {
    q: "Ist Kengo kompatibel mit dem Betriebsrat?",
    a: "Ja. Kengo wurde für den deutschen Markt entwickelt. Alle Aktionen des KI-Mitarbeiters sind transparent protokolliert. Es gibt keine verdeckte Leistungsüberwachung. Der Betriebsrat kann jederzeit Einsicht in die Audit-Logs nehmen.",
  },
];

/* ─── Page ──────────────────────────────────────────────── */

export default function SicherheitPage() {
  return (
    <>
      <Navigation />
      <main>
        {/* Section 1: Hero */}
        <section className="relative pt-32 pb-20 overflow-hidden">
          <div className="absolute inset-0 hero-glow" />
          <div className="absolute inset-0 bg-grid opacity-30" />
          <div className="relative z-10 max-w-page mx-auto px-6">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              <motion.div
                variants={sectionReveal}
                initial="hidden"
                animate="visible"
                custom={0}
              >
                <p className="text-sm font-semibold uppercase tracking-wider text-kengo mb-4">
                  Sicherheit
                </p>
                <h1 className="text-[36px] sm:text-[48px] md:text-[64px] font-display font-semibold tracking-[-0.03em] leading-[1.05] mb-6">
                  Deine Daten. Dein Land. Deine Kontrolle.
                </h1>
                <p className="text-lg md:text-xl text-text-secondary leading-[1.6] mb-8 max-w-xl">
                  Kengo schützt Geschäftsdaten auf Enterprise-Niveau — gehostet in
                  Deutschland, vollständig auditierbar, und so gebaut, dass kein Byte
                  dein Unternehmen unkontrolliert verlässt.
                </p>
                <a href="https://cal.eu/philhie/kengo" target="_blank" rel="noopener noreferrer" className="btn-primary-lg">
                  Demo vereinbaren
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </a>
              </motion.div>

              <motion.div
                variants={sectionReveal}
                initial="hidden"
                animate="visible"
                custom={0.3}
                className="flex items-center justify-center"
              >
                <div className="relative w-64 h-64">
                  <div className="absolute inset-0 rounded-full bg-kengo/5 animate-pulse" />
                  <div className="absolute inset-8 rounded-full bg-kengo/10" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <svg className="w-24 h-24 text-kengo" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
                    </svg>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </section>

        {/* Section 2: Trust Badges */}
        <section className="section-padding">
          <div className="max-w-page mx-auto px-6">
            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4"
            >
              {badges.map((badge) => (
                <motion.div
                  key={badge.title}
                  variants={staggerItem}
                  className="bg-surface border border-line rounded-2xl p-8"
                >
                  <span className="text-3xl block mb-4">{badge.icon}</span>
                  <h3 className="text-lg font-display font-semibold mb-2">
                    {badge.title}
                  </h3>
                  <p className="text-sm text-text-secondary leading-relaxed">
                    {badge.description}
                  </p>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Section 3: Sicherheitsarchitektur */}
        <section className="section-padding border-t border-line">
          <div className="max-w-page mx-auto px-6">
            <div className="grid lg:grid-cols-[1fr_2fr] gap-12 lg:gap-16">
              <motion.div
                variants={sectionReveal}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: "-100px" }}
                custom={0}
              >
                <h2 className="text-[32px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.15] sticky top-32">
                  Sicherheits&shy;architektur
                </h2>
              </motion.div>

              <motion.div
                variants={staggerContainer}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: "-50px" }}
              >
                {architectureItems.map((item) => (
                  <motion.div
                    key={item.title}
                    variants={staggerItem}
                    className="py-6 border-b border-line last:border-0"
                  >
                    <h3 className="text-base font-display font-semibold mb-2">
                      {item.title}
                    </h3>
                    <p className="text-sm text-text-secondary leading-relaxed">
                      {item.description}
                    </p>
                  </motion.div>
                ))}
              </motion.div>
            </div>
          </div>
        </section>

        {/* Section 4: Deployment-Optionen */}
        <section className="section-padding border-t border-line">
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
                Flexible Bereitstellung, passend zu deiner Infrastruktur
              </h2>
            </motion.div>

            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4"
            >
              {deploymentOptions.map((opt) => (
                <motion.div
                  key={opt.title}
                  variants={staggerItem}
                  className={`rounded-2xl p-8 ${
                    opt.highlighted
                      ? "bg-surface border-2 border-kengo"
                      : "bg-surface border border-line"
                  }`}
                >
                  <span
                    className={`inline-block text-xs font-semibold px-2.5 py-1 rounded-full mb-4 ${
                      opt.highlighted
                        ? "bg-kengo/10 text-kengo"
                        : "bg-surface text-muted"
                    }`}
                  >
                    {opt.tag}
                  </span>
                  <h3 className="text-lg font-display font-semibold mb-2">
                    {opt.title}
                  </h3>
                  <p className="text-sm text-text-secondary leading-relaxed">
                    {opt.description}
                  </p>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Section 5: Compliance & Governance */}
        <section className="section-padding border-t border-line">
          <div className="max-w-page mx-auto px-6">
            <div className="grid lg:grid-cols-[1fr_2fr] gap-12 lg:gap-16">
              <motion.div
                variants={sectionReveal}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: "-100px" }}
                custom={0}
              >
                <h2 className="text-[32px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.15] sticky top-32">
                  Compliance & Governance
                </h2>
              </motion.div>

              <motion.div
                variants={staggerContainer}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: "-50px" }}
              >
                {complianceItems.map((item) => (
                  <motion.div
                    key={item.title}
                    variants={staggerItem}
                    className="py-6 border-b border-line last:border-0"
                  >
                    <h3 className="text-base font-display font-semibold mb-2">
                      {item.title}
                    </h3>
                    <p className="text-sm text-text-secondary leading-relaxed">
                      {item.description}
                    </p>
                  </motion.div>
                ))}
              </motion.div>
            </div>
          </div>
        </section>

        {/* Section 6: Rechtliche Dokumente */}
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
              <h2 className="text-[32px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.15]">
                Rechtliche Dokumente
              </h2>
            </motion.div>

            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="max-w-3xl"
            >
              {legalDocs.map((doc) => (
                <motion.div
                  key={doc.title}
                  variants={staggerItem}
                  className="flex items-center justify-between py-5 border-b border-line"
                >
                  <span className="text-base font-display font-semibold">
                    {doc.title}
                  </span>
                  <a
                    href={doc.href}
                    {...("target" in doc ? { target: doc.target, rel: doc.rel } : {})}
                    className="text-sm text-kengo hover:text-kengo-light transition-colors font-medium"
                  >
                    {doc.cta}
                  </a>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Section 7: FAQ */}
        <section className="section-padding border-t border-line">
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
                Fragen & Antworten
              </h2>
            </motion.div>

            <div className="max-w-2xl mx-auto">
              {faqs.map((faq) => (
                <FAQItem key={faq.q} question={faq.q} answer={faq.a} />
              ))}
            </div>
          </div>
        </section>

        {/* Section 8: Final CTA */}
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
                Bereit, Ihre Daten in sicheren Händen zu wissen?
              </h2>
              <p className="text-lg text-text-secondary mb-10">
                Sprechen Sie mit uns über Ihre Sicherheitsanforderungen.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <a href="https://cal.eu/philhie/kengo" target="_blank" rel="noopener noreferrer" className="btn-primary-lg">
                  Demo vereinbaren
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </a>
                <a href="#" className="btn-secondary px-8 py-4">
                  Sicherheits-Datenblatt herunterladen
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

/* ─── FAQ Accordion ─────────────────────────────────────── */

function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="border-b border-line">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center justify-between w-full py-5 text-left"
      >
        <span className="text-base font-display font-semibold pr-4">
          {question}
        </span>
        <svg
          className={`w-5 h-5 text-text-secondary flex-shrink-0 transition-transform duration-200 ${
            open ? "rotate-45" : ""
          }`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={2}
        >
          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
        </svg>
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <p className="text-sm text-text-secondary leading-relaxed pb-5">
              {answer}
            </p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

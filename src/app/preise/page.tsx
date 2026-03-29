"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { sectionReveal, staggerContainer, staggerItem } from "@/lib/motion";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";

/* ─── Data ──────────────────────────────────────────────── */

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
      "Standard Support",
      "Monatlich kündbar",
    ],
    cta: "Demo vereinbaren",
    style: "secondary" as const,
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
      "Monatlich kündbar",
    ],
    cta: "Demo vereinbaren",
    style: "primary" as const,
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
      "Monatlich kündbar",
    ],
    cta: "Demo vereinbaren",
    style: "secondary" as const,
  },
];

const specialistPricing = [
  { name: "Finance", metric: "Pro Rechnung", price: "€0,75" },
  { name: "Customer Support", metric: "Pro Ticket", price: "€1,25" },
  { name: "HR", metric: "Pro Bewerbung", price: "€2,50" },
  { name: "Sales", metric: "Pro Lead", price: "€5,00" },
  { name: "Marketing", metric: "Pro Kampagne", price: "€15,00" },
  { name: "IT Ops", metric: "Pro Ticket", price: "€1,00" },
  { name: "Procurement", metric: "Pro Bestellung", price: "€1,50" },
  { name: "Compliance", metric: "Pro Report", price: "€25,00" },
  { name: "Cybersecurity", metric: "Pro Vorfall", price: "€50,00" },
];

const faqs = [
  {
    q: "Was passiert bei Fehlern?",
    a: "Dein KI-Mitarbeiter lernt kontinuierlich. Fehler werden sofort gemeldet und innerhalb von 24 Stunden korrigiert. Du behältst volle Kontrolle durch konfigurierbare Freigabe-Schwellenwerte. Kritische Aktionen erfordern immer menschliche Bestätigung.",
  },
  {
    q: "Kann ich jederzeit kündigen?",
    a: "Ja. Alle Pläne sind monatlich kündbar. Keine Mindestlaufzeit, kein Lock-in, keine versteckten Kündigungsgebühren. Deine Daten werden innerhalb von 30 Tagen nach Kündigung gelöscht.",
  },
  {
    q: "Wie funktioniert die Abrechnung?",
    a: "Der Grundpreis (KI-Assistent, KI-Fachkraft oder KI-Abteilung) wird monatlich im Voraus abgerechnet. Ergebnis-basierte Kosten für Spezialisten werden am Monatsende nach tatsächlichem Verbrauch berechnet. Du erhältst eine detaillierte Rechnung mit allen Einzelposten.",
  },
  {
    q: "Wo sind meine Daten?",
    a: "Alle Daten werden auf Hetzner-Servern in Deutschland gehostet. Kein Transfer in Drittländer. Vollständig DSGVO-konform. End-to-End-Verschlüsselung. Regelmäßige Penetrationstests und SOC 2 Typ II Audit in Vorbereitung.",
  },
  {
    q: "Wie lange dauert die Einarbeitung?",
    a: "5 Arbeitstage. Wir lernen dein Unternehmen kennen — Prozesse, Systeme, Ziele. Am Ende der Woche arbeitet dein KI-Mitarbeiter autonom. Dedizierter Onboarding-Manager bei KI-Fachkraft und KI-Abteilung.",
  },
  {
    q: "Kann ich mehrere Spezialisten gleichzeitig nutzen?",
    a: "Ja. Im KI-Fachkraft-Plan wählst du 3 Kompetenzen. Im KI-Abteilung-Plan sind alle Spezialisten unbegrenzt enthalten — und der KI-Abteilungsleiter koordiniert sie automatisch.",
  },
];

/* ─── Page ──────────────────────────────────────────────── */

export default function PreisePage() {
  return (
    <>
      <Navigation />
      <main>
        {/* Hero */}
        <section className="relative pt-32 pb-8 overflow-hidden">
          <div className="absolute inset-0 hero-glow" />
          <div className="relative z-10 max-w-page mx-auto px-6 text-center">
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              animate="visible"
              custom={0}
            >
              <h1 className="text-[40px] sm:text-[56px] md:text-[72px] font-display font-semibold tracking-[-0.03em] leading-[1.05] mb-4">
                Transparent. Bezahlbar.
                <br />
                Kein Risiko.
              </h1>
              <p className="text-lg md:text-xl text-text-secondary max-w-2xl mx-auto leading-relaxed">
                Ein festes Gehalt für deinen Generalisten. Spezialisten zahlen
                sich nur bei Ergebnissen aus. Monatlich kündbar. Keine
                versteckten Kosten.
              </p>
            </motion.div>
          </div>
        </section>

        {/* 3-Tier Pricing */}
        <section className="section-padding bg-light-bg">
          <div className="max-w-page mx-auto px-6">
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
                    <span className={`tracking-tight ${
                      tier.period
                        ? "text-[40px] font-mono font-bold text-text-primary-light"
                        : "text-2xl font-display font-semibold text-text-primary-light"
                    }`}>
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
                      <li
                        key={feature}
                        className="flex items-start gap-2.5 text-sm text-text-secondary-light"
                      >
                        <svg
                          className="w-4 h-4 text-kengo flex-shrink-0 mt-0.5"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                          strokeWidth={2}
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                        {feature}
                      </li>
                    ))}
                  </ul>

                  <a
                    href="https://cal.eu/philhie/kengo"
                    target="_blank"
                    rel="noopener noreferrer"
                    className={`inline-flex items-center justify-center gap-2 w-full font-semibold px-6 py-3 rounded-xl text-base transition-all duration-150 ${
                      tier.style === "primary"
                        ? "bg-kengo text-white hover:bg-kengo-light hover:scale-[1.02]"
                        : "bg-transparent border border-light-border text-text-primary-light hover:border-kengo"
                    }`}
                  >
                    {tier.cta}
                  </a>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Specialist Outcome Pricing */}
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
                Spezialisten: Bezahle nur Ergebnisse.
              </h2>
              <p className="text-lg text-text-secondary mt-4 max-w-xl mx-auto">
                Keine Ergebnisse, keine Kosten. Erste Kompetenz inklusive im
                KI-Arbeiter.
              </p>
            </motion.div>

            <motion.div
              variants={sectionReveal}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              custom={0.1}
              className="max-w-3xl mx-auto"
            >
              <div className="card overflow-hidden p-0">
                {/* Header */}
                <div className="grid grid-cols-4 text-sm font-semibold border-b border-line px-6 py-4">
                  <div className="col-span-1 text-text-secondary">Spezialist</div>
                  <div className="col-span-1 text-text-secondary">Metrik</div>
                  <div className="col-span-1 text-text-secondary">Preis</div>
                  <div className="col-span-1 text-text-secondary text-right">Status</div>
                </div>
                {/* Rows */}
                {specialistPricing.map((sp) => (
                  <div
                    key={sp.name}
                    className="grid grid-cols-4 text-sm border-b border-line last:border-0 px-6 py-4 items-center"
                  >
                    <div className="col-span-1 font-medium text-text-primary">{sp.name}</div>
                    <div className="col-span-1 text-text-secondary">{sp.metric}</div>
                    <div className="col-span-1 font-mono font-bold text-kengo">{sp.price}</div>
                    <div className="col-span-1 text-right">
                      <span className="badge-live">
                        <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-live" />
                        LIVE
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </section>

        {/* ROI Calculator */}
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
                Berechne deinen ROI.
              </h2>
              <p className="text-lg text-text-secondary-light mt-4 max-w-xl mx-auto">
                Wie viel spart dein Unternehmen mit Kengo? Gib deine Zahlen ein.
              </p>
            </motion.div>

            <ROICalculator />
          </div>
        </section>

        {/* FAQ */}
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
                Häufige Fragen.
              </h2>
            </motion.div>

            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="max-w-2xl mx-auto"
            >
              {faqs.map((faq) => (
                <FAQItem key={faq.q} question={faq.q} answer={faq.a} />
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
                15 Minuten. Kein Verkaufsdruck. Du siehst deinen KI-Mitarbeiter
                live.
              </p>
              <a href="https://cal.eu/philhie/kengo" target="_blank" rel="noopener noreferrer" className="btn-primary-lg text-lg">
                Demo vereinbaren
                <svg
                  className="w-4 h-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  strokeWidth={2}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M13 7l5 5m0 0l-5 5m5-5H6"
                  />
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

/* ─── ROI Calculator ────────────────────────────────────── */

function ROICalculator() {
  const [teamSize, setTeamSize] = useState(25);
  const [invoices, setInvoices] = useState(500);
  const [tickets, setTickets] = useState(300);

  // Cost assumptions
  const avgSalary = 4500; // monthly gross cost per FTE (Germany, admin/support)
  const adminHoursPerPerson = 32; // from Messaging Framework
  const hoursPerMonth = 160;
  const adminFTEs = (teamSize * adminHoursPerPerson) / hoursPerMonth;

  // Manual costs
  const manualInvoiceCost = invoices * 6.5; // €6.50 avg manual cost per invoice
  const manualTicketCost = tickets * 17.5; // €17.50 avg manual cost per ticket
  const manualAdminCost = adminFTEs * avgSalary;
  const totalManualCost = manualInvoiceCost + manualTicketCost + manualAdminCost;

  // Kengo costs
  const kengoBase = 2499; // KI-Fachkraft tier
  const kengoInvoiceCost = invoices * 0.75;
  const kengoTicketCost = tickets * 1.25;
  const totalKengoCost = kengoBase + kengoInvoiceCost + kengoTicketCost;

  const savings = totalManualCost - totalKengoCost;
  const savingsPercent = totalManualCost > 0 ? Math.round((savings / totalManualCost) * 100) : 0;

  const fmt = (n: number) =>
    n.toLocaleString("de-DE", { style: "currency", currency: "EUR", maximumFractionDigits: 0 });

  return (
    <motion.div
      variants={sectionReveal}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-50px" }}
      custom={0.1}
      className="max-w-4xl mx-auto"
    >
      <div className="grid md:grid-cols-2 gap-6">
        {/* Inputs */}
        <div className="bg-white border border-light-border rounded-2xl p-8">
          <h3 className="font-display font-semibold text-lg text-text-primary-light mb-6">
            Dein Unternehmen
          </h3>

          <div className="space-y-6">
            <SliderInput
              label="Teamgröße"
              value={teamSize}
              onChange={setTeamSize}
              min={5}
              max={500}
              step={5}
              suffix=" Mitarbeiter"
            />
            <SliderInput
              label="Rechnungen pro Monat"
              value={invoices}
              onChange={setInvoices}
              min={50}
              max={5000}
              step={50}
              suffix=""
            />
            <SliderInput
              label="Support-Tickets pro Monat"
              value={tickets}
              onChange={setTickets}
              min={50}
              max={5000}
              step={50}
              suffix=""
            />
          </div>
        </div>

        {/* Results */}
        <div className="bg-white border border-light-border rounded-2xl p-8">
          <h3 className="font-display font-semibold text-lg text-text-primary-light mb-6">
            Deine Ersparnis
          </h3>

          <div className="space-y-4 mb-8">
            <ResultRow label="Manuelle Kosten / Monat" value={fmt(totalManualCost)} muted />
            <ResultRow label="Kengo Kosten / Monat" value={fmt(totalKengoCost)} />
            <div className="h-px bg-light-border" />
            <ResultRow label="Ersparnis / Monat" value={fmt(savings)} highlight />
            <ResultRow label="Ersparnis / Jahr" value={fmt(savings * 12)} highlight />
          </div>

          <div className="bg-kengo/5 border border-kengo/20 rounded-xl p-5 text-center">
            <p className="text-[48px] font-mono font-bold text-kengo tracking-tight">
              {savingsPercent}%
            </p>
            <p className="text-sm text-text-secondary-light">
              weniger Kosten mit Kengo
            </p>
          </div>

          <a href="https://cal.eu/philhie/kengo" target="_blank" rel="noopener noreferrer" className="btn-primary w-full justify-center mt-6">
            Demo vereinbaren
          </a>
        </div>
      </div>

      <p className="text-xs text-text-secondary-light text-center mt-6">
        Basierend auf durchschnittlichen Verwaltungskosten im deutschen
        Mittelstand. Tatsächliche Ersparnis variiert je nach Unternehmen.
        KI-Fachkraft-Plan als Basis. Preise variieren je nach Unternehmensgröße.
      </p>
    </motion.div>
  );
}

function SliderInput({
  label,
  value,
  onChange,
  min,
  max,
  step,
  suffix,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min: number;
  max: number;
  step: number;
  suffix: string;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm text-text-secondary-light">{label}</label>
        <span className="text-sm font-mono font-bold text-text-primary-light">
          {value.toLocaleString("de-DE")}
          {suffix}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        className="w-full h-1.5 bg-light-border rounded-full appearance-none cursor-pointer accent-kengo [&::-webkit-slider-thumb]:bg-kengo [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:cursor-pointer"
      />
    </div>
  );
}

function ResultRow({
  label,
  value,
  muted,
  highlight,
}: {
  label: string;
  value: string;
  muted?: boolean;
  highlight?: boolean;
}) {
  return (
    <div className="flex items-center justify-between">
      <span className={`text-sm ${muted ? "text-text-secondary-light" : "text-text-primary-light"}`}>
        {label}
      </span>
      <span
        className={`text-sm font-mono font-bold ${
          highlight ? "text-kengo text-base" : muted ? "text-text-secondary-light" : "text-text-primary-light"
        }`}
      >
        {value}
      </span>
    </div>
  );
}

/* ─── FAQ Accordion ─────────────────────────────────────── */

function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [open, setOpen] = useState(false);

  return (
    <motion.div variants={staggerItem} className="border-b border-line">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center justify-between w-full py-5 text-left"
      >
        <span className="text-base font-display font-semibold pr-4">{question}</span>
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
      <div
        className={`overflow-hidden transition-all duration-300 ${
          open ? "max-h-96 pb-5" : "max-h-0"
        }`}
      >
        <p className="text-sm text-text-secondary leading-relaxed">{answer}</p>
      </div>
    </motion.div>
  );
}

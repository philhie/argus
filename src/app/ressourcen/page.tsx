"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { sectionReveal, staggerContainer, staggerItem } from "@/lib/motion";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";

/* ─── Data ──────────────────────────────────────────────── */

const resources = [
  {
    icon: "📄",
    title: "Executive Summary",
    description:
      "Die wichtigsten Fakten auf einer Seite. Was Kengo ist, was es kostet, wie schnell es live ist. Perfekt für die Geschäftsleitung.",
    cta: "PDF herunterladen",
    href: "#",
  },
  {
    icon: "📊",
    title: "ROI-Rechner",
    description:
      "Berechne in 60 Sekunden, wie viel dein Unternehmen mit einem KI-Mitarbeiter spart. Vergleiche Sachbearbeiter-Kosten mit Kengo.",
    cta: "ROI berechnen →",
    href: "#roi",
  },
  {
    icon: "📅",
    title: "Implementierungsplan",
    description:
      "5 Tage von der Entscheidung bis zum Go-Live. Der detaillierte Fahrplan für dein Onboarding.",
    cta: "Plan ansehen →",
    href: "#timeline",
  },
  {
    icon: "🔒",
    title: "Sicherheits-Datenblatt",
    description:
      "Technische Spezifikationen für deinen IT-Leiter: Hosting, Verschlüsselung, Compliance, Architektur.",
    cta: "PDF herunterladen",
    href: "#",
  },
  {
    icon: "⚖️",
    title: "Betriebsrats-Vorlage",
    description:
      "Muster-Betriebsvereinbarung für KI-Einsatz. Transparenz, Protokollierung, keine Leistungsüberwachung.",
    cta: "Vorlage herunterladen",
    href: "#",
  },
  {
    icon: "📈",
    title: "Vergleichsmatrix",
    description:
      "Kengo vs. Sachbearbeiter vs. ChatGPT vs. Copilot vs. Langdock. Alle Fakten auf einen Blick.",
    cta: "Vergleich ansehen →",
    href: "/vergleich",
  },
];

const timelineSteps = [
  {
    day: "Tag 1",
    title: "Discovery-Call",
    description:
      "30-Minuten-Gespräch: Wir lernen dein Unternehmen kennen. Welche Prozesse fressen Zeit? Wo liegt der größte Hebel?",
  },
  {
    day: "Tag 2",
    title: "Workflow-Design",
    description:
      "Wir designen die Workflows deines KI-Mitarbeiters. Welche E-Mails soll er bearbeiten? Welche Dokumente verarbeiten?",
  },
  {
    day: "Tag 3",
    title: "Setup & Konfiguration",
    description:
      "Deine dedizierte Kengo-Instanz wird aufgesetzt. Gehostet auf Hetzner. Verbunden mit deinen Tools (Email, Kalender, Slack/Teams).",
  },
  {
    day: "Tag 4",
    title: "Testing & Feintuning",
    description:
      "Wir testen deinen KI-Mitarbeiter mit echten Daten. Jeder Workflow wird geprüft und optimiert.",
  },
  {
    day: "Tag 5",
    title: "Go-Live & Training",
    description:
      "Dein KI-Mitarbeiter geht live. Dein Team bekommt ein 60-Minuten-Training. Support-Kanal ist ab sofort aktiv.",
  },
];

/* ─── Page ──────────────────────────────────────────────── */

export default function RessourcenPage() {
  return (
    <>
      <Navigation />
      <main>
        {/* Section 1: Hero */}
        <section className="relative pt-32 pb-20 overflow-hidden">
          <div className="absolute inset-0 hero-glow" />
          <div className="absolute inset-0 bg-grid opacity-30" />
          <div className="relative z-10 max-w-page mx-auto px-6 text-center">
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              animate="visible"
              custom={0}
            >
              <p className="text-sm font-semibold uppercase tracking-wider text-kengo mb-4">
                Ressourcen
              </p>
              <h1 className="text-[36px] sm:text-[48px] md:text-[64px] font-display font-semibold tracking-[-0.03em] leading-[1.05] mb-6">
                Alles, was du brauchst, um Kengo intern durchzusetzen.
              </h1>
              <p className="text-lg md:text-xl text-text-secondary max-w-2xl mx-auto leading-relaxed">
                Der Geschäftsführer will. Der IT-Leiter fragt. Der Betriebsrat prüft.
                Wir geben dir die Antworten — für jeden Stakeholder.
              </p>
            </motion.div>
          </div>
        </section>

        {/* Section 2: Resource Grid */}
        <section className="section-padding">
          <div className="max-w-page mx-auto px-6">
            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4"
            >
              {resources.map((r) => (
                <motion.div
                  key={r.title}
                  variants={staggerItem}
                  className="bg-surface border border-line rounded-2xl p-8 hover:border-kengo/50 transition-all"
                >
                  <span className="text-3xl block mb-4">{r.icon}</span>
                  <h3 className="text-xl font-display font-semibold mb-3">
                    {r.title}
                  </h3>
                  <p className="text-sm text-text-secondary leading-relaxed mb-6">
                    {r.description}
                  </p>
                  <a
                    href={r.href}
                    className="text-sm text-kengo hover:text-kengo-light transition-colors font-medium inline-flex items-center gap-1"
                  >
                    {r.cta}
                  </a>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Section 3: ROI Calculator */}
        <section id="roi" className="section-padding border-t border-line">
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
                Was spart dein Unternehmen mit Kengo?
              </h2>
            </motion.div>

            <ROICalculator />
          </div>
        </section>

        {/* Section 4: Implementation Timeline */}
        <section id="timeline" className="section-padding border-t border-line">
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
                5 Tage bis zum Go-Live
              </h2>
            </motion.div>

            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="max-w-4xl mx-auto"
            >
              {/* Desktop: horizontal timeline */}
              <div className="hidden md:grid grid-cols-5 gap-4">
                {timelineSteps.map((step, i) => (
                  <motion.div key={step.day} variants={staggerItem} className="text-center">
                    <div className="flex flex-col items-center">
                      <div className="w-12 h-12 rounded-full bg-kengo/10 border-2 border-kengo flex items-center justify-center mb-4">
                        <span className="font-mono text-sm font-bold text-kengo">
                          {i + 1}
                        </span>
                      </div>
                      {i < 4 && (
                        <div className="hidden md:block absolute w-full h-px bg-line top-6 left-1/2" />
                      )}
                    </div>
                    <p className="text-xs font-semibold uppercase tracking-wider text-kengo mb-1">
                      {step.day}
                    </p>
                    <h3 className="text-sm font-display font-semibold mb-2">
                      {step.title}
                    </h3>
                    <p className="text-xs text-text-secondary leading-relaxed">
                      {step.description}
                    </p>
                  </motion.div>
                ))}
              </div>

              {/* Mobile: vertical timeline */}
              <div className="md:hidden space-y-6">
                {timelineSteps.map((step, i) => (
                  <motion.div
                    key={step.day}
                    variants={staggerItem}
                    className="flex items-start gap-5"
                  >
                    <div className="w-12 h-12 rounded-full bg-kengo/10 border-2 border-kengo flex items-center justify-center flex-shrink-0">
                      <span className="font-mono text-sm font-bold text-kengo">
                        {i + 1}
                      </span>
                    </div>
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-wider text-kengo mb-1">
                        {step.day}
                      </p>
                      <h3 className="text-base font-display font-semibold mb-1">
                        {step.title}
                      </h3>
                      <p className="text-sm text-text-secondary leading-relaxed">
                        {step.description}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          </div>
        </section>

        {/* Section 5: Final CTA */}
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
                Bereit für dein erstes Team-Meeting über Kengo?
              </h2>
              <p className="text-lg text-text-secondary mb-10">
                Lade die Unterlagen herunter und überzeuge dein Team in 10 Minuten.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <a href="https://cal.eu/philhie/kengo" target="_blank" rel="noopener noreferrer" className="btn-primary-lg">
                  Demo vereinbaren
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </a>
                <a href="#" className="btn-secondary px-8 py-4">
                  Alle PDFs herunterladen
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

/* ─── ROI Calculator ────────────────────────────────────── */

function getKengoPrice(employees: number): number {
  if (employees <= 30) return 1999;
  if (employees <= 80) return 2499;
  if (employees <= 150) return 3499;
  if (employees <= 250) return 4999;
  if (employees <= 500) return 6999;
  return 8999;
}

function ROICalculator() {
  const [employees, setEmployees] = useState(50);
  const [salary, setSalary] = useState(3500);
  const [routineHours, setRoutineHours] = useState(15);

  // Calculations
  const fullCostPerEmployee = salary * 1.3 + 400; // 30% employer costs + workplace
  const kengoCost = getKengoPrice(employees);
  const monthlySavings = fullCostPerEmployee - kengoCost;
  const yearlySavings = monthlySavings * 12;
  const hoursPerMonth = routineHours * 4.33;

  const fmt = (n: number) =>
    Math.round(n).toLocaleString("de-DE", {
      style: "currency",
      currency: "EUR",
      maximumFractionDigits: 0,
    });

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
        <div className="bg-surface border border-line rounded-2xl p-8">
          <h3 className="font-display font-semibold text-lg mb-6">
            Dein Unternehmen
          </h3>
          <div className="space-y-6">
            <SliderInput
              label="Anzahl Mitarbeiter"
              value={employees}
              onChange={setEmployees}
              min={10}
              max={500}
              step={10}
              suffix=" Mitarbeiter"
            />
            <SliderInput
              label="Sachbearbeiter-Gehalt (brutto/Monat)"
              value={salary}
              onChange={setSalary}
              min={2000}
              max={6000}
              step={100}
              prefix="€"
              suffix=""
            />
            <SliderInput
              label="Routineaufgaben pro Woche (Stunden)"
              value={routineHours}
              onChange={setRoutineHours}
              min={5}
              max={40}
              step={1}
              suffix="h"
            />
          </div>
        </div>

        {/* Results */}
        <div className="bg-surface border border-line rounded-2xl p-8">
          <h3 className="font-display font-semibold text-lg mb-6">
            Deine Ersparnis
          </h3>
          <div className="space-y-4 mb-8">
            <ResultRow
              label="Vollkosten Sachbearbeiter/Monat"
              value={fmt(fullCostPerEmployee)}
              muted
            />
            <ResultRow
              label="Kengo Kosten/Monat"
              value={fmt(kengoCost)}
            />
            <p className="text-sm text-text-secondary mt-1 ml-1">
              Basierend auf {employees} Mitarbeitern
            </p>
            <div className="h-px bg-line" />
            <ResultRow
              label="Monatliche Ersparnis"
              value={fmt(monthlySavings)}
              highlight
            />
          </div>

          <div className="bg-kengo/5 border border-kengo/20 rounded-xl p-5 text-center">
            <p className="text-[48px] font-mono font-bold text-kengo tracking-tight">
              {fmt(yearlySavings)}
            </p>
            <p className="text-sm text-text-secondary">
              Jährliche Ersparnis
            </p>
          </div>

          <div className="mt-4 bg-surface border border-line rounded-xl p-4 text-center">
            <p className="text-2xl font-mono font-bold text-kengo">
              {Math.round(hoursPerMonth)}h
            </p>
            <p className="text-xs text-text-secondary">
              Stunden/Monat zurückgewonnen
            </p>
          </div>
        </div>
      </div>
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
  prefix,
  suffix,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  min: number;
  max: number;
  step: number;
  prefix?: string;
  suffix: string;
}) {
  return (
    <div>
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm text-text-secondary">{label}</label>
        <span className="text-sm font-mono font-bold">
          {prefix}
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
        className="w-full h-1.5 bg-line rounded-full appearance-none cursor-pointer accent-kengo [&::-webkit-slider-thumb]:bg-kengo [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:cursor-pointer"
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
      <span
        className={`text-sm ${muted ? "text-text-secondary" : "text-text-primary"}`}
      >
        {label}
      </span>
      <span
        className={`text-sm font-mono font-bold ${
          highlight
            ? "text-kengo text-base"
            : muted
              ? "text-text-secondary"
              : "text-text-primary"
        }`}
      >
        {value}
      </span>
    </div>
  );
}

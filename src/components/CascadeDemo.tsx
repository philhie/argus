"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

/* ─── Scenario data ───────────────────────────────────── */

interface CascadeStep {
  icon: string;
  system: string;
  action: string;
  detail: string;
}

interface Scenario {
  trigger: {
    icon: string;
    line1: string;
    line2: string;
  };
  steps: CascadeStep[];
  kicker: string;
}

const scenarios: Scenario[] = [
  // Scenario 1: Die Umplanung (reactive — email triggers chain)
  {
    trigger: {
      icon: "📧",
      line1: "Neue E-Mail von Schmidt AG",
      line2: "\"Können wir morgen auf 15 Uhr verschieben?\"",
    },
    steps: [
      { icon: "📅", system: "Kalender", action: "Meeting verschoben", detail: "14:00 → 15:00 · Alle Teilnehmer benachrichtigt" },
      { icon: "📋", system: "Briefing", action: "Agenda aktualisiert", detail: "⚠ Schmidt AG: 3× verspätet in Q1 — Verhandlungsposition nutzen" },
      { icon: "📧", system: "E-Mail", action: "Antwort gesendet", detail: "\"Kein Problem, 15 Uhr passt. Bis morgen.\"" },
      { icon: "🔧", system: "Workflow", action: "Erinnerung & Follow-up aktiv", detail: "14:45 Reminder · Auto-Protokoll nach Meeting an Team" },
    ],
    kicker: "4 Systeme · 0 Klicks · 12 Sekunden",
  },
  // Scenario 2: Der Morgen (proactive — no human trigger)
  {
    trigger: {
      icon: "☀️",
      line1: "06:00 — Dein KI-Arbeiter hat angefangen.",
      line2: "",
    },
    steps: [
      { icon: "📧", system: "E-Mail", action: "47 E-Mails sortiert", detail: "3 dringend · 12 wichtig · 32 informativ" },
      { icon: "📄", system: "DATEV", action: "Rechnung verarbeitet", detail: "Müller GmbH · €4.250 · Buchung #4721 erstellt" },
      { icon: "📅", system: "Kalender", action: "Tagesplan erstellt", detail: "3 Meetings · 2 Deadlines · 1 Erinnerung" },
      { icon: "📊", system: "Report", action: "Wochenreport generiert", detail: "Script → Daten → PDF → an Geschäftsführung gesendet" },
      { icon: "💬", system: "Wissen", action: "Mitarbeiter-Frage beantwortet", detail: "\"Reisekostenrichtlinie?\" → Aus Wissensdatenbank" },
      { icon: "🔧", system: "Workflow", action: "Neuer Workflow deployed", detail: "DSGVO-Anfragen → automatisch an Compliance-Team" },
    ],
    kicker: "6 Aufgaben erledigt, bevor du aufgewacht bist.",
  },
  // Scenario 3: Die Frage (intelligence — question to action)
  {
    trigger: {
      icon: "💬",
      line1: "\"Welche Kunden haben überfällige Rechnungen?\"",
      line2: "",
    },
    steps: [
      { icon: "🔍", system: "ERP", action: "3 Systeme durchsucht", detail: "DATEV, CRM, E-Mail-Archiv — in 2 Sekunden" },
      { icon: "📊", system: "Analyse", action: "7 Kunden gefunden", detail: "Gesamt: €34.750 überfällig · Älteste: 47 Tage" },
      { icon: "📄", system: "Report", action: "PDF generiert", detail: "Details pro Kunde, sortiert nach Betrag und Fälligkeit" },
      { icon: "📧", system: "E-Mail", action: "7 Mahnungen vorbereitet", detail: "Personalisierte E-Mails drafted · Warten auf Freigabe" },
      { icon: "🔧", system: "Workflow", action: "Auto-Mahnung erstellt", detail: "Künftig: >30 Tage überfällig → automatische Mahnung" },
    ],
    kicker: "Von Frage zu Aktion in 8 Sekunden.",
  },
];

/* ─── Animation config ────────────────────────────────── */

const STEP_DELAY = 900;       // ms between each cascade step
const TRIGGER_PAUSE = 1200;   // ms to show trigger before cascade starts
const KICKER_PAUSE = 600;     // ms after last step before kicker
const END_PAUSE = 3000;       // ms to hold the completed state

/* ─── Component ───────────────────────────────────────── */

export default function CascadeDemo() {
  const [scenarioIdx, setScenarioIdx] = useState(0);
  const [visibleSteps, setVisibleSteps] = useState(-1); // -1 = only trigger, 0+ = steps revealed
  const [showKicker, setShowKicker] = useState(false);
  const [transitioning, setTransitioning] = useState(false);
  const timeoutRefs = useRef<NodeJS.Timeout[]>([]);

  const scenario = scenarios[scenarioIdx];

  const clearTimeouts = useCallback(() => {
    timeoutRefs.current.forEach(clearTimeout);
    timeoutRefs.current = [];
  }, []);

  const runScenario = useCallback((idx: number) => {
    clearTimeouts();
    setTransitioning(false);
    setVisibleSteps(-1);
    setShowKicker(false);
    setScenarioIdx(idx);

    const sc = scenarios[idx];
    let elapsed = TRIGGER_PAUSE;

    // Reveal each step
    sc.steps.forEach((_, i) => {
      const t = setTimeout(() => setVisibleSteps(i), elapsed);
      timeoutRefs.current.push(t);
      elapsed += STEP_DELAY;
    });

    // Show kicker
    const kickerT = setTimeout(() => setShowKicker(true), elapsed + KICKER_PAUSE);
    timeoutRefs.current.push(kickerT);

    // Transition to next scenario
    const nextT = setTimeout(() => {
      setTransitioning(true);
      const fadeT = setTimeout(() => {
        runScenario((idx + 1) % scenarios.length);
      }, 400);
      timeoutRefs.current.push(fadeT);
    }, elapsed + KICKER_PAUSE + END_PAUSE);
    timeoutRefs.current.push(nextT);
  }, [clearTimeouts]);

  useEffect(() => {
    runScenario(0);
    return clearTimeouts;
  }, [runScenario, clearTimeouts]);

  return (
    <div className="relative max-w-2xl mx-auto">
      <motion.div
        animate={{ opacity: transitioning ? 0 : 1 }}
        transition={{ duration: 0.35 }}
        className="bg-surface border border-line rounded-2xl overflow-hidden"
      >
        <div className="p-5 sm:p-6 min-h-[380px] sm:min-h-[360px]">
          {/* Trigger */}
          <motion.div
            key={`trigger-${scenarioIdx}`}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
            className="flex items-start gap-3 mb-6"
          >
            <span className="text-xl flex-shrink-0">{scenario.trigger.icon}</span>
            <div>
              <p className="text-sm font-medium text-text-primary">
                {scenario.trigger.line1}
              </p>
              {scenario.trigger.line2 && (
                <p className="text-sm text-text-secondary mt-0.5">
                  {scenario.trigger.line2}
                </p>
              )}
            </div>
          </motion.div>

          {/* Cascade steps */}
          <div className="relative pl-5 ml-2">
            {/* Animated vertical line */}
            <motion.div
              className="absolute left-0 top-0 w-px bg-kengo"
              initial={{ height: 0 }}
              animate={{
                height: visibleSteps >= 0
                  ? `${Math.min(((visibleSteps + 1) / scenario.steps.length) * 100, 100)}%`
                  : "0%",
              }}
              transition={{ duration: 0.5, ease: "easeOut" }}
            />

            <div className="space-y-3">
              {scenario.steps.map((step, i) => (
                <AnimatePresence key={`${scenarioIdx}-${i}`}>
                  {visibleSteps >= i && (
                    <motion.div
                      initial={{ opacity: 0, x: -12 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{
                        duration: 0.35,
                        ease: [0.22, 1, 0.36, 1],
                      }}
                      className="relative flex items-start gap-3"
                    >
                      {/* Node dot on the line */}
                      <div className="absolute -left-5 top-1.5 w-[9px] h-[9px] rounded-full bg-surface border-2 border-kengo -translate-x-[4.5px]" />

                      <div className="flex items-start gap-3 flex-1 min-w-0">
                        <span className="text-base flex-shrink-0 mt-0.5">{step.icon}</span>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] font-semibold uppercase tracking-wider text-muted">
                              {step.system}
                            </span>
                            <span className="text-sm font-medium text-text-primary">
                              {step.action}
                            </span>
                            <motion.span
                              initial={{ opacity: 0, scale: 0.5 }}
                              animate={{ opacity: 1, scale: 1 }}
                              transition={{ duration: 0.2, delay: 0.15 }}
                            >
                              <svg className="w-3.5 h-3.5 text-kengo flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                                <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
                              </svg>
                            </motion.span>
                          </div>
                          <p className="text-xs text-muted mt-0.5 leading-relaxed">
                            {step.detail}
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              ))}
            </div>
          </div>

          {/* Kicker */}
          <AnimatePresence>
            {showKicker && (
              <motion.div
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.1 }}
                className="mt-6 pt-4 border-t border-line"
              >
                <p className="text-sm text-kengo font-medium text-center">
                  {scenario.kicker}
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Subtle glow */}
      <div className="absolute -inset-4 -z-10 bg-kengo/[0.03] rounded-3xl blur-2xl" />
    </div>
  );
}

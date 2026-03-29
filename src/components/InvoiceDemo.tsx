"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

/* ─── Invoice data pools (rotated each loop) ──────────── */

const invoices = [
  { company: "Müller GmbH", email: "buchhaltung@mueller-gmbh.de", nr: "RE-2024-0847", betrag: "€4.250,00", faellig: "15.04.2026", po: "PO-2024-0391", konto: "3400", kst: "120" },
  { company: "Schmidt AG", email: "rechnungen@schmidt-ag.de", nr: "RE-2024-1293", betrag: "€12.890,00", faellig: "22.04.2026", po: "PO-2024-0445", konto: "3300", kst: "200" },
  { company: "Weber Maschinenbau", email: "fibu@weber-maschinenbau.de", nr: "RE-2024-0562", betrag: "€1.780,50", faellig: "10.04.2026", po: "PO-2024-0287", konto: "3400", kst: "110" },
  { company: "Fischer Logistik", email: "invoice@fischer-logistik.de", nr: "RE-2024-2104", betrag: "€8.420,00", faellig: "30.04.2026", po: "PO-2024-0513", konto: "3310", kst: "300" },
  { company: "Braun Industries", email: "accounting@braun-industries.de", nr: "RE-2024-0931", betrag: "€3.150,75", faellig: "18.04.2026", po: "PO-2024-0398", konto: "3400", kst: "150" },
];

/* ─── Animation phases ────────────────────────────────── */

type Phase =
  | "idle"
  | "email"       // Email notification appears
  | "scanning"    // Fields extracting one by one
  | "field-1" | "field-2" | "field-3" | "field-4" | "field-5" | "field-6"
  | "result-1"    // DATEV export
  | "result-2"    // Confirmation sent
  | "done";       // Summary line

const PHASE_TIMING: Record<string, number> = {
  idle: 400,
  email: 1600,
  scanning: 600,
  "field-1": 350,
  "field-2": 300,
  "field-3": 300,
  "field-4": 280,
  "field-5": 320,
  "field-6": 400,
  "result-1": 500,
  "result-2": 500,
  done: 2500,
};

const PHASES: Phase[] = [
  "idle", "email", "scanning",
  "field-1", "field-2", "field-3", "field-4", "field-5", "field-6",
  "result-1", "result-2", "done",
];

/* ─── Component ───────────────────────────────────────── */

export default function InvoiceDemo() {
  const [phase, setPhase] = useState<Phase>("idle");
  const [invoiceIdx, setInvoiceIdx] = useState(0);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const inv = invoices[invoiceIdx % invoices.length];

  const phaseIndex = PHASES.indexOf(phase);
  const isAfter = (p: Phase) => phaseIndex >= PHASES.indexOf(p);

  const advancePhase = useCallback(() => {
    setPhase((current) => {
      const idx = PHASES.indexOf(current);
      if (idx >= PHASES.length - 1) {
        // Loop: reset and advance invoice
        setInvoiceIdx((i) => (i + 1) % invoices.length);
        return "idle";
      }
      return PHASES[idx + 1];
    });
  }, []);

  useEffect(() => {
    const duration = PHASE_TIMING[phase] || 500;
    timeoutRef.current = setTimeout(advancePhase, duration);
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [phase, advancePhase]);

  return (
    <div className="relative max-w-2xl mx-auto">
      <div className="bg-surface border border-line rounded-2xl overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-line">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-success animate-pulse-live" />
            <span className="text-xs font-medium text-text-secondary">Finance Spezialist</span>
          </div>
          <AnimatePresence>
            {isAfter("done") && (
              <motion.span
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-[10px] text-muted"
              >
                Nächste: 23 in Warteschlange
              </motion.span>
            )}
          </AnimatePresence>
        </div>

        <div className="p-5 min-h-[340px] sm:min-h-[300px]">
          {/* Phase 1: Email notification */}
          <AnimatePresence mode="wait">
            {isAfter("email") && (
              <motion.div
                key={`email-${inv.nr}`}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35, ease: [0.22, 1, 0.36, 1] }}
                className="mb-5"
              >
                <div className="flex items-start gap-3 bg-void/60 rounded-xl p-4">
                  <div className="w-8 h-8 rounded-lg bg-kengo/10 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <svg className="w-4 h-4 text-kengo" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                    </svg>
                  </div>
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-text-primary">Neue Eingangsrechnung</p>
                    <p className="text-xs text-text-secondary mt-0.5">
                      Von: {inv.company} &lt;{inv.email}&gt;
                    </p>
                    <p className="text-xs text-muted mt-1 flex items-center gap-1.5">
                      <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M18.375 12.739l-7.693 7.693a4.5 4.5 0 01-6.364-6.364l10.94-10.94A3 3 0 1119.5 7.372L8.552 18.32m.009-.01l-.01.01m5.699-9.941l-7.81 7.81a1.5 1.5 0 002.112 2.13" />
                      </svg>
                      Rechnung_{inv.company.replace(/\s/g, "_")}_{inv.nr.split("-").pop()}.pdf
                    </p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Phase 2: Field extraction */}
          {isAfter("scanning") && (
            <div className="space-y-0">
              <FieldRow visible={isAfter("field-1")} label="Lieferant" value={inv.company} delay={0} invoiceKey={inv.nr} />
              <FieldRow visible={isAfter("field-2")} label="Betrag" value={inv.betrag} delay={0.05} invoiceKey={inv.nr} />
              <FieldRow visible={isAfter("field-3")} label="Rechnungsnr" value={inv.nr} delay={0.1} invoiceKey={inv.nr} />
              <FieldRow visible={isAfter("field-4")} label="Fällig" value={inv.faellig} delay={0.15} invoiceKey={inv.nr} />
              <FieldRow visible={isAfter("field-5")} label="USt" value="19% geprüft" delay={0.2} invoiceKey={inv.nr} />
              <FieldRow visible={isAfter("field-6")} label="Bestellung" value={`${inv.po} — Match`} delay={0.25} invoiceKey={inv.nr} />
            </div>
          )}

          {/* Phase 3: Results */}
          <AnimatePresence>
            {isAfter("result-1") && (
              <motion.div
                key={`results-${inv.nr}`}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.3 }}
                className="mt-5 pt-4 border-t border-line space-y-2"
              >
                <ResultRow visible={isAfter("result-1")} text={`DATEV-Buchung erstellt — Konto ${inv.konto}, KSt ${inv.kst}`} />
                <ResultRow visible={isAfter("result-2")} text={`Bestätigung an ${inv.company} gesendet`} />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Phase 4: Summary */}
          <AnimatePresence>
            {isAfter("done") && (
              <motion.div
                initial={{ opacity: 0, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.1 }}
                className="mt-5 flex items-center justify-between text-xs"
              >
                <span className="text-muted">
                  Verarbeitet in <span className="text-kengo font-mono font-bold">8 Sek.</span>
                </span>
                <span className="text-muted">
                  Genauigkeit: <span className="text-kengo font-mono font-bold">99,2%</span>
                </span>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>

      {/* Subtle glow */}
      <div className="absolute -inset-4 -z-10 bg-kengo/[0.03] rounded-3xl blur-2xl" />
    </div>
  );
}

/* ─── Sub-components ──────────────────────────────────── */

function FieldRow({
  visible,
  label,
  value,
  delay,
  invoiceKey,
}: {
  visible: boolean;
  label: string;
  value: string;
  delay: number;
  invoiceKey: string;
}) {
  return (
    <AnimatePresence mode="wait">
      {visible && (
        <motion.div
          key={`${invoiceKey}-${label}`}
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.25, delay, ease: [0.22, 1, 0.36, 1] }}
          className="flex items-center justify-between py-2 px-1"
        >
          <span className="text-xs text-muted w-24 flex-shrink-0">{label}</span>
          <span className="text-sm font-mono text-text-primary">{value}</span>
          <motion.span
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.2, delay: delay + 0.15 }}
          >
            <svg className="w-4 h-4 text-kengo" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12.75l6 6 9-13.5" />
            </svg>
          </motion.span>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

function ResultRow({ visible, text }: { visible: boolean; text: string }) {
  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          initial={{ opacity: 0, x: -6 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
          className="flex items-center gap-2"
        >
          <svg className="w-4 h-4 text-success flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-sm text-success">{text}</span>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

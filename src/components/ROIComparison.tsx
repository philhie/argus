"use client";

import { motion } from "framer-motion";
import { sectionReveal, staggerContainer, staggerItem } from "@/lib/motion";

const rows = [
  { label: "Monatliche Kosten", human: "€4.750–5.333 (Vollkosten)", kengo: "ab €1.999" },
  { label: "Einstellungszeit", human: "70+ Tage", kengo: "5 Tage" },
  { label: "Arbeitszeit", human: "40h / Woche", kengo: "168h / Woche (24/7)" },
  { label: "Krankheitstage", human: "~15 pro Jahr", kengo: "0" },
  { label: "Urlaubstage", human: "30 pro Jahr", kengo: "0" },
  { label: "Kündigungsfrist", human: "1–6 Monate", kengo: "Monatlich kündbar" },
  { label: "Skalierung", human: "Monate pro Stelle", kengo: "Stunden pro Agent" },
  { label: "Einarbeitung neuer MA", human: "Wochen", kengo: "Sofort (Unternehmenskontext geteilt)" },
];

export default function ROIComparison() {
  return (
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
            Sachbearbeiter vs. Kengo Mitarbeiter
          </h2>
          <p className="text-lg text-text-secondary mt-4 max-w-2xl mx-auto">
            Der direkte Vergleich — warum sich der Wechsel ab Tag 1 rechnet.
          </p>
        </motion.div>

        <motion.div
          variants={sectionReveal}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          custom={0.1}
          className="max-w-4xl mx-auto"
        >
          <div className="card overflow-hidden p-0">
            {/* Header */}
            <div className="grid grid-cols-3 text-sm font-semibold border-b border-line px-6 py-4">
              <div className="text-text-secondary">Kriterium</div>
              <div className="text-text-secondary">Sachbearbeiter</div>
              <div className="text-kengo">Kengo Mitarbeiter</div>
            </div>

            {/* Rows */}
            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
            >
              {rows.map((row, i) => (
                <motion.div
                  key={row.label}
                  variants={staggerItem}
                  className={`grid grid-cols-3 text-sm border-b border-line last:border-0 px-6 py-4 items-center ${
                    i % 2 === 0 ? "bg-surface" : ""
                  }`}
                >
                  <div className="font-medium text-text-primary">{row.label}</div>
                  <div className="text-text-secondary">{row.human}</div>
                  <div className="text-kengo font-medium">{row.kengo}</div>
                </motion.div>
              ))}
            </motion.div>
          </div>

          {/* CTA */}
          <div className="text-center mt-10">
            <a href="https://cal.eu/philhie/kengo" target="_blank" rel="noopener noreferrer" className="btn-primary-lg">
              Demo vereinbaren
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </a>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

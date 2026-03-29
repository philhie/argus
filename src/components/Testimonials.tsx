"use client";

import { motion } from "framer-motion";
import { sectionReveal, staggerContainer, staggerItem } from "@/lib/motion";

const testimonials = [
  {
    quote:
      "Wir haben 1.300 IT-Tickets pro Tag. Seit 5 Jahren setzen wir KI ein — 50% werden schon autonom gelöst. Aber der nächste Schritt, vollständig autonome IT, das ist exponentielles Wachstum.",
    name: "VP IT Infrastructure",
    company: "Pharma-Konzern",
    detail: "80.000+ Mitarbeiter · Basel",
    initials: "MB",
  },
  {
    quote:
      "Wir suchen seit 8 Monaten eine Sachbearbeiterin für die Buchhaltung. Wenn ein KI-Mitarbeiter 60% dieser Arbeit übernehmen kann, ist das ein No-Brainer.",
    name: "Geschäftsführer",
    company: "Fertigungsunternehmen",
    detail: "85 Mitarbeiter · Baden-Württemberg",
    initials: "GF",
  },
  {
    quote:
      "Das Problem ist nicht das Tool — es ist die Orchestrierung. Wir haben 5 KI-Tools und keins spricht mit dem anderen. Was fehlt ist jemand, der das Ganze zusammenbringt.",
    name: "Head of IT",
    company: "FinTech",
    detail: "200+ Mitarbeiter · Berlin",
    initials: "AH",
  },
];

export default function Testimonials() {
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
          <p className="text-xs font-semibold uppercase tracking-wider text-kengo mb-4">
            Stimmen aus der Validierung
          </p>
          <h2 className="text-[32px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.15]">
            Was unsere Kunden sagen.
          </h2>
          <p className="text-lg text-text-secondary mt-4 max-w-2xl mx-auto">
            Was Entscheider im Mittelstand über ihre größten Herausforderungen sagen.
          </p>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid md:grid-cols-3 gap-4"
        >
          {testimonials.map((t) => (
            <motion.div
              key={t.initials}
              variants={staggerItem}
              className="card flex flex-col"
            >
              {/* Quote mark */}
              <svg className="w-8 h-8 text-kengo/30 mb-4" viewBox="0 0 24 24" fill="currentColor">
                <path d="M4.583 17.321C3.553 16.227 3 15 3 13.011c0-3.5 2.457-6.637 6.03-8.188l.893 1.378c-3.335 1.804-3.987 4.145-4.247 5.621.537-.278 1.24-.375 1.929-.311 1.804.167 3.226 1.648 3.226 3.489a3.5 3.5 0 01-3.5 3.5c-1.073 0-2.099-.49-2.748-1.179zm10 0C13.553 16.227 13 15 13 13.011c0-3.5 2.457-6.637 6.03-8.188l.893 1.378c-3.335 1.804-3.987 4.145-4.247 5.621.537-.278 1.24-.375 1.929-.311 1.804.167 3.226 1.648 3.226 3.489a3.5 3.5 0 01-3.5 3.5c-1.073 0-2.099-.49-2.748-1.179z" />
              </svg>

              <blockquote className="text-[15px] text-text-secondary leading-relaxed mb-8 flex-1">
                {t.quote}
              </blockquote>

              <div className="flex items-center gap-3 pt-4 border-t border-line">
                <div className="w-9 h-9 rounded-full bg-kengo/10 flex items-center justify-center">
                  <span className="text-xs font-bold text-kengo">{t.initials}</span>
                </div>
                <div>
                  <p className="text-sm font-medium text-text-primary">{t.name}</p>
                  <p className="text-xs text-muted">
                    {t.company} · {t.detail}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

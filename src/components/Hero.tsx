"use client";

import { motion } from "framer-motion";
import { wordReveal, wordItem, sectionReveal } from "@/lib/motion";
import CascadeDemo from "@/components/CascadeDemo";

const trustItems = [
  "Gehostet in Deutschland",
  "DSGVO-konform",
  "5 Tage Einarbeitung",
  "Monatlich kündbar",
  "Basierend auf OpenClaw (319K+ Stars)",
];

export default function Hero() {
  const line1 = ["Dein", "KI-Mitarbeiter."];
  const line2 = ["Für", "jede", "Abteilung."];

  return (
    <section className="relative overflow-hidden min-h-[85vh] flex items-center">
      {/* Background */}
      <div className="absolute inset-0 hero-glow" />
      <div className="absolute inset-0 bg-grid opacity-30" />

      <div className="relative z-10 max-w-page mx-auto px-6 pt-32 pb-20 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* LEFT: Text content */}
          <div className="space-y-6">
            {/* Headline with word-by-word reveal */}
            <motion.h1
              variants={wordReveal}
              initial="hidden"
              animate="visible"
              className="text-[40px] sm:text-[56px] md:text-[72px] font-display font-semibold tracking-[-0.03em] leading-[1.05]"
            >
              <span className="block">
                {line1.map((word, i) => (
                  <motion.span key={i} variants={wordItem} className="inline-block mr-[0.3em]">
                    {word}
                  </motion.span>
                ))}
              </span>
              <span className="block italic">
                {line2.map((word, i) => (
                  <motion.span key={i} variants={wordItem} className="inline-block mr-[0.3em]">
                    {word}
                  </motion.span>
                ))}
              </span>
            </motion.h1>

            {/* Sub-head */}
            <motion.p
              variants={sectionReveal}
              initial="hidden"
              animate="visible"
              custom={0.5}
              className="text-lg md:text-xl text-text-secondary leading-[1.6] max-w-lg"
            >
              Kengo stellt deinem Unternehmen KI-Mitarbeiter ein — einen
              Generalisten, der alles kann, und Spezialisten für Finance, Sales,
              HR, IT und mehr. Einarbeitung in 5 Tagen. Ab €1.999/Monat.
              Gehostet in Deutschland.
            </motion.p>

            {/* CTAs */}
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              animate="visible"
              custom={0.7}
              className="flex flex-col sm:flex-row gap-3"
            >
              <a href="https://cal.eu/philhie/kengo" target="_blank" rel="noopener noreferrer" className="btn-primary-lg">
                Demo vereinbaren
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </a>
              <a href="#solution" className="btn-secondary px-8 py-4">
                Produkte entdecken
              </a>
            </motion.div>
          </div>

          {/* RIGHT: Product Demo Animation */}
          <motion.div
            variants={sectionReveal}
            initial="hidden"
            animate="visible"
            custom={0.9}
            className="relative"
          >
            <CascadeDemo />
          </motion.div>
        </div>

        {/* Trust bar below — full width */}
        <motion.div
          variants={sectionReveal}
          initial="hidden"
          animate="visible"
          custom={1.1}
          className="mt-12 pt-8 border-t border-line"
        >
          <div className="flex flex-wrap items-center justify-center gap-x-6 gap-y-3">
            {trustItems.map((item) => (
              <div key={item} className="flex items-center gap-2 text-sm text-text-secondary">
                <svg className="w-4 h-4 text-kengo flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                {item}
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}

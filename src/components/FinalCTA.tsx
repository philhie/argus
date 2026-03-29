"use client";

import { motion } from "framer-motion";
import { sectionReveal } from "@/lib/motion";

export default function FinalCTA() {
  return (
    <section id="demo" className="section-padding">
      <div className="max-w-page mx-auto px-6">
        <motion.div
          variants={sectionReveal}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          custom={0}
          className="text-center max-w-2xl mx-auto"
        >
          <h2 className="text-[32px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.15] mb-6">
            Dein nächster Mitarbeiter wartet.
          </h2>

          <p className="text-lg text-text-secondary mb-10 leading-relaxed">
            15 Minuten. Keine Verpflichtung. Du siehst deinen KI-Mitarbeiter live.
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
  );
}

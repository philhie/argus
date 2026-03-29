"use client";

import { motion } from "framer-motion";
import { sectionReveal, springStagger, springItem } from "@/lib/motion";
import { specialists } from "@/lib/specialists";

export default function SpecialistGrid() {
  return (
    <section id="specialists" className="section-padding">
      <div className="max-w-page mx-auto px-6">
        <motion.div
          variants={sectionReveal}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          custom={0}
          className="text-center mb-4"
        >
          <h2 className="text-[32px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.15]">
            Ein Spezialist für jede Abteilung.
          </h2>
        </motion.div>

        <motion.p
          variants={sectionReveal}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          custom={0.1}
          className="text-lg text-text-secondary text-center max-w-2xl mx-auto mb-16 leading-relaxed"
        >
          Jeder Spezialist wird nur nach Ergebnissen bezahlt. Keine Ergebnisse,
          keine Kosten. Erste Kompetenz inklusive im KI-Arbeiter.
        </motion.p>

        <motion.div
          variants={springStagger}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4"
        >
          {specialists.map((specialist) => (
            <motion.a
              key={specialist.name}
              variants={springItem}
              href={specialist.href}
              className="card-hover group relative"
            >
              {/* LIVE badge */}
              <div className="absolute top-6 right-6">
                <span className="badge-live">
                  <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-live" />
                  LIVE
                </span>
              </div>

              <span className="text-2xl mb-4 block">{specialist.icon}</span>
              <h3 className="text-lg font-display font-semibold mb-2">
                {specialist.name}
              </h3>
              <p className="text-sm text-text-secondary leading-relaxed mb-4">
                {specialist.description}
              </p>
              <span className="text-sm text-text-secondary group-hover:text-kengo transition-colors flex items-center gap-1">
                Mehr erfahren
                <svg className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </span>
            </motion.a>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

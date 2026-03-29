"use client";

import { motion } from "framer-motion";
import { sectionReveal, staggerContainer, staggerItem } from "@/lib/motion";

const steps = [
  {
    number: "01",
    title: "Demo",
    description:
      "15 Minuten. Kein Verkaufsdruck. Du siehst deinen KI-Mitarbeiter live.",
  },
  {
    number: "02",
    title: "Einarbeitung",
    description:
      "5 Tage. Wir lernen dein Unternehmen kennen. Prozesse, Team, Ziele.",
  },
  {
    number: "03",
    title: "Go Live",
    description:
      "Dein KI-Mitarbeiter arbeitet. 24/7. Das gesamte Team kann ihn nutzen.",
  },
  {
    number: "04",
    title: "Wachstum",
    description:
      "Füge Spezialisten hinzu. Bau deine KI-Abteilung. Wir wachsen mit dir.",
  },
];

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="section-padding">
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
            In 5 Tagen produktiv.{" "}
            <span className="text-text-secondary">Nicht in 5 Monaten.</span>
          </h2>
        </motion.div>

        {/* Horizontal timeline */}
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid md:grid-cols-4 gap-4 relative"
        >
          {/* Connecting line (desktop) */}
          <div className="hidden md:block absolute top-[52px] left-[12.5%] right-[12.5%] h-px bg-line" />

          {steps.map((step, i) => (
            <motion.div
              key={step.number}
              variants={staggerItem}
              className="relative text-center"
            >
              {/* Number circle */}
              <div className="w-[72px] h-[72px] rounded-2xl bg-surface border border-line flex items-center justify-center mx-auto mb-6 relative z-10">
                <span className="font-mono text-sm font-bold text-kengo">
                  {step.number}
                </span>
              </div>

              <h3 className="text-lg font-display font-semibold mb-2">
                {step.title}
              </h3>
              <p className="text-sm text-text-secondary leading-relaxed max-w-[240px] mx-auto">
                {step.description}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

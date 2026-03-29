"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";
import { sectionReveal } from "@/lib/motion";

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

const stepThresholds = [0.2, 0.4, 0.6, 0.8];

function StepCard({
  step,
  index,
  scrollYProgress,
}: {
  step: (typeof steps)[0];
  index: number;
  scrollYProgress: import("framer-motion").MotionValue<number>;
}) {
  const threshold = stepThresholds[index];
  const opacity = useTransform(
    scrollYProgress,
    [threshold - 0.1, threshold],
    [0, 1]
  );
  const y = useTransform(
    scrollYProgress,
    [threshold - 0.1, threshold],
    [30, 0]
  );
  const circleBg = useTransform(
    scrollYProgress,
    [threshold - 0.05, threshold],
    ["rgba(0,122,255,0)", "rgba(0,122,255,1)"]
  );
  const circleTextColor = useTransform(
    scrollYProgress,
    [threshold - 0.05, threshold],
    ["rgba(0,122,255,1)", "rgba(255,255,255,1)"]
  );

  return (
    <motion.div
      style={{ opacity, y }}
      className="relative text-center"
    >
      {/* Number circle */}
      <motion.div
        style={{ backgroundColor: circleBg }}
        className="w-[72px] h-[72px] rounded-2xl border border-line flex items-center justify-center mx-auto mb-6 relative z-10"
      >
        <motion.span
          style={{ color: circleTextColor }}
          className="font-mono text-sm font-bold"
        >
          {step.number}
        </motion.span>
      </motion.div>

      <h3 className="text-lg font-display font-semibold mb-2">
        {step.title}
      </h3>
      <p className="text-sm text-text-secondary leading-relaxed max-w-[240px] mx-auto">
        {step.description}
      </p>
    </motion.div>
  );
}

export default function HowItWorks() {
  const sectionRef = useRef<HTMLElement>(null);
  const { scrollYProgress } = useScroll({
    target: sectionRef,
    offset: ["start end", "end start"],
  });

  const lineScaleX = useTransform(scrollYProgress, [0.15, 0.85], [0, 1]);

  return (
    <section id="how-it-works" className="section-padding" ref={sectionRef}>
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
        <div className="grid md:grid-cols-4 gap-4 relative">
          {/* Connecting line (desktop) - scroll-linked */}
          <div className="hidden md:block absolute top-[52px] left-[12.5%] right-[12.5%] h-px">
            {/* Background track */}
            <div className="absolute inset-0 bg-line" />
            {/* Animated fill */}
            <motion.div
              style={{ scaleX: lineScaleX, transformOrigin: "left" }}
              className="absolute inset-0 bg-kengo"
            />
          </div>

          {/* Connecting line (mobile) - vertical */}
          <div className="md:hidden absolute top-[36px] bottom-[36px] left-[36px] w-px">
            <div className="absolute inset-0 bg-line" />
            <motion.div
              style={{ scaleY: lineScaleX, transformOrigin: "top" }}
              className="absolute inset-0 bg-kengo"
            />
          </div>

          {steps.map((step, i) => (
            <StepCard
              key={step.number}
              step={step}
              index={i}
              scrollYProgress={scrollYProgress}
            />
          ))}
        </div>
      </div>
    </section>
  );
}

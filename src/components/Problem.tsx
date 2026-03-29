"use client";

import { motion, useInView } from "framer-motion";
import { useRef, useEffect, useState } from "react";
import { scaleReveal, sectionReveal } from "@/lib/motion";

const stats = [
  {
    value: 391000,
    display: "391.000",
    label: "unbesetzte Stellen",
    description:
      "Der Arbeitsmarkt liefert keine Mitarbeiter mehr. Die Lücke wächst jedes Jahr.",
  },
  {
    value: 32,
    display: "32h",
    suffix: "/Monat",
    label: "verloren an Admin",
    description:
      "Jedes Unternehmen verliert 32 Stunden monatlich an Routinearbeit, die keiner machen will.",
  },
  {
    value: 61,
    display: "€61 Mrd.",
    label: "verschwendet pro Jahr",
    description:
      "Der deutsche Mittelstand erstickt an Bürokratie. E-Mails, Rechnungen, Termine, Berichte.",
  },
];

function AnimatedStat({ stat }: { stat: (typeof stats)[0] }) {
  const ref = useRef<HTMLDivElement>(null);
  const isInView = useInView(ref, { once: true });
  const [displayValue, setDisplayValue] = useState("0");

  useEffect(() => {
    if (!isInView) return;

    const duration = 1200;
    const steps = 60;
    const stepDuration = duration / steps;
    let current = 0;

    const timer = setInterval(() => {
      current++;
      const progress = current / steps;
      const eased = 1 - Math.pow(1 - progress, 3); // easeOut

      if (stat.value >= 1000) {
        const val = Math.round(eased * stat.value);
        setDisplayValue(val.toLocaleString("de-DE"));
      } else {
        setDisplayValue(Math.round(eased * stat.value).toString());
      }

      if (current >= steps) {
        clearInterval(timer);
        setDisplayValue(stat.display.replace(/[€h ]/g, "").replace("Mrd.", ""));
      }
    }, stepDuration);

    return () => clearInterval(timer);
  }, [isInView, stat]);

  return (
    <div ref={ref} className="card text-center">
      <div className="text-[36px] md:text-[56px] font-mono font-bold text-kengo tracking-[-0.03em] mb-2">
        {stat.display.startsWith("€") && "€"}
        {displayValue}
        {stat.display.includes("h") && "h"}
        {stat.display.includes("Mrd.") && " Mrd."}
      </div>
      <p className="text-base font-display font-semibold text-text-primary mb-2">
        {stat.label}
      </p>
      <p className="text-sm text-text-secondary leading-relaxed">
        {stat.description}
      </p>
    </div>
  );
}

export default function Problem() {
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
          <h2 className="text-[32px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.15] mb-4">
            Dein bestes Team verbringt seine Zeit mit Verwaltung.
            <br />
            <span className="text-text-secondary">Und es gibt niemanden, der übernimmt.</span>
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-3 gap-4">
          {stats.map((stat) => (
            <motion.div
              key={stat.label}
              variants={scaleReveal}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
            >
              <AnimatedStat stat={stat} />
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
}

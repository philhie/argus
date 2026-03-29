"use client";

import { useRef } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { wordReveal, heroWordItem, sectionReveal } from "@/lib/motion";
import CascadeDemo from "@/components/CascadeDemo";
import FloatingOrbs from "@/components/FloatingOrbs";
import AnimatedGradientBorder from "@/components/AnimatedGradientBorder";
import Tilt3D from "@/components/Tilt3D";
import LiveCounter from "@/components/LiveCounter";

const trustItems = [
  "Gehostet in Deutschland",
  "DSGVO-konform",
  "5 Tage Einarbeitung",
  "Monatlich kündbar",
];

const socialLogos = [
  { name: "McDonald's", style: "font-bold text-lg tracking-tight" },
  { name: "Spotify", style: "font-medium text-lg tracking-tight" },
  { name: "The Economist", style: "font-serif text-base tracking-tight italic" },
];

export default function Hero() {
  const heroRef = useRef<HTMLDivElement>(null);
  const line1 = ["Dein", "KI-Mitarbeiter."];
  const line2 = ["Für", "jede", "Abteilung."];

  const { scrollYProgress } = useScroll({
    target: heroRef,
    offset: ["start start", "end start"],
  });

  const demoScale = useTransform(scrollYProgress, [0.5, 1], [1, 0.92]);
  const demoOpacity = useTransform(scrollYProgress, [0.6, 1], [1, 0]);
  const bgOpacity = useTransform(scrollYProgress, [0.5, 1], [1, 0]);

  return (
    <section
      ref={heroRef}
      className="relative overflow-hidden min-h-screen flex flex-col items-center justify-center"
      onMouseMove={(e) => {
        const glow = document.getElementById("mouse-glow");
        if (glow) {
          glow.style.transform = `translate3d(${e.clientX - 300}px, ${e.clientY - 300}px, 0)`;
        }
      }}
    >
      {/* Background layers */}
      <motion.div className="absolute inset-0" style={{ opacity: bgOpacity }}>
        <div className="gradient-mesh" />
        <div className="absolute inset-0 bg-grid-enhanced" />
        <FloatingOrbs />
      </motion.div>

      {/* Mouse-tracking glow */}
      <div
        id="mouse-glow"
        className="absolute pointer-events-none hidden lg:block"
        style={{
          width: 600,
          height: 600,
          background: "radial-gradient(circle, rgba(59,130,246,0.06), transparent 70%)",
          borderRadius: "50%",
          transition: "transform 0.15s ease-out",
        }}
      />

      {/* Content */}
      <div className="relative z-10 max-w-page mx-auto px-6 pt-28 pb-12 w-full">
        {/* Centered headline + subhead */}
        <div className="text-center max-w-4xl mx-auto mb-8">
          <motion.h1
            variants={wordReveal}
            initial="hidden"
            animate="visible"
            className="text-[40px] sm:text-[56px] md:text-[72px] font-display font-semibold tracking-[-0.03em] leading-[1.05] mb-6"
            style={{ perspective: 800 }}
          >
            <span className="block">
              {line1.map((word, i) => (
                <motion.span key={i} variants={heroWordItem} className="inline-block mr-[0.3em]">
                  {word}
                </motion.span>
              ))}
            </span>
            <span className="block italic">
              {line2.map((word, i) => (
                <motion.span key={i} variants={heroWordItem} className="inline-block mr-[0.3em]">
                  {word}
                </motion.span>
              ))}
            </span>
          </motion.h1>

          <motion.p
            variants={sectionReveal}
            initial="hidden"
            animate="visible"
            custom={0.4}
            className="text-lg md:text-xl text-text-secondary leading-[1.6] max-w-2xl mx-auto mb-8"
          >
            Kengo stellt deinem Unternehmen KI-Mitarbeiter ein — einen
            Generalisten, der alles kann, und Spezialisten für Finance, Sales,
            HR, IT und mehr. Einarbeitung in 5 Tagen. Ab €1.999/Monat.
          </motion.p>

          {/* CTAs */}
          <motion.div
            variants={sectionReveal}
            initial="hidden"
            animate="visible"
            custom={0.6}
            className="flex flex-col sm:flex-row gap-3 justify-center mb-10"
          >
            <a href="https://cal.eu/philhie/kengo" target="_blank" rel="noopener noreferrer" className="btn-primary-lg cta-glow">
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

        {/* CascadeDemo — centerpiece in glassmorphic container */}
        <motion.div
          style={{ scale: demoScale, opacity: demoOpacity }}
          className="relative max-w-3xl mx-auto"
        >
          <motion.div
            variants={sectionReveal}
            initial="hidden"
            animate="visible"
            custom={0.8}
          >
            <Tilt3D className="relative">
              {/* Animated gradient halo */}
              <AnimatedGradientBorder />

              {/* Glass container */}
              <div className="relative glass-panel p-1">
                <CascadeDemo />
              </div>
            </Tilt3D>
          </motion.div>
        </motion.div>

        {/* Trust bar + social proof + live counter */}
        <motion.div
          variants={sectionReveal}
          initial="hidden"
          animate="visible"
          custom={1.2}
          className="mt-12 space-y-6"
        >
          {/* Trust checkmarks */}
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

          {/* Social proof logos */}
          <div className="flex items-center justify-center gap-8">
            <span className="text-xs uppercase tracking-wider text-muted">Vertraut von</span>
            {socialLogos.map((logo) => (
              <span
                key={logo.name}
                className={`${logo.style} text-text-primary opacity-30 hover:opacity-60 transition-opacity duration-300 cursor-default select-none`}
              >
                {logo.name}
              </span>
            ))}
          </div>

          {/* Live counter */}
          <LiveCounter />
        </motion.div>
      </div>
    </section>
  );
}

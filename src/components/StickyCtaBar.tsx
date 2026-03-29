"use client";

import { useState } from "react";
import { motion, useScroll, useMotionValueEvent } from "framer-motion";

export default function StickyCtaBar() {
  const [visible, setVisible] = useState(false);
  const { scrollY } = useScroll();

  useMotionValueEvent(scrollY, "change", (latest) => {
    if (typeof window !== "undefined") {
      setVisible(latest > window.innerHeight * 0.8);
    }
  });

  return (
    <motion.div
      initial={{ y: 100 }}
      animate={{ y: visible ? 0 : 100 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className="fixed bottom-0 left-0 right-0 z-40 bg-void/80 backdrop-blur-xl border-t border-line"
    >
      <div className="max-w-page mx-auto px-6 h-14 flex items-center justify-between">
        <p className="text-sm text-text-secondary hidden sm:block">
          Dein nächster KI-Mitarbeiter wartet.
        </p>
        <a
          href="https://cal.eu/philhie/kengo"
          target="_blank"
          rel="noopener noreferrer"
          className="btn-primary text-sm sm:ml-auto"
        >
          Demo vereinbaren
          <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </a>
      </div>
    </motion.div>
  );
}

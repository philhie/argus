"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";

function getBaseCount(): number {
  const now = new Date();
  const hours = now.getHours() + now.getMinutes() / 60;
  return Math.floor(hours * 537 + 4200);
}

export default function LiveCounter() {
  const [count, setCount] = useState(getBaseCount);
  const [key, setKey] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      const increment = Math.floor(Math.random() * 3) + 1;
      setCount((c) => c + increment);
      setKey((k) => k + 1);
    }, 2500 + Math.random() * 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex items-center justify-center gap-6 text-sm">
      <div className="flex items-center gap-2">
        <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-live" />
        <span className="text-text-secondary">
          <AnimatePresence mode="popLayout">
            <motion.span
              key={key}
              initial={{ opacity: 0.5, y: -4 }}
              animate={{ opacity: 1, y: 0 }}
              className="inline-block font-mono font-bold text-kengo"
            >
              {count.toLocaleString("de-DE")}
            </motion.span>
          </AnimatePresence>
          {" "}Aufgaben heute erledigt
        </span>
      </div>
    </div>
  );
}

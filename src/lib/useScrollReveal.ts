"use client";

import { useRef } from "react";
import { useScroll, useTransform } from "framer-motion";

interface ScrollRevealOptions {
  offset?: ["start end" | "start center" | "end start" | "end end", "start end" | "start center" | "end start" | "end end"];
}

export function useScrollReveal(options?: ScrollRevealOptions) {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: options?.offset || ["start end", "start center"],
  });

  const opacity = useTransform(scrollYProgress, [0, 1], [0, 1]);
  const y = useTransform(scrollYProgress, [0, 1], [40, 0]);
  const scale = useTransform(scrollYProgress, [0, 1], [0.95, 1]);

  return { ref, opacity, y, scale, scrollYProgress };
}

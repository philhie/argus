"use client";

import { useEffect, type RefObject } from "react";
import { useMotionValue, useSpring } from "framer-motion";

export function useMousePosition(ref: RefObject<HTMLElement | null>) {
  const rawX = useMotionValue(0.5);
  const rawY = useMotionValue(0.5);

  const x = useSpring(rawX, { stiffness: 50, damping: 30 });
  const y = useSpring(rawY, { stiffness: 50, damping: 30 });

  useEffect(() => {
    const el = ref.current;
    if (!el) return;

    const handler = (e: MouseEvent) => {
      const rect = el.getBoundingClientRect();
      rawX.set((e.clientX - rect.left) / rect.width);
      rawY.set((e.clientY - rect.top) / rect.height);
    };

    el.addEventListener("mousemove", handler);
    return () => el.removeEventListener("mousemove", handler);
  }, [ref, rawX, rawY]);

  return { x, y };
}

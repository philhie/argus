"use client";

import { useRef } from "react";
import { motion, useSpring, useMotionValue, useTransform } from "framer-motion";

interface Tilt3DProps {
  children: React.ReactNode;
  className?: string;
  maxTilt?: number;
}

export default function Tilt3D({ children, className = "", maxTilt = 3 }: Tilt3DProps) {
  const ref = useRef<HTMLDivElement>(null);
  const rawX = useMotionValue(0.5);
  const rawY = useMotionValue(0.5);

  const springX = useSpring(rawX, { stiffness: 150, damping: 15 });
  const springY = useSpring(rawY, { stiffness: 150, damping: 15 });

  const rotateY = useTransform(springX, [0, 1], [-maxTilt, maxTilt]);
  const rotateX = useTransform(springY, [0, 1], [maxTilt, -maxTilt]);

  const handleMouseMove = (e: React.MouseEvent) => {
    const el = ref.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    rawX.set((e.clientX - rect.left) / rect.width);
    rawY.set((e.clientY - rect.top) / rect.height);
  };

  const handleMouseLeave = () => {
    rawX.set(0.5);
    rawY.set(0.5);
  };

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        perspective: 1000,
        rotateX,
        rotateY,
        transformStyle: "preserve-3d",
      }}
      className={className}
    >
      {children}
    </motion.div>
  );
}

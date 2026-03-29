"use client";

import { useRef } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";

export default function MouseGlow() {
  const containerRef = useRef<HTMLDivElement>(null);
  const rawX = useMotionValue(0);
  const rawY = useMotionValue(0);
  const x = useSpring(rawX, { stiffness: 50, damping: 30 });
  const y = useSpring(rawY, { stiffness: 50, damping: 30 });

  const handleMouseMove = (e: React.MouseEvent) => {
    rawX.set(e.clientX);
    rawY.set(e.clientY);
  };

  return (
    <div
      ref={containerRef}
      onMouseMove={handleMouseMove}
      className="absolute inset-0 overflow-hidden pointer-events-none"
      style={{ pointerEvents: "none" }}
    >
      <motion.div
        className="absolute pointer-events-none"
        style={{
          x,
          y,
          width: 600,
          height: 600,
          marginLeft: -300,
          marginTop: -300,
          background: "radial-gradient(circle, rgba(59,130,246,0.06), transparent 70%)",
          borderRadius: "50%",
        }}
      />
    </div>
  );
}

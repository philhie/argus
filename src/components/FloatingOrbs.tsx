"use client";

import { motion } from "framer-motion";

const orbs = [
  { size: 200, x: "15%", y: "20%", duration: 10, delay: 0 },
  { size: 160, x: "75%", y: "30%", duration: 12, delay: 2 },
  { size: 120, x: "50%", y: "70%", duration: 8, delay: 4 },
];

export default function FloatingOrbs() {
  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {orbs.map((orb, i) => (
        <motion.div
          key={i}
          className="absolute rounded-full"
          style={{
            width: orb.size,
            height: orb.size,
            left: orb.x,
            top: orb.y,
            background: "radial-gradient(circle, rgba(59,130,246,0.06), transparent 70%)",
            filter: "blur(40px)",
          }}
          animate={{
            y: [0, -20, 0],
            x: [0, 10, 0],
          }}
          transition={{
            duration: orb.duration,
            delay: orb.delay,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        />
      ))}
    </div>
  );
}

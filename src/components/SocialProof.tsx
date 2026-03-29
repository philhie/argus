"use client";

import { motion } from "framer-motion";
import { sectionReveal } from "@/lib/motion";

const customerLogos = [
  {
    name: "McDonald's",
    style: "font-bold text-2xl tracking-tight",
  },
  {
    name: "Spotify",
    style: "font-medium text-2xl tracking-tight",
  },
  {
    name: "The Economist",
    style: "font-serif text-xl tracking-tight italic",
  },
];

export default function SocialProof() {
  return (
    <section className="section-padding-sm border-t border-line">
      <div className="max-w-page mx-auto">
        <motion.div
          variants={sectionReveal}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          custom={0}
          className="text-center"
        >
          {/* Customer logos */}
          <p className="text-xs font-semibold uppercase tracking-wider text-muted mb-8">
            Vertraut von führenden Unternehmen weltweit
          </p>

          <div className="flex flex-wrap items-center justify-center gap-12 md:gap-16 mb-12">
            {customerLogos.map((logo) => (
              <span
                key={logo.name}
                className={`${logo.style} text-text-primary opacity-40 grayscale hover:opacity-100 hover:grayscale-0 transition-all duration-300 cursor-default select-none`}
              >
                {logo.name}
              </span>
            ))}
          </div>

        </motion.div>
      </div>
    </section>
  );
}


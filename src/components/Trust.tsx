"use client";

import { motion } from "framer-motion";
import { sectionReveal, staggerContainer, staggerItem } from "@/lib/motion";

const trustBlocks = [
  {
    title: "Hetzner Deutschland",
    description: "Alle Daten auf deutschen Servern. Kein Transfer in Drittländer. Volle Datensouveränität.",
    icon: (
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3 21V7l9-4 9 4v14M3 21h18M9 10h1M14 10h1M9 14h1M14 14h1M9 18h6" />
      </svg>
    ),
  },
  {
    title: "DSGVO-konform",
    description: "Vollständige Konformität mit der Datenschutz-Grundverordnung. Privacy by Design.",
    icon: (
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 10-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 002.25-2.25v-6.75a2.25 2.25 0 00-2.25-2.25H6.75a2.25 2.25 0 00-2.25 2.25v6.75a2.25 2.25 0 002.25 2.25z" />
      </svg>
    ),
  },
  {
    title: "NemoClaw Security",
    description: "Enterprise-grade Security Layer. End-to-End-Verschlüsselung. Regelmäßige Penetrationstests.",
    icon: (
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
      </svg>
    ),
  },
  {
    title: "Rollenbasierte Rechte",
    description: "Granulare Zugriffssteuerung. Jeder Mitarbeiter sieht nur, was er sehen soll.",
    icon: (
      <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15 19.128a9.38 9.38 0 002.625.372 9.337 9.337 0 004.121-.952 4.125 4.125 0 00-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 018.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0111.964-3.07M12 6.375a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zm8.25 2.25a2.625 2.625 0 11-5.25 0 2.625 2.625 0 015.25 0z" />
      </svg>
    ),
  },
];

export default function Trust() {
  return (
    <section id="ueber-uns" className="section-padding">
      <div className="max-w-page mx-auto px-6">
        <motion.div
          variants={sectionReveal}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          custom={0}
          className="text-center mb-16"
        >
          <h2 className="text-[32px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.15]">
            Deine Daten. In Deutschland.
            <br />
            <span className="text-text-secondary">Unter deutschem Recht.</span>
          </h2>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4"
        >
          {trustBlocks.map((block) => (
            <motion.div
              key={block.title}
              variants={staggerItem}
              className="card text-center"
            >
              <div className="w-12 h-12 rounded-xl bg-kengo/10 flex items-center justify-center text-kengo mx-auto mb-5">
                {block.icon}
              </div>
              <h3 className="text-base font-display font-semibold mb-2">
                {block.title}
              </h3>
              <p className="text-sm text-text-secondary leading-relaxed">
                {block.description}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

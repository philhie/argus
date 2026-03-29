"use client";

import { motion } from "framer-motion";
import { sectionReveal, staggerContainer, staggerItem } from "@/lib/motion";

const products = [
  {
    title: "KI-Arbeiter",
    subtitle: "Der Generalist",
    description:
      "Dein persönlicher AI Associate. Erledigt alles, was ein exzellenter Chief of Staff tun würde.",
    price: "ab €1.999/mo",
    href: "/produkte/arbeiter",
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0" />
      </svg>
    ),
  },
  {
    title: "KI-Fachkräfte",
    subtitle: "Die Spezialisten",
    description:
      "Finance. Sales. HR. Marketing. IT. Support. Procurement. Compliance. Cybersecurity.",
    price: "ab €0,75/Ergebnis",
    href: "#specialists",
    highlighted: true,
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 13.5l10.5-11.25L12 10.5h8.25L9.75 21.75 12 13.5H3.75z" />
      </svg>
    ),
  },
  {
    title: "KI-Abteilung",
    subtitle: "Das ganze Team",
    description:
      "Dein AI Department. Ein Abteilungsleiter koordiniert alle Agenten, berichtet dir, und optimiert alles.",
    price: "Individuell",
    href: "/produkte/abteilung",
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
        <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197" />
      </svg>
    ),
  },
];

export default function SolutionIntro() {
  return (
    <section id="solution" className="section-padding">
      <div className="max-w-page mx-auto px-6">
        <motion.div
          variants={sectionReveal}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          custom={0}
          className="text-center mb-6"
        >
          <h2 className="text-[32px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.15]">
            Ein Mitarbeiter. Ein Spezialist. Eine Abteilung.
            <br />
            <span className="text-kengo">Kengo stellt sie alle ein.</span>
          </h2>
        </motion.div>

        <motion.p
          variants={sectionReveal}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          custom={0.1}
          className="text-lg text-text-secondary text-center max-w-3xl mx-auto mb-16 leading-relaxed"
        >
          Starte mit einem Generalisten, der dein Unternehmen versteht und alles
          erledigt — E-Mails, Termine, Dokumente, Automatisierungen. Füge
          Spezialisten hinzu für Finance, Sales, HR, IT und mehr. Und wenn dein
          KI-Team wächst, koordiniert deine KI-Abteilung alles automatisch.
        </motion.p>

        {/* Product Triptych */}
        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid md:grid-cols-3 gap-4"
        >
          {products.map((product) => (
            <motion.a
              key={product.title}
              variants={staggerItem}
              href={product.href}
              className={`card-hover group flex flex-col ${
                product.highlighted
                  ? "border-kengo/50 relative"
                  : ""
              }`}
            >
              {product.highlighted && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="bg-kengo text-white text-[11px] font-semibold uppercase tracking-wider px-3 py-1 rounded-full">
                    Beliebteste Wahl
                  </span>
                </div>
              )}

              <div className="w-12 h-12 rounded-xl bg-kengo/10 flex items-center justify-center text-kengo mb-5">
                {product.icon}
              </div>

              <p className="text-xs font-semibold uppercase tracking-wider text-kengo mb-1">
                {product.subtitle}
              </p>
              <h3 className="text-xl font-display font-semibold mb-3">
                {product.title}
              </h3>
              <p className="text-[15px] text-text-secondary leading-relaxed mb-6 flex-1">
                {product.description}
              </p>

              <div className="flex items-center justify-between">
                <span className="text-sm font-mono font-bold text-kengo">
                  {product.price}
                </span>
                <span className="text-sm text-text-secondary group-hover:text-kengo transition-colors flex items-center gap-1">
                  Mehr erfahren
                  <svg className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
              </div>
            </motion.a>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

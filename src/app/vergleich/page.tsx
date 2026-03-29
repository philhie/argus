"use client";

import { motion } from "framer-motion";
import { sectionReveal, staggerContainer, staggerItem } from "@/lib/motion";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";

/* ─── Data ──────────────────────────────────────────────── */

const competitors = ["Kengo", "ChatGPT Enterprise", "Microsoft Copilot", "Langdock", "Sachbearbeiter"];

const rows: { label: string; values: string[] }[] = [
  {
    label: "Preis/Monat",
    values: [
      "ab €1.999 (flat)",
      "~€1.260/10 User ($25/User)",
      "~€1.500/10 User ($30/User)",
      "ab €790/10 User",
      "€4.750–5.333 (Vollkosten)",
    ],
  },
  {
    label: "Was ist inklusive",
    values: [
      "Kompletter KI-Mitarbeiter + Einrichtung + Support",
      "Chat-Zugang pro User",
      "Chat + Office-Integration pro User",
      "Chat + Wissensmanagement pro User",
      "Ein Mensch, 40h/Woche",
    ],
  },
  {
    label: "Setup-Zeit",
    values: [
      "5 Tage (wir machen alles)",
      "Self-Service",
      "IT-Rollout nötig",
      "Self-Service",
      "70+ Tage Recruiting",
    ],
  },
  {
    label: "Deutsch",
    values: ["✅ Muttersprachlich", "⚠️ Übersetzt", "⚠️ Übersetzt", "✅ Gutes Deutsch", "✅ Muttersprachlich"],
  },
  {
    label: "DATEV-Integration",
    values: ["✅ Nativ", "❌", "❌", "❌", "✅ Manuell"],
  },
  {
    label: "Hosting",
    values: [
      "🇩🇪 Deutschland (Hetzner)",
      "🇺🇸 USA (Microsoft Azure)",
      "🇺🇸 USA (Microsoft Azure)",
      "🇪🇺 EU (Azure)",
      "—",
    ],
  },
  {
    label: "DSGVO",
    values: ["✅ Vollständig", "⚠️ DPA nötig", "⚠️ DPA nötig", "✅ Konform", "✅"],
  },
  {
    label: "Open Source",
    values: [
      "✅ Auditierbar (OpenClaw)",
      "❌ Closed Source",
      "❌ Closed Source",
      "❌ Closed Source",
      "—",
    ],
  },
  {
    label: "Arbeitet autonom",
    values: [
      "✅ 24/7, proaktiv",
      "❌ Nur auf Anfrage",
      "❌ Nur auf Anfrage",
      "❌ Nur auf Anfrage",
      "⚠️ 40h/Woche",
    ],
  },
  {
    label: "Concierge-Onboarding",
    values: ["✅ Inklusive", "❌", "❌", "⚠️ Gegen Aufpreis", "—"],
  },
  {
    label: "Monatlich kündbar",
    values: [
      "✅",
      "✅ (Jahresvertrag günstiger)",
      "⚠️ Jahresvertrag",
      "⚠️ Jahresvertrag",
      "❌ 1-6 Monate Frist",
    ],
  },
  {
    label: "Skaliert sofort",
    values: ["✅ Stunden", "❌ Pro Seat", "❌ Pro Seat", "❌ Pro Seat", "❌ Monate"],
  },
  {
    label: "Betriebsrat-kompatibel",
    values: ["✅ Audit-Trail", "⚠️ Unklar", "⚠️ Unklar", "✅", "✅"],
  },
];

const differentiators = [
  {
    headline: "Wir arbeiten. Die anderen chatten.",
    body: "ChatGPT, Copilot und Langdock sind Werkzeuge — du musst sie bedienen. Kengo ist ein Mitarbeiter — er arbeitet selbstständig. 24/7. Ohne dass du einen Prompt schreiben musst.",
  },
  {
    headline:
      "Preis-Garantie: Für immer günstiger als die Summe der Teile.",
    body: "Ein ChatGPT Enterprise + Copilot + Langdock Setup kostet dich €3.550+/Monat für 10 User. Kengo kostet ab €1.999 — und macht mehr als alle drei zusammen.",
  },
  {
    headline: "Dein Unternehmen. Dein Land. Deine Daten.",
    body: "Während ChatGPT und Copilot deine Daten in US-Rechenzentren verarbeiten, läuft Kengo auf Hetzner in Deutschland. Open-Source. Auditierbar. DSGVO-konform.",
  },
];

/* ─── Page ──────────────────────────────────────────────── */

export default function VergleichPage() {
  return (
    <>
      <Navigation />
      <main>
        {/* Section 1: Hero */}
        <section className="relative pt-32 pb-20 overflow-hidden">
          <div className="absolute inset-0 hero-glow" />
          <div className="absolute inset-0 bg-grid opacity-30" />
          <div className="relative z-10 max-w-page mx-auto px-6 text-center">
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              animate="visible"
              custom={0}
            >
              <p className="text-sm font-semibold uppercase tracking-wider text-kengo mb-4">
                Vergleich
              </p>
              <h1 className="text-[36px] sm:text-[48px] md:text-[64px] font-display font-semibold tracking-[-0.03em] leading-[1.05] mb-6">
                Kengo vs. Alles andere.
              </h1>
              <p className="text-lg md:text-xl text-text-secondary max-w-2xl mx-auto leading-relaxed">
                Ein ehrlicher Vergleich. Keine Marketing-Tricks. Nur Fakten.
              </p>
            </motion.div>
          </div>
        </section>

        {/* Section 2: Comparison Table */}
        <section className="section-padding">
          <div className="max-w-page mx-auto px-6">
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              custom={0}
            >
              {/* Desktop Table */}
              <div className="hidden lg:block overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr>
                      <th className="text-left text-sm font-semibold text-text-secondary py-4 px-4 w-[160px]">
                        Kriterium
                      </th>
                      {competitors.map((c, i) => (
                        <th
                          key={c}
                          className={`text-left text-sm font-semibold py-4 px-4 ${
                            i === 0
                              ? "bg-kengo/5 border-t-2 border-kengo text-kengo rounded-t-lg"
                              : "text-text-secondary"
                          }`}
                        >
                          <div className="flex items-center gap-2">
                            {c}
                            {i === 0 && (
                              <span className="text-[10px] bg-kengo text-white px-2 py-0.5 rounded-full font-semibold uppercase tracking-wider">
                                Empfohlen
                              </span>
                            )}
                          </div>
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row, rowIdx) => (
                      <tr
                        key={row.label}
                        className={rowIdx % 2 === 0 ? "bg-surface/50" : ""}
                      >
                        <td className="text-sm font-medium text-text-primary py-4 px-4">
                          {row.label}
                        </td>
                        {row.values.map((val, colIdx) => (
                          <td
                            key={colIdx}
                            className={`text-sm py-4 px-4 ${
                              colIdx === 0
                                ? "bg-kengo/5 font-medium text-text-primary"
                                : "text-text-secondary"
                            }`}
                          >
                            <StatusText text={val} />
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Mobile Cards */}
              <div className="lg:hidden space-y-6">
                {competitors.map((competitor, compIdx) => (
                  <div
                    key={competitor}
                    className={`rounded-2xl p-6 ${
                      compIdx === 0
                        ? "bg-kengo/5 border-2 border-kengo"
                        : "bg-surface border border-line"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-4">
                      <h3 className={`text-lg font-display font-semibold ${compIdx === 0 ? "text-kengo" : ""}`}>
                        {competitor}
                      </h3>
                      {compIdx === 0 && (
                        <span className="text-[10px] bg-kengo text-white px-2 py-0.5 rounded-full font-semibold uppercase tracking-wider">
                          Empfohlen
                        </span>
                      )}
                    </div>
                    <div className="space-y-3">
                      {rows.map((row) => (
                        <div key={row.label} className="flex justify-between items-start gap-4">
                          <span className="text-xs text-muted flex-shrink-0">
                            {row.label}
                          </span>
                          <span className="text-sm text-right">
                            <StatusText text={row.values[compIdx]} />
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </section>

        {/* Section 3: Key Differentiators */}
        <section className="section-padding border-t border-line">
          <div className="max-w-page mx-auto px-6">
            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="space-y-4"
            >
              {differentiators.map((d) => (
                <motion.div
                  key={d.headline}
                  variants={staggerItem}
                  className="bg-surface rounded-2xl p-10"
                >
                  <h3 className="text-2xl font-display font-semibold mb-4">
                    {d.headline}
                  </h3>
                  <p className="text-lg text-text-secondary leading-relaxed">
                    {d.body}
                  </p>
                </motion.div>
              ))}
            </motion.div>
          </div>
        </section>

        {/* Section 4: Final CTA */}
        <section className="section-padding">
          <div className="max-w-page mx-auto px-6 text-center">
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-100px" }}
              custom={0}
              className="max-w-2xl mx-auto"
            >
              <h2 className="text-[32px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.15] mb-6">
                Überzeuge dich selbst.
              </h2>
              <p className="text-lg text-text-secondary mb-10">
                30 Minuten Demo-Call. Keine Verpflichtung. Keine Verkaufstricks.
              </p>
              <a href="https://cal.eu/philhie/kengo" target="_blank" rel="noopener noreferrer" className="btn-primary-lg text-lg">
                Demo vereinbaren
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </a>
            </motion.div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}

/* ─── Helpers ───────────────────────────────────────────── */

function StatusText({ text }: { text: string }) {
  if (text.startsWith("✅")) {
    return <span className="text-emerald-400">{text}</span>;
  }
  if (text.startsWith("❌")) {
    return <span className="text-red-400">{text}</span>;
  }
  if (text.startsWith("⚠️")) {
    return <span className="text-amber-400">{text}</span>;
  }
  return <span>{text}</span>;
}

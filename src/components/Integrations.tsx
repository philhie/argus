"use client";

import { motion } from "framer-motion";
import { sectionReveal, staggerContainer, staggerItem } from "@/lib/motion";

const integrations = [
  // Row 1 — Communication
  { icon: "📧", name: "E-Mail (IMAP/SMTP)", category: "Kommunikation" },
  { icon: "💬", name: "Slack", category: "Kommunikation" },
  { icon: "👥", name: "Microsoft Teams", category: "Kommunikation" },
  { icon: "📱", name: "WhatsApp", category: "Kommunikation" },
  // Row 2 — Productivity
  { icon: "📅", name: "Google Workspace", category: "Produktivität" },
  { icon: "📊", name: "Microsoft 365", category: "Produktivität" },
  { icon: "📝", name: "Notion", category: "Produktivität" },
  { icon: "🔄", name: "n8n / Make", category: "Automatisierung" },
  // Row 3 — Finance & HR
  { icon: "🏦", name: "DATEV", category: "Buchhaltung" },
  { icon: "📋", name: "sevDesk", category: "Buchhaltung" },
  { icon: "💰", name: "lexoffice", category: "Buchhaltung" },
  { icon: "👤", name: "Personio", category: "HR" },
  // Row 4 — CRM & More
  { icon: "🎯", name: "HubSpot", category: "CRM" },
  { icon: "📈", name: "Salesforce", category: "CRM" },
  { icon: "🎫", name: "Zendesk", category: "Support" },
  { icon: "➕", name: "Und 20+ weitere", category: "Mehr", isMore: true },
];

export default function Integrations() {
  return (
    <section className="section-padding">
      <div className="max-w-page mx-auto px-6">
        <motion.div
          variants={sectionReveal}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          custom={0}
          className="text-center mb-16"
        >
          <p className="text-sm uppercase tracking-wider text-kengo font-medium mb-4">
            Integrationen
          </p>
          <h2 className="text-[32px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.15] mb-4">
            Funktioniert mit deinen bestehenden Tools.
          </h2>
          <p className="text-lg text-text-secondary max-w-2xl mx-auto">
            Kengo verbindet sich mit den Systemen, die du bereits nutzt. Keine Migration. Kein Umstieg. Einfach dazu.
          </p>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4"
        >
          {integrations.map((item) => (
            <motion.div
              key={item.name}
              variants={staggerItem}
              className={`flex flex-col items-center justify-center py-6 px-4 rounded-xl transition-all ${
                item.isMore
                  ? "border border-dashed border-line/50 bg-surface/30 hover:border-kengo/30 hover:bg-surface/50"
                  : "bg-surface/50 border border-line/50 hover:border-kengo/30 hover:bg-surface"
              }`}
            >
              <span className="text-2xl mb-2">{item.icon}</span>
              <span className="font-medium text-sm text-center">{item.name}</span>
              <span className="text-xs text-text-secondary mt-1">{item.category}</span>
            </motion.div>
          ))}
        </motion.div>

        <motion.p
          variants={sectionReveal}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          custom={0.2}
          className="text-sm text-text-secondary text-center mt-8"
        >
          Fehlt eine Integration? Sag uns Bescheid — wir bauen sie in 48 Stunden.
        </motion.p>
      </div>
    </section>
  );
}

export interface Specialist {
  icon: string;
  name: string;
  description: string;
  href: string;
}

export const specialists: Specialist[] = [
  {
    icon: "💰",
    name: "Finance",
    description: "Rechnungen. DATEV. Mahnwesen. Cash Flow.",
    href: "/produkte/finance",
  },
  {
    icon: "🎯",
    name: "Customer Support",
    description: "Tickets. Anfragen. Eskalation. FAQ.",
    href: "/produkte/support",
  },
  {
    icon: "👥",
    name: "HR",
    description: "Bewerbungen. Interviews. Onboarding.",
    href: "/produkte/hr",
  },
  {
    icon: "📈",
    name: "Sales",
    description: "Leads. Pipeline. CRM. Angebote.",
    href: "/produkte/sales",
  },
  {
    icon: "📣",
    name: "Marketing",
    description: "Kampagnen. Content. Analytics.",
    href: "/produkte/marketing",
  },
  {
    icon: "🖥️",
    name: "IT Ops",
    description: "Tickets. Resets. Monitoring.",
    href: "/produkte/it-ops",
  },
  {
    icon: "📦",
    name: "Procurement",
    description: "Lieferanten. Bestellungen. Vergleiche.",
    href: "/produkte/procurement",
  },
  {
    icon: "⚖️",
    name: "Compliance",
    description: "Regulierung. Audits. DORA. NIS2.",
    href: "/produkte/compliance",
  },
  {
    icon: "🛡️",
    name: "Cybersecurity",
    description: "Threat Detection. NIS2. DORA.",
    href: "/produkte/cybersecurity",
  },
];

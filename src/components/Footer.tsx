"use client";

const footerLinks = {
  Produkte: [
    { label: "KI-Arbeiter", href: "/produkte/arbeiter" },
    { label: "KI-Fachkräfte", href: "#specialists" },
    { label: "KI-Abteilung", href: "/produkte/abteilung" },
    { label: "Preise", href: "/preise" },
    { label: "Vergleich", href: "/vergleich" },
  ],
  "Use Cases": [
    { label: "Finance & Buchhaltung", href: "/produkte/finance" },
    { label: "Customer Support", href: "/produkte/support" },
    { label: "HR & Recruiting", href: "/produkte/hr" },
    { label: "Sales", href: "/produkte/sales" },
    { label: "IT Operations", href: "/produkte/it-ops" },
  ],
  Unternehmen: [
    { label: "Über uns", href: "/ueber-uns" },
    { label: "Karriere", href: "/karriere" },
    { label: "Blog", href: "/blog" },
    { label: "Sicherheit", href: "/sicherheit" },
    { label: "Ressourcen", href: "/ressourcen" },
    { label: "Kontakt", href: "mailto:hello@kengo.de" },
  ],
  Rechtliches: [
    { label: "Datenschutz", href: "/datenschutz" },
    { label: "AGB", href: "/agb" },
    { label: "Cookie-Richtlinie", href: "/cookies" },
    { label: "Impressum", href: "/impressum" },
  ],
};

export default function Footer() {
  return (
    <footer className="border-t border-line py-16">
      <div className="max-w-page mx-auto px-6">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-8 mb-16">
          {/* Brand */}
          <div className="col-span-2 md:col-span-1">
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-7 h-7 rounded-lg bg-kengo flex items-center justify-center">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path d="M2 2v10M2 7h4l4-5v10L6 7" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
              </div>
              <span className="text-lg font-display font-semibold tracking-tight">
                kengo
              </span>
            </div>
            <p className="text-sm text-text-secondary leading-relaxed">
              KI-Mitarbeiter für jede Abteilung.
              <br />
              Sofort einsatzbereit.
            </p>
          </div>

          {/* Link columns */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h4 className="text-sm font-semibold mb-4 text-text-primary">
                {category}
              </h4>
              <ul className="space-y-2.5">
                {links.map((link) => (
                  <li key={link.label}>
                    <a
                      href={link.href}
                      className="text-sm text-text-secondary hover:text-text-primary transition-colors duration-150"
                    >
                      {link.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom bar */}
        <div className="flex flex-col md:flex-row items-center justify-between gap-4 pt-8 border-t border-line">
          <p className="text-xs text-muted">
            © {new Date().getFullYear()} Kengo GmbH. Alle Rechte vorbehalten.
          </p>
          <div className="flex items-center gap-6">
            <span className="text-xs text-muted">
              Gehostet in Deutschland
            </span>
            <div className="flex items-center gap-4">
              <a href="https://www.linkedin.com/company/stealth-startup-community/" target="_blank" rel="noopener noreferrer" className="text-muted hover:text-text-primary transition-colors" aria-label="LinkedIn">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
                </svg>
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

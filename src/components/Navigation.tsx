"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { specialists } from "@/lib/specialists";

function StatusDot() {
  return <span className="w-1.5 h-1.5 rounded-full bg-success animate-pulse-live" />;
}

export default function Navigation() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [produkteOpen, setProdukteOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <>
      <motion.header
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-200 ${
          scrolled
            ? "bg-void/95 backdrop-blur-xl border-b border-line"
            : "bg-transparent"
        }`}
      >
        <nav className="max-w-page mx-auto px-6 h-16 flex items-center justify-between">
          {/* Logo */}
          <a href="/" className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-kengo flex items-center justify-center">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M2 2v10M2 7h4l4-5v10L6 7" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <span className="text-lg font-display font-semibold tracking-tight text-text-primary">
              kengo
            </span>
          </a>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-8">
            {/* Produkte dropdown */}
            <div
              className="relative"
              onMouseEnter={() => setProdukteOpen(true)}
              onMouseLeave={() => setProdukteOpen(false)}
            >
              <button className="text-[15px] font-medium text-text-secondary hover:text-text-primary transition-colors duration-150 flex items-center gap-1">
                Produkte
                <svg className={`w-3.5 h-3.5 transition-transform duration-150 ${produkteOpen ? "rotate-180" : ""}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              <AnimatePresence>
                {produkteOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 8 }}
                    transition={{ duration: 0.15 }}
                    className="absolute top-full left-1/2 -translate-x-1/2 mt-2 w-[640px] bg-surface/95 backdrop-blur-xl border border-line rounded-2xl shadow-2xl shadow-black/20 overflow-hidden"
                  >
                    {/* Top section: Product tiers */}
                    <div className="grid grid-cols-2 gap-px bg-line/30">
                      <a href="/produkte/arbeiter" className="group block p-5 hover:bg-void/50 transition-colors bg-surface/95">
                        <div className="flex items-center gap-3 mb-2">
                          <div className="w-9 h-9 rounded-xl bg-kengo/10 flex items-center justify-center">
                            <svg className="w-[18px] h-[18px] text-kengo" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0" />
                            </svg>
                          </div>
                          <div>
                            <span className="font-display font-semibold text-sm text-text-primary block">KI-Arbeiter</span>
                            <span className="text-xs text-muted">ab €1.999/mo</span>
                          </div>
                        </div>
                        <p className="text-xs text-text-secondary leading-relaxed">
                          Der Generalist. Erledigt E-Mails, Termine, Dokumente, Automatisierungen.
                        </p>
                      </a>

                      <a href="/produkte/abteilung" className="group block p-5 hover:bg-void/50 transition-colors bg-surface/95">
                        <div className="flex items-center gap-3 mb-2">
                          <div className="w-9 h-9 rounded-xl bg-kengo/10 flex items-center justify-center">
                            <svg className="w-[18px] h-[18px] text-kengo" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                              <path strokeLinecap="round" strokeLinejoin="round" d="M18 18.72a9.094 9.094 0 003.741-.479 3 3 0 00-4.682-2.72m.94 3.198l.001.031c0 .225-.012.447-.037.666A11.944 11.944 0 0112 21c-2.17 0-4.207-.576-5.963-1.584A6.062 6.062 0 016 18.719m12 0a5.971 5.971 0 00-.941-3.197m0 0A5.995 5.995 0 0012 12.75a5.995 5.995 0 00-5.058 2.772m0 0a3 3 0 00-4.681 2.72 8.986 8.986 0 003.74.477m.94-3.197a5.971 5.971 0 00-.94 3.197" />
                            </svg>
                          </div>
                          <div>
                            <span className="font-display font-semibold text-sm text-text-primary block">KI-Abteilung</span>
                            <span className="text-xs text-muted">Individuell</span>
                          </div>
                        </div>
                        <p className="text-xs text-text-secondary leading-relaxed">
                          Das ganze Team. Ein Abteilungsleiter koordiniert alle Agenten.
                        </p>
                      </a>
                    </div>

                    {/* Specialists grid */}
                    <div className="border-t border-line/50 p-5">
                      <p className="text-[11px] font-semibold uppercase tracking-wider text-muted mb-3">
                        KI-Fachkräfte · ab €0,75/Ergebnis
                      </p>
                      <div className="grid grid-cols-3 gap-1">
                        {specialists.map((s) => (
                          <a
                            key={s.name}
                            href={s.href}
                            className="flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-text-secondary hover:text-text-primary hover:bg-void/50 transition-colors"
                          >
                            <StatusDot />
                            {s.name}
                          </a>
                        ))}
                      </div>
                    </div>

                    {/* Bottom bar: Vergleich */}
                    <div className="border-t border-line/50 px-5 py-3">
                      <a href="/vergleich" className="flex items-center justify-between text-sm text-text-secondary hover:text-kengo transition-colors group">
                        <span>Kengo vs. ChatGPT, Copilot, Langdock</span>
                        <svg className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                        </svg>
                      </a>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <a href="/preise" className="text-[15px] font-medium text-text-secondary hover:text-text-primary transition-colors duration-150">
              Preise
            </a>
            <a href="/sicherheit" className="text-[15px] font-medium text-text-secondary hover:text-text-primary transition-colors duration-150">
              Sicherheit
            </a>
            <a href="/ressourcen" className="text-[15px] font-medium text-text-secondary hover:text-text-primary transition-colors duration-150">
              Ressourcen
            </a>
            <a href="/ueber-uns" className="text-[15px] font-medium text-text-secondary hover:text-text-primary transition-colors duration-150">
              Über uns
            </a>
          </div>

          {/* CTA */}
          <div className="hidden md:block">
            <a href="https://cal.eu/philhie/kengo" target="_blank" rel="noopener noreferrer" className="btn-primary text-sm">
              Demo vereinbaren
            </a>
          </div>

          {/* Mobile hamburger */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden flex flex-col gap-1.5 p-2"
            aria-label="Menü öffnen"
          >
            <span className={`w-5 h-0.5 bg-white transition-all duration-300 ${mobileOpen ? "rotate-45 translate-y-2" : ""}`} />
            <span className={`w-5 h-0.5 bg-white transition-all duration-300 ${mobileOpen ? "opacity-0" : ""}`} />
            <span className={`w-5 h-0.5 bg-white transition-all duration-300 ${mobileOpen ? "-rotate-45 -translate-y-2" : ""}`} />
          </button>
        </nav>
      </motion.header>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-void/98 backdrop-blur-2xl md:hidden"
          >
            <div className="flex flex-col items-start justify-center h-full px-8 gap-6">
              <p className="text-xs font-semibold uppercase tracking-wider text-muted">Produkte</p>
              <a href="/produkte/arbeiter" onClick={() => setMobileOpen(false)} className="text-xl font-display font-semibold text-text-primary">KI-Arbeiter</a>
              <a href="#specialists" onClick={() => setMobileOpen(false)} className="text-xl font-display font-semibold text-text-primary">KI-Fachkräfte</a>
              <a href="/produkte/abteilung" onClick={() => setMobileOpen(false)} className="text-xl font-display font-semibold text-text-primary">KI-Abteilung</a>
              <div className="w-12 h-px bg-line my-2" />
              <a href="/preise" onClick={() => setMobileOpen(false)} className="text-xl font-display font-semibold text-text-primary">Preise</a>
              <a href="/sicherheit" onClick={() => setMobileOpen(false)} className="text-xl font-display font-semibold text-text-primary">Sicherheit</a>
              <a href="/ressourcen" onClick={() => setMobileOpen(false)} className="text-xl font-display font-semibold text-text-primary">Ressourcen</a>
              <a href="/vergleich" onClick={() => setMobileOpen(false)} className="text-xl font-display font-semibold text-text-primary">Vergleich</a>
              <a href="/ueber-uns" onClick={() => setMobileOpen(false)} className="text-xl font-display font-semibold text-text-primary">Über uns</a>
              <a href="https://cal.eu/philhie/kengo" target="_blank" rel="noopener noreferrer" onClick={() => setMobileOpen(false)} className="btn-primary mt-4">
                Demo vereinbaren
              </a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

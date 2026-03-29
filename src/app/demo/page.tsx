"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { sectionReveal } from "@/lib/motion";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";

/* ─── Types ─────────────────────────────────────────────── */

interface Task {
  icon: string;
  title: string;
  description: string;
  impact: string;
  demo: string[];
}

interface DemoResult {
  companyProfile: {
    name: string;
    industry: string;
    size: string;
    summary: string;
  };
  tasks: Task[];
  totalImpact: {
    hoursPerWeek: number;
    costPerMonth: number;
  };
}

/* ─── Page ──────────────────────────────────────────────── */

export default function DemoPage() {
  const [step, setStep] = useState<"input" | "loading" | "results">("input");
  const [companyName, setCompanyName] = useState("");
  const [industry, setIndustry] = useState("");
  const [employeeCount, setEmployeeCount] = useState("");
  const [loadingSteps, setLoadingSteps] = useState<string[]>([]);
  const [result, setResult] = useState<DemoResult | null>(null);

  const industries = [
    "Fertigung",
    "Handel",
    "Dienstleistung",
    "IT",
    "Gesundheitswesen",
    "Sonstiges",
  ];

  const employeeRanges = ["10-30", "30-100", "100-250", "250-500", "500+"];

  const handleSubmit = useCallback(async () => {
    if (!companyName.trim()) return;

    setStep("loading");
    setLoadingSteps([]);

    // Animated steps
    const steps = [
      `🔍 Analysiere ${companyName}...`,
      `🏢 Branche erkannt: ${industry || "Mittelstand"}`,
      "📊 Unternehmensprofil erstellt...",
      "⚡ Generiere 3 konkrete Aufgaben...",
      "✅ Dein KI-Mitarbeiter ist bereit.",
    ];

    // Show steps one by one
    for (let i = 0; i < steps.length; i++) {
      await new Promise((resolve) => setTimeout(resolve, 2000));
      setLoadingSteps((prev) => [...prev, steps[i]]);
    }

    // API call
    try {
      const res = await fetch("/api/demo", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ companyName, industry, employeeCount }),
      });
      const data = await res.json();
      setResult(data);
    } catch {
      // Fallback will be handled by the API
      setResult(null);
    }

    setStep("results");
  }, [companyName, industry, employeeCount]);

  const handleReset = () => {
    setStep("input");
    setCompanyName("");
    setIndustry("");
    setEmployeeCount("");
    setResult(null);
    setLoadingSteps([]);
  };

  return (
    <>
      <Navigation />
      <main>
        <section className="relative min-h-screen pt-32 pb-20 overflow-hidden">
          <div className="absolute inset-0 hero-glow" />
          <div className="absolute inset-0 bg-grid opacity-30" />

          <div className="relative z-10 max-w-page mx-auto px-6">
            <AnimatePresence mode="wait">
              {step === "input" && <InputPhase key="input" companyName={companyName} setCompanyName={setCompanyName} industry={industry} setIndustry={setIndustry} employeeCount={employeeCount} setEmployeeCount={setEmployeeCount} industries={industries} employeeRanges={employeeRanges} onSubmit={handleSubmit} />}
              {step === "loading" && <LoadingPhase key="loading" steps={loadingSteps} companyName={companyName} />}
              {step === "results" && result && <ResultsPhase key="results" result={result} onReset={handleReset} />}
            </AnimatePresence>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}

/* ─── Step 1: Input ─────────────────────────────────────── */

function InputPhase({
  companyName,
  setCompanyName,
  industry,
  setIndustry,
  employeeCount,
  setEmployeeCount,
  industries,
  employeeRanges,
  onSubmit,
}: {
  companyName: string;
  setCompanyName: (v: string) => void;
  industry: string;
  setIndustry: (v: string) => void;
  employeeCount: string;
  setEmployeeCount: (v: string) => void;
  industries: string[];
  employeeRanges: string[];
  onSubmit: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="max-w-lg mx-auto text-center"
    >
      <h1 className="text-[36px] sm:text-[48px] md:text-[56px] font-display font-semibold tracking-[-0.03em] leading-[1.05] mb-6">
        Erlebe deinen KI-Mitarbeiter. Jetzt. Live.
      </h1>
      <p className="text-lg text-text-secondary mb-10">
        Gib deinen Firmennamen ein und sieh in 30 Sekunden, was Kengo für dein
        Unternehmen tun kann.
      </p>

      <div className="space-y-4 text-left">
        <input
          type="text"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          placeholder="Dein Firmenname..."
          className="w-full bg-surface border border-line rounded-xl px-5 py-4 text-base text-text-primary placeholder:text-muted focus:outline-none focus:border-kengo transition-colors"
          onKeyDown={(e) => e.key === "Enter" && onSubmit()}
        />

        <select
          value={industry}
          onChange={(e) => setIndustry(e.target.value)}
          className="w-full bg-surface border border-line rounded-xl px-5 py-4 text-base text-text-primary focus:outline-none focus:border-kengo transition-colors appearance-none"
        >
          <option value="">Deine Branche (optional)</option>
          {industries.map((i) => (
            <option key={i} value={i}>
              {i}
            </option>
          ))}
        </select>

        <select
          value={employeeCount}
          onChange={(e) => setEmployeeCount(e.target.value)}
          className="w-full bg-surface border border-line rounded-xl px-5 py-4 text-base text-text-primary focus:outline-none focus:border-kengo transition-colors appearance-none"
        >
          <option value="">Anzahl Mitarbeiter (optional)</option>
          {employeeRanges.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>

        <button
          onClick={onSubmit}
          disabled={!companyName.trim()}
          className="w-full bg-kengo hover:bg-kengo-light disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold px-8 py-4 rounded-xl text-base transition-all duration-150 flex items-center justify-center gap-2"
        >
          KI-Mitarbeiter starten
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </button>
      </div>
    </motion.div>
  );
}

/* ─── Step 2: Loading ───────────────────────────────────── */

function LoadingPhase({
  steps,
  companyName,
}: {
  steps: string[];
  companyName: string;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      transition={{ duration: 0.3 }}
      className="max-w-lg mx-auto"
    >
      <div className="bg-surface border border-line rounded-2xl p-8">
        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-line">
          <div className="w-3 h-3 rounded-full bg-red-500" />
          <div className="w-3 h-3 rounded-full bg-yellow-500" />
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span className="text-xs text-muted font-mono ml-2">
            kengo-agent — {companyName}
          </span>
        </div>

        <div className="space-y-3 font-mono text-sm">
          {steps.map((step, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
              className="flex items-start gap-2"
            >
              <span className="text-kengo">$</span>
              <span className="text-text-secondary">{step}</span>
            </motion.div>
          ))}
          {steps.length < 5 && (
            <div className="flex items-center gap-2">
              <span className="text-kengo">$</span>
              <span className="inline-block w-2 h-4 bg-kengo animate-pulse" />
            </div>
          )}
        </div>

        {/* Progress bar */}
        <div className="mt-6 h-1 bg-line rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-kengo rounded-full"
            initial={{ width: "0%" }}
            animate={{ width: `${(steps.length / 5) * 100}%` }}
            transition={{ duration: 0.5 }}
          />
        </div>
      </div>
    </motion.div>
  );
}

/* ─── Step 3: Results ───────────────────────────────────── */

function ResultsPhase({
  result,
  onReset,
}: {
  result: DemoResult;
  onReset: () => void;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="max-w-4xl mx-auto"
    >
      {/* Company Card */}
      <div className="bg-surface border border-line rounded-2xl p-8 mb-8 text-center">
        <h2 className="text-2xl font-display font-semibold mb-2">
          {result.companyProfile.name}
        </h2>
        <p className="text-sm text-text-secondary mb-4">
          {result.companyProfile.industry} · {result.companyProfile.size}{" "}
          Mitarbeiter
        </p>
        <p className="text-base text-text-secondary max-w-2xl mx-auto">
          Basierend auf der Analyse Ihres Unternehmens hat Ihr Kengo
          KI-Mitarbeiter 3 Aufgaben identifiziert, die er sofort übernehmen
          kann.
        </p>
      </div>

      {/* Task Cards */}
      <div className="grid md:grid-cols-3 gap-4 mb-8">
        {result.tasks.map((task, i) => (
          <motion.div
            key={task.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.15, duration: 0.3 }}
            className="bg-surface border border-line rounded-2xl p-6"
          >
            <span className="text-2xl block mb-3">{task.icon}</span>
            <h3 className="text-base font-display font-semibold mb-2">
              {task.title}
            </h3>
            <p className="text-sm text-text-secondary leading-relaxed mb-4">
              {task.description}
            </p>
            <p className="text-xs font-mono font-bold text-kengo mb-4">
              {task.impact}
            </p>

            {/* Mini demo log */}
            <div className="bg-void rounded-lg p-3 space-y-1.5">
              {task.demo.map((line, j) => (
                <p key={j} className="text-xs text-text-secondary font-mono leading-relaxed">
                  {line}
                </p>
              ))}
            </div>
          </motion.div>
        ))}
      </div>

      {/* Total Impact */}
      <div className="bg-kengo/10 border border-kengo/20 rounded-2xl p-8 mb-8">
        <div className="flex flex-col sm:flex-row items-center justify-center gap-8 text-center">
          <div>
            <p className="text-3xl font-mono font-bold text-kengo">
              {result.totalImpact.hoursPerWeek}h
            </p>
            <p className="text-sm text-text-secondary">
              Geschätzte Zeitersparnis/Woche
            </p>
          </div>
          <div className="hidden sm:block w-px h-12 bg-kengo/20" />
          <div>
            <p className="text-3xl font-mono font-bold text-kengo">
              €{result.totalImpact.costPerMonth.toLocaleString("de-DE")}
            </p>
            <p className="text-sm text-text-secondary">
              Geschätzte Kostenersparnis/Monat
            </p>
          </div>
        </div>
      </div>

      {/* CTAs */}
      <div className="flex flex-col sm:flex-row gap-3 justify-center">
        <a href="https://cal.eu/philhie/kengo" target="_blank" rel="noopener noreferrer" className="btn-primary-lg">
          Diesen KI-Mitarbeiter für {result.companyProfile.name} einrichten
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </a>
        <button onClick={onReset} className="btn-secondary px-8 py-4">
          Nochmal versuchen
        </button>
      </div>
    </motion.div>
  );
}

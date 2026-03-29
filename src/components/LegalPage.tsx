"use client";

import { motion } from "framer-motion";
import { sectionReveal } from "@/lib/motion";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";

export default function LegalPage({
  title,
  lastUpdated,
  children,
}: {
  title: string;
  lastUpdated: string;
  children: React.ReactNode;
}) {
  return (
    <>
      <Navigation />
      <main>
        <section className="pt-32 pb-20">
          <div className="max-w-page mx-auto px-6">
            <motion.div
              variants={sectionReveal}
              initial="hidden"
              animate="visible"
              custom={0}
              className="max-w-3xl"
            >
              <h1 className="text-[36px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.1] mb-4">
                {title}
              </h1>
              <p className="text-sm text-muted mb-12">
                Zuletzt aktualisiert: {lastUpdated}
              </p>

              <div className="prose-legal space-y-8 text-[15px] text-text-secondary leading-relaxed">
                {children}
              </div>
            </motion.div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}

export function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div>
      <h2 className="text-lg font-display font-semibold text-text-primary mb-3">
        {title}
      </h2>
      {children}
    </div>
  );
}

export function SubSection({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="mt-4">
      <h3 className="text-base font-semibold text-text-primary mb-2">
        {title}
      </h3>
      {children}
    </div>
  );
}

"use client";

import { motion } from "framer-motion";
import { sectionReveal } from "@/lib/motion";
import type { BlogPost } from "@/lib/blog";

export default function BlogPostHeader({ post }: { post: BlogPost }) {
  return (
    <section className="relative pt-32 pb-8 overflow-hidden">
      <div className="absolute inset-0 hero-glow" />
      <div className="relative z-10 max-w-page mx-auto px-6">
        <motion.div
          variants={sectionReveal}
          initial="hidden"
          animate="visible"
          custom={0}
          className="max-w-3xl"
        >
          <a
            href="/blog"
            className="inline-flex items-center gap-1.5 text-sm text-text-secondary hover:text-text-primary transition-colors mb-8"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M10.5 19.5L3 12m0 0l7.5-7.5M3 12h18" />
            </svg>
            Alle Artikel
          </a>

          <div className="flex flex-wrap gap-2 mb-4">
            {post.tags.map((tag) => (
              <span
                key={tag}
                className="text-[11px] font-semibold uppercase tracking-wider text-kengo bg-kengo/10 px-2 py-0.5 rounded"
              >
                {tag}
              </span>
            ))}
          </div>

          <h1 className="text-[32px] sm:text-[40px] md:text-[48px] font-display font-semibold tracking-[-0.02em] leading-[1.15] mb-4">
            {post.title}
          </h1>

          <p className="text-lg text-text-secondary leading-relaxed mb-6">
            {post.description}
          </p>

          <div className="flex items-center gap-4 text-sm text-muted">
            <span>{post.author}</span>
            <span className="w-1 h-1 rounded-full bg-muted" />
            <span>
              {new Date(post.date).toLocaleDateString("de-DE", {
                day: "numeric",
                month: "long",
                year: "numeric",
              })}
            </span>
            <span className="w-1 h-1 rounded-full bg-muted" />
            <span>{post.readingTime}</span>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

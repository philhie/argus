"use client";

import { motion } from "framer-motion";
import { sectionReveal, staggerContainer, staggerItem } from "@/lib/motion";
import type { BlogPost } from "@/lib/blog";

export default function BlogList({ posts }: { posts: BlogPost[] }) {
  return (
    <>
      {/* Hero */}
      <section className="relative pt-32 pb-8 overflow-hidden">
        <div className="absolute inset-0 hero-glow" />
        <div className="relative z-10 max-w-page mx-auto px-6">
          <motion.div
            variants={sectionReveal}
            initial="hidden"
            animate="visible"
            custom={0}
          >
            <h1 className="text-[40px] sm:text-[56px] md:text-[72px] font-display font-semibold tracking-[-0.03em] leading-[1.05] mb-4">
              Blog
            </h1>
            <p className="text-lg md:text-xl text-text-secondary max-w-2xl leading-relaxed">
              Wissen über KI-Mitarbeiter, Automatisierung und digitale
              Transformation im Mittelstand.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Posts */}
      <section className="section-padding">
        <div className="max-w-page mx-auto px-6">
          {posts.length === 0 ? (
            <p className="text-text-secondary text-center">
              Noch keine Artikel. Bald mehr.
            </p>
          ) : (
            <motion.div
              variants={staggerContainer}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
              className="grid md:grid-cols-2 lg:grid-cols-3 gap-4"
            >
              {posts.map((post) => (
                <motion.a
                  key={post.slug}
                  variants={staggerItem}
                  href={`/blog/${post.slug}`}
                  className="card-hover group flex flex-col"
                >
                  <div className="flex flex-wrap gap-2 mb-4">
                    {post.tags.slice(0, 2).map((tag) => (
                      <span
                        key={tag}
                        className="text-[11px] font-semibold uppercase tracking-wider text-kengo bg-kengo/10 px-2 py-0.5 rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  <h2 className="text-lg font-display font-semibold mb-2 group-hover:text-kengo transition-colors">
                    {post.title}
                  </h2>

                  <p className="text-sm text-text-secondary leading-relaxed mb-4 flex-1">
                    {post.description}
                  </p>

                  <div className="flex items-center justify-between text-xs text-muted pt-4 border-t border-line">
                    <span>
                      {new Date(post.date).toLocaleDateString("de-DE", {
                        day: "numeric",
                        month: "long",
                        year: "numeric",
                      })}
                    </span>
                    <span>{post.readingTime}</span>
                  </div>
                </motion.a>
              ))}
            </motion.div>
          )}
        </div>
      </section>
    </>
  );
}

import { notFound } from "next/navigation";
import { getAllPosts, getPostBySlug } from "@/lib/blog";
import { MDXRemote } from "next-mdx-remote/rsc";
import type { Metadata } from "next";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import BlogPostHeader from "@/components/BlogPostHeader";

const mdxComponents = {
  h2: (props: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h2 className="text-[24px] md:text-[28px] font-bold tracking-[-0.01em] leading-[1.2] mb-4 mt-10 text-text-primary" {...props} />
  ),
  h3: (props: React.HTMLAttributes<HTMLHeadingElement>) => (
    <h3 className="text-lg font-bold mb-3 mt-8 text-text-primary" {...props} />
  ),
  p: (props: React.HTMLAttributes<HTMLParagraphElement>) => (
    <p className="text-[15px] text-text-secondary leading-[1.8] mb-4" {...props} />
  ),
  ul: (props: React.HTMLAttributes<HTMLUListElement>) => (
    <ul className="list-disc pl-5 space-y-2 mb-4 text-[15px] text-text-secondary leading-[1.8]" {...props} />
  ),
  ol: (props: React.HTMLAttributes<HTMLOListElement>) => (
    <ol className="list-decimal pl-5 space-y-2 mb-4 text-[15px] text-text-secondary leading-[1.8]" {...props} />
  ),
  li: (props: React.HTMLAttributes<HTMLLIElement>) => <li className="pl-1" {...props} />,
  a: (props: React.AnchorHTMLAttributes<HTMLAnchorElement>) => (
    <a className="text-kengo hover:text-kengo-light underline transition-colors" {...props} />
  ),
  blockquote: (props: React.HTMLAttributes<HTMLQuoteElement>) => (
    <blockquote className="border-l-2 border-kengo pl-6 my-6 text-text-primary italic" {...props} />
  ),
  code: (props: React.HTMLAttributes<HTMLElement>) => (
    <code className="bg-surface px-1.5 py-0.5 rounded text-sm font-mono text-kengo" {...props} />
  ),
  pre: (props: React.HTMLAttributes<HTMLPreElement>) => (
    <pre className="bg-surface border border-line rounded-xl p-4 overflow-x-auto mb-4 text-sm font-mono" {...props} />
  ),
  hr: () => <hr className="border-line my-8" />,
  strong: (props: React.HTMLAttributes<HTMLElement>) => (
    <strong className="text-text-primary font-semibold" {...props} />
  ),
  table: (props: React.HTMLAttributes<HTMLTableElement>) => (
    <div className="overflow-x-auto mb-4">
      <table className="w-full text-sm text-text-secondary" {...props} />
    </div>
  ),
  thead: (props: React.HTMLAttributes<HTMLTableSectionElement>) => (
    <thead className="border-b border-line" {...props} />
  ),
  th: (props: React.HTMLAttributes<HTMLTableCellElement>) => (
    <th className="text-left p-3 font-semibold text-text-primary" {...props} />
  ),
  td: (props: React.HTMLAttributes<HTMLTableCellElement>) => (
    <td className="p-3 border-b border-line" {...props} />
  ),
};

interface PageProps {
  params: { slug: string };
}

export async function generateStaticParams() {
  return getAllPosts().map((post) => ({ slug: post.slug }));
}

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const post = getPostBySlug(params.slug);
  if (!post) return {};
  return {
    title: `${post.title} | Kengo Blog`,
    description: post.description,
    openGraph: {
      title: post.title,
      description: post.description,
      type: "article",
      publishedTime: post.date,
      authors: [post.author],
    },
  };
}

export default function BlogPostPage({ params }: PageProps) {
  const post = getPostBySlug(params.slug);
  if (!post) notFound();

  return (
    <>
      <Navigation />
      <main>
        <BlogPostHeader post={post} />

        {/* MDX Content — server rendered */}
        <section className="py-16 px-6 sm:py-20 md:py-[80px]">
          <div className="max-w-3xl mx-auto">
            <MDXRemote source={post.content} components={mdxComponents} />
          </div>
        </section>

        {/* CTA */}
        <section className="section-padding">
          <div className="max-w-3xl mx-auto px-6 text-center">
            <div className="card p-10">
              <h2 className="text-2xl font-display font-semibold mb-3">
                Bereit für deinen KI-Mitarbeiter?
              </h2>
              <p className="text-sm text-text-secondary mb-6">
                15 Minuten Demo. Kein Verkaufsdruck.
              </p>
              <a href="https://cal.eu/philhie/kengo" target="_blank" rel="noopener noreferrer" className="btn-primary">
                Demo vereinbaren
              </a>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}

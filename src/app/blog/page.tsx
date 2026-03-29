import { getAllPosts } from "@/lib/blog";
import Navigation from "@/components/Navigation";
import Footer from "@/components/Footer";
import BlogList from "@/components/BlogList";

export default function BlogPage() {
  const posts = getAllPosts();

  return (
    <>
      <Navigation />
      <main>
        <BlogList posts={posts} />
      </main>
      <Footer />
    </>
  );
}

import Navigation from "@/components/Navigation";
import Hero from "@/components/Hero";
import SectionDivider from "@/components/SectionDivider";
import Problem from "@/components/Problem";
import SolutionIntro from "@/components/SolutionIntro";
import HowItWorks from "@/components/HowItWorks";
import SpecialistGrid from "@/components/SpecialistGrid";
import Integrations from "@/components/Integrations";
import PricingPreview from "@/components/PricingPreview";
import ROIComparison from "@/components/ROIComparison";
import Trust from "@/components/Trust";
import Testimonials from "@/components/Testimonials";
import FinalCTA from "@/components/FinalCTA";
import Footer from "@/components/Footer";
import StickyCtaBar from "@/components/StickyCtaBar";

export default function Home() {
  return (
    <main>
      <Navigation />
      <Hero />
      <SectionDivider />
      <Problem />
      <SectionDivider />
      <SolutionIntro />
      <SectionDivider />
      <HowItWorks />
      <SectionDivider />
      <SpecialistGrid />
      <SectionDivider />
      <Integrations />
      <PricingPreview />
      <ROIComparison />
      <SectionDivider />
      <Trust />
      <SectionDivider />
      <Testimonials />
      <SectionDivider />
      <FinalCTA />
      <Footer />
      <StickyCtaBar />
    </main>
  );
}

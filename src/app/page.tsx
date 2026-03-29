import Navigation from "@/components/Navigation";
import Hero from "@/components/Hero";
import SocialProof from "@/components/SocialProof";
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

export default function Home() {
  return (
    <main>
      <Navigation />
      <Hero />
      <SocialProof />
      <Problem />
      <SolutionIntro />
      <HowItWorks />
      <SpecialistGrid />
      <Integrations />
      <PricingPreview />
      <ROIComparison />
      <Trust />
      <Testimonials />
      <FinalCTA />
      <Footer />
    </main>
  );
}

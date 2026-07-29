import Link from "next/link";
import Scene from "@/components/canvas/Scene";
import HeroOverlay from "@/components/ui/HeroOverlay";
import ModuleExperiences from "@/components/ui/ModuleExperiences";
import SmoothScroll from "@/components/ui/SmoothScroll";

export default function Home() {
  return (
    <SmoothScroll>
      <div className="bg-black min-h-screen text-white overflow-hidden selection:bg-indigo-500/30">
        {/* Background 3D Scene */}
        <Scene />

        {/* Header - Kept intact as requested, but styled for the new theme */}
        <header className="fixed top-0 left-0 right-0 px-8 py-6 z-50 mix-blend-difference flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-white flex items-center justify-center">
              <span className="text-black font-bold text-xl leading-none">E</span>
            </div>
            <span className="font-bold text-xl tracking-tight text-white">EduFlow</span>
          </div>
          
          <div className="flex items-center gap-6">
            <Link href="/login" className="text-sm font-medium text-zinc-300 hover:text-white transition-colors uppercase tracking-widest">
              Log in
            </Link>
            <Link href="/setup" className="bg-white text-black px-5 py-2.5 rounded-none text-sm font-bold hover:bg-zinc-200 transition-colors uppercase tracking-widest">
              Get Started
            </Link>
          </div>
        </header>

        {/* Foreground Content */}
        <main className="relative z-10 w-full">
          <HeroOverlay />
          <ModuleExperiences />
        </main>
      </div>
    </SmoothScroll>
  );
}

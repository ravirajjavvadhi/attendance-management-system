import Link from "next/link";
import { ArrowRight, BarChart3, Users, Shield, CalendarCheck } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="flex justify-between items-center px-8 py-6 border-b bg-background/80 backdrop-blur-md sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-xl">E</span>
          </div>
          <span className="font-bold text-xl tracking-tight">EduFlow</span>
        </div>
        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-muted-foreground">
          <a href="#features" className="hover:text-foreground transition-colors">Features</a>
          <a href="#solutions" className="hover:text-foreground transition-colors">Solutions</a>
          <a href="#pricing" className="hover:text-foreground transition-colors">Pricing</a>
        </nav>
        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm font-medium hover:text-muted-foreground transition-colors">
            Log in
          </Link>
          <Link href="/setup" className="bg-primary text-primary-foreground px-4 py-2 rounded-full text-sm font-medium hover:bg-primary/90 transition-colors">
            Get Started
          </Link>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center px-4 pt-24 pb-32 text-center">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary text-secondary-foreground text-sm font-medium mb-8">
          <span className="flex h-2 w-2 rounded-full bg-blue-500"></span>
          EduFlow AI 2.0 is now live
        </div>
        
        <h1 className="text-5xl md:text-7xl font-bold tracking-tighter max-w-4xl leading-[1.1] mb-8">
          The operating system for <br className="hidden md:block"/>
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-500 to-violet-500">modern education.</span>
        </h1>
        
        <p className="text-xl text-muted-foreground max-w-2xl mb-12 leading-relaxed">
          Eliminate biometric queues, automate parent communication, and streamline academic records with our enterprise-grade SaaS platform.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 items-center">
          <Link href="/setup" className="flex items-center gap-2 bg-primary text-primary-foreground px-8 py-4 rounded-full text-lg font-medium hover:bg-primary/90 transition-colors shadow-lg shadow-primary/20">
            Start for free <ArrowRight className="w-5 h-5" />
          </Link>
          <Link href="/login" className="px-8 py-4 rounded-full text-lg font-medium border hover:bg-secondary transition-colors">
            Book a demo
          </Link>
        </div>
        
        <div className="mt-32 w-full max-w-6xl aspect-[16/9] rounded-2xl border bg-secondary/50 shadow-2xl relative overflow-hidden flex items-center justify-center">
          <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&q=80&w=2000')] bg-cover bg-center opacity-20 dark:opacity-40"></div>
          <div className="z-10 p-8 text-left bg-background/80 backdrop-blur-md rounded-xl border max-w-sm m-auto">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 rounded-full bg-green-500/20 flex items-center justify-center text-green-500">
                <Shield className="w-5 h-5" />
              </div>
              <div>
                <p className="font-semibold text-foreground">Secure Architecture</p>
                <p className="text-sm text-muted-foreground">Multi-tenant isolation</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-500">
                <BarChart3 className="w-5 h-5" />
              </div>
              <div>
                <p className="font-semibold text-foreground">Real-time Analytics</p>
                <p className="text-sm text-muted-foreground">Instant attendance tracking</p>
              </div>
            </div>
          </div>
        </div>
      </main>
      
      <footer className="border-t py-12 px-8 text-center text-sm text-muted-foreground flex flex-col items-center justify-center">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-6 h-6 rounded bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-xs">E</span>
          </div>
          <span className="font-bold text-foreground">EduFlow AI</span>
        </div>
        <p>© 2026 EduFlow AI Inc. All rights reserved.</p>
      </footer>
    </div>
  );
}

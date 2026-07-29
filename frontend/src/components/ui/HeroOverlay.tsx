"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

export default function HeroOverlay() {
  const containerRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"],
  });

  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.5], [1, 1.5]);
  const y = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);

  return (
    <div ref={containerRef} className="h-[150vh] relative z-10 w-full">
      <motion.div 
        style={{ opacity, scale, y }}
        className="sticky top-0 h-screen flex flex-col items-center justify-center text-white"
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 2, ease: "easeOut" }}
          className="flex flex-col items-center"
        >
          <div className="w-4 h-4 bg-indigo-500 rounded-full animate-pulse shadow-[0_0_30px_10px_rgba(99,102,241,0.5)] mb-8" />
          <h1 className="text-7xl md:text-9xl font-bold tracking-tighter mix-blend-difference z-20">
            EduFlow
          </h1>
          <p className="mt-6 text-xl md:text-2xl text-zinc-400 font-light tracking-wide">
            The Living Campus
          </p>
        </motion.div>
      </motion.div>
    </div>
  );
}

"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

const modules = [
  { id: "attendance", title: "Attendance", subtitle: "Living presence, captured in real-time.", align: "left" },
  { id: "faculty", title: "Faculty", subtitle: "Empowering educators with instant insights.", align: "right" },
  { id: "finance", title: "Finance", subtitle: "Fluid transactions, transparent operations.", align: "left" },
  { id: "transport", title: "Transport", subtitle: "Tracking the journey, every step of the way.", align: "right" },
];

function ModuleSection({ data, index }: { data: any; index: number }) {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ["start end", "center center"],
  });

  const opacity = useTransform(scrollYProgress, [0, 0.5, 1], [0, 0, 1]);
  const y = useTransform(scrollYProgress, [0, 1], [100, 0]);

  return (
    <div ref={ref} className="h-screen flex items-center w-full max-w-7xl mx-auto px-8 relative z-10">
      <motion.div 
        style={{ opacity, y }}
        className={`w-full md:w-1/2 flex flex-col ${data.align === "right" ? "md:ml-auto items-end text-right" : "items-start text-left"}`}
      >
        <h2 className="text-6xl md:text-8xl font-bold text-transparent bg-clip-text bg-gradient-to-br from-zinc-100 to-zinc-600 mb-4 tracking-tighter">
          {data.title}
        </h2>
        <p className="text-xl md:text-3xl text-zinc-400 font-light max-w-lg">
          {data.subtitle}
        </p>
      </motion.div>
    </div>
  );
}

export default function ModuleExperiences() {
  return (
    <div className="relative z-10 w-full py-32 pb-[50vh]">
      {modules.map((mod, i) => (
        <ModuleSection key={mod.id} data={mod} index={i} />
      ))}
      
      <div className="h-screen flex items-center justify-center text-center px-4 mt-32">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          whileInView={{ opacity: 1, scale: 1 }}
          transition={{ duration: 1 }}
          viewport={{ once: true }}
        >
          <h2 className="text-4xl md:text-6xl font-medium text-white mb-6 leading-tight">
            Every Classroom. <br />
            Every Department. <br />
            Every Decision. <br />
            <span className="text-indigo-400 font-bold">One Intelligence.</span>
          </h2>
        </motion.div>
      </div>
    </div>
  );
}

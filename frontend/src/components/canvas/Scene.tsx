"use client";

import { Canvas } from "@react-three/fiber";
import { Environment, Stars } from "@react-three/drei";
import NetworkNodes from "./NetworkNodes";
import { useEffect, useState } from "react";
import * as THREE from "three";

export default function Scene() {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY);
    };
    
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <div className="fixed inset-0 z-0 pointer-events-none bg-black">
      <Canvas
        camera={{ position: [0, 0, 8], fov: 60 }}
        gl={{ antialias: true, toneMapping: THREE.NoToneMapping }}
      >
        <color attach="background" args={["#000000"]} />
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        
        {/* The deep space/universe background */}
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade speed={1} />
        
        {/* The living network */}
        <NetworkNodes scrollY={scrollY} />
        
        <Environment preset="city" />
      </Canvas>
    </div>
  );
}

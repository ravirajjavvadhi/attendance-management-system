"use client";

import { useFrame } from "@react-three/fiber";
import { useRef, useMemo } from "react";
import * as THREE from "three";
import { Line, Sphere } from "@react-three/drei";

export default function NetworkNodes({ scrollY }: { scrollY: number }) {
  const groupRef = useRef<THREE.Group>(null);
  const nodesCount = 30;

  const nodes = useMemo(() => {
    return Array.from({ length: nodesCount }).map(() => ({
      position: new THREE.Vector3(
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 10,
        (Math.random() - 0.5) * 10
      ),
      velocity: new THREE.Vector3(
        (Math.random() - 0.5) * 0.02,
        (Math.random() - 0.5) * 0.02,
        (Math.random() - 0.5) * 0.02
      ),
    }));
  }, [nodesCount]);

  useFrame(() => {
    if (groupRef.current) {
      // Rotate the entire network based on scroll
      groupRef.current.rotation.y = scrollY * 0.001;
      groupRef.current.rotation.x = scrollY * 0.0005;

      // Animate individual nodes
      nodes.forEach((node, i) => {
        node.position.add(node.velocity);
        
        // Bounce off bounds
        if (Math.abs(node.position.x) > 5) node.velocity.x *= -1;
        if (Math.abs(node.position.y) > 5) node.velocity.y *= -1;
        if (Math.abs(node.position.z) > 5) node.velocity.z *= -1;

        const child = groupRef.current?.children[i] as THREE.Mesh;
        if (child) {
          child.position.copy(node.position);
        }
      });
    }
  });

  return (
    <group ref={groupRef}>
      {/* Central Node representing EduFlow */}
      <Sphere args={[0.3, 32, 32]} position={[0, 0, 0]}>
        <meshBasicMaterial color="#ffffff" transparent opacity={0.9} />
      </Sphere>

      {/* Orbiting Nodes */}
      {nodes.map((node, i) => (
        <Sphere key={i} args={[0.08, 16, 16]} position={node.position}>
          <meshBasicMaterial color="#4f46e5" transparent opacity={0.7} />
        </Sphere>
      ))}

      {/* Connections (Lines) */}
      {nodes.map((node, i) => {
        // Connect to center
        const connections = [
          <Line
            key={`line-center-${i}`}
            points={[[0, 0, 0], [node.position.x, node.position.y, node.position.z]]}
            color="#4f46e5"
            opacity={0.2}
            transparent
            lineWidth={1}
          />
        ];

        // Connect to nearest neighbor
        if (i < nodes.length - 1) {
          connections.push(
            <Line
              key={`line-neighbor-${i}`}
              points={[
                [node.position.x, node.position.y, node.position.z],
                [nodes[i + 1].position.x, nodes[i + 1].position.y, nodes[i + 1].position.z]
              ]}
              color="#3b82f6"
              opacity={0.15}
              transparent
              lineWidth={0.5}
            />
          );
        }
        return connections;
      })}
    </group>
  );
}

"use client";

import { useEffect, useRef, useState } from "react";

type Point = { x: number; y: number; r: number; kind: "fact" | "uncertain" | "branch"; label?: string };

const points: Point[] = [
  { x: 8, y: 50, r: 4, kind: "fact", label: "1789" },
  { x: 24, y: 43, r: 5, kind: "fact" },
  { x: 42, y: 50, r: 8, kind: "fact", label: "18 BRUMAIRE" },
  { x: 58, y: 39, r: 4, kind: "fact" },
  { x: 75, y: 31, r: 5, kind: "uncertain" },
  { x: 91, y: 24, r: 3, kind: "fact", label: "1815" },
  { x: 59, y: 62, r: 4, kind: "branch" },
  { x: 75, y: 71, r: 5, kind: "branch" },
  { x: 91, y: 77, r: 3, kind: "branch", label: "ALTERNATIVE" },
];

const lines = [
  [0, 1, "fact"], [1, 2, "fact"], [2, 3, "fact"], [3, 4, "uncertain"], [4, 5, "fact"],
  [2, 6, "branch"], [6, 7, "branch"], [7, 8, "branch"], [1, 3, "faint"],
] as const;

export function CausalLoom() {
  const ref = useRef<HTMLDivElement>(null);
  const [active, setActive] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const move = (event: PointerEvent) => {
      const rect = el.getBoundingClientRect();
      el.style.setProperty("--px", `${((event.clientX - rect.left) / rect.width - .5) * 2}`);
      el.style.setProperty("--py", `${((event.clientY - rect.top) / rect.height - .5) * 2}`);
    };
    el.addEventListener("pointermove", move);
    return () => el.removeEventListener("pointermove", move);
  }, []);

  return (
    <div className={`loom ${active ? "loom--broken" : ""}`} ref={ref} aria-label="Interactive causal timeline preview">
      <div className="loom__halo" />
      <svg viewBox="0 0 1000 520" role="img" aria-label="Napoleonic causal graph with an alternative branch">
        <defs>
          <filter id="glow"><feGaussianBlur stdDeviation="4" result="b" /><feMerge><feMergeNode in="b" /><feMergeNode in="SourceGraphic" /></feMerge></filter>
          <linearGradient id="gold" x1="0" x2="1"><stop stopColor="#8c6734" /><stop offset=".5" stopColor="#f4d38b" /><stop offset="1" stopColor="#917047" /></linearGradient>
          <linearGradient id="blue" x1="0" x2="1"><stop stopColor="#2d6e87" /><stop offset=".7" stopColor="#65dfff" /><stop offset="1" stopColor="#2c718c" /></linearGradient>
        </defs>
        {lines.map(([a, b, kind], index) => {
          const from = points[a]; const to = points[b];
          const x1 = from.x * 10, y1 = from.y * 5.2, x2 = to.x * 10, y2 = to.y * 5.2;
          return <path key={index} className={`loom__line loom__line--${kind} line-${index}`} d={`M${x1},${y1} C${(x1+x2)/2},${y1} ${(x1+x2)/2},${y2} ${x2},${y2}`} />;
        })}
        {points.map((point, index) => (
          <g key={index} className={`loom__point loom__point--${point.kind} point-${index}`} transform={`translate(${point.x * 10} ${point.y * 5.2})`}>
            <circle className="loom__ring" r={point.r + 8} />
            <circle className="loom__dot" r={point.r} />
            {point.label && <text y={index === 2 ? -26 : -17} textAnchor="middle">{point.label}</text>}
          </g>
        ))}
      </svg>
      <button className="loom__trigger" onClick={() => setActive(value => !value)} aria-pressed={active}>
        <span>{active ? "Restore thread" : "Break this thread"}</span>
        <i aria-hidden="true" />
      </button>
      <div className="loom__status"><span>Live intervention</span><strong>{active ? "Branch calculated" : "Baseline intact"}</strong></div>
    </div>
  );
}

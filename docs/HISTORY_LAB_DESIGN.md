# History Lab UI architecture

The History Lab is a client-only workspace at `/history`. It has four separated layers:

1. `lib/thread-api.ts` owns validated HTTP contracts and cancellation.
2. `stores/history-lab.ts` owns graph, selection, scenario, comparison, and explicit animation phase.
3. `lib/history-layout.ts` maps event date/category to stable coordinates; scenario changes never move nodes.
4. `components/history/LoomScene.tsx` renders the 3D presentation. The surrounding DOM supplies the accessible event list, evidence, status labels, controls, and a deterministic 2D fallback.

The intervention controller creates a scenario, records `REMOVE_EVENT`, runs the backend simulation, and only then transitions to `READY_TO_ANIMATE`. GSAP maps backend semantics to presentation: `CUT_THREAD` fractures the selected anchor and `DIM_DEPENDENCY` dims the exact identified relationship. Replay uses the saved response and never reruns inference.

Mobile and reduced-motion users receive the DOM/SVG timeline instead of mandatory WebGL. The baseline/alternative toggle changes semantic styles while preserving coordinates and selection.


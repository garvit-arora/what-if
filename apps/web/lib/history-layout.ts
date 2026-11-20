import type { GraphNode } from "./thread-api";
const lanes:Record<string,number>={revolution:2.8,political:1.4,government:0,law:-1.4,war:-2.8,diplomacy:-4};
export function layoutNode(node:GraphNode,min=1789,max=1848):[number,number,number]{const year=Number(node.date.slice(0,4));const x=((year-min)/(max-min)-.5)*22;const y=lanes[node.category]??-4;const z=Math.sin(year*1.71)*.55;return[x,y,z]}

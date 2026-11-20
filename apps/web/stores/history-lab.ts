import {create} from "zustand";
import type {EventDetail,GraphEdge,GraphNode,Simulation,World} from "@/lib/thread-api";
export type Phase="IDLE"|"SELECTED"|"SUBMITTING"|"SIMULATING"|"READY_TO_ANIMATE"|"FRACTURING"|"PROPAGATING"|"REVEALING"|"COMPLETE"|"ERROR";
type State={worlds:World[];nodes:GraphNode[];edges:GraphEdge[];selected:EventDetail|null;simulation:Simulation|null;scenarioId:string|null;phase:Phase;mode:"baseline"|"alternative";query:string;category:string;error:string|null;set:(p:Partial<State>)=>void;reset:()=>void};
export const useHistoryLab=create<State>((set)=>({worlds:[],nodes:[],edges:[],selected:null,simulation:null,scenarioId:null,phase:"IDLE",mode:"baseline",query:"",category:"all",error:null,set,reset:()=>set({simulation:null,scenarioId:null,phase:"IDLE",mode:"baseline",error:null})}));

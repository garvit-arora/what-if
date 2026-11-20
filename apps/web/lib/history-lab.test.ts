import {describe,expect,it} from "vitest";
import {layoutNode} from "./history-layout";
import {edgeInstruction,eventVisualState} from "./visual-state";
import type {Simulation} from "./thread-api";
const node={id:"event_coup_18_brumaire_1799",title:"Coup of 18 Brumaire",date:"1799-11-09",category:"political"};
const simulation={affected_events:[{id:node.id,previous_state:"present",new_state:"directly_intervened",reason_code:"DIRECTLY_INTERVENED"}],graph_diff:{removed_edges:[{id:"cut",source_id:node.id,target_id:node.id,relationship_type:"INTERVENTION",change_classification:"CUT_THREAD",reason:"branch only"}],updated_edges:[],added_nodes:[],removed_nodes:[],updated_nodes:[],added_edges:[]}} as unknown as Simulation;
describe("History Lab deterministic presentation",()=>{it("returns stable chronological coordinates",()=>{expect(layoutNode(node)).toEqual(layoutNode({...node}));expect(layoutNode(node)[0]).toBeLessThan(layoutNode({...node,date:"1815-01-01"})[0])});it("maps intervention status without inventing outcomes",()=>{expect(eventVisualState(node.id,simulation)).toBe("intervened");expect(eventVisualState("unaffected",simulation)).toBe("recorded")});it("maps only backend semantic instructions",()=>{expect(edgeInstruction("cut",simulation)).toBe("CUT_THREAD");expect(edgeInstruction("missing",simulation)).toBeNull()})});

import type { Simulation } from "./thread-api";
export type VisualState="recorded"|"intervened"|"disrupted"|"indeterminate"|"supported";
export function eventVisualState(id:string,simulation:Simulation|null):VisualState{const state=simulation?.affected_events.find(x=>x.id===id)?.new_state;if(state==="directly_intervened")return"intervened";if(state==="dependency_disrupted")return"disrupted";if(state==="indeterminate")return"indeterminate";if(state==="still_supported_by_another_pathway")return"supported";return"recorded"}
export function edgeInstruction(id:string,simulation:Simulation|null){const all=[...(simulation?.graph_diff.removed_edges??[]),...(simulation?.graph_diff.updated_edges??[])];return all.find(x=>x.id===id)?.change_classification??null}

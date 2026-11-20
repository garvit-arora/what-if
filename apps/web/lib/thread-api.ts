import { z } from "zod";

export type GraphNode={id:string;title:string;date:string;category:string};
export type GraphEdge={id:string;source_id:string;target_id:string;type:string;mechanism_id?:string;certainty?:string};
export type World={id:string;name:string;start_year:number;end_year:number;dataset_version:string};
export type EventDetail=GraphNode&{end_date?:string|null;wikidata_id:string;description:string;sources:{id:string;title:string;url:string;kind:string}[];mechanisms:{id:string;title:string;certainty:string;reason:string;output_id:string}[]};
export type DiffNode={id:string;previous_state:string;new_state:string;reason_code:string};
export type DiffEdge={id:string;source_id:string;target_id:string;relationship_type:string;previous_state?:string;new_state?:string;change_classification:string;mechanism_id?:string;evidence_ids?:string[];reason:string};
export type Simulation={scenario_id:string;simulation_id:string;baseline_world_id:string;intervention:{type:string;target_id:string};affected_events:DiffNode[];preserved_events:DiffNode[];indeterminate_events:DiffNode[];affected_relationships:DiffEdge[];graph_diff:{added_nodes:unknown[];removed_nodes:unknown[];updated_nodes:DiffNode[];added_edges:DiffEdge[];removed_edges:DiffEdge[];updated_edges:DiffEdge[]};explanations:{reason_code:string;mechanism_id:string;event_id:string;text:string;certainty:string}[];model_version:string;dataset_version:string};
const API=process.env.NEXT_PUBLIC_THREAD_API_URL??"http://127.0.0.1:8000/api/v1";
const idSchema=z.object({id:z.string().min(1)}).passthrough();
async function request<T>(path:string,init?:RequestInit,signal?:AbortSignal):Promise<T>{const response=await fetch(`${API}${path}`,{...init,signal,headers:{"Content-Type":"application/json",...init?.headers},cache:"no-store"});if(!response.ok)throw new Error(`${response.status}: ${(await response.json().catch(()=>({detail:"Request failed"}))).detail}`);return response.json() as Promise<T>}
export const threadApi={
  worlds:(signal?:AbortSignal)=>request<World[]>("/worlds",undefined,signal),
  graph:(id:string,signal?:AbortSignal)=>request<{world_id:string;nodes:GraphNode[];edges:GraphEdge[]}>(`/worlds/${encodeURIComponent(id)}/graph`,undefined,signal),
  event:(id:string,signal?:AbortSignal)=>request<EventDetail>(`/events/${encodeURIComponent(id)}`,undefined,signal),
  relationships:(id:string,signal?:AbortSignal)=>request<GraphEdge[]>(`/events/${encodeURIComponent(id)}/relationships`,undefined,signal),
  createScenario:async(name:string,baseline_world_id:string)=>{const value=await request<Record<string,unknown>>("/scenarios",{method:"POST",body:JSON.stringify({name,baseline_world_id})});return idSchema.parse(value) as {id:string}},
  intervene:(scenario:string,target_id:string)=>request<{id:string}>(`/scenarios/${scenario}/interventions`,{method:"POST",body:JSON.stringify({type:"REMOVE_EVENT",target_id})}),
  simulate:(scenario:string)=>request<Simulation>(`/scenarios/${scenario}/simulate`,{method:"POST"}),
  scenario:(id:string)=>request<Record<string,unknown>>(`/scenarios/${id}`),
};

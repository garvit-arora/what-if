from __future__ import annotations
import json,uuid
from datetime import datetime,timezone
from app.db.relate_repository import RelateRepository
from app.domains.history.models import HistoricalDataset,InterventionCreate,ScenarioCreate
from app.simulation.causal import Mechanism,Mode,Status,simulate

MODEL_VERSION="causal-1.1.0"
def _id(prefix:str)->str:return f"{prefix}_{uuid.uuid4().hex}"
def worlds(repo):return repo.execute("MATCH (w:World) RETURN w.id AS id,w.name AS name,w.start_year AS start_year,w.end_year AS end_year,w.dataset_version AS dataset_version ORDER BY w.id")
def event(repo,event_id):
    rows=repo.execute("MATCH (e:Event {id:$id}) RETURN e.id AS id,e.title AS title,e.date AS date,e.end_date AS end_date,e.category AS category,e.wikidata_id AS wikidata_id,e.description AS description",{"id":event_id})
    if not rows:return None
    value=rows[0]
    value["sources"]=repo.execute("MATCH (e:Event {id:$id})-[:SUPPORTED_BY]->(s:Source) RETURN s.id AS id,s.title AS title,s.url AS url,s.kind AS kind",{"id":event_id})
    value["mechanisms"]=repo.execute("MATCH (e:Event {id:$id})-[:REQUIRES]->(m:CausalMechanism)-[:PRODUCES]->(o:Event) RETURN m.id AS id,m.title AS title,m.certainty AS certainty,m.reason AS reason,o.id AS output_id",{"id":event_id})
    return value
def graph(repo,world_id):
    nodes=repo.execute("MATCH (e:Event)-[:PART_OF]->(w:World {id:$id}) RETURN e.id AS id,e.title AS title,e.date AS date,e.category AS category ORDER BY e.date",{"id":world_id})
    edges=[]
    for rel in ("PRECEDED","REQUIRES","PRODUCES","SUPPORTED_BY","PARTICIPATED_IN","DERIVED_FROM","MODIFIES"):
        edges += repo.execute(f"MATCH (a)-[r:{rel}]->(b) WHERE r.id IS NOT NULL RETURN r.id AS id,a.id AS source_id,b.id AS target_id,'{rel}' AS type ORDER BY r.id")
    causal=repo.execute("MATCH (a:Event)-[:REQUIRES]->(m:CausalMechanism)-[:PRODUCES]->(b:Event) RETURN a.id AS source_id,b.id AS target_id,m.id AS mechanism_id,m.certainty AS certainty ORDER BY m.id,a.id")
    edges += [{"id":f"rel_causal_{row['mechanism_id']}_{row['source_id']}_{row['target_id']}","source_id":row["source_id"],"target_id":row["target_id"],"type":"CAUSAL_DEPENDENCY","mechanism_id":row["mechanism_id"],"certainty":row["certainty"]} for row in causal]
    return {"world_id":world_id,"nodes":nodes,"edges":edges}
def relationships(repo,event_id):
    out=[]
    for rel in ("PRECEDED","REQUIRES","PRODUCES","SUPPORTED_BY","PARTICIPATED_IN"):
        out += repo.execute(f"MATCH (a)-[r:{rel}]->(b) WHERE a.id=$id OR b.id=$id RETURN r.id AS id,a.id AS source_id,b.id AS target_id,'{rel}' AS type",{"id":event_id})
    return out
def create_scenario(repo,p:ScenarioCreate):
    if not repo.execute("MATCH (w:World {id:$id}) RETURN w.id AS id",{"id":p.baseline_world_id}):raise ValueError("baseline world not found")
    sid=_id("scenario");now=datetime.now(timezone.utc).isoformat()
    repo.transaction([("MATCH (w:World {id:$world}) CREATE (s:Scenario {id:$id,name:$name,created_at:$now,status:'draft'})-[:DERIVED_FROM {id:$rel}]->(w)",{"world":p.baseline_world_id,"id":sid,"name":p.name,"now":now,"rel":f"rel_derived_{sid}"})])
    return get_scenario(repo,sid)
def get_scenario(repo,sid):
    rows=repo.execute("MATCH (s:Scenario {id:$id})-[:DERIVED_FROM]->(w:World) OPTIONAL MATCH (s)-[:MODIFIES]->(i:Intervention) RETURN s.id AS id,s.name AS name,s.status AS status,w.id AS baseline_world_id,i.id AS intervention_id,i.type AS intervention_type,i.target_id AS target_id",{"id":sid})
    return rows[0] if rows else None
def add_intervention(repo,sid,p:InterventionCreate):
    if not get_scenario(repo,sid):raise ValueError("scenario not found")
    if not event(repo,p.target_id):raise ValueError("target event not found")
    iid=_id("intervention")
    repo.transaction([("MATCH (s:Scenario {id:$sid}) CREATE (i:Intervention {id:$iid,type:$type,target_id:$target}) CREATE (s)-[:MODIFIES {id:$rel}]->(i)",{"sid":sid,"iid":iid,"type":p.type,"target":p.target_id,"rel":f"rel_modifies_{iid}"})])
    return {"id":iid,**p.model_dump()}
def run_simulation(repo,sid,d:HistoricalDataset):
    scenario=get_scenario(repo,sid)
    if not scenario:raise ValueError("scenario not found")
    if not scenario.get("target_id"):raise ValueError("scenario has no intervention")
    mechanisms=[Mechanism(m.id,tuple(m.inputs),m.output,Mode(m.mode),m.certainty) for m in d.mechanisms]
    result=simulate({e.id for e in d.events},mechanisms,{scenario["target_id"]})
    affected=[];preserved=[];indeterminate=[]
    for eid,status in result.statuses.items():
        item={"id":eid,"previous_state":"present","new_state":status.value,"reason_code":status.name}
        (preserved if status is Status.UNCHANGED else affected).append(item)
        if status is Status.INDETERMINATE:indeterminate.append(item)
    updated_edges=[];explanations=[]
    for step in result.trace:
        mech=next(m for m in d.mechanisms if m.id==step.mechanism_id)
        if not step.supported:
            for inp in mech.inputs:
                if result.statuses[inp] is Status.UNCHANGED:
                    continue
                rid=f"rel_requires_{mech.id}_{inp}"
                updated_edges.append({"id":rid,"source_id":inp,"target_id":mech.id,"relationship_type":"REQUIRES","previous_state":"active","new_state":"unsatisfied" if mech.certainty=="documented" else "indeterminate","change_classification":"DIM_DEPENDENCY","mechanism_id":mech.id,"evidence_ids":mech.source_ids,"reason":mech.reason})
            explanations.append({"reason_code":"PREREQUISITE_UNSATISFIED" if mech.certainty=="documented" else "COUNTERFACTUAL_INDETERMINATE","mechanism_id":mech.id,"event_id":mech.output,"text":mech.reason,"certainty":mech.certainty})
    target=scenario["target_id"]
    graph_diff={"added_nodes":[],"removed_nodes":[],"updated_nodes":affected,"added_edges":[],"removed_edges":[{"id":f"intervention_cut_{target}","source_id":target,"target_id":target,"relationship_type":"INTERVENTION","change_classification":"CUT_THREAD","reason":"Removed only in this scenario"}],"updated_edges":updated_edges}
    payload={"scenario_id":sid,"baseline_world_id":scenario["baseline_world_id"],"intervention":{"type":scenario["intervention_type"],"target_id":target},"affected_events":affected,"preserved_events":preserved,"indeterminate_events":indeterminate,"affected_relationships":updated_edges,"graph_diff":graph_diff,"explanations":explanations,"model_version":MODEL_VERSION,"dataset_version":d.dataset_version}
    simid=_id("simulation");payload["simulation_id"]=simid;encoded=json.dumps(payload,sort_keys=True,separators=(",",":"))
    repo.transaction([("MATCH (s:Scenario {id:$sid}) SET s.status='simulated' CREATE (r:SimulationRun {id:$rid,model_version:$model,dataset_version:$dataset,result_json:$result,created_at:$created}) CREATE (r)-[:DERIVED_FROM {id:$rel}]->(s)",{"sid":sid,"rid":simid,"model":MODEL_VERSION,"dataset":d.dataset_version,"result":encoded,"created":datetime.now(timezone.utc).isoformat(),"rel":f"rel_run_{simid}"})])
    return payload
def latest_result(repo,sid):
    rows=repo.execute("MATCH (r:SimulationRun)-[:DERIVED_FROM]->(s:Scenario {id:$id}) RETURN r.result_json AS result ORDER BY r.created_at DESC LIMIT 1",{"id":sid})
    return json.loads(rows[0]["result"]) if rows else None

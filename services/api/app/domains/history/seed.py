import json
from pathlib import Path
from app.db.relate_repository import RelateRepository
from app.domains.history.models import HistoricalDataset

def load_dataset(path:Path)->HistoricalDataset:
    return HistoricalDataset.model_validate(json.loads(path.read_text(encoding="utf-8")))

def seed_history(repo:RelateRepository,d:HistoricalDataset)->dict[str,int]:
    s:list[tuple[str,dict]]=[]; w=d.world
    s.append(("MERGE (n:World {id:$id}) SET n.name=$name,n.start_year=$start_year,n.end_year=$end_year,n.dataset_version=$dataset_version",{**w.model_dump(),"dataset_version":d.dataset_version}))
    for label,items in (("Source",d.sources),("Person",d.people),("Institution",d.institutions),("Place",d.places),("Event",d.events)):
        for item in items:
            data={k:v for k,v in item.model_dump().items() if v is not None}; assignments=", ".join(f"n.{k}=${k}" for k in data if k!="id")
            s.append((f"MERGE (n:{label} {{id:$id}}) SET {assignments}",data))
    for e in d.events:
        s += [
          ("MATCH (e:Event {id:$event_id}),(w:World {id:$world_id}) MERGE (e)-[:PART_OF {id:$id}]->(w)",{"event_id":e.id,"world_id":w.id,"id":f"rel_part_of_{e.id}"}),
          ("MATCH (e:Event {id:$event_id}),(x:Source {id:'src_wikidata'}) MERGE (e)-[:SUPPORTED_BY {id:$id}]->(x)",{"event_id":e.id,"id":f"rel_source_{e.id}"})]
    ordered=sorted(d.events,key=lambda e:e.date)
    for a,b in zip(ordered,ordered[1:]): s.append(("MATCH (a:Event {id:$a}),(b:Event {id:$b}) MERGE (a)-[:PRECEDED {id:$id}]->(b)",{"a":a.id,"b":b.id,"id":f"rel_preceded_{a.id}_{b.id}"}))
    for p in d.participants: s.append(("MATCH (p:Person {id:$person_id}),(e:Event {id:$event_id}) MERGE (p)-[:PARTICIPATED_IN {id:$id}]->(e)",{**p.model_dump(),"id":f"rel_participated_{p.person_id}_{p.event_id}"}))
    for m in d.mechanisms:
        s.append(("MERGE (m:CausalMechanism {id:$id}) SET m.title=$title,m.mode=$mode,m.certainty=$certainty,m.output=$output,m.reason=$reason",m.model_dump(exclude={"inputs","source_ids"})))
        claim_id=f"claim_{m.id}"
        s.append(("MERGE (c:HistoricalClaim {id:$id}) SET c.text=$text,c.classification=$classification",{"id":claim_id,"text":m.reason,"classification":m.certainty}))
        s.append(("MATCH (m:CausalMechanism {id:$mechanism_id}),(c:HistoricalClaim {id:$claim_id}) MERGE (m)-[:DERIVED_FROM {id:$id}]->(c)",{"mechanism_id":m.id,"claim_id":claim_id,"id":f"rel_claim_{m.id}"}))
        for i in m.inputs:s.append(("MATCH (e:Event {id:$event_id}),(m:CausalMechanism {id:$mechanism_id}) MERGE (e)-[:REQUIRES {id:$id}]->(m)",{"event_id":i,"mechanism_id":m.id,"id":f"rel_requires_{m.id}_{i}"}))
        s.append(("MATCH (m:CausalMechanism {id:$mechanism_id}),(e:Event {id:$event_id}) MERGE (m)-[:PRODUCES {id:$id}]->(e)",{"mechanism_id":m.id,"event_id":m.output,"id":f"rel_produces_{m.id}"}))
        for x in m.source_ids:
            s.append(("MATCH (m:CausalMechanism {id:$mechanism_id}),(x:Source {id:$source_id}) MERGE (m)-[:SUPPORTED_BY {id:$id}]->(x)",{"mechanism_id":m.id,"source_id":x,"id":f"rel_mech_source_{m.id}_{x}"}))
            s.append(("MATCH (c:HistoricalClaim {id:$claim_id}),(x:Source {id:$source_id}) MERGE (c)-[:SUPPORTED_BY {id:$id}]->(x)",{"claim_id":claim_id,"source_id":x,"id":f"rel_claim_source_{m.id}_{x}"}))
    repo.transaction(s); return {"events":len(d.events),"mechanisms":len(d.mechanisms),"sources":len(d.sources)}

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fastapi.testclient import TestClient
from app.db.relate_repository import RelateRepository
from app.domains.history.seed import load_dataset,seed_history
from app.main import create_app

ROOT=Path(__file__).resolve().parents[3];SEED=ROOT/"data"/"seeds"/"napoleonic_history.json"

def test_seed_is_idempotent_and_sources_persist(tmp_path):
    path=tmp_path/"history.rl";data=load_dataset(SEED)
    with RelateRepository(path) as repo:
        seed_history(repo,data);seed_history(repo,data)
        assert repo.execute("MATCH (e:Event) RETURN count(e) AS n")[0]["n"]==22
        assert repo.execute("MATCH (e:Event {id:$id})-[:SUPPORTED_BY]->(s:Source) RETURN s.url AS url",{"id":"event_coup_18_brumaire_1799"})
    with RelateRepository(path) as repo:
        assert repo.execute("MATCH (:Event)-[r:PRECEDED]->(:Event) RETURN count(r) AS n")[0]["n"]==21

def test_complete_intervention_persists_and_baseline_survives(tmp_path):
    path=tmp_path/"api.rl";app=create_app(path,SEED)
    with TestClient(app) as client:
        assert client.get("/api/v1/health").status_code==200
        graph=client.get("/api/v1/worlds/world_napoleonic_europe/graph").json();assert len(graph["nodes"])==22
        assert client.get("/api/v1/events/event_coup_18_brumaire_1799").status_code==200
        scenario=client.post("/api/v1/scenarios",json={"name":"France without 18 Brumaire","baseline_world_id":"world_napoleonic_europe"}).json();sid=scenario["id"]
        assert client.post(f"/api/v1/scenarios/{sid}/interventions",json={"type":"REMOVE_EVENT","target_id":"event_coup_18_brumaire_1799"}).status_code==201
        result=client.post(f"/api/v1/scenarios/{sid}/simulate").json()
        assert result["graph_diff"]["removed_edges"][0]["change_classification"]=="CUT_THREAD"
        assert any(x["id"]=="event_empire_1804" for x in result["indeterminate_events"])
        assert client.get(f"/api/v1/scenarios/{sid}/diff").status_code==200
        assert client.get(f"/api/v1/scenarios/{sid}/explanations").json()
        assert client.get("/api/v1/events/event_coup_18_brumaire_1799").status_code==200
        with ThreadPoolExecutor(max_workers=8) as pool:
            statuses=list(pool.map(lambda _:client.get("/api/v1/worlds").status_code,range(24)))
        assert statuses==[200]*24
    with TestClient(create_app(path,SEED)) as restarted:
        assert restarted.get(f"/api/v1/scenarios/{sid}").status_code==200
        assert restarted.get(f"/api/v1/scenarios/{sid}/diff").status_code==200

def test_invalid_intervention(tmp_path):
    with TestClient(create_app(tmp_path/"invalid.rl",SEED)) as client:
        sid=client.post("/api/v1/scenarios",json={"name":"bad target","baseline_world_id":"world_napoleonic_europe"}).json()["id"]
        response=client.post(f"/api/v1/scenarios/{sid}/interventions",json={"type":"REMOVE_EVENT","target_id":"missing"})
        assert response.status_code==404

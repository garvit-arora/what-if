import json,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/".vendor"));sys.path.insert(0,str(ROOT/"services"/"api"))
from fastapi.testclient import TestClient
from app.main import create_app
with tempfile.TemporaryDirectory() as folder:
    with TestClient(create_app(Path(folder)/"demo.rl",ROOT/"data"/"seeds"/"napoleonic_history.json")) as client:
        scenario=client.post("/api/v1/scenarios",json={"name":"France without 18 Brumaire","baseline_world_id":"world_napoleonic_europe"}).json()
        client.post(f"/api/v1/scenarios/{scenario['id']}/interventions",json={"type":"REMOVE_EVENT","target_id":"event_coup_18_brumaire_1799"})
        result=client.post(f"/api/v1/scenarios/{scenario['id']}/simulate").json()
        print(json.dumps({"scenario_id":result["scenario_id"],"simulation_id":result["simulation_id"],"affected_events":result["affected_events"],"indeterminate_events":result["indeterminate_events"],"updated_edges":result["graph_diff"]["updated_edges"]},indent=2))

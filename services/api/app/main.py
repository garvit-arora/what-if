from __future__ import annotations
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI,HTTPException,Request
from fastapi.middleware.cors import CORSMiddleware
from app.db.relate_repository import RelateRepository
from app.domains.history.models import InterventionCreate,ScenarioCreate
from app.domains.history.seed import load_dataset,seed_history
from app.domains.history import service
ROOT=Path(__file__).resolve().parents[3]

def create_app(database_path:Path|None=None,seed_path:Path|None=None)->FastAPI:
    db_path=database_path or ROOT/"data"/"thread.rl"; data_path=seed_path or ROOT/"data"/"seeds"/"napoleonic_history.json"
    @asynccontextmanager
    async def lifespan(app:FastAPI):
        app.state.repo=RelateRepository(db_path);app.state.dataset=load_dataset(data_path);seed_history(app.state.repo,app.state.dataset)
        yield
        app.state.repo.close()
    app=FastAPI(title="THREAD API",version="0.2.0",lifespan=lifespan)
    app.add_middleware(CORSMiddleware,allow_origins=["http://localhost:3000","http://127.0.0.1:3000"],allow_methods=["GET","POST"],allow_headers=["Content-Type"])
    def repo(r:Request):return r.app.state.repo
    @app.get("/api/v1/health")
    async def health(r:Request):return {"status":"ok","database":"relate","dataset_version":r.app.state.dataset.dataset_version}
    @app.get("/api/v1/worlds")
    async def worlds(r:Request):return service.worlds(repo(r))
    @app.get("/api/v1/worlds/{world_id}/graph")
    async def world_graph(world_id:str,r:Request):return service.graph(repo(r),world_id)
    @app.get("/api/v1/events/{event_id}")
    async def get_event(event_id:str,r:Request):
        value=service.event(repo(r),event_id)
        if not value:raise HTTPException(404,"event not found")
        return value
    @app.get("/api/v1/events/{event_id}/relationships")
    async def event_rels(event_id:str,r:Request):return service.relationships(repo(r),event_id)
    @app.post("/api/v1/scenarios",status_code=201)
    async def scenario_create(p:ScenarioCreate,r:Request):
        try:return service.create_scenario(repo(r),p)
        except ValueError as e:raise HTTPException(404,str(e)) from e
    @app.get("/api/v1/scenarios/{sid}")
    async def scenario_get(sid:str,r:Request):
        value=service.get_scenario(repo(r),sid)
        if not value:raise HTTPException(404,"scenario not found")
        return value
    @app.post("/api/v1/scenarios/{sid}/interventions",status_code=201)
    async def intervention(sid:str,p:InterventionCreate,r:Request):
        try:return service.add_intervention(repo(r),sid,p)
        except ValueError as e:raise HTTPException(404,str(e)) from e
    @app.post("/api/v1/scenarios/{sid}/simulate")
    async def simulate(sid:str,r:Request):
        try:return service.run_simulation(repo(r),sid,r.app.state.dataset)
        except ValueError as e:raise HTTPException(400,str(e)) from e
    @app.get("/api/v1/scenarios/{sid}/diff")
    async def diff(sid:str,r:Request):
        value=service.latest_result(repo(r),sid)
        if not value:raise HTTPException(404,"simulation not found")
        return value["graph_diff"]
    @app.get("/api/v1/scenarios/{sid}/explanations")
    async def explanations(sid:str,r:Request):
        value=service.latest_result(repo(r),sid)
        if not value:raise HTTPException(404,"simulation not found")
        return value["explanations"]
    return app

app=create_app()

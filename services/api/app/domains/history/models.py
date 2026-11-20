from typing import Literal
from pydantic import BaseModel, Field
class WorldSeed(BaseModel): id:str; name:str; start_year:int; end_year:int
class SourceSeed(BaseModel): id:str; title:str; url:str; kind:str
class NamedSeed(BaseModel): id:str; name:str; wikidata_id:str|None=None
class EventSeed(BaseModel):
    id:str; title:str; date:str; end_date:str|None=None; category:str; wikidata_id:str; description:str
class ParticipantSeed(BaseModel): person_id:str; event_id:str
class MechanismSeed(BaseModel):
    id:str; title:str; mode:Literal["ALL","ANY"]; certainty:Literal["documented","model_assumption","contested"]
    inputs:list[str]=Field(min_length=1); output:str; source_ids:list[str]=Field(min_length=1); reason:str
class HistoricalDataset(BaseModel):
    dataset_version:str; world:WorldSeed; sources:list[SourceSeed]; people:list[NamedSeed]
    institutions:list[NamedSeed]; places:list[NamedSeed]; events:list[EventSeed]
    participants:list[ParticipantSeed]; mechanisms:list[MechanismSeed]
class ScenarioCreate(BaseModel):
    name:str=Field(min_length=1,max_length=120); baseline_world_id:str
class InterventionCreate(BaseModel): type:Literal["REMOVE_EVENT"]; target_id:str

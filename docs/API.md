# HTTP API

Run one worker:

```powershell
$env:PYTHONPATH = ".vendor;services/api"
python -m uvicorn app.main:app --port 8000 --workers 1
```

Routes:

- `GET /api/v1/health`
- `GET /api/v1/worlds`
- `GET /api/v1/worlds/{id}/graph`
- `GET /api/v1/events/{id}`
- `GET /api/v1/events/{id}/relationships`
- `POST /api/v1/scenarios`
- `GET /api/v1/scenarios/{id}`
- `POST /api/v1/scenarios/{id}/interventions`
- `POST /api/v1/scenarios/{id}/simulate`
- `GET /api/v1/scenarios/{id}/diff`
- `GET /api/v1/scenarios/{id}/explanations`

The OpenAPI document is available at `/docs`. No arbitrary Cypher endpoint exists.


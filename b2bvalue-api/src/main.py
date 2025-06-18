from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from src.memory.core import MemoryManager
from src.memory.types import KnowledgeEntity, MemoryTier
from datetime import datetime, timedelta
import uuid
import jwt

SECRET_KEY = "b2bvalue-secret-key"  # Use env var in production
ALGORITHM = "HS256"

app = FastAPI(title="B2BValue API", description="API for B2BValue GTM Platform", version="1.0.0")

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- In-memory user store (demo only) ---
users_db = {"demo-user": {"username": "demo-user", "password": "demo-pass"}}

# --- JWT Auth ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=1))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None or username not in users_db:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return users_db[username]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")

# --- Memory Manager ---
memory_manager = MemoryManager()
memory_manager.initialize()

# --- Pydantic Schemas ---
class KnowledgeEntityIn(BaseModel):
    content: str
    content_type: str
    creator_id: str
    sensitivity: Optional[str] = None

class KnowledgeEntityOut(BaseModel):
    id: str
    content: str
    content_type: str
    creator_id: str
    created_at: datetime
    updated_at: datetime
    sensitivity: Optional[str]
    tier: str

class UserRegister(BaseModel):
    username: str
    password: str

# --- Auth Endpoints ---
@app.post("/api/register")
def register(user: UserRegister):
    if user.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    users_db[user.username] = {"username": user.username, "password": user.password}
    return {"message": "Registered successfully"}

@app.post("/api/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    token = create_access_token({"sub": user["username"]})
    return {"access_token": token, "token_type": "bearer"}

# --- API Endpoints ---
@app.post("/api/start-analysis")
async def start_analysis(entity: KnowledgeEntityIn, user=Depends(get_current_user)):
    entity_obj = KnowledgeEntity(
        id=str(uuid.uuid4()),
        content=entity.content,
        content_type=entity.content_type,
        creator_id=entity.creator_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        sensitivity=entity.sensitivity,
        tier=MemoryTier.SEMANTIC,
    )
    entity_id = await memory_manager.store(entity_obj, user_id=entity.creator_id)
    return {"id": entity_id}

@app.get("/api/analysis-progress/{id}")
async def get_analysis_progress(id: str, user=Depends(get_current_user)):
    # Placeholder: in production, fetch progress from workflow/episodic memory
    return {"id": id, "progress": 100, "status": "complete"}

@app.get("/api/analysis-results/{id}")
async def get_analysis_results(id: str, user=Depends(get_current_user)):
    entity = await memory_manager.retrieve(id, tier=MemoryTier.SEMANTIC)
    if not entity:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return entity.to_dict()

@app.get("/api/business-metrics")
async def get_business_metrics():
    # Public endpoint: return static metrics or query semantic memory
    return {"roi": 0.35, "payback_period": 12, "npv": 120000}

@app.get("/api/industry-templates")
async def get_industry_templates():
    return [
        {"id": "template1", "name": "SaaS ROI Template"},
        {"id": "template2", "name": "Manufacturing Value Prop"},
    ]

@app.get("/api/market-insights")
async def get_market_insights():
    return [
        {"trend": "AI adoption in B2B up 30% YoY"},
        {"trend": "Cloud ROI highest in Financial Services"},
    ]

@app.post("/api/generate-report")
async def generate_report(data: dict, user=Depends(get_current_user)):
    # Placeholder: generate a report (PDF, etc.)
    return {"report_url": "/reports/sample.pdf"}

# --- Memory & Agent Endpoints ---
@app.post("/api/memory/knowledge")
async def store_knowledge(entity: KnowledgeEntityIn, user=Depends(get_current_user)):
    entity_obj = KnowledgeEntity(
        id=str(uuid.uuid4()),
        content=entity.content,
        content_type=entity.content_type,
        creator_id=entity.creator_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        sensitivity=entity.sensitivity,
        tier=MemoryTier.SEMANTIC,
    )
    entity_id = await memory_manager.store(entity_obj, user_id=entity.creator_id)
    return {"id": entity_id}

@app.get("/api/memory/knowledge/{id}", response_model=KnowledgeEntityOut)
async def get_knowledge(id: str, user=Depends(get_current_user)):
    entity = await memory_manager.retrieve(id, tier=MemoryTier.SEMANTIC)
    if not entity:
        raise HTTPException(status_code=404, detail="Not found")
    return KnowledgeEntityOut(**entity.to_dict())

@app.get("/api/memory/knowledge/search")
async def search_knowledge(q: str, limit: int = 10, user=Depends(get_current_user)):
    results = await memory_manager.semantic_search(q, limit=limit)
    return [r.to_dict() for r in results]

# --- Agent Execution Endpoint (stub) ---
@app.post("/api/agent/execute")
async def execute_agent(agent_name: str, input_data: dict, user=Depends(get_current_user)):
    # TODO: Integrate real agent execution logic
    return {"result": f"Agent {agent_name} executed with input: {input_data}"}

# --- Episodic Memory Endpoints (stub) ---
@app.get("/api/episodic/{id}")
async def get_episodic(id: str, user=Depends(get_current_user)):
    # TODO: Integrate with EpisodicMemory
    return {"id": id, "history": []}

@app.get("/api/episodic/search")
async def search_episodic(q: str = "", user=Depends(get_current_user)):
    # TODO: Integrate with EpisodicMemory search
    return []

# --- Deployment Notes ---
# Run with: uvicorn src.main:app --reload
# Use a production server (gunicorn/uvicorn) and secure SECRET_KEY in production

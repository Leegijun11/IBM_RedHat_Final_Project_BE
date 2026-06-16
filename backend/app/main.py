from fastapi import FastAPI
from app.routers import health, items
from app.db.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware




Base.metadata.create_all(bind=engine)

app = FastAPI(title="Backend API")

app.include_router(health.router)
app.include_router(items.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
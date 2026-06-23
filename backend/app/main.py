from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 중복 임포트 정리
from app.db.database import Base, engine
from app.routers import health, items, users


# 서버가 켜질 때 비동기로 DB 테이블을 안전하게 자동 생성하는 수명 주기 설정
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield



app = FastAPI(title="Backend API", lifespan=lifespan)  

# 라우터 등록
app.include_router(health.router)
app.include_router(items.router)
app.include_router(users.router)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
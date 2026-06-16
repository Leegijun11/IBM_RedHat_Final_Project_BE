from fastapi import FastAPI
from app.routers import health, items
from app.db.database import engine, Base

# 앱 구동 시 테이블 자동 생성 (Alembic 도입 전 간단한 확인용)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Backend API")

# 라우터 등록 (prefix는 각 라우터 파일 내부에 정의해 두었습니다)
app.include_router(health.router)
app.include_router(items.router)
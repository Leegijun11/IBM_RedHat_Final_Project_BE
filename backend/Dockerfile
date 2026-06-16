FROM python:3.11-slim

WORKDIR /workspace

# 1. requirements.txt 파일을 컨테이너 내부로 먼저 복사
COPY requirements.txt .

# 2. 복사한 파일을 기반으로 파이썬 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# 3. 백엔드 소스 코드를 컨테이너 내부로 복사
COPY ./app /workspace/app

# 4. 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
# scheduler.py (APScheduler 예시)
# AWS EventBridge 로 대체 가능
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import date
from daily_agent import daily_app
from db import get_today_images, get_today_diaries

def run_daily_job():
    today = date.today().isoformat()
    images = get_today_images(today)   # DB에서 오늘 업로드된 이미지 조회
    diaries = get_today_diaries(today) # DB에서 오늘 작성된 일기 조회

    daily_app.invoke({
        "date": today,
        "image_paths": [i["path"] for i in images],
        "image_names": [i["name"] for i in images],
        "user_diary_texts": [d["text"] for d in diaries],
    })

scheduler = BlockingScheduler()
scheduler.add_job(run_daily_job, "cron", hour=23, minute=0)  # 매일 23:00 실행
scheduler.start()
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db, SessionLocal
from datetime import datetime
import uuid
import os
import asyncio

from app.ai.predict import load_inference_model, predict_image

from app.db.scheme.babyimages import BabyImage_Create, BabyImage_Update, BabyImage_Read, BabyImage_Multi_del
from app.services.babyimages import BabyImage_Service

AI_MODEL = load_inference_model()

router=APIRouter(prefix='/babyimages', tags=['BabyImage'])


def router_babyimages_ai_update_db(i_id: int, imagepath: str):
    ai_result = predict_image(AI_MODEL, imagepath)
    
    with SessionLocal() as db:
        try:
            update_data = BabyImage_Update(i_label=ai_result)
            
            asyncio.run(
                BabyImage_Service.services_babyimages_update(
                    db=db, 
                    i_id=i_id, 
                    babyimage=update_data
                )
            )
            print(f"[AI 완료] 이미지 {i_id}번의 라벨을 '{ai_result}'로 업데이트했습니다.")
        except Exception as e:
            db.rollback()
            print(f"[DB 업데이트 실패] {e}")



async def run_ai_and_update_db(i_id: int, imagepath: str):
    try:
        await run_in_threadpool(router_babyimages_ai_update_db, i_id, imagepath)
    except Exception as e:
        print(f"[AI 백그라운드 오류 발생] {e}")



# POST 이미지 등록
@router.post('/create', response_model=BabyImage_Read)
async def router_babyimages_create(b_id: int,
                                   file: UploadFile = File(...),
                                   background_tasks: BackgroundTasks = Depends(),
                                   db: AsyncSession = Depends(get_db)):
    
    origin = os.path.splitext(file.filename)[1]
    save = f"{uuid.uuid4()}{origin}"
    
    today_str = datetime.now().strftime("%Y%m%d")

    imagefolder=f"../images/{b_id}/{today_str}"
    imagepath=f"{imagefolder}/{save}"
    
    os.makedirs(imagefolder, exist_ok=True)

    contents = await file.read()
    with open(imagepath, "wb") as f:
        f.write(contents)


    data = BabyImage_Create(i_save=save,
                            i_origin=file.filename,
                            i_label="분석 중...",
                            b_id=b_id,
                            i_image=imagepath)
    
    image_data = await BabyImage_Service.services_babyimages_create(db, data)

    background_tasks.add_task(
        run_ai_and_update_db, 
        i_id=image_data.i_id,  
        imagepath=imagepath
    )

    return image_data


# GET 이미지 목록
@router.get('/list', response_model=list[BabyImage_Read])
async def router_babyimages_list(b_id:int, 
                                 i_date:datetime, 
                                 db: AsyncSession=Depends(get_db)):
    return await BabyImage_Service.services_babyimages_list(db, b_id, i_date)


# PUT 이미지 수정
@router.put("/edit", response_model=BabyImage_Read)
async def router_user_update_u_id(update: BabyImage_Update,
                                  i_id:int,
                                  db: AsyncSession = Depends(get_db)):
    return await BabyImage_Service.services_babyimages_update(db, i_id, update)


# DELETE 이미지 삭제
@router.delete("/del")
async def router_babyimages_del(i_id:int,
                                db: AsyncSession = Depends(get_db)):
    return await BabyImage_Service.services_babyimages_del(db, i_id)


# DELETE 다중 이미지 삭제
@router.delete("/multi_del")
async def router_babyimages_multi_del(request: BabyImage_Multi_del,
                                      db: AsyncSession = Depends(get_db)):
    return await BabyImage_Service.services_babyimages_multi_del(db, request.i_ids)
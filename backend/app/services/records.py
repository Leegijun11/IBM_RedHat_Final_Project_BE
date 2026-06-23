from sqlalchemy.ext.asyncio import AsyncSession
from app.db.scheme import Record_Create, Record_Update, Record_Read
from app.db.crud import Record_Crud, Baby_Crud
from datetime import datetime
from fastapi import HTTPException

class RecordService:

    # 1. 성장기록 등록
    @staticmethod
    async def service_records_create(db:AsyncSession, record:Record_Create):
        if record.r_height <= 0 or record.r_weight <= 0:
            raise  HTTPException(status_code=400, detail="성장기록 정보 등록에 실패했습니다.")
        try:
            db_data=await Record_Crud.crud_records_create(db=db, record=record)
            return db_data
        except Exception as e:
            raise HTTPException(status_code=400, detail="성장기록 정보 등록에 실패했습니다.")
    
    # 2. 성장기록 조회
    @staticmethod
    async def service_records_list(db:AsyncSession, b_id:int, start_date:datetime, end_date:datetime):
        try:
            exist_baby=await Baby_Crud.crud_babies_detail(db=db, b_id=b_id)
            if exist_baby is None:
                raise HTTPException(status_code=400, detail="성장기록을 불러오는데 실패했습니다.")
            db_data=await Record_Crud.crud_records_details(db=db, b_id=b_id, start_date=start_date, end_date=end_date)
            return db_data
        except Exception as e:
            raise HTTPException(status_code=400, detail="성장기록을 불러오는데 실패했습니다.")
        
    # 3. 성장기록 수정
    @staticmethod
    async def service_records_update(db:AsyncSession, r_id:int):
        try:
            exist_record=await Record_Crud.crud_records_update(db=db, r_id=r_id, record=Record_Update())
            if exist_record is None:
                raise HTTPException(status_code=400, detail="성장기록 수정에 실패하였습니다.")
            
            baby_info=await Baby_Crud.crud_babies_detail(db=db, b_id=exist_record.b_id)
            if baby_info is None:
                raise HTTPException(status_code=400, detail="성장기록 수정에 실패하였습니다.")
            
            record_update_data=Record_Update(
                r_weight=baby_info.b_weight,
                r_height=baby_info.b_height
            )

            if record_update_data.r_weight <= 0 or record_update_data.r_height <= 0:
                raise HTTPException(status_code=400, detail="키와 몸무게는 0보다 커야 합니다.")
        
            db_data=await Record_Crud.crud_records_update(db=db, r_id=r_id, record=record_update_data)
            return db_data
        except HTTPException as ee:
            raise ee
        except Exception as e:
            raise HTTPException(status_code=400, detail="성장기록 수정에 실패하였습니다.")
            
    # 4. 성장기록 삭제
    @staticmethod
    async def service_records_delete(db:AsyncSession, r_id:int):
        try:
            db_data=await Record_Crud.crud_records_del(db=db, r_id=r_id)
            if db_data is None:
                raise HTTPException(status_code=400, detail="성장기록 삭제에 실패하였습니다.")
            return db_data
        except Exception as e:
            raise HTTPException(status_code=400, detail="성장기록 삭제에 실패하였습니다.")
#service_alarm_create 알람 추가
#service_alarm_list 내 알람 목록
#service_alarm_delete 알람 삭제


from pydantic import BaseModel, Field, EmailStr, ConfigDict
from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional

from app.db.models.users import User
from app.db.crud.users import User_Crud
from app.db.models.care_group import Care_Group
from app.db.crud.parents import Parent_Crud
from app.db.models.parents import Parent

from app.db.models.alarms import Alarm
from app.db.scheme.alarms import Alarm_Base, Alarm_Create, Alarm_Read
from app.db.crud.alarms import Alarm_Crud


class Alarm_Service:

    #알람 생성
    @staticmethod
    async def service_alarm_create(db: AsyncSession, send_id: int, receive_account: str):
        try:
            # 계정으로 받는 사람 찾기
            receiver = await User_Crud.crud_users_get_by_account(db, receive_account)
            if not receiver:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="존재하지 않는 계정입니다")

            receive_id = receiver.u_id

            if receive_id == send_id:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="자기 자신은 초대할 수 없습니다")

            # 받는 사람이 이미 다른 그룹에 속해 있는지 확인
            receiver_parent = select(Parent).where(Parent.u_id == receive_id)
            result_receiver = await db.execute(receiver_parent)
            receiver_group = result_receiver.scalar_one_or_none()

            if receiver_group and receiver_group.g_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="이미 다른 공동 양육 그룹에 속해 있는 사용자입니다"
                )

            # 보내는 사람의 그룹 확인
            sender = select(Parent).where(Parent.u_id == send_id)
            result_sender = await db.execute(sender)
            group_sender = result_sender.scalar_one_or_none()

            if not group_sender or group_sender.g_id is None:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="그룹에 없는 유저")

            alarm_data = Alarm_Create(
                send_id=send_id,
                receive_id=receive_id,
                g_id=group_sender.g_id)

            db_data = await Alarm_Crud.crud_alarms_create(db, alarm=alarm_data)
            await db.commit()

            return db_data

        except HTTPException:
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"알람 생성 실패: {e}"
            )


    #내 알람 목록
    @staticmethod
    async def service_alarm_list(db:AsyncSession, receive_id:int):
        try:
            alarms=await Alarm_Crud.crud_alarms_list(db, receive_id=receive_id)
            
            return alarms
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"알람 조회 실패 :{e}"
            )
        
    #알람 삭제
    @staticmethod
    async def service_alarm_delete(db:AsyncSession, a_id:int):
        try:
            delete_alarm=await Alarm_Crud.crud_alarms_del(db, a_id=a_id)
            
            if not delete_alarm:
                raise HTTPException(status.HTTP_404_NOT_FOUND, detail="삭제 할 알람이 없음")
            
            await db.commit()
            return {"msg":"알람이 삭제되었습니다"}
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"알람 삭제 실패 :{e}"
            )
        
    # 알람 전체 삭제
    @staticmethod
    async def service_alarm_all_del(db:AsyncSession, receive_id:int):
        try:
            db_data=await Alarm_Crud.crud_alarms_all_del(db, receive_id)

            if not db_data:
                return {"msg":"삭제할 알람이 없습니다."}
            
            await db.commit()
            return {"msg":f"전체 알람이 {db_data}개 삭제되었습니다."}
        
        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"알람 전체 삭제 실패 : {e}")
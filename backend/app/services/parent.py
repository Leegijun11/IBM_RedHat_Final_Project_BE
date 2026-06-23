#service_parents_create 양육자 등록
#service_parents_list 양육자 목록
#service_parents_delete 양육자 삭제




from pydantic import BaseModel, Field, EmailStr, ConfigDict
from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.crud.parents import Parent_Crud
from app.db.scheme.parents import Parent_Create,Parent_Base,Parent_Update,Parent_Read


# class Parent_Service:

#     #양육자 등록
#     @staticmethod
#     async def service_parents_create(db:AsyncSession, u_id:int, parent_data:Parent_Create):
#         try:
#             group=await Parent_Crud.crud_parents_create(db, )
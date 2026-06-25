#service_stories_create : 디지털북 생성
#service_stories_list : b_id별 디지털북 목록
#service_stories_detail : 디지털북 상세
#service_stories_delete : 디지털북 삭제

from fastapi import status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.scheme.stories import Story_Create
from app.db.crud.stories import Story_Crud
from app.ai.llm import generate_story_content


class Story_Service:

    # 디지털북 생성
    @staticmethod
    async def service_stories_create(db: AsyncSession, story: Story_Create):
        try:
            diaries = await Story_Crud.crud_stories_get_diaries(db, story.b_id, story.start_date, story.end_date)

            if not diaries:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="해당 기간의 일기 정보가 없습니다"
                )

            llm_result = await generate_story_content(diaries)

            story_data = {
                "s_name": llm_result["s_name"],
                "s_content": llm_result["s_content"],
                "b_id": story.b_id,
            }

            new_story = await Story_Crud.crud_stories_create(db, story_data)

            await db.commit()
            await db.refresh(new_story)

            return new_story

        except HTTPException:
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"디지털북 생성 실패: {e}"
            )

    # b_id별 디지털북 목록
    @staticmethod
    async def service_stories_list(db: AsyncSession, b_id: int):
        try:
            stories = await Story_Crud.crud_stories_list(db, b_id)

            if not stories:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="책 목록을 불러오는데 실패했습니다"
                )

            return stories

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"책 목록을 불러오는데 실패했습니다: {e}"
            )

    # 디지털북 상세
    @staticmethod
    async def service_stories_detail(db: AsyncSession, s_id: int):
        try:
            story = await Story_Crud.crud_stories_detail(db, s_id)

            if not story:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="책을 불러오는데 실패했습니다"
                )

            return story

        except HTTPException:
            raise

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"책을 불러오는데 실패했습니다: {e}"
            )

    # 디지털북 삭제
    @staticmethod
    async def service_stories_delete(db: AsyncSession, s_id: int):
        try:
            deleted_story = await Story_Crud.crud_stories_del(db, s_id)

            if not deleted_story:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="책 삭제에 실패했습니다"
                )

            await db.commit()

            return {"msg": "책을 삭제하였습니다."}

        except HTTPException:
            raise

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"책 삭제에 실패했습니다: {e}"
            )
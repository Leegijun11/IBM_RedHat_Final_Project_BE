import asyncio
from fastapi import HTTPException
from app.ai.llm_config import get_watsonx
from app.ai.llm_main import LLMDiary


async def ai_llm_story_run(input: str):
    try:
        config = get_watsonx()
        pipeline = LLMDiary()

        final_story = await pipeline.ai_llm_story_model_run(input, config)

        return {"input":input,
                "s_content": final_story}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"디지털북 파이프라인 가동 실패 원인: {str(e)}")


if __name__ == "__main__":
    ai = asyncio.run(ai_llm_story_run(
        """

이유 없이 자꾸 깨서 서럽게 우는 걸 보니 이앓이가 시작된 것 같음. 낮에도 침을 엄청 흘리고 손에 잡히는 건 다 치발기처럼 뜯어댐. 안쓰러워서 하루 종일 안아줬더니 어깨랑 허리가 끊어질 것 같음. 저녁에 젖병 거부 살짝 있어서 걱정했는데 겨우 달래서 먹임. 밤에는 아프지 말고 푹 자 주라.


        """
    ))
    print("input\n", ai["input"].strip())
    print("\n\n디지털북\n", ai["s_content"].strip())

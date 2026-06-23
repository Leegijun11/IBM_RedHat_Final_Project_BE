from db import get_daily_diaries_by_range, save_digital_book
from itertools import groupby
from typing import TypedDict, List
from model import llm
import re


class BookAgent(TypedDict):
    start_date: str
    end_date: str
    daily_diaries: List[dict]   # [{"date": ..., "blocks": [...], "labels": [...]}]
    chapters: List[dict]        # [{"month": ..., "blocks": [...]}]
    book_title: str
    full_book_blocks: List[dict]


def fetch_daily_diaries(state: BookAgent):
    diaries = get_daily_diaries_by_range(state["start_date"], state["end_date"])
    return {"daily_diaries": diaries}


def generate_chapters(state: BookAgent):
    diaries = sorted(state["daily_diaries"], key=lambda d: d["date"])

    def get_month(d):
        return d["date"][:7]

    chapters = []
    for month, group in groupby(diaries, key=get_month):
        entries = list(group)

        # 텍스트만 추출해서 LLM에 전달 (이미지 블록은 따로 보관)
        day_texts = []
        for e in entries:
            text_only = " ".join(b["content"] for b in e["blocks"] if b["type"] == "text")
            day_texts.append(f"[{e['date']}] {text_only}")

        combined = "\n\n".join(day_texts)

        prompt = f"""
다음은 {month}월 한 달 동안 매일 쓰여진 아이의 하루 일기들입니다.
이걸 이어붙여서 동화책의 한 챕터로 재구성해줘.

{combined}

조건:
- 하루 일기들을 자연스럽게 이어지는 하나의 이야기로 다듬기
- 동화처럼 따뜻한 어투 유지
- 챕터 제목도 함께 지어줘 (첫 줄에 "제목: ..." 형식으로)
"""
        response = llm.invoke(prompt)
        chapter_text = response.content

        # 제목 추출
        title_match = re.match(r"제목:\s*(.+)", chapter_text)
        title = title_match.group(1).strip() if title_match else f"{month}월 이야기"
        body = re.sub(r"제목:\s*.+\n?", "", chapter_text, count=1).strip()

        # 이 달의 이미지들을 날짜순으로 전부 모음 (각 day의 image 블록만 추출)
        chapter_images = []
        for e in entries:
            for b in e["blocks"]:
                if b["type"] == "image":
                    chapter_images.append(b["path"])

        chapters.append({
            "month": month,
            "title": title,
            "text": body,
            "images": chapter_images
        })

    return {"chapters": chapters}


def assemble_book(state: BookAgent):
    """챕터를 순서대로 블록 리스트로 합치기 (텍스트 한 덩어리 + 그 달 사진들 묶음)"""
    full_blocks = []
    for c in state["chapters"]:
        full_blocks.append({"type": "chapter_title", "content": c["title"]})
        full_blocks.append({"type": "text", "content": c["text"]})
        for img_path in c["images"]:
            full_blocks.append({"type": "image", "path": img_path})

    return {
        "full_book_blocks": full_blocks,
        "book_title": f"{state['start_date']} ~ {state['end_date']} 성장일기"
    }


def save_book(state: BookAgent):
    save_digital_book(
        title=state["book_title"],
        start_date=state["start_date"],
        end_date=state["end_date"],
        blocks=state["full_book_blocks"]
    )
    return {}


book_graph = StateGraph(BookAgent)
book_graph.add_node("fetch_daily_diaries", fetch_daily_diaries)
book_graph.add_node("generate_chapters", generate_chapters)
book_graph.add_node("assemble_book", assemble_book)
book_graph.add_node("save_book", save_book)

book_graph.set_entry_point("fetch_daily_diaries")
book_graph.add_edge("fetch_daily_diaries", "generate_chapters")
book_graph.add_edge("generate_chapters", "assemble_book")
book_graph.add_edge("assemble_book", "save_book")
book_graph.add_edge("save_book", END)

book_app = book_graph.compile()


#[오늘 사진 n장 + 일기 m개]
#   ↓ classify_images (라벨만 추출, 사진 내용 분석 X)
#   ↓ generate_daily_diary (LLM: 라벨+일기 텍스트만 보고 글 작성 + IMG 위치 표시)
#   ↓ assemble_daily_blocks (placeholder → 실제 이미지 경로로 치환)
#   ↓ save: daily_summary.blocks = [text, image, text, image, ...]

#[기간 지정 → 디지털북 생성]
#   ↓ fetch_daily_diaries (blocks 그대로 가져옴)
#  ↓ generate_chapters (텍스트만 LLM에 넘겨서 챕터로 재구성, 이미지는 따로 보관)
#   ↓ assemble_book (챕터 텍스트 + 그 기간 사진들을 블록으로 합침)
#   ↓ save: digital_book.blocks = [chapter_title, text, image, image, ...]
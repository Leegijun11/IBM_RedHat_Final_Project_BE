from classifier import predict_batch
from model import llm
from db import save_image_record, save_daily_diary_record
from langgraph.graph import StateGraph, END
from typing import TypedDict, List
import re


class DailyAgent(TypedDict):
    date: str
    image_paths: List[str]
    image_names: List[str]
    user_diary_texts: List[str]
    labels: List[str]
    confidences: List[float]
    raw_diary_with_placeholders: str   # LLM 원본 출력 (placeholder 포함)
    daily_diary_blocks: List[dict]      # 최종 결과: 텍스트/이미지 블록 순서대로 정리


def classify_images(state: DailyAgent):
    results = predict_batch(state["image_paths"], batch_size=32)
    label_map = {path: (label, conf) for path, label, conf in results}

    labels = [label_map[p][0] for p in state["image_paths"]]
    confidences = [label_map[p][1] for p in state["image_paths"]]

    return {"labels": labels, "confidences": confidences}


def save_images(state: DailyAgent):
    for name, path, label in zip(state["image_names"], state["image_paths"], state["labels"]):
        save_image_record(
            image_name=name,
            image_path=path,
            label=label,
            date=state["date"]
        )
    return {}


def generate_daily_diary(state: DailyAgent):
    labels = state["labels"]
    user_texts = state["user_diary_texts"]

    # 사진 정보를 [IMG_1: 라벨] 형식으로 LLM에 전달 (사진 자체는 안 보여줌, 라벨 텍스트만)
    if labels:
        image_info = "\n".join(
            f"- IMG_{i+1}: {label}" for i, label in enumerate(labels)
        )
    else:
        image_info = "오늘은 사진이 없었어요"

    diary_summary = "\n".join(f"- {t}" for t in user_texts) if user_texts else "기록된 일기가 없어요"

    prompt = f"""
다음은 {state['date']}에 부모가 남긴 아이의 사진 활동 기록과 일기 메모입니다.
이 정보를 종합해서, 아이의 하루를 동화처럼 따뜻하게 담은 짧은 '하루 일기' 한 편을 작성해줘.

[오늘 찍은 사진들의 활동 라벨]
{image_info}

[부모가 남긴 메모/일기]
{diary_summary}

작성 조건:
- 1~2문단 정도의 짧은 분량
- 아이의 하루를 다정하고 사랑스럽게 묘사
- 각 사진(IMG_1, IMG_2, ...)이 묘사하는 활동과 가장 잘 어울리는 문장 바로 뒤에 [IMG_1], [IMG_2] 같은 표시를 본문에 직접 삽입해줘
  (예: "공원에서 신나게 뛰어놀았다. [IMG_1] 집에 와서는 낮잠을 잤다. [IMG_2]")
- 사진의 실제 모습은 모르니, 라벨(활동명)만 보고 자연스러운 위치에 배치하면 돼
- IMG 표시 외에는 다른 특수 기호나 마크다운을 쓰지 마
"""
    response = llm.invoke(prompt)
    return {"raw_diary_with_placeholders": response.content}


def assemble_daily_blocks(state: DailyAgent):
    """
    LLM이 만든 [IMG_n] placeholder를 실제 이미지 경로로 치환하고,
    텍스트/이미지를 순서대로 나열한 블록 리스트로 정리
    """
    text = state["raw_diary_with_placeholders"]
    image_paths = state["image_paths"]

    # [IMG_1], [IMG_2] ... 패턴 기준으로 텍스트 분리
    pattern = re.compile(r"\[IMG_(\d+)\]")
    blocks = []
    last_end = 0

    for match in pattern.finditer(text):
        idx = int(match.group(1)) - 1
        # placeholder 앞까지의 텍스트
        chunk = text[last_end:match.start()].strip()
        if chunk:
            blocks.append({"type": "text", "content": chunk})

        # 이미지 블록 (인덱스 범위 체크)
        if 0 <= idx < len(image_paths):
            blocks.append({"type": "image", "path": image_paths[idx]})

        last_end = match.end()

    # 마지막 남은 텍스트
    remaining = text[last_end:].strip()
    if remaining:
        blocks.append({"type": "text", "content": remaining})

    # LLM이 일부 IMG를 빼먹었을 경우, 안 쓰인 이미지는 맨 끝에 붙여서 누락 방지
    used_indices = {int(m.group(1)) - 1 for m in pattern.finditer(text)}
    for i, path in enumerate(image_paths):
        if i not in used_indices:
            blocks.append({"type": "image", "path": path})

    return {"daily_diary_blocks": blocks}


def save_daily_diary(state: DailyAgent):
    save_daily_diary_record(
        date=state["date"],
        blocks=state["daily_diary_blocks"],   # [{"type": "text", "content": ...}, {"type": "image", "path": ...}, ...]
        labels=state["labels"]
    )
    return {}


daily_graph = StateGraph(DailyAgent)
daily_graph.add_node("classify_images", classify_images)
daily_graph.add_node("save_images", save_images)
daily_graph.add_node("generate_daily_diary", generate_daily_diary)
daily_graph.add_node("assemble_daily_blocks", assemble_daily_blocks)
daily_graph.add_node("save_daily_diary", save_daily_diary)

daily_graph.set_entry_point("classify_images")
daily_graph.add_edge("classify_images", "save_images")
daily_graph.add_edge("save_images", "generate_daily_diary")
daily_graph.add_edge("generate_daily_diary", "assemble_daily_blocks")
daily_graph.add_edge("assemble_daily_blocks", "save_daily_diary")
daily_graph.add_edge("save_daily_diary", END)

daily_app = daily_graph.compile()
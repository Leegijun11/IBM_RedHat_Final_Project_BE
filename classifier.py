# classifier.py
import os
import torch
import torch.nn as nn
import torchvision.transforms.v2 as transforms
from PIL import Image
from torchvision.models import resnet50
from typing import List, Tuple

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(CURRENT_DIR, "baby_resnet50_all_layers.pth")

CLASS_NAMES = [
    "01 lying (눕기)",
    "02 tummyTime (터미타임)",
    "03 rolling (뒤집기)",
    "04 sitting (앉기)",
    "05 crawling (기기)",
    "06 standing (잡고서기)",
    "07 walking (독립보행달리기)",
    "08 climbing (기어오르기)",
    "09 handManipulation (손동작)",
    "10 playActivity (오감인지 놀이)",
    "11 reading (독서)",
    "12 interacting (상호작용,사회적관계)",
    "13 diet (구강 섭취식사)",
    "14 hygiene (위생케어)",
    "15 sleeping (수면하품)"
]

test_transforms = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToImage(),
    transforms.ToDtype(torch.float32, scale=True),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])


def load_inference_model():
    model = resnet50(weights=None)
    num_features = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(0.4),
        nn.Linear(num_features, len(CLASS_NAMES))
    )
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"가중치 파일을 찾을 수 없습니다: {MODEL_PATH}")
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True))
    model = model.to(DEVICE)
    model.eval()
    return model


_model = load_inference_model()


def predict_batch(img_paths: List[str], batch_size: int = 16) -> List[Tuple[str, float]]:
    """
    여러 이미지 경로를 받아 (라벨, 확신도) 리스트를 반환.
    batch_size 단위로 끊어서 GPU에 올림 (한꺼번에 1년치 다 올리면 메모리 터짐 방지)
    """
    results = []

    for i in range(0, len(img_paths), batch_size):
        batch_paths = img_paths[i:i + batch_size]

        # 이미지 로드 + 전처리 → 배치 텐서로 쌓기
        tensors = []
        valid_paths = []
        for path in batch_paths:
            try:
                image = Image.open(path).convert("RGB")
                tensors.append(test_transforms(image))
                valid_paths.append(path)
            except Exception as e:
                print(f"이미지 로드 실패: {path} ({e})")
                results.append((path, "ERROR", 0.0))

        if not tensors:
            continue

        batch_tensor = torch.stack(tensors).to(DEVICE)  # (N, C, H, W)

        with torch.no_grad():
            outputs = _model(batch_tensor)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            confidences, predicted_idxs = torch.max(probabilities, dim=1)

        for path, idx, conf in zip(valid_paths, predicted_idxs, confidences):
            label = CLASS_NAMES[idx.item()]
            results.append((path, label, conf.item()))

    return results
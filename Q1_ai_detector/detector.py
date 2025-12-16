\
from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import Dict, Tuple, Optional, List

import numpy as np

# Optional heavy dependency: transformers/torch. We import lazily to speed up Streamlit cold start.
_PIPE = None


@dataclass
class DetectionResult:
    ai_prob: float       # 0~1
    human_prob: float    # 0~1
    label: str           # "AI" or "Human" (best guess)
    model_label: str     # raw model label
    model_score: float   # raw model score for model_label
    stats: Dict[str, float]


def _basic_stats(text: str) -> Dict[str, float]:
    text = text.strip()
    if not text:
        return {
            "chars": 0,
            "words": 0,
            "sentences": 0,
            "avg_sentence_len_words": 0.0,
            "punct_ratio": 0.0,
            "repeat_ratio": 0.0,
        }

    # Rough sentence split for Chinese/English mixed text
    sents = re.split(r"[。！？!?]\s*|\n+", text)
    sents = [s for s in sents if s.strip()]
    words = re.findall(r"\w+|[\u4e00-\u9fff]", text)  # crude: CJK char as token
    punct = re.findall(r"[，,。.!?；;：:、\-—（）()《》「」『』\"'…]", text)

    # repetition ratio: top-1 token frequency
    if words:
        vals, counts = np.unique(words, return_counts=True)
        repeat_ratio = float(counts.max() / max(1, len(words)))
    else:
        repeat_ratio = 0.0

    avg_len = float(len(words) / max(1, len(sents)))

    return {
        "chars": float(len(text)),
        "words": float(len(words)),
        "sentences": float(len(sents)),
        "avg_sentence_len_words": avg_len,
        "punct_ratio": float(len(punct) / max(1, len(text))),
        "repeat_ratio": repeat_ratio,
    }


def _load_pipeline(model_name: str = "openai-community/roberta-base-openai-detector"):
    global _PIPE
    if _PIPE is not None:
        return _PIPE

    from transformers import pipeline  # lazy import

    # Use CPU by default on Streamlit Cloud
    _PIPE = pipeline("text-classification", model=model_name, truncation=True)
    return _PIPE


def detect_ai_vs_human(
    text: str,
    model_name: str = "openai-community/roberta-base-openai-detector",
    extra_heuristics: bool = True,
) -> DetectionResult:
    """
    Returns AI/Human probabilities.

    Notes:
    - The HuggingFace detector model is historically trained for GPT-2-like outputs.
      It can still be used as a baseline detector, but accuracy is NOT guaranteed.
    - We optionally apply light heuristic smoothing for very short text.
    """
    stats = _basic_stats(text)

    if not text or stats["words"] < 5:
        # too short: return uncertain
        return DetectionResult(
            ai_prob=0.5,
            human_prob=0.5,
            label="Uncertain",
            model_label="N/A",
            model_score=0.0,
            stats=stats,
        )

    pipe = _load_pipeline(model_name=model_name)

    # Get both-class scores if supported; fall back to top-1
    out = pipe(text)
    # Some pipelines return list[dict]; some return list[list[dict]]
    if isinstance(out, list) and out and isinstance(out[0], list):
        out = out[0]

    scores = {d["label"]: float(d["score"]) for d in out} if isinstance(out, list) else {out["label"]: float(out["score"])}

    # Common labels for this detector: "Real" and "Fake"
    human = scores.get("Real")
    ai = scores.get("Fake")

    if human is None or ai is None:
        # If only top label was returned, approximate
        top_label = out[0]["label"] if isinstance(out, list) else out["label"]
        top_score = float(out[0]["score"] if isinstance(out, list) else out["score"])
        if top_label.lower() in ("real", "human"):
            human, ai = top_score, 1.0 - top_score
        else:
            ai, human = top_score, 1.0 - top_score
    
        # --- Feature-based scoring (simple heuristics) ---
    # 目標：對「結構化、規律、條列」這類更像 AI 的文本給較高 ai_feature 分數
    w = stats["words"]
    avg_len = stats["avg_sentence_len_words"]
    punct_ratio = stats["punct_ratio"]
    repeat_ratio = stats["repeat_ratio"]

    # 條列/格式化線索：常見符號（- • 1) 2) ① 等）
    bullet_hits = len(re.findall(r"(^|\n)\s*([-•*]|(\d+[\.\)])|(①|②|③|④|⑤|⑥|⑦|⑧|⑨))\s+", text))
    bullet_score = min(1.0, bullet_hits / 5.0)

    # 句長一致性：越規律越可能像模型生成（非常粗略）
    # 我們用 avg_sentence_len_words 讓極端短句/極端長句降低 AI 分數，鼓勵中等規律
    len_score = 1.0 - min(1.0, abs(avg_len - 18.0) / 18.0)  # 18 words as a soft center

    # 標點比例：太低像口語、太高像堆砌；取中等偏高作為 AI 偏好（粗略）
    punct_score = max(0.0, min(1.0, (punct_ratio - 0.01) / 0.06))  # 0.01~0.07 映射到 0~1

    # 重複率：AI 有時會重複模板；但過高也可能是人類口癖 → 只給輕微加分
    repeat_score = max(0.0, min(1.0, (repeat_ratio - 0.06) / 0.14))  # 0.06~0.20

    # 短文本懲罰：太短一律不自信
    short_penalty = 0.0 if w >= 60 else (1.0 - w / 60.0)  # 0~1

    ai_feature = (
        0.35 * bullet_score +
        0.25 * len_score +
        0.25 * punct_score +
        0.15 * repeat_score
    )
    # 讓短文本往 0.5 拉回（降低武斷）
    ai_feature = ai_feature * (1.0 - 0.6 * short_penalty) + 0.5 * (0.6 * short_penalty)

    # --- Combine model + feature (ensemble) ---
    # 權重可在報告說明：模型為主、特徵輔助
    alpha = 0.75  # model weight
    ai = alpha * ai + (1 - alpha) * ai_feature
    human = 1.0 - ai


    # Optional heuristics: soften extremes for shorter text
    if extra_heuristics:
        w = stats["words"]
        # for 5~80 words, shrink confidence a bit
        shrink = 0.25 * (1.0 - min(1.0, (w - 5) / 75.0))
        ai = ai * (1 - shrink) + 0.5 * shrink
        human = 1.0 - ai

    label = "AI" if ai >= human else "Human"
    # raw best label from model
    if isinstance(out, list):
        best = max(out, key=lambda d: d["score"])
        model_label = str(best["label"])
        model_score = float(best["score"])
    else:
        model_label = str(out["label"])
        model_score = float(out["score"])

    return DetectionResult(
        ai_prob=float(ai),
        human_prob=float(human),
        label=label,
        model_label=model_label,
        model_score=model_score,
        stats=stats,
    )

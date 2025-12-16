\
import streamlit as st
from detector import detect_ai_vs_human

st.set_page_config(page_title="Q1 — AI / Human 文章偵測器", layout="centered")

st.title("Q1 — AI / Human 文章偵測器（MVP）")
st.caption("輸入一段文本 → 即時輸出 AI% / Human%（示範版，請勿作高風險決策用途）")

with st.expander("使用說明 / 限制（請務必放進報告）", expanded=False):
    st.write(
        "- 本工具使用公開的 Transformer 偵測模型作為 baseline，並加上少量統計特徵做穩定化。\n"
        "- 這類偵測器對於：短文本、改寫、混合人機、不同語言/領域文本，準確率不保證。\n"
        "- 建議在報告中描述：你如何測試、遇到的失敗案例、以及你做了哪些 UI/工程上的改善。"
    )

default_text = "請貼上你要判斷的文本（建議 > 50 字）"
text = st.text_area("輸入文本", value=default_text, height=220)

col_a, col_b = st.columns(2)
with col_a:
    use_heuristics = st.checkbox("啟用短文本穩定化（heuristics）", value=True)
with col_b:
    st.write("")

if st.button("開始判斷", type="primary"):
    with st.spinner("模型推論中…（首次載入可能較久）"):
        res = detect_ai_vs_human(text, extra_heuristics=use_heuristics)
    
    # 依照機率加上解讀（避免硬判）
    ai_pct = res.ai_prob * 100

    if 45 <= ai_pct <= 55:
        interpret = "不確定（介於 45%～55%）"
    elif ai_pct >= 70:
        interpret = "偏 AI（高機率）"
    elif ai_pct <= 30:
        interpret = "偏 Human（高機率）"
    else:
        interpret = "略偏某一方（中等信心）"

    st.info(f"解讀：{interpret}")

    st.subheader("判斷結果")
    c1, c2, c3 = st.columns(3)
    c1.metric("AI %", f"{res.ai_prob*100:.1f}%")
    c2.metric("Human %", f"{res.human_prob*100:.1f}%")
    c3.metric("Best Guess", res.label)

    st.progress(int(res.ai_prob * 100))

    st.divider()
    st.subheader("文字統計（可選加分項）")
    st.json(res.stats)

    st.caption(f"Model raw: {res.model_label} (score={res.model_score:.4f})")

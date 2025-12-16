\
import streamlit as st
from redesign import apply_style

st.set_page_config(page_title="Q3 — PPT 換版型（AI 重新設計）", layout="centered")

st.title("Q3 — PPT 換版型（AI 重新設計）Demo")
st.caption("上傳 PPTX → 產出兩種不同風格的新 PPTX（python-pptx 版型重設）")

uploaded = st.file_uploader("上傳 .pptx", type=["pptx"])
st.write("若你還沒有可用的 PPT，也可以先用 Repo 內的 sample_input.pptx 測試。")

style_a = "dark_neon"
style_b = "clean_minimal"

if uploaded and st.button("產生兩種新風格", type="primary"):
    pptx_bytes = uploaded.read()

    with st.spinner("產生風格 A（Dark/Neon）…"):
        out_a = apply_style(pptx_bytes, style_a)

    with st.spinner("產生風格 B（Clean/Minimal）…"):
        out_b = apply_style(pptx_bytes, style_b)

    st.success("完成！請下載兩份新版 PPTX。")

    st.download_button(
        "下載：風格A_DarkNeon.pptx",
        data=out_a,
        file_name="styleA_dark_neon.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )
    st.download_button(
        "下載：風格B_CleanMinimal.pptx",
        data=out_b,
        file_name="styleB_clean_minimal.pptx",
        mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
    )

with st.expander("報告建議寫法（加分）", expanded=False):
    st.write(
        "- 說明你定義了兩套風格規格（背景、標題/內文顏色、字級、粗體等）\n"
        "- 說明你如何辨識 Title placeholder vs Body placeholder\n"
        "- 描述你遇到的限制：不同模板的 placeholder 結構不一致、字型在雲端環境可能缺字等\n"
    )

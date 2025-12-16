\
import streamlit as st
import requests
import json

st.set_page_config(page_title="Q2 — n8n AI Workflow Demo", layout="centered")

st.title("Q2 — n8n AI Workflow（仿小林 AI）Demo")
st.caption("Streamlit 端作為前台，透過 Webhook 呼叫 n8n workflow。")

with st.expander("先決條件（一定要做）", expanded=True):
    st.write(
        "1. 先在 n8n 匯入 `workflow.json`\n"
        "2. 在 workflow 內把 OpenAI credentials 設定完成（不要把 key 寫進 JSON）\n"
        "3. 取得 Webhook Production URL，貼到下面\n"
    )

webhook_url = st.text_input("n8n Webhook Production URL（POST）", value="", placeholder="https://<your-n8n-domain>/webhook/hw5-ai")

action = st.selectbox("Action", ["summary", "translate", "reply", "notes"], index=0)
target_lang = st.text_input("Target language（action=translate 時使用）", value="zh-TW")

text = st.text_area("Input text", height=220, value="請貼上要處理的文字…")

if st.button("送出到 n8n", type="primary", disabled=(not webhook_url.strip())):
    payload = {"action": action, "text": text, "target_lang": target_lang}
    with st.spinner("呼叫 webhook…"):
        try:
            r = requests.post(webhook_url.strip(), json=payload, timeout=120)
            st.write("HTTP status:", r.status_code)
            if r.headers.get("content-type", "").startswith("application/json"):
                st.json(r.json())
            else:
                st.code(r.text)
        except Exception as e:
            st.error(f"Webhook 呼叫失敗：{e}")

st.divider()
st.subheader("Payload 預覽")
st.code(json.dumps({"action": action, "text": text[:60] + ("..." if len(text) > 60 else ""), "target_lang": target_lang}, ensure_ascii=False, indent=2))

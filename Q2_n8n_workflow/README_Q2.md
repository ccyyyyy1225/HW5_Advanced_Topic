# Q2 — n8n 自動化流程（仿小林 AI）— 使用說明（MVP）

## 你會得到什麼
- `workflow/workflow.json`：可匯入 n8n 的 workflow 模板
- `streamlit_app.py`：可輸入 webhook URL，從 Streamlit 呼叫 n8n workflow

## n8n workflow 功能
Webhook POST 接收：
```json
{
  "action": "summary | translate | reply | notes",
  "text": "要處理的文字",
  "target_lang": "zh-TW | en | ko | ja | ..."
}
```

然後以 HTTP Request 方式呼叫 OpenAI `/v1/responses` 產生結果，再用 Respond to Webhook 回傳 JSON。

## 匯入與設定（重點）
1. 進入 n8n → Workflows → Import from file → 選 `workflow.json`
2. 打開每個 `HTTP Request` 節點，設定 OpenAI API Key（建議用 n8n credentials）
3. Webhook 節點會顯示 Test/Production URL
4. 把 Production URL 貼到 Streamlit 介面中測試

> 若你使用自架 n8n 在 localhost，測試 webhook 可能需要 tunnel 模式（n8n docs 有說明）。


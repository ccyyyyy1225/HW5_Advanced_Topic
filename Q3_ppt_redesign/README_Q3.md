# Q3 — PPT 換版型（AI 重新設計）

本專案使用 python-pptx 實作 PowerPoint 版型自動重設計系統。
使用者上傳原始簡報後，系統將自動輸出兩種不同設計風格之 PPT 檔案。

---

## 功能說明
- 上傳原始 `.pptx`
- 自動解析投影片內容
- 輸出兩種不同設計風格：
  - Style A：Dark / Neon
  - Style B：Clean / Minimal
- 下載重新設計後的簡報檔案

---

## 設計風格
### Style A — Dark / Neon
- 黑色背景
- 亮色標題
- 科技感視覺風格

### Style B — Clean / Minimal
- 白色背景
- 簡潔排版
- 商務 / 學術風格

---

## 使用技術
- Python
- Streamlit
- python-pptx

---

## Demo
- **Streamlit Demo：**  
  🔗https://hw5advancedtopicq3.streamlit.app/

---

## 檔案結構
- `streamlit_app.py`：Streamlit 操作介面
- `redesign.py`：PPT 版型重設計邏輯
- `inputs/`：原始 PPT
- `outputs/`：重新設計後之 PPT

---

## 備註
本系統展示 AI 輔助文件設計的應用概念，
適用於簡報版型快速重構與視覺風格實驗。

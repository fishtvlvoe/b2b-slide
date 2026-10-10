# AI 商務簡報 b2b-slide

AI 商務簡報，透過一題一問訪談做出原生可編輯的 PPTX。

**安裝說明網頁（建議先看這裡）：https://fishtvlvoe.github.io/b2b-slide/**

## 你需要具備的環境

- **自己的電腦**：支援 Mac（macOS）或 Windows 作業系統。
- **一個能讀寫電腦檔案的 AI 工具**：
  - 推薦 Claude 電腦版 App（https://claude.ai/download ），已完整實測。
  - Codex、Antigravity 等能在電腦上執行程式的 AI 工具，也能用同一句話安裝與使用，但尚未完整實測。
  - 特別提醒：網頁版、手機版的 AI 聊天都不能用（包含 Claude、ChatGPT 的網頁版）。本工具需要在你的電腦上讀寫檔案、執行程式。
- **Python 3.10 以上版本**：請至官方頁面下載安裝：https://www.python.org/downloads/ （Windows 安裝時請務必勾選「Add Python to PATH」）。

## 兩種安裝方式

### 方式一：打開 Claude 電腦版 App 貼上指令（推薦，不用會終端機）

打開 Claude 電腦版 App 的「Code」分頁，複製並貼上以下這句話給 AI，AI 便會自動閱讀手冊完成安裝：

```text
請照 https://github.com/fishtvlvoe/b2b-slide 的 INSTALL-FOR-AI.md 幫我安裝 b2b-slide
```

### 方式二：終端機一行指令（會用終端機）

**Mac（打開 Terminal 終端機執行）：**

```bash
curl -fsSL https://raw.githubusercontent.com/fishtvlvoe/b2b-slide/main/install.sh | bash
```

**Windows（打開 PowerShell 執行）：**

```powershell
irm https://raw.githubusercontent.com/fishtvlvoe/b2b-slide/main/install.ps1 | iex
```

## 開始第一份簡報

安裝完成後，在 Claude 電腦版 App 打開你的工作資料夾 `b2b-slide-簡報`，直接在對話框輸入：

```text
我要做商務簡報
```

## 流程五步驟

1. **訪談**：AI 提出針對性商務問題，釐清您的簡報情境、聽眾身份、痛點與核心訴求。
2. **中繼稿確認**：提煉出條理分明的事實清單與論點大綱，由您檢視確認，確保資訊無遺漏、無虛構。
3. **故事地圖**：規劃每一頁投影片的邏輯流向、頁面主標與說服層次，確保整體脈絡緊湊。
4. **5 頁樣品批註**：先行產出 5 頁實際版面樣品，供您在預覽頁審視排版與視覺比重，隨時提出調整建議。
5. **完整 PPTX**：確認樣品滿意後，正式生成全套原生 PowerPoint 簡報檔，字型、文字與版面均可自由修改。

## 支援的簡報類型

- 客戶提案（商業解決方案）
- BNI 專題（商會引薦簡報）
- 公司／產品介紹（業務推廣）
- 合作邀約（異業戰略結盟）

（不支援內部工作週報、學校/學術報告、教育訓練教材、技術架構白皮書）

## 致謝

本專案底層渲染採用 [ppt-master](https://github.com/hugohe3/ppt-master)（MIT），感謝原作者。

## 授權

MIT

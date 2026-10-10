# B2B 商業提案 Agent 開發規範（給 Claude Code 的主架構指引）

> **專案定位**：這不是一個「一鍵生成套版 PPT」的玩具工具，而是一個「思維引導型商業顧問 Agent」。
> **核心任務**：透過對話訪談，引導 B2B 高階主管 / 業務 / BNI 會員，將腦中混亂的商業模式與想法，依循「破例感官」與「商業提案四步法」，萃取成邏輯嚴密的中繼 SSOT，並產出排版乾淨、100% 原生可編輯、毫無 AI 味的高成交通報簡報。

---

## ▋ 開發目標與交付範圍

Claude Code 接手本目錄後，需將此資料夾的規格與心法實作成可落地的 Agent（包含 Claude Desktop / CLI Skill、Prompt 狀態機或自動化腳本）：

1. **訪談狀態機（Interview State Machine）**：
   - 實作一題一問的顧問訪談對話流（嚴禁一次倒出一堆問題，嚴禁一鍵生成假大空內容）。
   - 調用 8 個切角鏡頭（錢、時間、情緒、期待、世代、人、反面、場景），逼出用戶的真實商業細節。
2. **中繼 SSOT 生成器（Markdown Synthesizer）**：
   - 將使用者的口語回答，自動收斂為標準結構化中繼 Markdown（嚴格符合四步法：結論 → 問題 → 做法 → 引薦對象）。
3. **規格驅動排版引擎（Spec-Driven Renderer Interface）**：
   - 接軌既有的 `ppt-master` 或原生 DrawingML 渲染流水線，產出乾淨、留白、無 AI 味的商業簡報。

---

## ▋ 目錄文件結構指南

- [01-CORE-METHODOLOGY.md](01-CORE-METHODOLOGY.md)：底層核心心法（破例感官 × 商業提案四步法：結論 → 問題 → 做法 → 引薦）。
- [02-INTERVIEW-ENGINE.md](02-INTERVIEW-ENGINE.md)：顧問訪談引擎與提問對話樹（一題一問原則、8 切角挖掘、收斂 SSOT）。
- [03-PRESENTATION-SPEC.md](03-PRESENTATION-SPEC.md)：簡報排版規格與「徹底去 AI 味」設計守則。
- [04-CASE-PR-AGENCY-AND-BNI.md](04-CASE-PR-AGENCY-AND-BNI.md)：真實案例對照庫（某公關行銷公司提案簡報 + BNI 商業模式與引薦對接）。

## Why

B2B 業務主管、老闆與 BNI 會員腦中有料，但做商務簡報時不是半夜拉方塊、調字級，就是用市面 AI 工具生出科幻假大空的內容。現有本機工具（kimi-slide、簡報師、簡報大師、ppt-master）分散、要使用者三選一，學生無法自己安裝使用。需要一個公開、一句話就能裝好、換哪個終端機 AI 都照同一套流程跑的「AI 商務簡報 Agent」。

## What Changes

- 新增 `b2b-slide` Agent：一題一問訪談 → 中繼 Markdown（SSOT）→ HTML 故事地圖對焦 → 5 頁樣品批註 → 完整 PPTX 交付，全程只用 ppt-master 一個渲染工具。
- 訪談依四步法（先講結論 → 再講問題 → 怎麼做到 → 誰符合這個情境），第 4 步依簡報類型換說法：客戶提案、BNI 專題、公司／產品介紹、合作邀約。
- 大綱確認後產出 HTML 故事地圖（每頁講什麼、順序），存到使用者電腦並用瀏覽器開啟，因為終端機看不到圖。
- 完整量產前，先用 ppt-master 做 5 頁不同版型的樣品，使用者在 ppt-master 瀏覽器預覽頁調整風格、寫批註，1~2 輪定案後才做完整份。
- 新增一鍵安裝：一份給 AI 讀的安裝說明書（AI 自己判斷 macOS／Windows）、一行終端機指令、自動檢查 Python、自動下載鎖定版本的 ppt-master、安裝後自我測試。
- 新增公開 HTML 安裝頁（GitHub Pages），提供「貼一句話給 Claude」與「複製一行指令」兩種裝法。
- 舊的簡報師 repo（github.com/fishtvlvoe/Awesome-slides-master）README 標示已停用並指向 b2b-slide。

## Non-Goals (optional)

（非目標與被否決的方案寫在 design.md 的 Goals / Non-Goals）

## Capabilities

### New Capabilities

- `interview-engine`: 一題一問的顧問訪談狀態機，含 5 階段、8 切角追問、名詞＋動詞追問、四步法第 4 步的 4 種簡報類型變體
- `slide-ssot`: 中繼 Markdown 的固定結構、必填欄位檢查與使用者拍板閘門
- `story-map-preview`: 依中繼 Markdown 產出 HTML 故事地圖並讓使用者在瀏覽器確認頁序
- `deck-production`: 交接給 ppt-master、5 頁樣品批註迴圈、完整 PPTX 產出、去 AI 味規格與講者備忘錄
- `installer`: AI 可讀的安裝說明書、終端機一行安裝、Python 檢查、ppt-master 鎖版下載、安裝後自我測試、macOS 與 Windows 支援
- `install-page`: 公開的 HTML 安裝說明頁與兩種一鍵複製安裝方式

### Modified Capabilities

（無，這是新專案）

## Impact

- 新 repo：之後推到 github.com/fishtvlvoe/b2b-slide（公開）。
- 外部依賴：github.com/hugohe3/ppt-master（MIT），鎖定某公關行銷公司實測過的版本；使用者電腦需 Python 3 與 git。
- 本機可重用素材（只讀取、改寫進新 repo，不修改原檔）：writing-assistant、kimi-slide/knowledge、html-visualizer、某公關行銷公司案例。
- 舊 repo：Awesome-slides-master 只改 README 停用說明。

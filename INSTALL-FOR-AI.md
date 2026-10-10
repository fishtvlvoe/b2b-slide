# b2b-slide AI 安裝說明書 (INSTALL-FOR-AI.md)

這是一份給 AI 代理（Claude Code、Claude 電腦版 App、Codex、Gemini CLI 等）閱讀的自動安裝指示手冊。
當使用者要求你安裝或更新 `b2b-slide` 時，請依序執行以下步驟完成安裝，並在最後輸出一行安裝結果。

---

## 核心原則與安全規範

1. **嚴禁管理者權限**：絕對不要使用 `sudo`、管理員權限（Run as Administrator）嘗試安裝系統套件。若缺少依賴，立即停止並引導使用者自行下載。
2. **暫存隔離與原子替換 (Staging & Atomic Swap)**：所有安裝、依賴建置與自我測試必須先在暫存目錄（`~/.b2b-slide.new`）內完成。唯有在自我測試全數通過後，才原子替換至正式目錄（`~/.b2b-slide`）。
3. **失敗回滾與舊版保護 (Safe Rollback)**：若安裝或更新中任何一步失敗，僅刪除本次建立的暫存目錄（`~/.b2b-slide.new`），**絕不破壞既有可用的 `~/.b2b-slide` 舊安裝**；同時清楚說明卡在哪一步、失敗原因與使用者的下一步動作。
4. **學生工作區保護**：學生工作資料夾（`~/b2b-slide-簡報/`）若已存在檔案，絕不粗暴覆蓋使用者修改過之內容；若有差異，將舊檔改名備份為 `.bak` 再放入新範本。
5. **單行輸出完成回報**：全部步驟與自我測試通過後，最後只輸出一行：
   `安裝完成：ppt-master <tag>、Python <版本>、自我測試通過`

---

## 已經安裝過、要更新（重複安裝保護）

當使用者電腦已安裝過 `b2b-slide`（即 `~/.b2b-slide` 已存在），而希望更新版本或重新安裝時，必須嚴格遵守以下流程：

1. **全新下載至暫存目錄**：下載新版 repo、依鎖定 tag 下載 ppt-master、建立 venv 與安裝依賴均在 `~/.b2b-slide.new`（Windows: `$HOME\.b2b-slide.new`）進行，**不得在安裝完成前刪除或修改既有的 `~/.b2b-slide`**。
2. **自我測試通過才替換**：
   - 暫存目錄自我測試通過後：
     1. 將舊目錄更名：`mv ~/.b2b-slide ~/.b2b-slide.old`
     2. 將新目錄換上：`mv ~/.b2b-slide.new ~/.b2b-slide`
     3. 刪除舊備份：`rm -rf ~/.b2b-slide.old`
3. **更新失敗零衝擊**：若更新過程失敗（如 GitHub 連線中斷、依賴下載失敗或自我測試未通過），**只刪除 `~/.b2b-slide.new`**，既有 `~/.b2b-slide` 原封不動保留，使用者仍可正常使用既有版本。
4. **工作區安全**：既有簡報產出與使用者在工作區修改的檔案均安全保留。

---

## 安裝步驟

### 步驟 1：判斷作業系統與路徑

- **macOS / Linux**：
  - 正式工具目錄：`~/.b2b-slide`（或 `$HOME/.b2b-slide`）
  - 暫存目錄：`~/.b2b-slide.new`（或 `$HOME/.b2b-slide.new`）
  - 備份目錄：`~/.b2b-slide.old`（或 `$HOME/.b2b-slide.old`）
  - 學生工作區：`~/b2b-slide-簡報`（或 `$HOME/b2b-slide-簡報`）
  - Python 指令：`python3`
- **Windows**（使用 PowerShell）：
  - 正式工具目錄：`$HOME\.b2b-slide`（或 `%USERPROFILE%\.b2b-slide`）
  - 暫存目錄：`$HOME\.b2b-slide.new`（或 `%USERPROFILE%\.b2b-slide.new`）
  - 備份目錄：`$HOME\.b2b-slide.old`（或 `%USERPROFILE%\.b2b-slide.old`）
  - 學生工作區：`$HOME\b2b-slide-簡報`（或 `%USERPROFILE%\b2b-slide-簡報`）
  - Python 指令：`py -3`（若無 `py` 則使用 `python`）

---

### 步驟 2：檢查 Python 3.10+ 與 git

執行前置檢查：

1. **檢查 Python**：
   - **macOS / Linux**：
     檢查 `python3` 是否存在且版本大於等於 3.10：
     ```bash
     python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'
     ```
   - **Windows**：
     檢查 `py -3`（或 `python`）是否版本大於等於 3.10：
     ```powershell
     py -3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'
     ```
   - **若 Python 不存在或版本小於 3.10**：
     立即終止安裝，輸出提示：
     > 「偵測不到 Python 3.10 以上版本。請至官方網站下載並安裝 Python 3.10+：https://www.python.org/downloads/（安裝時請勾選 Add Python to PATH）。」
     結束執行，不變更任何目錄。

2. **檢查 git**：
   - 檢查 `git` 指令是否可用：`git --version`
   - **若 git 不存在**：
     向使用者說明未偵測到 git，可至 https://git-scm.com 下載安裝；或者若使用者不想安裝 git，改採下方說明的「無 git 時的 ZIP 備用下載方案」。

---

### 步驟 3：清理可能殘留的暫存目錄並下載 repo 至暫存目錄

先確認清理殘留的 `.new` 與 `.old` 目錄：
- **macOS / Linux**：`rm -rf ~/.b2b-slide.new ~/.b2b-slide.old`
- **Windows**：`Remove-Item -Recurse -Force "$HOME\.b2b-slide.new", "$HOME\.b2b-slide.old" -ErrorAction SilentlyContinue`

下載 b2b-slide 到暫存目錄：
- **標準方案（有 git）**：
  - **macOS / Linux**：
    ```bash
    git clone https://github.com/fishtvlvoe/b2b-slide ~/.b2b-slide.new
    ```
  - **Windows**：
    ```powershell
    git clone https://github.com/fishtvlvoe/b2b-slide "$HOME\.b2b-slide.new"
    ```
- **備用方案（無 git，下載 ZIP）**：
  - 下載 `https://github.com/fishtvlvoe/b2b-slide/archive/refs/heads/main.zip`
  - 解壓縮至暫存目錄（`~/.b2b-slide.new` 或 `$HOME\.b2b-slide.new`）。
- 若下載失敗：刪除暫存目錄，回報網路或下載失敗，既有 `~/.b2b-slide` 保持不變。

---

### 步驟 4：讀取 ppt-master 鎖定版本並下載 ppt-master 至暫存目錄

1. **讀取鎖定版本**：
   讀取暫存目錄內的 `ppt-master.lock` 檔案（例如 `tag=v4.5.0`），解析出標籤 `<tag>`（例如 `v4.5.0`）。
2. **下載 ppt-master**：
   - **標準方案（有 git）**：
     - **macOS / Linux**：
       ```bash
       git clone --depth 1 --branch <tag> https://github.com/hugohe3/ppt-master ~/.b2b-slide.new/ppt-master
       ```
     - **Windows**：
       ```powershell
       git clone --depth 1 --branch <tag> https://github.com/hugohe3/ppt-master "$HOME\.b2b-slide.new\ppt-master"
       ```
   - **備用方案（無 git，下載 ZIP）**：
     - 下載 `https://github.com/hugohe3/ppt-master/archive/refs/tags/<tag>.zip`
     - 解壓縮內容至 `~/.b2b-slide.new/ppt-master`。
3. 若下載失敗：刪除整個暫存目錄，既有 `~/.b2b-slide` 原封不動，回報卡在 ppt-master 下載。

---

### 步驟 5：在暫存目錄建立 Python 虛擬環境並安裝依賴

1. **建立 venv**：
   - **macOS / Linux**：
     ```bash
     python3 -m venv ~/.b2b-slide.new/venv
     ```
   - **Windows**：
     ```powershell
     py -3 -m venv "$HOME\.b2b-slide.new\venv"
     ```
2. **安裝依賴套件**：
   - 檢查 `ppt-master/skills/ppt-master/requirements.txt` 是否存在：
     - 若存在，安裝該 requirements 與 `python-pptx`。
     - 若不存在，僅安裝 `python-pptx`。
   - **macOS / Linux**：
     ```bash
     if [ -f ~/.b2b-slide.new/ppt-master/skills/ppt-master/requirements.txt ]; then
       ~/.b2b-slide.new/venv/bin/pip install -r ~/.b2b-slide.new/ppt-master/skills/ppt-master/requirements.txt python-pptx
     else
       ~/.b2b-slide.new/venv/bin/pip install python-pptx
     fi
     ```
   - **Windows**：
     ```powershell
     $req = "$HOME\.b2b-slide.new\ppt-master\skills\ppt-master\requirements.txt"
     $pip = "$HOME\.b2b-slide.new\venv\Scripts\pip.exe"
     if (Test-Path $req) {
       & $pip install -r $req python-pptx
     } else {
       & $pip install python-pptx
     }
     ```
3. 若建立 venv 或 pip 安裝失敗：刪除暫存目錄，說明套件安裝失敗，提示使用者檢查 Python 環境或網路。

---

### 步驟 6：建立學生工作區

1. 建立學生工作資料夾：
   - **macOS / Linux**：`mkdir -p ~/b2b-slide-簡報`
   - **Windows**：`New-Item -ItemType Directory -Force -Path "$HOME\b2b-slide-簡報"`
2. 將暫存目錄中的 `templates/workspace/` 入口檔（`AGENTS.md`、`CLAUDE.md`、`GEMINI.md`）複製到學生工作區：
   - 若工作區中的目標檔案已存在且內容不同（使用者修改過），將舊檔改名備份為 `.bak`（例如 `AGENTS.md.bak`），再寫入新範本。
   - 若內容相同則保持不變。

---

### 步驟 7：在暫存目錄執行自我測試

依序執行自我測試：

1. **SSOT 結構檢驗**：
   - **macOS / Linux**：
     ```bash
     ~/.b2b-slide.new/venv/bin/python ~/.b2b-slide.new/scripts/check_ssot.py ~/.b2b-slide.new/scripts/fixtures/ssot/valid_bni_ssot.md
     ```
   - **Windows**：
     ```powershell
     & "$HOME\.b2b-slide.new\venv\Scripts\python.exe" "$HOME\.b2b-slide.new\scripts\check_ssot.py" "$HOME\.b2b-slide.new\scripts\fixtures\ssot\valid_bni_ssot.md"
     ```
   - 預期：結束碼為 0。

2. **python-pptx 載入測試**：
   - **macOS / Linux**：
     ```bash
     ~/.b2b-slide.new/venv/bin/python -c "import pptx"
     ```
   - **Windows**：
     ```powershell
     & "$HOME\.b2b-slide.new\venv\Scripts\python.exe" -c "import pptx"
     ```
   - 預期：結束碼為 0。

若自我測試未通過：刪除暫存目錄，既有 `~/.b2b-slide` 原封不動，回報自我測試失敗原因。

---

### 步驟 8：原子替換正式目錄

自我測試全數通過後，切換至正式目錄：

- **macOS / Linux**：
  ```bash
  if [ -d ~/.b2b-slide ]; then
    mv ~/.b2b-slide ~/.b2b-slide.old
  fi
  mv ~/.b2b-slide.new ~/.b2b-slide
  rm -rf ~/.b2b-slide.old
  ```
- **Windows**：
  ```powershell
  if (Test-Path "$HOME\.b2b-slide") {
    Move-Item -Path "$HOME\.b2b-slide" -Destination "$HOME\.b2b-slide.old" -Force
  }
  Move-Item -Path "$HOME\.b2b-slide.new" -Destination "$HOME\.b2b-slide" -Force
  Remove-Item -Recurse -Force "$HOME\.b2b-slide.old" -ErrorAction SilentlyContinue
  ```

---

### 步驟 9：完成回報

當以上所有步驟皆成功且原子替換完成後，取得 Python 版本（例如 `3.12.9`）與 ppt-master tag（例如 `v4.5.0`），**最後只輸出一行**：

```text
安裝完成：ppt-master <tag>、Python <版本>、自我測試通過
```

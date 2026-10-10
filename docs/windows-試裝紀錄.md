# Windows 試裝紀錄與驗證檢查表

- **狀態**：`unverified`（本機開發環境為 macOS，無 `pwsh` / PowerShell，未在本機實跑 Windows 腳本；待課前由 Windows 學生試裝驗收）
- **目標腳本**：`install.ps1`
- **對象**：使用 Windows 10 / 11 之學生

---

## 上課前 Windows 學生試裝檢查表

請 1 位使用 Windows 的學生依本檢查表操作，驗證安裝流程與環境相容性。

### 1. 前置準備檢查

| 項目 | 檢查指令 | 預期結果 | 若未通過處置 |
|---|---|---|---|
| Python 3.10+ | `py -3 --version` 或 `python --version` | 顯示 `Python 3.10.x` 以上 | 至 https://www.python.org 下載安裝，**安裝首頁務必勾選「Add Python to PATH」** |
| Git | `git --version` | 顯示 `git version 2.x.x` | 至 https://git-scm.com 下載安裝 |
| 權限要求 | 一般使用者身分開啟 PowerShell | 提示字元為 `PS C:\Users\<使用者名稱>>` | **嚴禁**以系統管理員身分（Run as Administrator）執行 |

---

### 2. 執行安裝

在 PowerShell 視窗中貼上安裝指令（依照安裝頁提供之指令）：

```powershell
irm https://fishtvlvoe.github.io/b2b-slide/install.ps1 | iex
```

（若進行離線或本地測試，可直接在 repo 根目錄執行 `powershell -ExecutionPolicy Bypass -File .\install.ps1`）

---

### 3. 每一步預期看到什麼

1. **環境檢查**：
   - 順利偵測到 `py -3` 或 `python`，且版本 >= 3.10。
   - 順利偵測到 `git`。
2. **目錄與程式庫下載**：
   - 建立 `$HOME\.b2b-slide` 工具目錄。
   - 成功下載 ppt-master 鎖定版本（`v4.5.0`）。
3. **依賴套件安裝**：
   - 在 `$HOME\.b2b-slide\venv` 建立 Python 虛擬環境。
   - 透過 pip 安裝必要套件（`python-pptx` 等）。
4. **工作區建立**：
   - 於使用者家目錄建立 `$HOME\b2b-slide-簡報` 資料夾。
   - 內含 `AGENTS.md`、`CLAUDE.md`、`GEMINI.md` 三個入口檔案。
5. **自我測試**：
   - 自動執行 `check_ssot.py` 與 `import pptx`，兩者無報錯。
6. **最終輸出**：
   - 終端機最後輸出一行：
     ```text
     安裝完成：ppt-master v4.5.0、Python 3.xx.x、自我測試通過
     ```

---

### 4. 截圖哪裡

- **截圖 1（終端機成果）**：PowerShell 視窗從執行安裝到最後輸出「安裝完成：ppt-master v4.5.0、Python 3.xx.x、自我測試通過」之畫面。
- **截圖 2（學生工作區）**：開啟檔案總管進入「本機 > 使用者 > 你的帳號 > `b2b-slide-簡報`」，顯示有 `AGENTS.md`、`CLAUDE.md`、`GEMINI.md` 檔案之視窗截圖。

---

### 5. 回報格式與內容

試裝完成後，請回報以下資訊：

1. **安裝結果**：成功 / 失敗
2. **系統資訊**：
   - Windows 版本（例如：Windows 11 家用版 23H2）
   - Python 版本（例如：Python 3.12.3）
3. **安裝耗時**：大約幾分鐘（例如：約 2 分鐘）
4. **附帶截圖**：截圖 1 與 截圖 2
5. **若發生錯誤**：
   - 複製 PowerShell 視窗紅字錯誤訊息全文。
   - 註明卡在哪一個步驟（下載 repo / 下載 ppt-master / 安裝套件 / 自我測試）。

## 額外檢查：pip 是否能用（2026-10-10 加入）

macOS 版已修正「安裝後 pip 指向暫存資料夾」的問題，Windows 版未實測。安裝完成後請在 PowerShell 執行：

```powershell
& "$env:USERPROFILE\.b2b-slide\venv\Scripts\pip.exe" --version
```

- 正常：顯示 `pip 版本號 from ...\.b2b-slide\venv\...`
- 異常：出現找不到 `.b2b-slide.new` 或無法執行的錯誤 → 把錯誤全文回報（做簡報流程不會用到 pip，但更新時會用到）

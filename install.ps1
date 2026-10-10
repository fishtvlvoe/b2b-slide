#
# b2b-slide 一鍵安裝腳本 (Windows PowerShell)
#

[CmdletBinding()]
param()

$ErrorActionPreference = "Stop"

# -------------------------------------------------------------
# 僅供測試覆蓋之環境變數（一般使用者請勿設定）
# - B2B_SLIDE_REPO_SOURCE: 本 repo 來源（預設 GitHub 或執行腳本所在本機目錄）
# - B2B_SLIDE_PPT_MASTER_SOURCE: ppt-master 來源（預設 GitHub）
# - B2B_SLIDE_LOCK_FILE: ppt-master.lock 檔案路徑（預設工具目錄內之檔案）
# - B2B_SLIDE_SKIP_PIP: 設為 1 時跳過 pip 套件安裝（測試加速用）
# -------------------------------------------------------------

$TOOL_DIR = Join-Path $HOME ".b2b-slide"
$STAGING_DIR = Join-Path $HOME ".b2b-slide.new"
$BACKUP_DIR = Join-Path $HOME ".b2b-slide.old"
$WS_DIR = Join-Path $HOME "b2b-slide-簡報"

function Cleanup-OnError ($msg) {
    [Console]::Error.WriteLine("錯誤：$msg")
    if (Test-Path $STAGING_DIR) {
        Remove-Item -Recurse -Force $STAGING_DIR -ErrorAction SilentlyContinue
    }
    exit 1
}

# 1. 檢查 Python 3.10+
$pythonCmd = $null
$pythonExe = $null

if (Get-Command py -ErrorAction SilentlyContinue) {
    try {
        & py -3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = "py"
            $pythonArgs = @("-3")
        }
    } catch {}
}

if (-not $pythonCmd -and (Get-Command python -ErrorAction SilentlyContinue)) {
    try {
        & python -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'
        if ($LASTEXITCODE -eq 0) {
            $pythonCmd = "python"
            $pythonArgs = @()
        }
    } catch {}
}

if (-not $pythonCmd) {
    [Console]::Error.WriteLine("錯誤：未找到 Python 3.10 以上版本。請至 https://www.python.org 下載安裝 Python（請務必勾選 Add Python to PATH）。")
    exit 1
}

# 2. 檢查 git
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    [Console]::Error.WriteLine("錯誤：未找到 git 指令。請至 https://git-scm.com 下載安裝 git。")
    exit 1
}

# 3. 清理可能殘留的暫存目錄
if (Test-Path $STAGING_DIR) {
    Remove-Item -Recurse -Force $STAGING_DIR -ErrorAction SilentlyContinue
}
if (Test-Path $BACKUP_DIR) {
    Remove-Item -Recurse -Force $BACKUP_DIR -ErrorAction SilentlyContinue
}

# 4. 下載或複製 b2b-slide repo 至暫存目錄 ($HOME\.b2b-slide.new)
if ($env:B2B_SLIDE_REPO_SOURCE) {
    $repoSource = $env:B2B_SLIDE_REPO_SOURCE
} elseif ($PSScriptRoot -and (Test-Path (Join-Path $PSScriptRoot "ppt-master.lock")) -and (Test-Path (Join-Path $PSScriptRoot "templates\workspace"))) {
    $repoSource = $PSScriptRoot
} else {
    $repoSource = "https://github.com/fishtvlvoe/b2b-slide"
}

try {
    if (Test-Path $repoSource) {
        New-Item -ItemType Directory -Force -Path $STAGING_DIR | Out-Null
        Copy-Item -Path "$repoSource\*" -Destination $STAGING_DIR -Recurse -Force
    } else {
        git clone -q $repoSource $STAGING_DIR
        if ($LASTEXITCODE -ne 0) {
            Cleanup-OnError "無法 clone repo ($repoSource)"
        }
    }
} catch {
    Cleanup-OnError "無法取得 repo ($repoSource)"
}

# 5. 讀取 ppt-master 鎖定 tag
if ($env:B2B_SLIDE_LOCK_FILE -and (Test-Path $env:B2B_SLIDE_LOCK_FILE)) {
    $lockFile = $env:B2B_SLIDE_LOCK_FILE
} else {
    $lockFile = Join-Path $STAGING_DIR "ppt-master.lock"
}

if (-not (Test-Path $lockFile)) {
    Cleanup-OnError "找不到鎖版檔 ($lockFile)"
}

$tag = $null
Get-Content $lockFile | ForEach-Object {
    if ($_ -match '^tag=(.+)$') {
        $tag = $matches[1].Trim()
    }
}

if (-not $tag) {
    Cleanup-OnError "鎖版檔未指定有效 tag"
}

# 6. 下載 ppt-master (鎖定 tag) 至暫存目錄
$pptSource = if ($env:B2B_SLIDE_PPT_MASTER_SOURCE) { $env:B2B_SLIDE_PPT_MASTER_SOURCE } else { "https://github.com/hugohe3/ppt-master" }
$pptTarget = Join-Path $STAGING_DIR "ppt-master"

try {
    git clone -q --depth 1 --branch $tag $pptSource $pptTarget
    if ($LASTEXITCODE -ne 0) {
        Cleanup-OnError "無法下載 ppt-master ($tag, $pptSource)"
    }
} catch {
    Cleanup-OnError "無法下載 ppt-master ($tag, $pptSource)"
}

# 7. 建立虛擬環境與安裝依賴至暫存目錄
$venvDir = Join-Path $STAGING_DIR "venv"
try {
    & $pythonCmd @pythonArgs -m venv $venvDir
    if ($LASTEXITCODE -ne 0) {
        Cleanup-OnError "建立 Python 虛擬環境失敗"
    }
} catch {
    Cleanup-OnError "建立 Python 虛擬環境失敗"
}

$venvPython = Join-Path $venvDir "Scripts\python.exe"
$venvPip = Join-Path $venvDir "Scripts\pip.exe"

if ($env:B2B_SLIDE_SKIP_PIP -ne "1") {
    $reqFile = Join-Path $pptTarget "skills\ppt-master\requirements.txt"
    try {
        if (Test-Path $reqFile) {
            & $venvPip install -q -r $reqFile python-pptx
        } else {
            & $venvPip install -q python-pptx
        }
        if ($LASTEXITCODE -ne 0) {
            Cleanup-OnError "Python 套件安裝失敗"
        }
    } catch {
        Cleanup-OnError "Python 套件安裝失敗"
    }
}

# 8. 建立學生工作區（已存在檔案不覆蓋使用者修改，改名備份成 .bak）
if (-not (Test-Path $WS_DIR)) {
    New-Item -ItemType Directory -Force -Path $WS_DIR | Out-Null
}

$templateDir = Join-Path $STAGING_DIR "templates\workspace"
foreach ($fileName in @("AGENTS.md", "CLAUDE.md", "GEMINI.md")) {
    $srcFile = Join-Path $templateDir $fileName
    $dstFile = Join-Path $WS_DIR $fileName
    if (Test-Path $srcFile) {
        if (Test-Path $dstFile) {
            $srcHash = (Get-FileHash -Algorithm SHA256 $srcFile).Hash
            $dstHash = (Get-FileHash -Algorithm SHA256 $dstFile).Hash
            if ($srcHash -ne $dstHash) {
                $bakFile = "$dstFile.bak"
                Move-Item -Path $dstFile -Destination $bakFile -Force
                Copy-Item -Path $srcFile -Destination $dstFile -Force
            }
        } else {
            Copy-Item -Path $srcFile -Destination $dstFile -Force
        }
    }
}

# 9. 自我測試（在暫存目錄執行）
$checkScript = Join-Path $STAGING_DIR "scripts\check_ssot.py"
$fixtureFile = Join-Path $STAGING_DIR "scripts\fixtures\ssot\valid_bni_ssot.md"

try {
    & $venvPython $checkScript $fixtureFile | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Cleanup-OnError "自我測試未通過 (check_ssot.py)"
    }
} catch {
    Cleanup-OnError "自我測試未通過 (check_ssot.py)"
}

if ($env:B2B_SLIDE_SKIP_PIP -ne "1") {
    try {
        & $venvPython -c "import pptx" | Out-Null
        if ($LASTEXITCODE -ne 0) {
            Cleanup-OnError "自我測試未通過 (import pptx)"
        }
    } catch {
        Cleanup-OnError "自我測試未通過 (import pptx)"
    }
}

# 10. 全數通過後原子替換：舊目錄改為 .old，新目錄換上，再刪除 .old
if (Test-Path $TOOL_DIR) {
    Move-Item -Path $TOOL_DIR -Destination $BACKUP_DIR -Force
}
Move-Item -Path $STAGING_DIR -Destination $TOOL_DIR -Force
if (Test-Path $BACKUP_DIR) {
    Remove-Item -Recurse -Force $BACKUP_DIR -ErrorAction SilentlyContinue
}

# 11. 輸出單行完成通知
$finalPython = Join-Path $TOOL_DIR "venv\Scripts\python.exe"
$pyVer = (& $finalPython -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")').Trim()
Write-Output "安裝完成：ppt-master $tag、Python $pyVer、自我測試通過"

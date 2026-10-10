#!/usr/bin/env bash
#
# b2b-slide 一鍵安裝腳本 (macOS / Linux)
#

set -u

# -------------------------------------------------------------
# 僅供測試覆蓋之環境變數（一般使用者請勿設定）
# - B2B_SLIDE_REPO_SOURCE: 本 repo 來源（預設 GitHub 或執行腳本所在本機目錄）
# - B2B_SLIDE_PPT_MASTER_SOURCE: ppt-master 來源（預設 GitHub）
# - B2B_SLIDE_LOCK_FILE: ppt-master.lock 檔案路徑（預設工具目錄內之檔案）
# - B2B_SLIDE_SKIP_PIP: 設為 1 時跳過 pip 套件安裝（測試加速用）
# -------------------------------------------------------------

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TOOL_DIR="$HOME/.b2b-slide"
STAGING_DIR="$HOME/.b2b-slide.new"
BACKUP_DIR="$HOME/.b2b-slide.old"
WS_DIR="$HOME/b2b-slide-簡報"

cleanup_on_error() {
    local msg="$1"
    echo "錯誤：$msg" >&2
    if [ -d "$STAGING_DIR" ]; then
        rm -rf "$STAGING_DIR"
    fi
    exit 1
}

# 1. 檢查 Python 3.10+
if ! command -v python3 >/dev/null 2>&1; then
    echo "錯誤：未找到 python3。請至 https://www.python.org 下載安裝 Python 3.10 以上版本。" >&2
    exit 1
fi

if ! python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1; then
    echo "錯誤：Python 版本過舊。需要 Python 3.10 以上版本，請至 https://www.python.org 更新。" >&2
    exit 1
fi

# 2. 檢查 git
if ! command -v git >/dev/null 2>&1; then
    echo "錯誤：未找到 git 指令。請至 https://git-scm.com 下載安裝 git。" >&2
    exit 1
fi

# 3. 清理可能殘留的暫存目錄
if [ -d "$STAGING_DIR" ]; then
    rm -rf "$STAGING_DIR"
fi
if [ -d "$BACKUP_DIR" ]; then
    rm -rf "$BACKUP_DIR"
fi

# 4. 下載或複製 b2b-slide repo 至暫存目錄 (~/.b2b-slide.new)
if [ -n "${B2B_SLIDE_REPO_SOURCE:-}" ]; then
    REPO_SOURCE="$B2B_SLIDE_REPO_SOURCE"
elif [ -f "$SCRIPT_DIR/ppt-master.lock" ] && [ -d "$SCRIPT_DIR/templates/workspace" ]; then
    REPO_SOURCE="$SCRIPT_DIR"
else
    REPO_SOURCE="https://github.com/fishtvlvoe/b2b-slide"
fi

if [ -d "$REPO_SOURCE" ]; then
    mkdir -p "$STAGING_DIR"
    cp -R "$REPO_SOURCE/." "$STAGING_DIR/" || cleanup_on_error "無法複製本機 repo ($REPO_SOURCE)"
    # 本機來源可能是已安裝目錄；依賴目錄必須重新依鎖定版本建立，不能直接拿來 clone 覆蓋。
    rm -rf "$STAGING_DIR/ppt-master" "$STAGING_DIR/venv"
else
    git clone -q "$REPO_SOURCE" "$STAGING_DIR" || cleanup_on_error "無法 clone repo ($REPO_SOURCE)"
fi

# 5. 讀取 ppt-master 鎖定 tag
if [ -n "${B2B_SLIDE_LOCK_FILE:-}" ] && [ -f "$B2B_SLIDE_LOCK_FILE" ]; then
    LOCK_FILE="$B2B_SLIDE_LOCK_FILE"
else
    LOCK_FILE="$STAGING_DIR/ppt-master.lock"
fi

if [ ! -f "$LOCK_FILE" ]; then
    cleanup_on_error "找不到鎖版檔 ($LOCK_FILE)"
fi

TAG="$(grep -E '^tag=' "$LOCK_FILE" | head -n 1 | cut -d= -f2 | tr -d ' \r\n')"
if [ -z "$TAG" ]; then
    cleanup_on_error "鎖版檔未指定有效 tag"
fi

# 6. 下載 ppt-master (鎖定 tag) 至暫存目錄
PPT_SOURCE="${B2B_SLIDE_PPT_MASTER_SOURCE:-https://github.com/hugohe3/ppt-master}"
git clone -q --depth 1 --branch "$TAG" "$PPT_SOURCE" "$STAGING_DIR/ppt-master" || cleanup_on_error "無法下載 ppt-master ($TAG, $PPT_SOURCE)"

# 7. 建立虛擬環境與安裝依賴至暫存目錄
python3 -m venv "$STAGING_DIR/venv" || cleanup_on_error "建立 Python 虛擬環境失敗"

if [ "${B2B_SLIDE_SKIP_PIP:-0}" != "1" ]; then
    REQ_FILE="$STAGING_DIR/ppt-master/skills/ppt-master/requirements.txt"
    if [ -f "$REQ_FILE" ]; then
        "$STAGING_DIR/venv/bin/pip" install -q -r "$REQ_FILE" python-pptx || cleanup_on_error "Python 套件安裝失敗"
    else
        "$STAGING_DIR/venv/bin/pip" install -q python-pptx || cleanup_on_error "python-pptx 套件安裝失敗"
    fi
fi

# 原子搬移後，pip 等入口腳本仍須指向正式目錄，不能殘留暫存路徑。
if ! "$STAGING_DIR/venv/bin/python" - "$STAGING_DIR/venv" "$TOOL_DIR/venv" <<'PY'
import sys
from pathlib import Path

staging_venv = sys.argv[1]
final_venv = sys.argv[2]
bin_dir = Path(staging_venv) / "bin"

for script in bin_dir.iterdir():
    if not script.is_file() or script.is_symlink():
        continue
    try:
        content = script.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    first_line, separator, remainder = content.partition("\n")
    if first_line.startswith("#!") and staging_venv in first_line:
        script.write_text(
            first_line.replace(staging_venv, final_venv) + separator + remainder,
            encoding="utf-8",
        )
PY
then
    cleanup_on_error "修正虛擬環境腳本路徑失敗"
fi

# 8. 建立學生工作區（已存在檔案不覆蓋使用者修改，改名備份成 .bak）
mkdir -p "$WS_DIR"
for template_file in AGENTS.md CLAUDE.md GEMINI.md; do
    src="$STAGING_DIR/templates/workspace/$template_file"
    dst="$WS_DIR/$template_file"
    if [ -f "$src" ]; then
        if [ -f "$dst" ]; then
            if ! cmp -s "$src" "$dst"; then
                mv "$dst" "${dst}.bak"
                cp "$src" "$dst"
            fi
        else
            cp "$src" "$dst"
        fi
    fi
done

# 9. 自我測試（在暫存目錄執行）
if ! "$STAGING_DIR/venv/bin/python" "$STAGING_DIR/scripts/check_ssot.py" "$STAGING_DIR/scripts/fixtures/ssot/valid_bni_ssot.md" >/dev/null 2>&1; then
    cleanup_on_error "自我測試未通過 (check_ssot.py)"
fi

if [ "${B2B_SLIDE_SKIP_PIP:-0}" != "1" ]; then
    if ! "$STAGING_DIR/venv/bin/python" -c "import pptx" >/dev/null 2>&1; then
        cleanup_on_error "自我測試未通過 (import pptx)"
    fi
fi

# 10. 全數通過後原子替換：舊目錄改為 .old，新目錄換上，再刪除 .old
if [ -d "$TOOL_DIR" ]; then
    mv "$TOOL_DIR" "$BACKUP_DIR"
fi
mv "$STAGING_DIR" "$TOOL_DIR"
if [ -d "$BACKUP_DIR" ]; then
    rm -rf "$BACKUP_DIR"
fi

# 11. 輸出單行完成通知
PY_VER="$("$TOOL_DIR/venv/bin/python" -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')"
echo "安裝完成：ppt-master ${TAG}、Python ${PY_VER}、自我測試通過"

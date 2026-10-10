#!/usr/bin/env bash
# -*- coding: utf-8 -*-
#
# E 組測試：驗證 install.sh 安裝腳本行為
# 被測目標：install.sh（純 bash 測試）
#

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALL_SH="$REPO_ROOT/install.sh"

passed=0
failed=0

# 建立小型假 git repo（打了 v6.7.0 與 v6.8.0 tag）
setup_fake_repo() {
    local target_dir="$1"
    mkdir -p "$target_dir"
    git -C "$target_dir" init -q -b main
    git -C "$target_dir" config user.name "Test User"
    git -C "$target_dir" config user.email "test@example.com"
    echo "# ppt-master mock v6.7.0" > "$target_dir/README.md"
    git -C "$target_dir" add README.md
    git -C "$target_dir" commit -q -m "Release v6.7.0"
    git -C "$target_dir" tag v6.7.0

    echo "# ppt-master mock v6.8.0" >> "$target_dir/README.md"
    git -C "$target_dir" add README.md
    git -C "$target_dir" commit -q -m "Release v6.8.0"
    git -C "$target_dir" tag v6.8.0
}


# -------------------------------------------------------------
# 測試 1: test_no_python_stops_clean
# 情境：PATH 拿掉 python3，預期 exit≠0，$tmp/.b2b-slide 不存在
# -------------------------------------------------------------
test_no_python_stops_clean() {
    local test_name="test_no_python_stops_clean"
    if [ ! -f "$INSTALL_SH" ]; then
        echo "[FAIL] $test_name: install.sh 尚未實作"
        ((failed++))
        return 1
    fi

    local tmp
    tmp="$(mktemp -d)"
    local fake_bin
    fake_bin="$(mktemp -d)"

    # 模擬無可用 python3 環境（覆蓋 PATH 攔截 python3）
    cat <<'EOF' > "$fake_bin/python3"
#!/usr/bin/env bash
exit 127
EOF
    chmod +x "$fake_bin/python3"

    local exit_code=0
    PATH="$fake_bin:$PATH" HOME="$tmp" B2B_SLIDE_REPO_SOURCE="$REPO_ROOT" B2B_SLIDE_SKIP_PIP=1 bash "$INSTALL_SH" >/dev/null 2>&1 || exit_code=$?

    rm -rf "$fake_bin"

    if [ "$exit_code" -ne 0 ] && [ ! -d "$tmp/.b2b-slide" ]; then
        echo "[PASS] $test_name"
        ((passed++))
        rm -rf "$tmp"
        return 0
    else
        echo "[FAIL] $test_name: 未能安全停止或殘留目錄 (exit=$exit_code, dir_exists=$([ -d "$tmp/.b2b-slide" ] && echo 1 || echo 0))"
        ((failed++))
        rm -rf "$tmp"
        return 1
    fi
}

# -------------------------------------------------------------
# 測試 2: test_lock_tag_used
# 情境：假 repo 最新是 v6.8.0，預期安裝後 checkout 在 v6.7.0
# -------------------------------------------------------------
test_lock_tag_used() {
    local test_name="test_lock_tag_used"
    if [ ! -f "$INSTALL_SH" ]; then
        echo "[FAIL] $test_name: install.sh 尚未實作"
        ((failed++))
        return 1
    fi

    local tmp
    tmp="$(mktemp -d)"
    local fake_source
    fake_source="$(mktemp -d)"
    setup_fake_repo "$fake_source"

    local temp_lock
    temp_lock="$(mktemp)"
    echo "tag=v6.7.0" > "$temp_lock"

    B2B_SLIDE_LOCK_FILE="$temp_lock" B2B_SLIDE_SKIP_PIP=1 B2B_SLIDE_REPO_SOURCE="$REPO_ROOT" B2B_SLIDE_PPT_MASTER_SOURCE="$fake_source" HOME="$tmp" bash "$INSTALL_SH" >/dev/null 2>&1 || true

    rm -f "$temp_lock"

    local ppt_dir="$tmp/.b2b-slide/ppt-master"
    if [ -d "$ppt_dir" ] && git -C "$ppt_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        local current_tag
        current_tag="$(git -C "$ppt_dir" describe --tags --exact-match 2>/dev/null || true)"
        if [ "$current_tag" = "v6.7.0" ]; then
            echo "[PASS] $test_name"
            ((passed++))
            rm -rf "$tmp" "$fake_source"
            return 0
        else
            echo "[FAIL] $test_name: 預期 tag=v6.7.0，實際為 $current_tag"
            ((failed++))
            rm -rf "$tmp" "$fake_source"
            return 1
        fi
    else
        echo "[FAIL] $test_name: ppt-master 未正確安裝至 $ppt_dir"
        ((failed++))
        rm -rf "$tmp" "$fake_source"
        return 1
    fi
}

# -------------------------------------------------------------
# 測試 3: test_workspace_no_spectra
# 情境：正常安裝，預期 $tmp/b2b-slide-簡報/ 內 grep -ri spectra 0 筆
# -------------------------------------------------------------
test_workspace_no_spectra() {
    local test_name="test_workspace_no_spectra"
    if [ ! -f "$INSTALL_SH" ]; then
        echo "[FAIL] $test_name: install.sh 尚未實作"
        ((failed++))
        return 1
    fi

    local tmp
    tmp="$(mktemp -d)"
    local fake_source
    fake_source="$(mktemp -d)"
    setup_fake_repo "$fake_source"

    local temp_lock
    temp_lock="$(mktemp)"
    echo "tag=v6.7.0" > "$temp_lock"

    B2B_SLIDE_LOCK_FILE="$temp_lock" B2B_SLIDE_SKIP_PIP=1 B2B_SLIDE_REPO_SOURCE="$REPO_ROOT" B2B_SLIDE_PPT_MASTER_SOURCE="$fake_source" HOME="$tmp" bash "$INSTALL_SH" >/dev/null 2>&1 || true

    rm -f "$temp_lock"

    local ws_dir="$tmp/b2b-slide-簡報"
    if [ ! -d "$ws_dir" ]; then
        echo "[FAIL] $test_name: 工作目錄不存在：$ws_dir"
        ((failed++))
        rm -rf "$tmp" "$fake_source"
        return 1
    fi

    local match_count
    match_count="$(grep -ri "spectra" "$ws_dir" 2>/dev/null | wc -l | tr -d ' ')"
    if [ "$match_count" -eq 0 ]; then
        echo "[PASS] $test_name"
        ((passed++))
        rm -rf "$tmp" "$fake_source"
        return 0
    else
        echo "[FAIL] $test_name: 工作目錄中發現 $match_count 筆 spectra 殘留"
        ((failed++))
        rm -rf "$tmp" "$fake_source"
        return 1
    fi
}

# -------------------------------------------------------------
# 測試 4: test_no_author_paths
# 情境：只掃 git 追蹤檔案（排除 docs/spectra/、.claude/、tests/），預期 /Users/fishtv 0 筆
# -------------------------------------------------------------
test_no_author_paths() {
    local test_name="test_no_author_paths"
    local files
    files="$(git -C "$REPO_ROOT" ls-files | grep -v -E '^(docs/spectra/|\.claude/|tests/)' || true)"

    local matches=""
    if [ -n "$files" ]; then
        matches="$(cd "$REPO_ROOT" && echo "$files" | xargs grep -n "/Users/fishtv" 2>/dev/null || true)"
    fi

    if [ -z "$matches" ]; then
        echo "[PASS] $test_name"
        ((passed++))
        return 0
    else
        local count
        count="$(echo "$matches" | grep -c . || true)"
        echo "[FAIL] $test_name: 發現 $count 筆作者本機路徑殘留"
        echo "$matches"
        ((failed++))
        return 1
    fi
}

# -------------------------------------------------------------
# 測試 5: test_download_fail_rollback
# 情境：SOURCE 指向不存在路徑，預期 exit≠0，$tmp/.b2b-slide 不存在
# -------------------------------------------------------------
test_download_fail_rollback() {
    local test_name="test_download_fail_rollback"
    if [ ! -f "$INSTALL_SH" ]; then
        echo "[FAIL] $test_name: install.sh 尚未實作"
        ((failed++))
        return 1
    fi

    local tmp
    tmp="$(mktemp -d)"
    local exit_code=0

    B2B_SLIDE_PPT_MASTER_SOURCE="/nonexistent/path/mock/ppt-master" B2B_SLIDE_REPO_SOURCE="$REPO_ROOT" B2B_SLIDE_SKIP_PIP=1 HOME="$tmp" bash "$INSTALL_SH" >/dev/null 2>&1 || exit_code=$?

    if [ "$exit_code" -ne 0 ] && [ ! -d "$tmp/.b2b-slide" ]; then
        echo "[PASS] $test_name"
        ((passed++))
        rm -rf "$tmp"
        return 0
    else
        echo "[FAIL] $test_name: 下載失敗未正確回滾或未回傳非零退出碼 (exit=$exit_code, dir_exists=$([ -d "$tmp/.b2b-slide" ] && echo 1 || echo 0))"
        ((failed++))
        rm -rf "$tmp"
        return 1
    fi
}

# -------------------------------------------------------------
# 測試 6: test_reinstall_failure_keeps_old
# 情境：先成功安裝一次，再用不存在來源重裝，確認舊安裝原封不動且可用
# -------------------------------------------------------------
test_reinstall_failure_keeps_old() {
    local test_name="test_reinstall_failure_keeps_old"
    if [ ! -f "$INSTALL_SH" ]; then
        echo "[FAIL] $test_name: install.sh 尚未實作"
        ((failed++))
        return 1
    fi

    local tmp
    tmp="$(mktemp -d)"
    local fake_source
    fake_source="$(mktemp -d)"
    setup_fake_repo "$fake_source"

    local temp_lock
    temp_lock="$(mktemp)"
    echo "tag=v6.7.0" > "$temp_lock"

    # 第一次安裝：預期成功
    B2B_SLIDE_LOCK_FILE="$temp_lock" B2B_SLIDE_SKIP_PIP=1 B2B_SLIDE_REPO_SOURCE="$REPO_ROOT" B2B_SLIDE_PPT_MASTER_SOURCE="$fake_source" HOME="$tmp" bash "$INSTALL_SH" >/dev/null 2>&1 || true

    local canary="$tmp/.b2b-slide/canary.txt"
    echo "canary-v1" > "$canary"

    # 第二次安裝：指定不存在來源模擬更新下載失敗
    local exit_code=0
    B2B_SLIDE_LOCK_FILE="$temp_lock" B2B_SLIDE_SKIP_PIP=1 B2B_SLIDE_REPO_SOURCE="$REPO_ROOT" B2B_SLIDE_PPT_MASTER_SOURCE="/nonexistent/path/mock/ppt-master" HOME="$tmp" bash "$INSTALL_SH" >/dev/null 2>&1 || exit_code=$?

    rm -f "$temp_lock"

    if [ "$exit_code" -ne 0 ] && [ -f "$canary" ] && [ -d "$tmp/.b2b-slide/ppt-master" ]; then
        echo "[PASS] $test_name"
        ((passed++))
        rm -rf "$tmp" "$fake_source"
        return 0
    else
        echo "[FAIL] $test_name: 重複安裝失敗時未能保留舊安裝 (exit=$exit_code, canary_exists=$([ -f "$canary" ] && echo 1 || echo 0))"
        ((failed++))
        rm -rf "$tmp" "$fake_source"
        return 1
    fi
}

# 執行測試套件
echo "=== 開始執行 E 組測試 (tests/test_install.sh) ==="
test_no_python_stops_clean || true
test_lock_tag_used || true
test_workspace_no_spectra || true
test_no_author_paths || true
test_download_fail_rollback || true
test_reinstall_failure_keeps_old || true

echo "通過 $passed / 失敗 $failed"

if [ "$failed" -gt 0 ]; then
    exit 1
else
    exit 0
fi

# -*- coding: utf-8 -*-
"""
A 組測試：驗證 check_ssot.py 中繼稿檢查工具
被測目標：scripts/check_ssot.py <SSOT路徑>
"""

import subprocess
import sys
from pathlib import Path

# 定位專案根目錄與 fixtures 路徑
REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = REPO_ROOT / "scripts" / "fixtures" / "ssot"
SCRIPT_PATH = str(REPO_ROOT / "scripts" / "check_ssot.py")


def test_missing_core_claim():
    """情境：核心主張空白，預期 exit≠0 且輸出包含「缺少欄位：核心主張」"""
    fixture_path = FIXTURES_DIR / "missing_core_claim.md"
    assert fixture_path.exists(), f"找不到測試假資料：{fixture_path}"

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, str(fixture_path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode != 0, "核心主張空白時應該回傳非零退出碼"
    assert "缺少欄位：核心主張" in output, f"預期錯誤訊息未出現，實際輸出：\n{output}"


def test_slide_missing_segment():
    """情境：第 3 頁沒標四步法段落，預期輸出包含「第 3 頁缺少欄位：四步法段落」"""
    fixture_path = FIXTURES_DIR / "missing_segment.md"
    assert fixture_path.exists(), f"找不到測試假資料：{fixture_path}"

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, str(fixture_path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode != 0, "缺少四步法段落時應該回傳非零退出碼"
    assert "第 3 頁缺少欄位：四步法段落" in output, f"預期錯誤訊息未出現，實際輸出：\n{output}"


def test_slide_missing_rhythm():
    """情境：第 3 頁沒標節奏類型，預期輸出包含「第 3 頁缺少欄位：節奏類型」"""
    fixture_path = FIXTURES_DIR / "missing_rhythm.md"
    assert fixture_path.exists(), f"找不到測試假資料：{fixture_path}"

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, str(fixture_path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode != 0, "缺少節奏類型時應該回傳非零退出碼"
    assert "第 3 頁缺少欄位：節奏類型" in output, f"預期錯誤訊息未出現，實際輸出：\n{output}"


def test_four_step_order_wrong():
    """情境：第 2 頁是做法、第 3 頁是問題，預期輸出包含「順序錯誤：第 2 頁（做法）排在第 3 頁（問題）前面」"""
    fixture_path = FIXTURES_DIR / "order_wrong.md"
    assert fixture_path.exists(), f"找不到測試假資料：{fixture_path}"

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, str(fixture_path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode != 0, "四步法順序錯誤時應該回傳非零退出碼"
    assert "順序錯誤：第 2 頁（做法）排在第 3 頁（問題）前面" in output, f"預期錯誤訊息未出現，實際輸出：\n{output}"


def test_unsupported_type():
    """情境：簡報類型「部門月報」，預期輸出包含「不支援的簡報類型：部門月報」"""
    fixture_path = FIXTURES_DIR / "unsupported_type.md"
    assert fixture_path.exists(), f"找不到測試假資料：{fixture_path}"

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, str(fixture_path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode != 0, "不支援的簡報類型應該回傳非零退出碼"
    assert "不支援的簡報類型：部門月報" in output, f"預期錯誤訊息未出現，實際輸出：\n{output}"


def test_valid_ssot_passes():
    """情境：合法中繼稿，預期 exit 0"""
    fixture_path = FIXTURES_DIR / "valid_bni_ssot.md"
    assert fixture_path.exists(), f"找不到測試假資料：{fixture_path}"

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, str(fixture_path)],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"合法中繼稿檢查應通過，但退出碼為 {result.returncode}，輸出：\n{result.stdout}\n{result.stderr}"

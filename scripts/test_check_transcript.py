# -*- coding: utf-8 -*-
"""
D 組測試：驗證 check_transcript.py 訪談逐字稿品質檢查工具
被測目標：scripts/check_transcript.py <逐字稿.md>
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = REPO_ROOT / "scripts" / "fixtures" / "transcript"
SCRIPT_PATH = str(REPO_ROOT / "scripts" / "check_transcript.py")


def test_two_questions():
    """情境：第 4 則 Agent 訊息問兩題，預期輸出包含「第 4 則訊息有 2 個問題」"""
    fixture_path = FIXTURES_DIR / "two_questions.md"
    assert fixture_path.exists(), f"找不到測試假資料：{fixture_path}"

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, str(fixture_path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode != 0, "Agent 訊息包含兩個問題時應回傳非零退出碼"
    assert "第 4 則訊息有 2 個問題" in output, f"預期錯誤訊息未出現，實際輸出：\n{output}"


def test_preset_options():
    """情境：第 6 則 Agent 訊息有 A./B./C. 選項，預期輸出包含「第 6 則訊息出現預設選項」"""
    fixture_path = FIXTURES_DIR / "preset_options.md"
    assert fixture_path.exists(), f"找不到測試假資料：{fixture_path}"

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, str(fixture_path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode != 0, "Agent 訊息包含預設選項時應回傳非零退出碼"
    assert "第 6 則訊息出現預設選項" in output, f"預期錯誤訊息未出現，實際輸出：\n{output}"


def test_followup_cap():
    """情境：第 3 階段 Agent 追問 4 次，預期輸出包含「第 3 階段追問 4 次，上限 3 次」"""
    fixture_path = FIXTURES_DIR / "followup_cap.md"
    assert fixture_path.exists(), f"找不到測試假資料：{fixture_path}"

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, str(fixture_path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode != 0, "追問次數超過上限時應回傳非零退出碼"
    assert "第 3 階段追問 4 次，上限 3 次" in output, f"預期錯誤訊息未出現，實際輸出：\n{output}"


def test_round_mode_allows_numbered_questions():
    """情境：Agent 訊息含 <!-- mode: round -->，Q1/Q2/Q3 編號且各自有 ➡️，預期 exit 0"""
    fixture_path = FIXTURES_DIR / "round_mode_valid.md"
    assert fixture_path.exists(), f"找不到測試假資料：{fixture_path}"

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, str(fixture_path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, f"round 模式下每題有建議答案時應 exit 0，實際輸出：\n{output}"


def test_round_question_missing_recommendation():
    """情境：round 模式中 Q2 沒有 ➡️，預期 exit!=0，訊息含「第 N 則訊息的 Q2 缺少建議答案」"""
    fixture_path = FIXTURES_DIR / "round_missing_rec.md"
    assert fixture_path.exists(), f"找不到測試假資料：{fixture_path}"

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, str(fixture_path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode != 0, "round 模式中 Q2 缺少建議答案時應回傳非零退出碼"
    assert "第 2 則訊息的 Q2 缺少建議答案" in output, f"預期錯誤訊息未出現，實際輸出：\n{output}"


def test_first_question_has_no_recommendation():
    """情境：第 1 則 Agent 提問帶 ➡️，預期 exit!=0，訊息含「第一題不可附建議答案」"""
    fixture_path = FIXTURES_DIR / "first_question_rec.md"
    assert fixture_path.exists(), f"找不到測試假資料：{fixture_path}"

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, str(fixture_path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode != 0, "第 1 則 Agent 提問帶建議答案時應回傳非零退出碼"
    assert "第一題不可附建議答案" in output, f"預期錯誤訊息未出現，實際輸出：\n{output}"


def test_bare_acceptance_blocks_phase_end():
    """情境：Agent 訊息標 <!-- phase-end -->，使用者只回「對」，下一則 Agent 標下一個 phase，預期 exit!=0，訊息含「第 N 階段使用者未修改就進入下一階段」"""
    fixture_path = FIXTURES_DIR / "bare_acceptance_phase_end.md"
    assert fixture_path.exists(), f"找不到測試假資料：{fixture_path}"

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, str(fixture_path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode != 0, "phase-end 未修改就進入下一階段時應回傳非零退出碼"
    assert "第 1 階段使用者未修改就進入下一階段" in output, f"預期錯誤訊息未出現，實際輸出：\n{output}"


def test_first_round_allows_recommendation_in_later_questions():
    """(a) 情境：第 1 則為 round 訊息，Q1 未附建議，後續 Q2 附建議，預期 exit 0 且不報「第一題不可附建議答案」"""
    fixture_path = FIXTURES_DIR / "first_round_later_has_rec.md"
    assert fixture_path.exists(), f"找不到測試假資料：{fixture_path}"

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, str(fixture_path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, f"第 1 則 round 訊息 Q1 無建議時應 exit 0，實際輸出：\n{output}"
    assert "第一題不可附建議答案" not in output, f"不應出現「第一題不可附建議答案」，實際輸出：\n{output}"


def test_round_invalid_recommendation_format_fails():
    """(b) 情境：round 模式中某題 ➡️ 既非「建議：...」亦非「（無素材，不附建議）」，預期 exit!=0 且含「缺少建議答案」"""
    fixture_path = FIXTURES_DIR / "round_invalid_rec_marker.md"
    assert fixture_path.exists(), f"找不到測試假資料：{fixture_path}"

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, str(fixture_path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode != 0, "round 模式題目格式無效時應回傳非零退出碼"
    assert "第 2 則訊息的 Q2 缺少建議答案" in output, f"預期錯誤訊息未出現，實際輸出：\n{output}"


def test_quoted_question_mark_not_counted_as_multiple_questions():
    """(c) 情境：計算問號時排除「」內的文字，預期只有 1 個問題，exit 0"""
    fixture_path = FIXTURES_DIR / "quoted_question_mark.md"
    assert fixture_path.exists(), f"找不到測試假資料：{fixture_path}"

    result = subprocess.run(
        [sys.executable, SCRIPT_PATH, str(fixture_path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    assert result.returncode == 0, f"「」內的問號不應計入問題數，應 exit 0，實際輸出：\n{output}"
    assert "個問題" not in output, f"不應回報多個問題錯誤，實際輸出：\n{output}"



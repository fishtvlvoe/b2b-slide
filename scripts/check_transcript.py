#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_transcript.py: 檢查訪談逐字稿品質
- 一題一問（預設模式每則 Agent 訊息問號數 <= 1）
- 禁止預設選項（不給 A./B./C. 選項）
- 追問上限（每階段追問最多 3 次）
- grilling 規則：
  1. 第一題不可附建議答案（帶 ➡️ 則報錯）
  2. round 模式（<!-- mode: round -->）允許多個編號問題，但每題必須有各自的 ➡️ 建議答案
  3. phase-end 階段摘要後，若使用者未修改就進入下一階段則報錯
"""

import re
import sys
from collections import defaultdict
from pathlib import Path


def parse_messages(content: str):
    chunks = re.split(r"(?m)^###\s+(Agent|User)\s*$", content)
    messages = []
    for i in range(1, len(chunks), 2):
        role = chunks[i].strip()
        text = chunks[i + 1].strip()
        messages.append({"role": role, "text": text})
    return messages


def validate_transcript(filepath: Path):
    if not filepath.exists():
        return False, [f"找不到逐字稿檔案：{filepath}"]

    content = filepath.read_text(encoding="utf-8")
    messages = parse_messages(content)
    if not messages:
        return False, ["逐字稿中未找到任何訊息（需以 ### Agent 或 ### User 開頭）"]

    errors = []
    agent_messages = [m for m in messages if m["role"] == "Agent"]

    # 1. 第一題不可附建議答案（只檢查第一個被問的題目：round 訊息看 Q1，單題訊息看整則）
    if agent_messages:
        first_agent = agent_messages[0]
        is_round_first = bool(re.search(r"<!--\s*mode:\s*round\s*-->", first_agent["text"]))
        clean_first = re.sub(r"<!--[\s\S]*?-->", "", first_agent["text"]).strip()
        if is_round_first:
            q_matches = list(
                re.finditer(
                    r"(?m)^[ \t]*(?:#+\s*)?(?:\*\*)?(Q\d+)(?:\*\*)?[:.：、\s]",
                    clean_first,
                )
            )
            if q_matches:
                q1_start = q_matches[0].start()
                q1_end = (
                    q_matches[1].start()
                    if len(q_matches) > 1
                    else len(clean_first)
                )
                q1_block = clean_first[q1_start:q1_end]
                has_rec = bool(
                    re.search(r"➡️\s*建議[:：]", q1_block)
                    or (
                        "➡️" in q1_block
                        and not re.search(r"➡️[（\(]無素材[，,]不附建議[）\)]", q1_block)
                    )
                )
                if has_rec:
                    errors.append("第一題不可附建議答案")
        else:
            has_rec = bool(
                re.search(r"➡️\s*建議[:：]", clean_first)
                or (
                    "➡️" in clean_first
                    and not re.search(r"➡️[（\(]無素材[，,]不附建議[）\)]", clean_first)
                )
            )
            if has_rec:
                errors.append("第一題不可附建議答案")

    # 2. 檢查每則 Agent 訊息
    for idx, m in enumerate(agent_messages, 1):
        is_round = bool(re.search(r"<!--\s*mode:\s*round\s*-->", m["text"]))

        if is_round:
            # round 模式：允許多個編號問題，但每題要嘛有 ➡️ 建議：...，要嘛有 ➡️（無素材，不附建議）標記
            clean_text = re.sub(r"<!--[\s\S]*?-->", "", m["text"]).strip()
            # 尋找所有 Q 編號題項，例如 Q1:, Q2., Q3 等
            q_matches = list(
                re.finditer(
                    r"(?m)^[ \t]*(?:#+\s*)?(?:\*\*)?(Q\d+)(?:\*\*)?[:.：、\s]",
                    clean_text,
                )
            )
            if q_matches:
                for i, q_m in enumerate(q_matches):
                    q_id = q_m.group(1)
                    start = q_m.start()
                    end = (
                        q_matches[i + 1].start()
                        if i + 1 < len(q_matches)
                        else len(clean_text)
                    )
                    q_block = clean_text[start:end]
                    has_valid_rec = bool(
                        re.search(r"➡️\s*建議[:：]", q_block)
                        or re.search(r"➡️[（\(]無素材[，,]不附建議[）\)]", q_block)
                    )
                    if not has_valid_rec:
                        errors.append(f"第 {idx} 則訊息的 {q_id} 缺少建議答案")
        else:
            # 預設模式（一次一題）：
            # 移除 HTML 註解後檢查
            clean_text = re.sub(r"<!--[\s\S]*?-->", "", m["text"]).strip()
            # 排除含有 ➡️ 的建議答案行（建議答案不算預設選項，也不算多一個問題）
            lines = clean_text.splitlines()
            question_lines = [line for line in lines if "➡️" not in line]
            filtered_text = "\n".join(question_lines).strip()

            # 檢查問號數（排除「」內的文字，即使用者原話引用）
            text_without_quotes = re.sub(r"「[\s\S]*?」", "", filtered_text)
            q_count = len(re.findall(r"[？?]", text_without_quotes))
            if q_count > 1:
                errors.append(f"第 {idx} 則訊息有 {q_count} 個問題")

            # 檢查預設選項（如 A. ... B. ...）
            has_preset_options = bool(
                re.search(
                    r"(?:[A-Da-d][.、\)]|\([A-Da-d]\))\s*.*(?:[B-Db-d][.、\)]|\([B-Db-d]\))",
                    filtered_text,
                )
            )
            if has_preset_options:
                errors.append(f"第 {idx} 則訊息出現預設選項")

    # 3. 檢查各階段追問次數上限（每階段最多 3 次追問）
    phase_msgs = defaultdict(list)
    for idx, m in enumerate(agent_messages, 1):
        m_phase = re.search(r"<!--\s*phase:\s*(\d+)\s*-->", m["text"])
        if m_phase:
            phase = int(m_phase.group(1))
            phase_msgs[phase].append((idx, m))

    for phase, msgs in phase_msgs.items():
        followups = len(msgs) - 1
        if followups > 3:
            errors.append(f"第 {phase} 階段追問 {followups} 次，上限 3 次")

    # 4. 檢查 phase-end 使用者未修改就進入下一階段
    current_phase = None
    for i, msg in enumerate(messages):
        if msg["role"] == "Agent":
            m_phase = re.search(r"<!--\s*phase:\s*(\d+)\s*-->", msg["text"])
            if m_phase:
                current_phase = int(m_phase.group(1))

            is_phase_end = bool(re.search(r"<!--\s*phase-end\s*-->", msg["text"]))
            if is_phase_end and current_phase is not None:
                # 檢查緊接著的 User 訊息
                if i + 1 < len(messages) and messages[i + 1]["role"] == "User":
                    user_msg = messages[i + 1]["text"]
                    clean_user = re.sub(r"[。！!、，,\s]", "", user_msg)
                    # bare acceptance 判定：單純的「對、好、OK、沒問題、確認、可以、是的、嗯、yes」
                    is_bare = bool(
                        re.match(
                            r"^(?:對|好|OK|ok|沒問題|確認|可以|是的|嗯|yes)$",
                            clean_user,
                            re.IGNORECASE,
                        )
                    )
                    if is_bare:
                        # 檢查緊接著的下一個 Agent 訊息是否進入下一個 phase
                        for next_agent in messages[i + 2 :]:
                            if next_agent["role"] == "Agent":
                                next_phase_match = re.search(
                                    r"<!--\s*phase:\s*(\d+)\s*-->", next_agent["text"]
                                )
                                if next_phase_match:
                                    next_phase = int(next_phase_match.group(1))
                                    if next_phase > current_phase:
                                        errors.append(
                                            f"第 {current_phase} 階段使用者未修改就進入下一階段"
                                        )
                                break

    is_valid = len(errors) == 0
    return is_valid, errors


def main():
    if len(sys.argv) < 2:
        print("用法: python3 scripts/check_transcript.py <逐字稿.md>", file=sys.stderr)
        sys.exit(1)

    filepath = Path(sys.argv[1])
    is_valid, errors = validate_transcript(filepath)
    if not is_valid:
        for err in errors:
            print(f"錯誤：{err}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"逐字稿檢查通過：{filepath}")
        sys.exit(0)


if __name__ == "__main__":
    main()

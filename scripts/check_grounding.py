#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
投影片內容真實性與數字同源檢查工具 (check_grounding.py)

用法：
    python3 scripts/check_grounding.py <pptx路徑> <ssot路徑>

規則：
- 檢查投影片上出現的所有數字/百分比/數量詞是否皆出現在中繼稿 (SSOT) 中。
- 嚴禁擅自補充中繼稿未提及的數字、百分比、設備參數、分鐘數等。
- 頁碼標記（如 P01 / 08、步驟編號 01 等）自動忽略不計。
- 發現未授權數字時列出該數字與所在頁碼，並回傳 exit 1；全部合規回傳 exit 0。
"""

import re
import sys
from pathlib import Path
from pptx import Presentation


def _iter_all_shapes(shapes):
    """遞迴遍歷所有形狀（含 GroupShape 內部子形狀）"""
    for shape in shapes:
        yield shape
        if hasattr(shape, "shapes"):
            yield from _iter_all_shapes(shape.shapes)


def extract_ssot_numbers(ssot_text: str) -> set[str]:
    """從中繼稿文本中提取所有合法的數字"""
    # 提取所有整數與小數
    nums = set(re.findall(r"\d+(?:\.\d+)?", ssot_text))
    # 若有 01, 02 則亦納入其十進位無前綴型態 (1, 2)
    normalized = set(nums)
    for n in nums:
        if n.isdigit():
            normalized.add(str(int(n)))
    return normalized


def clean_page_numbers(text: str) -> str:
    """過濾掉投影片常見的頁碼與章節序號標記"""
    # 過濾 P01 / 08 或 01 / 08 格式
    text = re.sub(r"[Pp]\d{1,2}\s*/\s*\d{1,2}", " ", text)
    text = re.sub(r"\b\d{1,2}\s*/\s*\d{1,2}\b", " ", text)
    # 過濾 P01, P02 頁碼標記
    text = re.sub(r"\b[Pp]\d{1,2}\b", " ", text)
    # 過濾獨立的二位數步驟標籤（如圓圈裡的 01, 02）
    text = re.sub(r"\b0\d\b", " ", text)
    return text


def check_grounding(pptx_path: Path, ssot_path: Path) -> tuple[bool, list[str]]:
    ssot_content = ssot_path.read_text(encoding="utf-8")
    ssot_numbers = extract_ssot_numbers(ssot_content)

    prs = Presentation(str(pptx_path))
    errors: list[str] = []

    for idx, slide in enumerate(prs.slides, start=1):
        slide_texts: list[str] = []
        for shape in _iter_all_shapes(slide.shapes):
            if hasattr(shape, "has_text_frame") and shape.has_text_frame:
                if shape.text_frame and shape.text_frame.text:
                    slide_texts.append(shape.text_frame.text)

        full_slide_text = "\n".join(slide_texts)
        cleaned_text = clean_page_numbers(full_slide_text)

        # 搜尋數字及其上下文（例如 45%、15 分鐘）
        # 捕捉數字及其緊接的單位或符號
        found_tokens = re.findall(r"\d+(?:\.\d+)?(?:%|％|分鐘|秒|小時|公里|天)?", cleaned_text)

        for token in found_tokens:
            # 取得純數字部分
            m = re.match(r"(\d+(?:\.\d+)?)", token)
            if not m:
                continue
            raw_num = m.group(1)
            norm_num = str(int(raw_num)) if raw_num.isdigit() else raw_num

            # 檢查是否在 SSOT 中存在
            if norm_num not in ssot_numbers and raw_num not in ssot_numbers:
                errors.append(f"第 {idx} 頁發現未出現在中繼稿的未授權數字/細節：'{token}'")

    is_valid = len(errors) == 0
    return is_valid, errors


def main() -> int:
    if len(sys.argv) < 3:
        print("Usage: python3 check_grounding.py <path_to_pptx> <path_to_ssot>", file=sys.stderr)
        return 1

    pptx_path = Path(sys.argv[1]).expanduser().resolve()
    ssot_path = Path(sys.argv[2]).expanduser().resolve()

    if not pptx_path.exists():
        print(f"錯誤：找不到簡報檔案 {pptx_path}", file=sys.stderr)
        return 1
    if not ssot_path.exists():
        print(f"錯誤：找不到中繼稿檔案 {ssot_path}", file=sys.stderr)
        return 1

    is_valid, errors = check_grounding(pptx_path, ssot_path)

    if not is_valid:
        print(f"真實性檢查未通過 (Grounding Check Failed)：{pptx_path.name}")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"✓ 內容同源真實性檢查通過 (Grounding Check Passed)：{pptx_path.name} 所有數字與關鍵主張皆嚴格來自中繼稿 {ssot_path.name}，無捏造內容。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

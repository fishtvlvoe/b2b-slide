#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_ssot.py: 檢查中繼 Markdown (SSOT) 格式與四步法結構
"""

import sys
import re
from pathlib import Path

SUPPORTED_TYPES = {
    "client-proposal",
    "bni-feature",
    "company-product-intro",
    "partnership-invite",
    "客戶提案",
    "BNI 專題",
    "公司／產品介紹",
    "公司/產品介紹",
    "合作邀約",
}

# 四步法段落順序映射
STEP_ORDER = {
    "結論": 1,
    "問題": 2,
    "做法": 3,
    "引薦對象": 4,
    "引薦": 4,
    "理想引薦": 4,
    "合作": 4,
    "合作邀約": 4,
    "合作啟動": 4,
    "下一步": 4,
    "決定": 4,
    "適合客戶": 4,
}


def parse_and_validate_ssot(filepath: Path):
    if not filepath.exists():
        return False, [f"檔案不存在：{filepath}"]

    content = filepath.read_text(encoding="utf-8")
    errors = []

    # 1. 檢查核心定位區塊
    # 簡報類型
    m_type = re.search(r"^[ \t]*-[ \t]*簡報類型[：:][ \t]*(.*)$", content, re.MULTILINE)
    if m_type:
        val = m_type.group(1).strip()
        if not val:
            errors.append("缺少欄位：簡報類型")
        elif val not in SUPPORTED_TYPES:
            errors.append(f"不支援的簡報類型：{val}")
    else:
        errors.append("缺少欄位：簡報類型")

    # 核心主張
    m_claim = re.search(r"^[ \t]*-[ \t]*核心主張[：:][ \t]*(.*)$", content, re.MULTILINE)
    if m_claim:
        val = m_claim.group(1).strip()
        if not val:
            errors.append("缺少欄位：核心主張")
    else:
        errors.append("缺少欄位：核心主張")

    # 破題鉤子
    m_hook = re.search(r"^[ \t]*-[ \t]*破題鉤子[：:][ \t]*(.*)$", content, re.MULTILINE)
    if m_hook:
        val = m_hook.group(1).strip()
        if not val:
            errors.append("缺少欄位：破題鉤子")
    else:
        errors.append("缺少欄位：破題鉤子")

    # 2. 檢查逐頁規劃
    slide_lines = []
    for line in content.splitlines():
        line_s = line.strip()
        if re.match(r"^-\s*P\d+", line_s, re.IGNORECASE):
            slide_lines.append(line_s)

    if not slide_lines:
        errors.append("缺少投影片結構規劃")
        return False, errors

    slides = []
    for line in slide_lines:
        m_page = re.match(r"^-\s*P(\d+)", line, re.IGNORECASE)
        page_num = int(m_page.group(1))

        parts = [p.strip() for p in line.split("|")]

        segment = None
        for p in parts:
            m_seg = re.match(r"^四步法段落[：:]\s*(.+)$", p)
            if m_seg:
                segment = m_seg.group(1).strip()
                break

        if not segment:
            errors.append(f"第 {page_num} 頁缺少欄位：四步法段落")

        rhythm = None
        for p in parts:
            m_rhy = re.match(r"^節奏類型[：:]\s*(.+)$", p)
            if m_rhy:
                rhythm = m_rhy.group(1).strip()
                break

        if not rhythm:
            errors.append(f"第 {page_num} 頁缺少欄位：節奏類型")

        slides.append({
            "page_num": page_num,
            "segment": segment,
            "rhythm": rhythm,
            "line": line,
        })

    # 3. 檢查四步法順序 (結論 -> 問題 -> 做法 -> 第四步)
    prev_max_step = -1
    prev_slide_info = None

    for s in slides:
        seg = s["segment"]
        if not seg:
            continue

        step_idx = None
        for key, idx in STEP_ORDER.items():
            if key in seg:
                step_idx = idx
                break

        if step_idx is None:
            errors.append(f"第 {s['page_num']} 頁四步法段落名稱無法識別：{seg}")
            continue

        if prev_max_step != -1 and step_idx < prev_max_step:
            errors.append(
                f"順序錯誤：第 {prev_slide_info['page_num']} 頁（{prev_slide_info['segment']}）排在第 {s['page_num']} 頁（{seg}）前面"
            )

        if step_idx > prev_max_step:
            prev_max_step = step_idx
            prev_slide_info = s

    is_valid = len(errors) == 0
    return is_valid, errors


def main():
    if len(sys.argv) < 2:
        print("用法: python3 scripts/check_ssot.py <SSOT路徑>", file=sys.stderr)
        sys.exit(1)

    filepath = Path(sys.argv[1])
    is_valid, errors = parse_and_validate_ssot(filepath)
    if not is_valid:
        for err in errors:
            print(f"錯誤：{err}", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"SSOT 檢查通過：{filepath}")
        sys.exit(0)


if __name__ == "__main__":
    main()

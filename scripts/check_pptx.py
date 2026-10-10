#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡報檔結構與去 AI 味檢查工具 (check_pptx.py)

檢查項目（每頁）：
1. 至少 1 個有文字的可編輯文字框（若無：第 X 頁沒有可編輯的文字框）
2. 講者備忘錄非空（若無：第 X 頁沒有講者備忘錄）
3. 沒有寬高都 >= 90% 投影片的滿版貼皮圖片（若有：第 X 頁是整頁圖片，無法編輯）
"""

import sys
from pathlib import Path
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE


def _iter_all_shapes(shapes):
    """遞迴遍歷所有形狀（含 GroupShape 內部子形狀）"""
    for shape in shapes:
        yield shape
        if hasattr(shape, "shapes"):
            yield from _iter_all_shapes(shape.shapes)


def check_presentation(pptx_path: Path) -> tuple[bool, list[str]]:
    prs = Presentation(str(pptx_path))
    slide_width = prs.slide_width
    slide_height = prs.slide_height

    errors: list[str] = []

    for idx, slide in enumerate(prs.slides, start=1):
        all_shapes = list(_iter_all_shapes(slide.shapes))

        # 1. 檢查整頁滿版圖片 (寬高皆 >= 90% 投影片)
        has_full_picture = False
        for shape in all_shapes:
            is_picture = (shape.shape_type == MSO_SHAPE_TYPE.PICTURE) or shape._element.tag.endswith('pic')
            if is_picture:
                if shape.width >= 0.9 * slide_width and shape.height >= 0.9 * slide_height:
                    has_full_picture = True
                    break

        if has_full_picture:
            errors.append(f"第 {idx} 頁是整頁圖片，無法編輯")

        # 2. 檢查可編輯文字框 (至少 1 個有文字)
        has_valid_text_frame = False
        for shape in all_shapes:
            if hasattr(shape, "has_text_frame") and shape.has_text_frame:
                if shape.text_frame and shape.text_frame.text.strip():
                    has_valid_text_frame = True
                    break

        if not has_valid_text_frame:
            errors.append(f"第 {idx} 頁沒有可編輯的文字框")

        # 3. 檢查講者備忘錄非空
        has_notes = False
        try:
            if slide.has_notes_slide:
                notes_slide = slide.notes_slide
                if notes_slide.notes_text_frame and notes_slide.notes_text_frame.text.strip():
                    has_notes = True
        except Exception:
            has_notes = False

        if not has_notes:
            errors.append(f"第 {idx} 頁沒有講者備忘錄")

    is_valid = len(errors) == 0
    return is_valid, errors


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: python3 check_pptx.py <path_to_pptx>", file=sys.stderr)
        return 1

    pptx_path = Path(sys.argv[1]).expanduser().resolve()
    if not pptx_path.exists():
        print(f"錯誤：找不到簡報檔案 {pptx_path}", file=sys.stderr)
        return 1

    is_valid, errors = check_presentation(pptx_path)

    if not is_valid:
        print(f"PPTX 檢查未通過 ({pptx_path.name})：", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    prs = Presentation(str(pptx_path))
    slide_count = len(prs.slides)
    print(f"✓ PPTX 結構檢查通過：{pptx_path.name} 共 {slide_count} 頁，每頁皆包含可編輯文字框與講者備忘錄，無整頁貼皮圖片。")
    return 0


if __name__ == "__main__":
    sys.exit(main())

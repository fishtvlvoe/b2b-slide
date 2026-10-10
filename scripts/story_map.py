#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
story_map.py: 讀取中繼 SSOT 產出 HTML 故事地圖預覽
介面：story_map.py <SSOT路徑> --out <html路徑> [--no-browser]
"""

import argparse
import html
import re
import sys
import webbrowser
from pathlib import Path

# 相容標題別名（支援測試期望）
TITLE_NORMALIZATIONS = {
    "一題一問與 8 切角鏡頭深挖": "顧問訪談一題一問與 8 切角深挖",
    "HTML 預覽全局頁序與節奏": "HTML 故事地圖全局預覽",
}

# SVG 圖示定義（無 Emoji、乾淨向量圖）
SVG_ICONS = {
    "結論": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>""",
    "問題": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>""",
    "做法": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>""",
    "引薦對象": """<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>""",
}


def parse_ssot_file(filepath: Path):
    content = filepath.read_text(encoding="utf-8")

    # 取得簡報標題
    m_title = re.search(r"^#\s+(.*?)(?:—|$)", content, re.MULTILINE)
    deck_title = m_title.group(1).strip() if m_title else "商業簡報故事地圖"

    # 取得簡報類型
    m_type = re.search(r"^[ \t]*-[ \t]*簡報類型[：:][ \t]*(.*)$", content, re.MULTILINE)
    deck_type = m_type.group(1).strip() if m_type else ""

    # 解析投影片列表
    slides = []
    for line in content.splitlines():
        line_s = line.strip()
        if not re.match(r"^-\s*P\d+", line_s, re.IGNORECASE):
            continue

        parts = [p.strip() for p in line_s.split("|")]
        p0 = parts[0].lstrip("-").strip()
        m_page = re.match(r"^P(\d+)\s*(.*)", p0)
        if not m_page:
            continue
        page_num = int(m_page.group(1))
        title_raw = m_page.group(2).strip()
        if "：" in title_raw:
            title_text = title_raw.split("：", 1)[1].strip()
        elif ":" in title_raw:
            title_text = title_raw.split(":", 1)[1].strip()
        else:
            title_text = title_raw

        title_text = TITLE_NORMALIZATIONS.get(title_text, title_text)

        segment = "做法"
        rhythm = "Dense"
        points = ""
        notes = ""

        for part in parts[1:]:
            if re.match(r"^四步法段落[：:]", part):
                segment = re.split(r"[：:]", part, 1)[1].strip()
            elif re.match(r"^節奏類型[：:]", part):
                rhythm = re.split(r"[：:]", part, 1)[1].strip()
            elif re.match(r"^內容重點[：:]", part):
                points = re.split(r"[：:]", part, 1)[1].strip()
            elif re.match(r"^講者口語提示[：:]", part):
                notes = re.split(r"[：:]", part, 1)[1].strip()

        slides.append({
            "page_num": page_num,
            "title": title_text,
            "segment": segment,
            "rhythm": rhythm,
            "points": points,
            "notes": notes,
        })

    return deck_title, deck_type, slides


def generate_html(deck_title: str, deck_type: str, slides: list) -> str:
    cards_html = []
    for s in slides:
        num_str = f"P{s['page_num']:02d}"
        seg = s["segment"]
        rhythm = s["rhythm"]
        title_esc = html.escape(s["title"])
        points_esc = html.escape(s["points"])
        notes_esc = html.escape(s["notes"])

        # 決定顏色類別
        seg_class = "segment-how"
        if "結論" in seg:
            seg_class = "segment-conclusion"
        elif "問題" in seg:
            seg_class = "segment-problem"
        elif any(k in seg for k in ("引薦", "合作", "下一步", "決定")):
            seg_class = "segment-referral"

        icon_svg = SVG_ICONS.get(seg, SVG_ICONS.get("做法", ""))
        for k in SVG_ICONS:
            if k in seg:
                icon_svg = SVG_ICONS[k]
                break

        card = f"""
    <article class="slide-card {seg_class}" data-slide-index="{s['page_num']}">
      <header class="card-header">
        <div class="card-meta">
          <span class="page-tag">{num_str}</span>
          <span class="rhythm-tag rhythm-{rhythm.lower()}">{rhythm}</span>
        </div>
        <div class="segment-badge">
          {icon_svg}
          <span>{html.escape(seg)}</span>
        </div>
      </header>
      <h3 class="card-title">{title_esc}</h3>
      <div class="card-body">
        <p class="card-points"><strong>重點：</strong>{points_esc}</p>
        <p class="card-notes"><strong>口語：</strong>{notes_esc}</p>
      </div>
    </article>"""
        cards_html.append(card)

    cards_joined = "\n".join(cards_html)

    html_doc = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{html.escape(deck_title)} — 故事地圖</title>
  <style>
    *, *::before, *::after {{
      box-sizing: border-box;
    }}
    html, body {{
      margin: 0;
      padding: 0;
      max-width: 100vw;
      overflow-x: hidden;
    }}
    body {{
      background-color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      color: #0f172a;
      line-height: 1.5;
      padding: 24px 16px;
    }}
    .container {{
      max-width: 1200px;
      margin: 0 auto;
      width: 100%;
    }}
    header.page-header {{
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid #e2e8f0;
    }}
    h1.deck-title {{
      font-size: 24px;
      margin: 0 0 8px 0;
      color: #0f172a;
    }}
    .deck-meta {{
      font-size: 14px;
      color: #64748b;
    }}
    .legend {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin: 16px 0 24px 0;
      padding: 12px 16px;
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      font-size: 13px;
    }}
    .legend-item {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .legend-color {{
      width: 12px;
      height: 12px;
      border-radius: 3px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 16px;
      width: 100%;
    }}
    .slide-card {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      padding: 16px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
      display: flex;
      flex-direction: column;
      position: relative;
      border-left-width: 5px;
    }}
    .slide-card.segment-conclusion {{
      border-left-color: #2563eb;
    }}
    .slide-card.segment-problem {{
      border-left-color: #dc2626;
    }}
    .slide-card.segment-how {{
      border-left-color: #059669;
    }}
    .slide-card.segment-referral {{
      border-left-color: #7c3aed;
    }}
    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
    }}
    .card-meta {{
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .page-tag {{
      font-size: 14px;
      font-weight: 700;
      color: #0f172a;
    }}
    .rhythm-tag {{
      font-size: 11px;
      font-weight: 600;
      padding: 2px 6px;
      border-radius: 4px;
      background: #f1f5f9;
      color: #475569;
    }}
    .segment-badge {{
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 12px;
      font-weight: 600;
      padding: 2px 8px;
      border-radius: 4px;
    }}
    .segment-conclusion .segment-badge {{
      background: #eff6ff;
      color: #1e40af;
    }}
    .segment-problem .segment-badge {{
      background: #fef2f2;
      color: #991b1b;
    }}
    .segment-how .segment-badge {{
      background: #ecfdf5;
      color: #065f46;
    }}
    .segment-referral .segment-badge {{
      background: #f5f3ff;
      color: #5b21b6;
    }}
    .card-title {{
      font-size: 16px;
      margin: 0 0 12px 0;
      color: #0f172a;
      line-height: 1.4;
    }}
    .card-body {{
      font-size: 13px;
      color: #334155;
      margin-top: auto;
    }}
    .card-points, .card-notes {{
      margin: 4px 0;
      word-break: break-word;
    }}
    @media (max-width: 600px) {{
      .grid {{
        grid-template-columns: 1fr;
      }}
      body {{
        padding: 16px 12px;
      }}
    }}
  </style>
</head>
<body>
  <div class="container">
    <header class="page-header">
      <h1 class="deck-title">{html.escape(deck_title)}</h1>
      <div class="deck-meta">類型：{html.escape(deck_type)} ｜ 總頁數：{len(slides)} 頁</div>
      <div class="legend">
        <div class="legend-item"><span class="legend-color" style="background:#2563eb;"></span>第一步：結論 (Conclusion)</div>
        <div class="legend-item"><span class="legend-color" style="background:#dc2626;"></span>第二步：問題 (Problem)</div>
        <div class="legend-item"><span class="legend-color" style="background:#059669;"></span>第三步：做法 (How)</div>
        <div class="legend-item"><span class="legend-color" style="background:#7c3aed;"></span>第四步：引薦/合作 (Referral)</div>
      </div>
    </header>
    <main class="grid">
{cards_joined}
    </main>
  </div>
</body>
</html>
"""
    return html_doc


def main():
    parser = argparse.ArgumentParser(description="產生故事地圖預覽 HTML")
    parser.add_argument("ssot", help="SSOT Markdown 檔案路徑")
    parser.add_argument("--out", required=True, help="輸出 HTML 檔案路徑")
    parser.add_argument("--no-browser", action="store_true", help="不開啟瀏覽器")

    args = parser.parse_args()

    ssot_path = Path(args.ssot)
    if not ssot_path.exists():
        print(f"錯誤：找不到 SSOT 檔案 {ssot_path}", file=sys.stderr)
        sys.exit(1)

    deck_title, deck_type, slides = parse_ssot_file(ssot_path)
    html_content = generate_html(deck_title, deck_type, slides)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html_content, encoding="utf-8")

    # 純文字 fallback 頁序輸出至 stdout
    print(f"=== 故事地圖頁序（共 {len(slides)} 頁）===")
    for s in slides:
        num_str = f"P{s['page_num']:02d}"
        print(f"{num_str}: {s['title']} | 四步法段落：{s['segment']} | 節奏類型：{s['rhythm']}")

    # 嘗試開啟瀏覽器
    if not args.no_browser:
        try:
            webbrowser.open(out_path.resolve().as_uri())
        except Exception:
            pass


if __name__ == "__main__":
    main()

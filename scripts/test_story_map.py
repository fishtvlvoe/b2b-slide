# -*- coding: utf-8 -*-
"""
B 組測試：驗證 story_map.py 故事地圖預覽工具
被測目標：scripts/story_map.py <SSOT路徑> --out <html路徑> [--no-browser]
"""

import re
import subprocess
import sys
from pathlib import Path
from bs4 import BeautifulSoup

REPO_ROOT = Path(__file__).resolve().parent.parent
SSOT_FIXTURE = REPO_ROOT / "scripts" / "fixtures" / "ssot" / "valid_bni_ssot.md"
SCRIPT_PATH = str(REPO_ROOT / "scripts" / "story_map.py")

EXPECTED_TITLES = [
    "5 分鐘搞定 B2B 高成交通報簡報",
    "業務主管半夜還在拉 PPT 方塊",
    "市面 AI 生出一堆假大空科幻廢話",
    "思維引導型商業顧問 Agent",
    "顧問訪談一題一問與 8 切角深挖",
    "標準四步法 SSOT 中繼稿",
    "HTML 故事地圖全局預覽",
    "5 頁多版型樣品批註鎖定風格",
    "100% DrawingML 原生可編輯交付",
    "每頁自帶講者口語備忘提示",
    "手下無企劃的 B2B 中小企業老闆",
    "立刻預約 15 分鐘顧問諮詢體驗",
]


def _calc_color_luminance(color_str: str) -> float:
    """計算顏色亮度 (0.0 ~ 1.0)"""
    color = color_str.strip().lower()
    # 支援 #fff 或 #ffffff
    hex_match = re.match(r"^#([0-9a-f]{3}|[0-9a-f]{6})$", color)
    if hex_match:
        hex_val = hex_match.group(1)
        if len(hex_val) == 3:
            r = int(hex_val[0] * 2, 16)
            g = int(hex_val[1] * 2, 16)
            b = int(hex_val[2] * 2, 16)
        else:
            r = int(hex_val[0:2], 16)
            g = int(hex_val[2:4], 16)
            b = int(hex_val[4:6], 16)
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

    # 支援 rgb(r, g, b)
    rgb_match = re.match(r"^rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$", color)
    if rgb_match:
        r = int(rgb_match.group(1))
        g = int(rgb_match.group(2))
        b = int(rgb_match.group(3))
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0

    if color in ("white", "#fff", "#ffffff"):
        return 1.0
    return 0.0


def test_page_count_matches(tmp_path):
    """情境：合法 12 頁中繼稿，預期產出 html 內頁卡數量 = 12"""
    out_html = tmp_path / "02-故事地圖.html"
    result = subprocess.run(
        [
            sys.executable,
            SCRIPT_PATH,
            str(SSOT_FIXTURE),
            "--out",
            str(out_html),
            "--no-browser",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"故事地圖生成失敗，退出碼：{result.returncode}，輸出：\n{result.stderr}"
    assert out_html.exists(), "產出之 html 檔案不存在"

    soup = BeautifulSoup(out_html.read_text(encoding="utf-8"), "html.parser")
    cards = soup.select(".slide-card, .card, [data-slide-index], .story-card, article.slide")
    assert len(cards) == 12, f"預期頁卡數量為 12，實際為 {len(cards)}"


def test_page_order_matches(tmp_path):
    """情境：合法 12 頁中繼稿，預期 html 內頁卡標題順序與中繼稿一致"""
    out_html = tmp_path / "02-故事地圖.html"
    result = subprocess.run(
        [
            sys.executable,
            SCRIPT_PATH,
            str(SSOT_FIXTURE),
            "--out",
            str(out_html),
            "--no-browser",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"故事地圖生成失敗，退出碼：{result.returncode}，輸出：\n{result.stderr}"
    assert out_html.exists(), "產出之 html 檔案不存在"

    html_content = out_html.read_text(encoding="utf-8")
    last_pos = -1
    for title in EXPECTED_TITLES:
        pos = html_content.find(title)
        assert pos != -1, f"HTML 中未找到預期標題：{title}"
        assert pos > last_pos, f"標題順序錯誤：{title} 應排在上一標題之後"
        last_pos = pos


def test_no_emoji_light_bg(tmp_path):
    """情境：合法 12 頁中繼稿，預期 html 無 Emoji 字元（Unicode emoji 範圍），body 背景色為淺色（亮度 > 0.85）"""
    out_html = tmp_path / "02-故事地圖.html"
    result = subprocess.run(
        [
            sys.executable,
            SCRIPT_PATH,
            str(SSOT_FIXTURE),
            "--out",
            str(out_html),
            "--no-browser",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"故事地圖生成失敗，退出碼：{result.returncode}，輸出：\n{result.stderr}"
    assert out_html.exists(), "產出之 html 檔案不存在"

    html_content = out_html.read_text(encoding="utf-8")

    # 1. Emoji 檢測（常見 Emoji Unicode 範圍）
    emoji_regex = re.compile(
        r"[\U0001F600-\U0001F64F]"  # 表情
        r"|[\U0001F300-\U0001F5FF]"  # 符號與象形文字
        r"|[\U0001F680-\U0001F6FF]"  # 交通與地圖
        r"|[\U0001F700-\U0001F77F]"  # 煉金術符號
        r"|[\U0001F780-\U0001F7FF]"  # 幾何形狀擴展
        r"|[\U0001F800-\U0001F8FF]"  # 箭頭擴展
        r"|[\U0001F900-\U0001F9FF]"  # 補充符號
        r"|[\U0001FA00-\U0001FA6F]"  # 象棋與符號
        r"|[\U0001FA70-\U0001FAFF]"  # 符號與圖形擴展
        r"|[\u2600-\u26FF]"          # 雜項符號
        r"|[\u2700-\u27BF]"          # 裝飾符號
    )
    assert not emoji_regex.search(html_content), "HTML 內容中發現 Emoji 字元，違反去 AI 味規範"

    # 2. 檢測 body 背景色亮度
    bg_match = re.search(r"body\s*\{[^}]*background(?:-color)?:\s*([^;}\n]+)", html_content, re.IGNORECASE)
    if not bg_match:
        # 也支援 inline style: <body style="background: ...">
        bg_match = re.search(r"<body[^>]*style=[\"'][^\"']*background(?:-color)?:\s*([^;\"]+)", html_content, re.IGNORECASE)

    assert bg_match, "HTML 中未找到 body 背景色樣式定義"
    bg_color = bg_match.group(1).strip()
    luminance = _calc_color_luminance(bg_color)
    assert luminance > 0.85, f"背景色亮度過低（{luminance:.2f} <= 0.85，顏色為 {bg_color}），必須為淺色底"


def test_text_fallback_printed(tmp_path):
    """情境：加 --no-browser，預期 stdout 印出純文字頁序（含每頁頁碼與標題）"""
    out_html = tmp_path / "02-故事地圖.html"
    result = subprocess.run(
        [
            sys.executable,
            SCRIPT_PATH,
            str(SSOT_FIXTURE),
            "--out",
            str(out_html),
            "--no-browser",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"執行失敗，退出碼：{result.returncode}，輸出：\n{result.stderr}"

    stdout = result.stdout
    # 檢查每頁頁碼
    for i in range(1, 13):
        page_tag = f"P{i:02d}"
        assert page_tag in stdout, f"純文字 fallback 輸出中缺少頁碼：{page_tag}"

    # 檢查每頁標題
    for title in EXPECTED_TITLES:
        assert title in stdout, f"純文字 fallback 輸出中缺少標題：{title}"

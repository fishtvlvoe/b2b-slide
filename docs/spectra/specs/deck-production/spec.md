# deck-production Specification

## Purpose

Defines how a confirmed SSOT becomes a native editable PowerPoint deck through ppt-master, with a five-slide style sample reviewed in the browser before full production. It exists so style mistakes cost five slides, not forty, and so the final file stays editable in PowerPoint.

## Requirements

### Requirement: Handoff package

Before rendering, the agent SHALL write `03-ppt-master-交接包.md` containing the confirmed SSOT, the presentation spec constraints (light background, type scale Hero 42 / Title 34 / Subtitle 24 / Card Title 20 / Body 18 / Caption 14-16 on a 1280x720 canvas, banned gradients, neon, 3D figures and uniform three-card grids), and the five sample slides chosen.

#### Scenario: Handoff package written

- **WHEN** the user confirms the story map
- **THEN** `03-ppt-master-交接包.md` exists with the SSOT, constraints, and five sample slide numbers

---
### Requirement: Five-slide style sample

The agent SHALL render exactly five slides first, chosen from the plan so that at least four different layout types appear (for example data chart, category grid, side-by-side comparison, timeline, anchor statement), and SHALL start the ppt-master browser preview and report its localhost address.

#### Scenario: Sample rendered with varied layouts

- **WHEN** sample rendering finishes
- **THEN** five slides exist, at least four layout types are represented, and the preview address is shown to the user

##### Example: plan shorter than five slides

| Planned slides | Sample size |
| --- | --- |
| 20 | 5 |
| 5 | 5, then full production renders nothing extra |
| 3 | 3, all slides |

---
### Requirement: Annotation review loop

The user SHALL be able to change colors, fonts, sizes and positions, insert their own photo, an SVG icon or a simple geometric shape, or leave annotations in the preview; the agent SHALL read the changes and annotations back and revise the sample. The style SHALL be locked into ppt-master's spec lock only after the user explicitly says the style is confirmed.

#### Scenario: Annotation applied

- **WHEN** the user annotates slide 2 "標題改成極簡、旁邊放一個 icon" and submits
- **THEN** the agent revises slide 2 accordingly and asks the user to review again

#### Scenario: Preview unavailable fallback

- **WHEN** the localhost preview cannot be opened
- **THEN** the agent exports PNG previews of the five slides and accepts text feedback instead

---
### Requirement: Full production and export

After style confirmation the agent SHALL render the remaining slides with the locked style, run ppt-master quality checks, and export `04-<presentation-name>.pptx` where every slide uses native editable text boxes and shapes and has non-empty speaker notes.

#### Scenario: Final deck verified

- **WHEN** export finishes
- **THEN** reading the pptx with python-pptx shows every slide has at least one editable text frame, non-empty notes, and no full-slide picture, and the agent reports the file path and slide count

---
### Requirement: Slide content grounded in SSOT

Every text element on rendered slides SHALL come from the confirmed SSOT (titles, content points, speaker talking points) or files the user provided. The agent MUST NOT add facts, numbers, percentages, durations, frequencies, equipment, procedures or promises that are absent from those sources. When a slide has little content, the agent SHALL use whitespace (Anchor or Breathing rhythm) instead of filler text. A checker `scripts/check_grounding.py <pptx> <ssot>` SHALL report every number on the slides that does not appear in the SSOT and exit non-zero when any is found.

#### Scenario: Invented statistic is rejected

- **WHEN** a slide contains "噪音降低 45%" and the SSOT never mentions 45
- **THEN** `check_grounding.py` exits non-zero and lists "45%" with its slide number

##### Example: number grounding

| Slide text | SSOT contains | Result |
| --- | --- | --- |
| "先陪牠玩 10 分鐘" | "10 分鐘" | pass |
| "到府前 15 分鐘 LINE 通知" | no "15" | fail, slide lists 15 |
| "每 3 分鐘稍作撫觸" | no "3 分鐘" | fail |
| "P05 / 08" page number | not required | ignored |

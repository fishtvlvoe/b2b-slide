## Purpose

Defines the HTML story map that lets a terminal user see the whole slide order before any slide is drawn. It exists because terminal interfaces show only text and ordering mistakes are expensive to fix after rendering.

## ADDED Requirements

### Requirement: Story map generation

After SSOT confirmation, the agent SHALL generate `02-故事地圖.html` in the presentation folder showing every planned slide in order with its one-sentence title, four-step segment, and rhythm type, using a light background, SVG icons, and no emoji.

#### Scenario: Story map created from SSOT

- **WHEN** the user confirms the SSOT
- **THEN** `02-故事地圖.html` exists and lists the same slide count and order as the SSOT

### Requirement: Open in browser with text fallback

The agent SHALL open the story map in the default browser and SHALL also print a plain-text slide list in the conversation.

#### Scenario: Browser cannot be opened

- **WHEN** opening the browser fails
- **THEN** the agent reports the file path and the plain-text slide list is still shown

### Requirement: Order changes flow back to SSOT

Slide order or content changes requested at the story map stage SHALL be written to `01-中繼-SSOT.md` first and the story map SHALL be regenerated from it.

#### Scenario: User swaps two slides

- **WHEN** the user asks to swap slide 4 and slide 5
- **THEN** the SSOT is updated and the regenerated story map shows the new order

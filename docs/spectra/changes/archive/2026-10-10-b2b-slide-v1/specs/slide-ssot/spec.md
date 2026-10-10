## Purpose

Defines the intermediate Markdown single source of truth that captures every business decision of a presentation before any visual work. It exists so layout tools only render confirmed content and never invent it.

## ADDED Requirements

### Requirement: SSOT file location and structure

After the interview, the agent SHALL write `01-中繼-SSOT.md` inside a per-presentation folder named `<YYYY-MM-DD>-<presentation-name>` under the user's workspace folder. The file SHALL contain a core positioning section (presentation type, core claim, opening hook, step-four content) and a per-slide plan where each slide lists page number, one-sentence conclusion title, four-step segment, rhythm type (Anchor, Dense, Breathing), content points, and speaker talking points.

#### Scenario: SSOT written after interview

- **WHEN** all five interview phases have recorded answers
- **THEN** the agent writes `01-中繼-SSOT.md` with both sections in the presentation folder

### Requirement: Required field gate

The agent MUST check every required field before presenting the SSOT and MUST NOT proceed to the story map while any required field is empty.

#### Scenario: Missing field blocks progress

- **WHEN** the per-slide plan has a slide without a four-step segment
- **THEN** the agent asks the one question needed to fill it and does not generate the story map

##### Example: required field check

| Field state | Result |
| --- | --- |
| all fields present | SSOT presented for confirmation |
| core claim empty | asks for core claim |
| slide 3 rhythm type empty | asks for slide 3 rhythm |

### Requirement: Four-step order in slide plan

The per-slide plan SHALL order slides so that conclusion slides precede problem slides, problem slides precede how slides, and the type-specific step-four slide is last before any closing slide.

#### Scenario: Out-of-order plan is corrected

- **WHEN** a draft plan places a pricing or how slide before the problem slide
- **THEN** the agent reorders it to conclusion, problem, how, step four before presenting

##### Example: reorder

- **GIVEN** draft order: P01 conclusion, P02 pricing (how), P03 problem, P04 referral (step four)
- **WHEN** the agent validates the plan
- **THEN** the presented order is P01 conclusion, P02 problem, P03 pricing (how), P04 referral (step four)

### Requirement: Explicit user confirmation

The agent SHALL advance past the SSOT only after the user explicitly confirms it; edits requested by the user SHALL be applied to the same file before asking for confirmation again.

#### Scenario: User requests a change

- **WHEN** the user asks to change the opening hook
- **THEN** the agent updates `01-中繼-SSOT.md` and asks for confirmation again without generating the story map

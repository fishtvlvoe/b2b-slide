# interview-engine Specification

## Purpose

Defines the one-question-at-a-time consultant interview that extracts a user's real business context for an outward-facing business presentation, following the four-step sequence (conclusion, problem, how, who fits). It exists so any terminal AI produces the same disciplined interview instead of one-click generated filler.

## Requirements

### Requirement: Presentation type selection

The agent SHALL begin each new presentation by asking for the presentation type as an open question and SHALL classify the answer into exactly one of: client-proposal, bni-feature, company-product-intro, partnership-invite. When the answer fits none of these (for example an internal monthly report or a course deck), the agent SHALL state that version 1 does not support it and SHALL NOT start the interview.

#### Scenario: Supported type is classified

- **WHEN** the user answers the type question
- **THEN** the agent records one of the four supported types and proceeds to phase 1

##### Example: classification table

| User answer | Classified type | Interview starts |
| --- | --- | --- |
| "下週要跟大客戶報價提案" | client-proposal | yes |
| "BNI 8 分鐘專題" | bni-feature | yes |
| "介紹我們公司的新產品" | company-product-intro | yes |
| "想找異業結盟夥伴" | partnership-invite | yes |
| "部門月報" | unsupported | no, explains v1 scope |
| "上課用的投影片" | unsupported | no, explains v1 scope |

---
### Requirement: One question per message

In the default one-at-a-time mode, every agent message during the interview MUST contain at most one question to the user and MUST NOT offer lettered or numbered answer choices for an open question. A recommended answer line is not an answer choice.

#### Scenario: Single question enforced

- **WHEN** the agent sends any interview message in one-at-a-time mode
- **THEN** the message contains no more than one question mark directed at the user and no lettered or numbered answer choices

##### Example: message checks

| Agent message | Passes |
| --- | --- |
| "這次簡報你最想讓對方帶走的一句話是什麼？" | yes |
| "你的客戶是誰？他們卡在哪裡？" | no, two questions |
| "你想強調：A. 效率 B. 成本 C. 品質？" | no, preset options |
| "你的目標客戶是誰？ ➡️ 建議：依你剛才說的，是沒有企劃人員的中小企業老闆" | yes, one question with a recommendation |

---
### Requirement: Round mode on request

When the user asks to go faster (for example "快一點" or "一次問完"), the agent SHALL switch to round mode: each message asks every question whose prerequisites are already settled, numbered, each followed either by its own recommended answer line or, when the grounded-recommendation rule forbids one (first question of the interview, or no user material), by an explicit marker line `➡️（無素材，不附建議）`, and SHALL NOT include a question that depends on another question still open in the same round. The user SHALL be able to switch back to one-at-a-time mode at any time.

#### Scenario: Switch to round mode

- **WHEN** the user says "一次問完" during phase 3
- **THEN** the next agent message lists the remaining independent questions numbered Q1, Q2, ... each with a recommended answer or the no-material marker, and the user can reply by number

##### Example: dependency kept out of the same round

- **GIVEN** the presentation type is still unanswered
- **WHEN** the agent builds a round
- **THEN** the type-specific phase 5 question is not in that round

---
### Requirement: Grounded recommended answers

From the second question onward, each question SHALL carry one recommended answer, worded so that replying "對" accepts it. The recommendation MUST be built only from what the user has said earlier in this presentation's interview or from files the user provided, and MUST NOT introduce facts, numbers, names or claims the user has not given. The first question of the interview (the first question the agent asks, whether sent alone or as Q1 of a round) SHALL carry no recommendation. When nothing grounded is available, the agent SHALL ask the question without a recommendation.

#### Scenario: Recommendation uses only user material

- **WHEN** the user earlier said their clients are "沒有企劃的中小企業老闆" and the agent asks about the ideal referral target
- **THEN** the recommendation reuses that wording and contains no new company names, numbers or claims

#### Scenario: Nothing to ground on

- **WHEN** the agent asks a question whose topic the user has not touched and no provided file covers
- **THEN** the question is sent without a recommended answer

---
### Requirement: Faithful transcript and quoted echoes

The agent SHALL write each interview message to `00-訪談逐字稿.md` exactly as it was sent to the user, without adding or removing questions. When a message echoes the user's own words (summaries, confirmations), the echoed words SHALL be wrapped in 「」, and question marks inside 「」 SHALL NOT count as questions asked by the agent.

#### Scenario: Echoed hook question is not counted

- **WHEN** a phase summary echoes the user's hook 「你的員工每天走了多少冤枉路？」 and then asks 「這句話你想調整哪裡？」
- **THEN** the message counts as one question and passes the one-question check

#### Scenario: Transcript differs from sent message

- **WHEN** the sent message contains one question but the transcript entry for it contains an extra template question
- **THEN** this is a defect; the transcript entry MUST match the sent message

---
### Requirement: Phase-end active edit

At the end of each phase the agent SHALL present a phase summary and SHALL NOT advance until the user has changed or added at least one piece of wording. A bare acceptance such as "對", "好", "OK" or "沒問題" SHALL be answered by asking which word or sentence the user wants to adjust or add.

#### Scenario: Bare acceptance at phase end

- **WHEN** the user replies "對" to the phase 2 summary
- **THEN** the agent asks the user to change or add at least one sentence and stays in phase 2

---
### Requirement: Provided files read before asking

When the user provides files (for example a company profile, quotation or meeting transcript), the agent SHALL read them before asking, SHALL record which interview fields they answer, and SHALL NOT ask the user for information already found in them; it SHALL instead show the extracted value as the recommended answer for confirmation.

#### Scenario: Quotation already answers pricing

- **WHEN** the user provides a quotation file that lists two plans and their prices
- **THEN** the agent does not ask for prices and presents the extracted plans as the recommendation in phase 4

---
### Requirement: Five-phase state machine

The interview SHALL progress through five phases in fixed order: core conclusion, opening hook, current problem with concrete scene, solution and deliverables, and the type-specific step four. The agent SHALL NOT advance to the next phase until the current phase has a recorded answer.

#### Scenario: Phases advance in order

- **WHEN** the user answers the phase 2 question
- **THEN** the agent records the hook and asks the phase 3 question, never skipping to phase 4 or 5

---
### Requirement: Type-specific step four

Phase 5 SHALL ask the question that matches the recorded presentation type.

#### Scenario: Step four question varies by type

- **WHEN** the interview reaches phase 5
- **THEN** the question asked matches the type mapping

##### Example: step four mapping

| Type | Phase 5 asks about |
| --- | --- |
| client-proposal | the decision the client must make next and its approval conditions |
| bni-feature | the ideal referral target and a one-sentence introduction others can repeat |
| company-product-intro | which customers fit best and in what situation they think of the user |
| partnership-invite | what partner is wanted and what each side gains |

---
### Requirement: Concrete noun-and-verb follow-up

When an answer relies on abstract adjectives without an observable action, the agent SHALL ask a follow-up requesting the concrete action or scene.

#### Scenario: Abstract answer triggers follow-up

- **WHEN** the user answers "客戶很困擾、效率很差"
- **THEN** the agent asks what specific action the customer was doing when stuck, instead of advancing

---
### Requirement: Eight-lens rotation with follow-up cap

When an answer is vague, the agent SHALL follow up using one of the eight lenses (money, time, emotion, expectation, generation, person, inverse, scene) not yet used in the current phase. The agent SHALL ask at most 3 follow-ups per phase; after the third it SHALL summarize what it has and ask the user to confirm or correct the summary.

#### Scenario: Follow-up cap reached

- **WHEN** the user has given 3 vague answers in the same phase
- **THEN** the agent presents a summary of the phase and asks for confirmation instead of a fourth lens question

---
### Requirement: No one-click generation

The agent MUST refuse to generate a full deck without completing the interview and SHALL return to the current phase question.

#### Scenario: User asks to skip the interview

- **WHEN** the user says "直接幫我生成整份簡報"
- **THEN** the agent explains the tool does not do one-click generation and repeats the current phase question

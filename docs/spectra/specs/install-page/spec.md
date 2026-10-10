# install-page Specification

## Purpose

Defines the public HTML install page that is the single link students receive. It exists so students can install by copying one sentence or one command without reading the repository.

## Requirements

### Requirement: Public install page content

The repository SHALL publish an install page at `https://fishtvlvoe.github.io/b2b-slide/` containing, in order: a download link for the Claude desktop app, a copyable install sentence for the Claude app, copyable terminal commands for macOS and Windows, the first message to start a presentation, and a troubleshooting section covering missing Python and stuck installs. The page SHALL use a light background, SVG icons and no emoji, and SHALL be readable at 375px width without horizontal scrolling.

#### Scenario: Student copies the install sentence

- **WHEN** a student clicks the copy button next to the install sentence
- **THEN** the exact sentence referencing `github.com/fishtvlvoe/b2b-slide` is in the clipboard

#### Scenario: Mobile width

- **WHEN** the page is viewed at 375px width
- **THEN** all sections are readable and no horizontal scroll bar appears

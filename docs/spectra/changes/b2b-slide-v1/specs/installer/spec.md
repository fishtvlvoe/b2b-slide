## Purpose

Defines how a student installs the agent on their own macOS or Windows computer with one pasted sentence or one command, including the pinned ppt-master download and a self-test. It exists so students who cannot use a terminal still get a working setup.

## ADDED Requirements

### Requirement: AI-readable install guide

The repository SHALL contain `INSTALL-FOR-AI.md` that an AI agent can follow to install on macOS or Windows: detect the operating system, check Python 3 and git, download ppt-master at the tag in `ppt-master.lock`, install its Python dependencies, place the tool in a hidden tool folder (`~/.b2b-slide/`), create the student workspace folder (`~/b2b-slide-簡報/`) with entry files `AGENTS.md`, `CLAUDE.md` and `GEMINI.md`, and run the self-test.

#### Scenario: Install via pasted sentence

- **WHEN** a student pastes the install sentence into the Claude desktop app Code tab
- **THEN** the AI completes installation and prints one line naming the ppt-master tag, the Python version and the self-test result

### Requirement: Terminal one-liners

The repository SHALL provide `install.sh` for macOS and `install.ps1` for Windows that perform the same steps as the install guide.

#### Scenario: macOS terminal install

- **WHEN** a user runs the curl one-liner from the install page on macOS
- **THEN** the same tool folder, workspace folder and self-test result are produced as the AI-guided install

### Requirement: Pinned ppt-master version

The installer MUST read the ppt-master tag from `ppt-master.lock` and MUST NOT install an unpinned latest version.

#### Scenario: Lock file drives version

- **WHEN** `ppt-master.lock` contains `tag=v6.7.0`
- **THEN** the installed ppt-master checkout is at tag v6.7.0

### Requirement: Safe failure

When Python or git is missing or the download fails, the installer SHALL stop, leave no partial tool folder, and tell the user the exact next step. It MUST NOT request administrator privileges on its own.

#### Scenario: Python missing

- **WHEN** no Python 3 is found
- **THEN** installation stops with a message pointing to python.org and `~/.b2b-slide/` does not exist afterwards

### Requirement: No author-machine dependencies

Installed files MUST NOT reference paths from the author's machine.

#### Scenario: Author path scan

- **WHEN** the shipped agent and install files are searched for "/Users/fishtv"
- **THEN** there are zero matches outside developer-only Spectra configuration

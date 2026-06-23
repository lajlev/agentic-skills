# Agent Templates

Drop-in starter kit for personalized AI coding agents. Clone the repo into your workspace and let the runtime generate a merged `AGENTS.md` from system rules plus the editable custom block in `CUSTOM_INSTRUCTIONS.md`.

## How It Works

- `AGENTS.md` is runtime-managed and read-only.
- `AGENTS.md` includes the compiled custom block from `CUSTOM_INSTRUCTIONS.md`.
- `CUSTOM_INSTRUCTIONS.md` holds onboarding answers, personality, tone, timezone, and workspace preferences.
- `skills/skills-registry.md` tracks installed skills and skill coverage.
- `skills/skill-operations.md` describes how to add, update, or retire skills.

## First Run

- Start with `CUSTOM_INSTRUCTIONS.md` in `onboarding_status: pending`.
- The runtime compiles `CUSTOM_INSTRUCTIONS.md` into `AGENTS.md`, so the agent sees the onboarding instructions in its main prompt surface.
- The agent should ask the onboarding questions once, write the answers back into `CUSTOM_INSTRUCTIONS.md`, and mark onboarding complete.
- After that, future sessions should keep using the compiled `AGENTS.md` plus the updated `CUSTOM_INSTRUCTIONS.md` source file.

## Customization

- Update `CUSTOM_INSTRUCTIONS.md` to change assistant identity, tone, or workflow preferences.
- Update the skills files when recurring tasks should become reusable capabilities.

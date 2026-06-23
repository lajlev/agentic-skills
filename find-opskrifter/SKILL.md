---
name: find-opskrifter
description: "Find opskrifter i Firestore ud fra bestemte ingredienser. Brug altid Firestore-klienten og vis tider som fx Forberedelse: 45min (ikke PT45M)."
---

# Find Opskrifter

Brug denne skill, når brugeren vil finde opskrifter ud fra én eller flere ingredienser.

Datakilde:
- project: `lillefar-com`
- database: `recipes`
- collections: `recipes`, `ingredients`

Krav:
- Brug altid Firestore-klienten (`google.cloud.firestore`).
- Brug aldrig Datastore-klienten til denne skill.
- Vis aldrig rå ISO-varighed (`PT45M`) i brugeroutput.
- Brug i stedet menneskeligt format, fx `Forberedelse: 45min` og `Tilberedning: 35min`.
- Når brugeren beder om opskrift, skriv altid labels med formatet:
  - `Forberedelse: <tid>`
  - `Tilberedning: <tid>`
  - Eksempel: `Forberedelse: 45min` (ikke `Forberedelse: PT45M`)

## Workflow

1. Kør via den fælles venv-runner i `/workspace`:
```bash
scripts/venv_run.sh --version
```

2. Kør scriptet fra `/workspace`:
```bash
scripts/venv_run.sh skills/find-opskrifter/scripts/find_recipes.py \
  --query "Find 3 opskrifter der bruger broccoli og nudler"
```

3. Standard matcher alle ingredienser.
- Brug `--any`, hvis mindst én ingrediens er nok.

4. Svar med:
- titel,
- id,
- formateret tid (`Forberedelse`, `Tilberedning`),
- ét konkret ingrediens-hit.
- Telegram-format: ren tekst uden markdown-tabeller, overskrifter, fed/kursiv, kodeblokke eller markdown-links.

## Argumenter

- `--query`: naturligt sprog, fx `Find 3 opskrifter der bruger broccoli og nudler`.
- `--ingredients` / `-i`: eksplicitte ingredienser.
- `--limit` / `-n`: antal resultater (default `3`).
- `--database`: Firestore database-id (default `recipes`).
- `--scan-limit`: hvor mange docs der scannes (default `3000`).
- `--any`: match mindst én ingrediens.
- `--json`: JSON-output.

## Miljø

Nødvendige secrets/env vars:
- `GOOGLE_APPLICATION_CREDENTIALS_JSON`
- `FIRESTORE_PROJECT_ID`

Hvis de mangler, bed brugeren tilføje dem via Secrets-panelet.

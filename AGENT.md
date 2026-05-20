# AGENT.md

This file is the global Codex entrypoint for work in this repository.

## Goal

Keep the default context small, then load only the specialist agent that matches the task.
Use this file for shared rules only. Use `.github/agents/*.agent.md` for domain-specific guidance.

## Project Snapshot

- Project: `zendure-local-ha`
- Type: Home Assistant custom integration
- Domain: `zendure_local`
- Device family: Zendure SolarFlow hub-based devices
- Runtime model: local REST polling every 30 seconds
- Constraints: no cloud, no MQTT, HACS-compatible
- Stack: Python 3.12+, Home Assistant, pytest, GitHub Actions

## Global Rules

1. Preserve the local-first architecture: no cloud dependency, no webhook, no MQTT.
2. Route all device I/O through `custom_components/zendure_local/coordinator.py`.
3. Keep changes aligned with Home Assistant patterns and async expectations.
4. Add or update tests for behavior changes.
5. Keep user-facing strings synchronized in `strings.json`, `translations/en.json`, and `translations/fr.json`.
6. Use Conventional Commits when preparing commits.

## Agent Routing

- Use `.github/agents/integration-dev.agent.md` for entities, coordinator, config flow, translations, and integration behavior.
- Use `.github/agents/tests-review.agent.md` for test additions, regression analysis, and review-oriented work.
- Use `.github/agents/ci-release.agent.md` for GitHub Actions, release automation, packaging, and repo hygiene.
- Use `.github/agents/docs-maintainer.agent.md` for README, CONTRIBUTING, badges, release notes, and public-repo polish.

## Shared Commands

```bash
source .venv/bin/activate
pip install -r requirements_test.txt
pytest
pytest --cov
```

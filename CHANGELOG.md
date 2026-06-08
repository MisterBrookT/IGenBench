# Changelog

All notable changes to IGenBench are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/);
versioning follows [PEP 440](https://peps.python.org/pep-0440/).

---

## [0.1.0] — 2026-06

### Added
- `igenbench gen` — generate a single infographic from a VISItem JSON
- `igenbench eval` — evaluate a single generated image against benchmark questions
- `igenbench batch-gen` — generate infographics for the full dataset with `--resume`
- `igenbench batch-eval` — evaluate the full dataset with `--resume`
- `igenbench score` — aggregate Q-ACC / I-ACC scores with optional `--by-source` / `--by-type` breakdown
- Provider support: Google (Gemini), OpenRouter, Replicate
- `@register_caller` plugin API for adding custom LLM providers
- `VISItem` data model with full JSON serialisation
- Incremental progress: every question result is saved immediately so interrupted runs resume cleanly
- ACL 2026 camera-ready release

### Fixed
- Align default evaluation model and README examples with the paper's `gemini-2.5-pro` setting.

# AGENTS.md — IGenBench Codebase Guide for AI Coding Agents

This file helps AI agents (Claude Code, GitHub Copilot, Cursor, etc.) navigate and modify this codebase correctly.

---

## What This Project Does

IGenBench is a CLI benchmark tool for evaluating the **reliability** of text-to-infographic generation models. Given a dataset of `VISItem` JSON files (each containing a prompt, reference image, and evaluation questions), it:

1. **Generates** infographics using a text-to-image model (`igenbench gen` / `igenbench batch-gen`)
2. **Evaluates** generated images by asking an LLM to answer factual Q&A questions about the image (`igenbench eval` / `igenbench batch-eval`)
3. **Scores** the results to compute Q-ACC and I-ACC metrics (`igenbench score`)

---

## Architecture

```
CLI (typer)
  └── Workflow (orchestration + resume logic)
        └── Engine (single-item gen/eval step)
              └── LLMCaller (provider abstraction)
                    ├── GoogleCaller
                    ├── OpenrouterCaller
                    └── ReplicateCaller
```

### Key Files

| File | Purpose |
|------|---------|
| `igenbench/vis_item.py` | Core data model. **Read this first.** |
| `igenbench/cli/main.py` | Typer app; registers all sub-commands |
| `igenbench/cli/gen_cli.py` | `igenbench gen` command |
| `igenbench/cli/eval_cli.py` | `igenbench eval` command |
| `igenbench/cli/batch_cli.py` | `igenbench batch-gen` and `batch-eval` |
| `igenbench/cli/score_cli.py` | `igenbench score` command |
| `igenbench/workflow/gen_workflow.py` | Generation orchestration |
| `igenbench/workflow/eval_workflow.py` | Evaluation orchestration with resume |
| `igenbench/engine/gen_engine.py` | Calls LLMCaller.generate_image for one item |
| `igenbench/engine/eval_engine.py` | Calls LLMCaller.understand_image + parses answer |
| `igenbench/utils/llm/llm_caller.py` | All provider implementations + `LLMCaller` base |
| `igenbench/utils/llm/caller_registry.py` | `@register_caller` decorator + lookup |
| `igenbench/utils/state_manager.py` | Reads/writes VISItem JSON to disk |
| `igenbench/utils/path_resolver.py` | Resolves output paths from item id + model name |
| `prompts/gen_text2image.py` | Prompt template for image generation |
| `prompts/eval_judge_factual_qa.py` | Prompt template for evaluation |

---

## Data Model

```python
VISItem
  id: str                        # e.g. "001"
  t2i_prompt: str                # generation prompt
  chart_type: str                # e.g. "bar", "pie"
  reference_image_url: str       # URL of ground-truth image
  generation: dict[model, path]  # generated image paths keyed by model name
  evaluation: list[EvalEntry]

EvalEntry
  source: str          # "prompt" | "seed"
  question: str        # e.g. "How many bars are there?"
  ground: str          # ground-truth answer
  question_type: str   # reliability dimension (e.g. "count", "ordering")
  judgments: list[Judgment]

Judgment
  gen_model: str       # model that generated the image
  eval_model: str      # model that evaluated it
  analysis: str        # chain-of-thought reasoning
  answer: str          # "1" (correct) or "0" (incorrect)
```

All items are serialised to `{output_dir}/{item_id}/{item_id}.json`.

---

## How to Add a New Provider

```python
# igenbench/utils/llm/llm_caller.py
from .caller_registry import register_caller
from .llm_caller import LLMCaller

@register_caller("my_provider")
class MyProviderCaller(LLMCaller):
    def __init__(self) -> None:
        # initialise your SDK / client here
        pass

    def generate_image(self, model: str, prompt: str, **kwargs):
        # return a PIL.Image.Image
        ...

    def understand_image(self, model: str, prompt: str, image_path: str, **kwargs) -> str:
        # return the model's text response
        ...
```

Then call with `--provider my_provider`.

---

## Dev Commands

```bash
# Install (including dev deps)
uv sync --dev

# Lint
uv run ruff check .

# Format
uv run ruff format .

# Tests (no API keys needed)
uv run pytest tests/ -v

# Run a single gen (requires GOOGLE_API_KEY)
uv run igenbench gen \
  --info-path hf_datasets/data/1.json \
  --output-dir outputs/ \
  --provider google \
  --model gemini-2.5-flash-image
```

---

## Output Directory Layout

```
outputs/
└── {item_id}/
    ├── {item_id}.json          # VISItem state (generation + evaluation results)
    └── {gen_model}/
        └── {item_id}.png       # generated image
```

---

## Common Mistakes to Avoid

- **Never** add API keys to source files. Use environment variables (see `.env.example`).
- `VISItem.from_dict(path)` takes a **file path**, not a dict.
- `EvalEntry.judgments` is a list — multiple (gen_model, eval_model) pairs can coexist on the same question (multi-model comparison).
- The `Question` dataclass in `vis_item.py` is **deprecated** and will be removed in a future version. Migrate to `EvalEntry`: replace `q` → `question`, `q_ground` → `ground`, `q_type` → `question_type`, and use `VISItem.evaluation: list[EvalEntry]` instead of a separate JSONL questions file.
- When editing CLI commands, register them via `igenbench/cli/main.py` imports (side-effect import pattern).

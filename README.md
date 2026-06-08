<p align="center">
    <a href="">
<img width="600" alt="image" src="assets/title.jpg">
     </a>
   <p align="center">

<p align="center">
    <a href="https://arxiv.org/abs/2601.04498"><img src='https://img.shields.io/badge/arXiv-PDF-red?style=flat&logo=arXiv&logoColor=red' alt='arXiv PDF'></a>
    <a href="https://arxiv.org/abs/2601.04498"><img src='https://img.shields.io/badge/ACL-2026-blue?style=flat' alt='ACL 2026'></a>
    <a href="https://huggingface.co/datasets/Brookseeworld/IGenBench-Dataset"><img src="https://img.shields.io/static/v1?label=%F0%9F%A4%97%20Hugging%20Face&message=Dataset&color=yellow"></a>
    <a href='https://igen-bench.vercel.app/'><img src='assets/website.svg' alt='webpage-Web'></a>
</p>

![xbhs3](assets/igenbench.png)

## 📢 News
- **[2026-06]** 🎉 IGenBench has been accepted to **ACL 2026** (Main Conference)!

# 🔬 About

> Text-to-image models can generate visually appealing infographics — but are they *correct*?

**IGenBench** is an ACL 2026 benchmark for evaluating the **reliability** of text-to-infographic generation. We test whether generated infographics are factually correct, numerically accurate, and semantically faithful across **10 reliability dimensions** — covering 600 test cases and 10 state-of-the-art models.

## 🏆 Key Results

| Model | Q-ACC ↑ | I-ACC ↑ |
|-------|:-------:|:-------:|
| Nanobanana-Pro | **0.90** | **0.49** |
| Seedream-4.5 | 0.61 | 0.06 |
| GPT-Image-1.5 | 0.55 | 0.12 |
| Nanobanana | 0.48 | 0.02 |
| Qwen-Image | 0.36 | 0.01 |
| Z-Image-Turbo | 0.35 | 0.00 |
| P-Image | 0.34 | 0.00 |
| Image-01 | 0.13 | 0.00 |
| HIDream-I1 | 0.11 | 0.00 |
| FLUX.1-dev | 0.10 | 0.00 |

**Q-ACC**: question-level accuracy &nbsp;|&nbsp; **I-ACC**: infographic-level accuracy (all dimensions correct)

> The top model achieves Q-ACC of **0.90** but I-ACC of only **0.49** — high per-question accuracy does not guarantee a reliable infographic. Data-related dimensions (completeness, encoding, ordering) are universal bottlenecks with average accuracy below 0.30.

*Some model names follow the arXiv preprint; the camera-ready version will include updated names.*

**Reproducibility note:** the paper results in Section 5.4 were evaluated with `gemini-2.5-pro`.

---

# 🔨 Installation

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) as the package manager, then:

```bash
git clone https://github.com/MisterBrookT/IGenBench.git
cd IGenBench
uv sync
```

Or with pip:

```bash
pip install -e .
```

---

## 🔧 Prepare

### Download Dataset

```bash
mkdir hf_datasets && cd hf_datasets
hf download Brookseeworld/IGenBench-Dataset \
  --repo-type dataset --local-dir .
```

### Set API Keys

| Provider | Environment Variable | Supported Tasks |
|----------|---------------------|-----------------|
| Google | `GOOGLE_API_KEY` | Generation + Evaluation |
| OpenRouter | `OPENROUTER_API_KEY` | Generation + Evaluation |
| Replicate | `REPLICATE_API_TOKEN` | Generation only |

```bash
export GOOGLE_API_KEY="your-google-api-key"
export OPENROUTER_API_KEY="your-openrouter-api-key"
export REPLICATE_API_TOKEN="your-replicate-api-token"
```

For Replicate, install the extra dependency:

```bash
pip install "igenbench[replicate]"   # or: uv sync --extra replicate
```

---

# 💪 Usage

## Single Item

**Generate** an infographic from a text prompt:

```bash
igenbench gen \
  --info-path hf_datasets/data/1.json \
  --output-dir outputs/ \
  --provider google \
  --model gemini-2.5-flash-image
```

**Evaluate** a generated image against benchmark questions:

```bash
igenbench eval \
  --info-path hf_datasets/data/1.json \
  --gen-model gemini-2.5-flash-image \
  --output-dir outputs/ \
  --provider google \
  --model gemini-2.5-pro
```

<details>
<summary>All parameters</summary>

**`gen`**
- `--info-path`: Path to the VISItem JSON file
- `--output-dir`: Output directory (default: `outputs/`)
- `--provider`: LLM provider (default: `google`)
- `--model`: Generation model (default: `gemini-2.0-flash-exp`)
- `--resume`: Skip already-generated images

**`eval`**
- `--info-path`: Path to the VISItem JSON file
- `--gen-model`: Name of the model that generated the image *(required)*
- `--image-path`: Path to the image (auto-resolved from `--output-dir` if omitted)
- `--output-dir`: Output directory (default: `outputs/`)
- `--provider`: LLM provider (default: `google`)
- `--model`: Evaluation model (default: `gemini-2.5-pro`)
- `--resume`: Skip already-evaluated questions

</details>

## Batch Processing

Process the full dataset in one command. `--resume` is enabled by default so interrupted runs continue automatically.

```bash
# Generate
igenbench batch-gen \
  --data-dir hf_datasets/data/ \
  --output-dir outputs/ \
  --provider google \
  --model gemini-2.5-flash-image

# Evaluate
igenbench batch-eval \
  --data-dir hf_datasets/data/ \
  --gen-model gemini-2.5-flash-image \
  --output-dir outputs/ \
  --provider google \
  --model gemini-2.5-pro
```

## Score Aggregation

```bash
igenbench score --output-dir outputs/

# Filter by model + breakdown by question source and type
igenbench score \
  --output-dir outputs/ \
  --gen-model gemini-2.5-flash-image \
  --eval-model gemini-2.5-pro \
  --by-source --by-type
```

---

## Adding Custom Models

Implement a `LLMCaller` subclass in [`igenbench/utils/llm/llm_caller.py`](igenbench/utils/llm/llm_caller.py) and register it:

```python
from igenbench.utils.llm.caller_registry import register_caller
from igenbench.utils.llm.llm_caller import LLMCaller
from PIL.Image import Image as PILImage

@register_caller("my_provider")
class MyProviderCaller(LLMCaller):
    def __init__(self) -> None:
        pass  # initialize your API client

    def generate_image(self, model: str, prompt: str, **kwargs) -> PILImage: ...
    def understand_image(self, model: str, prompt: str, image_path: str, **kwargs) -> str: ...
```

Use it with `--provider my_provider`.

---

# 📝 Citation

If you find *IGenBench* useful for your research, please cite our paper:

```bibtex
@inproceedings{tang2026igenbench,
    title     = {IGenBench: Benchmarking the Reliability of Text-to-Infographic Generation},
    author    = {Yinghao Tang and Xueding Liu and Boyuan Zhang and Tingfeng Lan and Yupeng Xie and Jiale Lao and Yiyao Wang and Haoxuan Li and Tingting Gao and Bo Pan and Luoxuan Weng and Xiuqi Huang and Minfeng Zhu and Yingchaojie Feng and Yuyu Luo and Wei Chen},
    booktitle = {Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (ACL 2026)},
    year      = {2026},
    url       = {https://arxiv.org/abs/2601.04498},
}
```

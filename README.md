<p align="center">
    <a href="">
<img width="600" alt="image" src="assets/title.jpg">
     </a>
   <p align="center">

<p align="center">
    <a href="https://arxiv.org/abs/2601.04498"><img src='https://img.shields.io/badge/arXiv-PDF-red?style=flat&logo=arXiv&logoColor=red' alt='arXiv PDF'></a>
<a href="https://huggingface.co/datasets/Brookseeworld/IGenBench-Dataset"><img src="https://img.shields.io/static/v1?label=%F0%9F%A4%97%20Hugging%20Face&message=Dataset&color=yellow"></a>
    <a href='https://igen-bench.vercel.app/'><img src='assets/website.svg' alt='webpage-Web'>
         </a>
</p>

![xbhs3](assets/igenbench.png)

# 🔬 About
>Text-to-image models can generate visually appealing infographics — but are they correct?

IGenBench focuses on information **reliability** — whether a generated infographic is factually correct, numerically accurate, and semantically faithful to the input text and data.


# 🔨 Installation

You need to first install uv as package manager.

Installation methods: https://docs.astral.sh/uv/getting-started/installation/

Then, run the following commands:

```bash
# Clone the repository
git clone https://github.com/MisterBrookT/IGenBench.git
cd IGenBench
uv sync 

# Or install dev dependencies (optional)
uv sync --dev
```
---
## 🔧 Prepare

Before running IGenBench, please complete the following preparation steps.

### Download Dataset

Download the benchmark dataset from Hugging Face:

```bash
# Using huggingface-hub (recommended)
mkdir hf_datasets
cd hf_datasets
hf download Brookseeworld/IGenBench-Dataset \
  --repo-type dataset \
  --local-dir .
```
### Set API Keys
IGenBench currently supports the following providers:
- Google — official Google API.
- OpenRouter — proxy provider for multiple LLMs.
- Replicate — proxy provider for image generation.

Please follow the official documentation of your chosen provider and set the required API keys as environment variables.
Also, feel free to add your model or new provider, related code are in nanochart/utils/llm/llm_caller.py

---
# 💪 Usage

## Image Generation

Generate infographic images from text prompts:

```bash
igenbench gen \
  --info-path hf_datasets/data/1.json \
  --output-dir outputs/ \
  --provider google \
  --model gemini-2.5-flash-image
```

**Parameters:**
- `--info-path`: Path to the VISItem JSON file
- `--output-dir`: Directory to save generated images (default: `outputs/`)
- `--provider`: LLM provider (default: `google`)
- `--model`: Model name for generation (default: `gemini-2.0-flash-exp`)
- `--resume`: Resume from existing state to skip already generated images

## Evaluation

Evaluate generated images using the benchmark questions:

```bash
igenbench eval \
  --info-path hf_datasets/data/1.json \
  --gen-model gemini-2.5-flash-image \
  --image-path outputs/1/1_gemini_2_5_flash_image.png \
  --output-dir outputs/ \
  --provider google \
  --model gemini-2.5-flash
```

**Parameters:**
- `--info-path`: Path to the VISItem JSON file
- `--gen-model`: Name of the model that generated the image
- `--image-path`: Path to the generated image (optional, auto-resolved if not provided)
- `--output-dir`: Directory to save evaluation results (default: `outputs/`)
- `--provider`: LLM provider for evaluation (default: `google`)
- `--model`: Model name for evaluation (default: `gemini-2.5-flash`)
- `--resume`: Resume from existing state to skip already evaluated questions

**Example output:**
```
09:54:29 | INFO | eval_workflow.py:75 | 🔍 Evaluating item 1 with gemini-2.5-flash on test-model
09:54:29 | INFO | eval_workflow.py:109 | ⏭️  Skipping question 1 / 8 (already evaluated by gemini-2.5-flash on test-model)
09:54:29 | INFO | eval_workflow.py:109 | ⏭️  Skipping question 2 / 8 (already evaluated by gemini-2.5-flash on test-model)
09:54:29 | INFO | eval_workflow.py:109 | ⏭️  Skipping question 3 / 8 (already evaluated by gemini-2.5-flash on test-model)
09:54:29 | INFO | eval_workflow.py:115 | 🔍 Evaluating item 1 with gemini-2.5-flash on test-model -> 4 / 8
09:54:32 | INFO | eval_workflow.py:115 | 🔍 Evaluating item 1 with gemini-2.5-flash on test-model -> 5 / 8
09:54:36 | INFO | eval_workflow.py:115 | 🔍 Evaluating item 1 with gemini-2.5-flash on test-model -> 6 / 8
09:54:39 | INFO | eval_workflow.py:115 | 🔍 Evaluating item 1 with gemini-2.5-flash on test-model -> 7 / 8
09:54:43 | INFO | eval_workflow.py:115 | 🔍 Evaluating item 1 with gemini-2.5-flash on test-model -> 8 / 8
09:54:48 | INFO | eval_cli.py:56 | ✅ Evaluation completed successfully for 1.json, saved to tmp/test_eval_output/1/1.json
```




# 📝 Citation

If you find *IGenBench* useful for your research, please cite our paper:

```bibtex
@misc{tang2026igenbenchbenchmarkingreliabilitytexttoinfographic,
      title={IGenBench: Benchmarking the Reliability of Text-to-Infographic Generation}, 
      author={Yinghao Tang and Xueding Liu and Boyuan Zhang and Tingfeng Lan and Yupeng Xie and Jiale Lao and Yiyao Wang and Haoxuan Li and Tingting Gao and Bo Pan and Luoxuan Weng and Xiuqi Huang and Minfeng Zhu and Yingchaojie Feng and Yuyu Luo and Wei Chen},
      year={2026},
      eprint={2601.04498},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/2601.04498}, 
}
```
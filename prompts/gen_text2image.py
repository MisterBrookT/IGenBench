from nanochart.vis_item import VISItem


def get_prompt_text2image(item: VISItem) -> str:
    design_draft = item.design_space.design_draft.strip()

    prompt = f"""

\"\"\"{design_draft}\"\"\"

**Requirements**:
1. Follow the layout, structure, and visual intent implied by the design draft, including charts, text, and any suggested icons.
2. Use the dataset exactly as given; do not change or invent values.
3. Maintain a clean, modern, readable aesthetic with clear data encoding.

**Output**:
A polished infographic image that reflects both the dataset and the design draft.
"""
    return prompt

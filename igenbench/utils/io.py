import os
import re
from pathlib import Path
import json


def read_prompt(file_path: str | Path) -> str:
    """
    Read a prompt from a text or markdown file.
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")


def extract_from_markdown(text: str) -> dict | str:
    """
    Extract content from LLM response with fenced code block.
    If no code block found, try to parse as JSON, otherwise return original text.
    """
    # First try to parse the entire text as JSON (in case it's already JSON)
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Match any fenced code block: ```lang or just ```
    pattern = r"```(?:\w+)?\s*(.*?)\s*```"
    match = re.search(pattern, text, re.DOTALL)

    if match:
        content = match.group(1).strip()
        # Try JSON first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return content

    # No code block and not JSON, return original text
    return text


def read_csv(file_path: str | Path) -> str:
    """
    Read a CSV file and return the content as a string.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def get_output_subdir(info_path: str, output_dir: str = "outputs/") -> str:
    """
    Get output subdirectory based on input file prefix.

    e.g., "tmp/1.json" + "outputs/" -> "outputs/1/"
    """
    prefix = os.path.basename(info_path).split(".")[0]
    sub_dir = os.path.join(output_dir, prefix)
    os.makedirs(sub_dir, exist_ok=True)
    return sub_dir


def get_source_image_path(info_path: str) -> str | None:
    """
    Find source image file in the same directory as info_path.

    e.g., "tmp/0.json" -> looks for "tmp/0.jpeg", "tmp/0.jpg", "tmp/0.png", "tmp/0.webp"

    Args:
        info_path: Path to the JSON file (e.g., "tmp/0.json")

    Returns:
        Path to the image file if found, None otherwise
    """
    info_path_obj = Path(info_path)
    directory = info_path_obj.parent
    prefix = info_path_obj.stem

    # Try common image extensions
    for ext in [".jpeg", ".jpg", ".png", ".webp"]:
        candidate = directory / f"{prefix}{ext}"
        if candidate.exists():
            return str(candidate)

    return None


def get_model_name_from_image_path(image_path: Path | str) -> str:
    """
    Get the model name from the image path.

    Note: This function is deprecated in favor of passing gen_model_name directly
    to evaluation workflows. It's kept for backward compatibility.
    """
    image_path = Path(image_path)
    stem = image_path.stem
    return stem.split("_")[-1]


def split_senmantic_and_data_in_t2i_prompt(t2i_prompt: str) -> tuple[str, str]:
    """
    Split the semantic and data parts of the T2I prompt.
    """
    return t2i_prompt.split("The given data is:")



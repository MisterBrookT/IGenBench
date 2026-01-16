from __future__ import annotations
import json
import os
from dataclasses import dataclass, asdict, field
from typing import Any, Optional, List, Dict


@dataclass
class Judgment:
    """Single judgment result for an evaluation question."""

    eval_model: str
    gen_model: str
    analysis: str
    answer: str


@dataclass
class Question:
    """Evaluation question with metadata."""

    item_id: str
    q_id: str
    q_ground: str
    q: str
    q_type: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "item_id": self.item_id,
            "q_id": self.q_id,
            "q_ground": self.q_ground,
            "q": self.q,
            "q_type": self.q_type,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Question":
        """Create Question from dictionary."""
        return cls(
            item_id=data["item_id"],
            q_id=data["q_id"],
            q_ground=data["q_ground"],
            q=data["q"],
            q_type=data["q_type"],
        )

    @classmethod
    def from_jsonl_line(cls, line: str) -> "Question":
        """Create Question from JSONL line."""
        data = json.loads(line.strip())
        return cls.from_dict(data)

    def to_jsonl_line(self) -> str:
        """Convert to JSONL line format."""
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def load_from_jsonl(
        cls, file_path: str, item_id: Optional[str] = None
    ) -> List["Question"]:
        """Load questions from JSONL file, optionally filtered by item_id."""
        questions = []
        try:
            with open(file_path, "r") as f:
                for line in f:
                    if line.strip():
                        question = cls.from_jsonl_line(line)
                        if item_id is None or question.item_id == item_id:
                            questions.append(question)
        except FileNotFoundError:
            pass  # Return empty list if file doesn't exist
        return questions


@dataclass
class EvalEntry:
    """Evaluation entry containing a question and its judgments."""

    source: str = ""  # "prompt" or "seed"
    ground: str = ""
    question: str = ""
    question_type: str = ""
    judgments: List[Judgment] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "EvalEntry":
        """Create EvalEntry from dict."""
        # Convert judgments from dict to Judgment objects
        judgments_data = data.get("judgments", [])
        judgments = []
        for j in judgments_data:
            if isinstance(j, dict):
                judgments.append(
                    Judgment(
                        eval_model=j.get("eval_model", ""),
                        gen_model=j.get("gen_model", ""),
                        analysis=j.get("analysis", ""),
                        answer=j.get("answer", ""),
                    )
                )
            elif isinstance(j, Judgment):
                judgments.append(j)

        return cls(
            source=data.get("source", ""),
            question=data.get("question", ""),
            ground=data.get("ground", ""),
            question_type=data.get("question_type", ""),
            judgments=judgments,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert EvalEntry to dict."""
        result = {
            "source": self.source,
            "ground": self.ground,
            "question": self.question,
            "question_type": self.question_type,
            "judgments": [asdict(j) for j in self.judgments],
        }
        return result

    def has_judgment(self, gen_model: str, eval_model: str) -> bool:
        """Check if judgment exists for given models."""
        return any(
            j.gen_model == gen_model and j.eval_model == eval_model
            for j in self.judgments
        )

    def add_judgment(
        self, gen_model: str, eval_model: str, analysis: str, answer: str
    ) -> None:
        """Add a new judgment."""
        self.judgments.append(
            Judgment(
                eval_model=eval_model,
                gen_model=gen_model,
                analysis=analysis,
                answer=answer,
            )
        )


@dataclass
class VISItem:
    # Core fields
    id: str | None = None
    reference_image_url: Optional[str] = None
    t2i_prompt: Optional[str] = None
    chart_type: Optional[str] = None
    
    # generation result: {model_name: image_path}
    generation: Optional[dict] = field(default_factory=dict)

    # evaluation result: List[EvalEntry] with source field
    # Each entry has: source ("prompt" or "seed"), ground, question, question_type, judgments
    evaluation: List[EvalEntry] = field(default_factory=list)

    def update_generation(self, model: str, image_path: str) -> None:
        """Update the generation result."""
        self.generation[model] = image_path

    def check_generation_exists(self, model: str) -> bool:
        """Check if generation result exists for a model."""
        return model in self.generation and self.generation[model] is not None

    def get_evaluation_by_source(self, source: str) -> List[EvalEntry]:
        """Get evaluation entries filtered by source (prompt or seed)."""
        return [entry for entry in self.evaluation if hasattr(entry, 'source') and entry.source == source]

    def check_evaluation_complete(
        self, gen_model: str, eval_model: str
    ) -> bool:
        """Check if all questions have been fully evaluated for the given models."""
        if not self.evaluation:
            return False

        for eval_entry in self.evaluation:
            if not eval_entry.has_judgment(gen_model, eval_model):
                return False

        return True

    @classmethod
    def from_dict(cls, info_path: str) -> "VISItem":
        """Create VISItem from a json file"""
        info_data = json.load(open(info_path, "r"))

        # Build kwargs for new format
        kwargs = {
            "id": info_data["id"],
        }

        # Add optional fields
        if "reference_image_url" in info_data:
            kwargs["reference_image_url"] = info_data["reference_image_url"]
        if "t2i_prompt" in info_data:
            kwargs["t2i_prompt"] = info_data["t2i_prompt"]
        if "chart_type" in info_data:
            kwargs["chart_type"] = info_data["chart_type"]
        if "generation" in info_data:
            kwargs["generation"] = info_data["generation"]
        
        # Handle evaluation - now a list with source field
        if "evaluation" in info_data:
            evaluation = []
            for entry in info_data["evaluation"]:
                eval_entry = EvalEntry.from_dict(entry) if isinstance(entry, dict) else entry
                # Add source field to eval_entry if it exists in the data
                if isinstance(entry, dict) and "source" in entry:
                    eval_entry.source = entry["source"]
                evaluation.append(eval_entry)
            kwargs["evaluation"] = evaluation

        return cls(**kwargs)

    def build_save_dir(self, output_dir: str) -> str:
        """Build the save directory for the VISItem"""
        return os.path.join(output_dir, self.id)

    def build_save_path(self, output_dir: str) -> str:
        """Build the save path for the VISItem"""
        return os.path.join(output_dir, self.id, f"{self.id}.json")

    def save_item(self, output_path: str) -> None:
        """Save VISItem to a json file

        Args:
            output_path: Can be either a directory path or a file path.
                        If it's a directory, saves to {output_path}/{id}/{id}.json
                        If it's a file path (ends with .json), saves directly to that path
        """
        # Check if output_path is a file path or directory path
        if output_path.endswith(".json"):
            save_path = output_path
        else:
            save_path = self.build_save_path(output_path)

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        # Convert to dict with proper serialization
        data = asdict(self)
        
        # Convert EvalEntry objects to dicts and preserve source field
        evaluation_list = []
        for entry in data["evaluation"]:
            entry_dict = entry.to_dict() if isinstance(entry, EvalEntry) else entry
            # Add source field if it exists
            if hasattr(entry, 'source'):
                entry_dict["source"] = entry.source
            evaluation_list.append(entry_dict)
        data["evaluation"] = evaluation_list

        with open(save_path, "w") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

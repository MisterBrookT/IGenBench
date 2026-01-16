from igenbench.engine.base_engine import BaseEngine
from igenbench.utils.llm.client import LLMClient
from igenbench.vis_item import Judgment, VISItem, EvalEntry
from prompts.eval_judge_factual_qa import build_factual_qa_judgment_prompt


class EvalEngine(BaseEngine):
    """Evaluation engine for judgment tasks."""

    def __init__(self, llm_client: LLMClient, model: str):
        super().__init__(llm_client, model)

    def check_eval_entry_being_judged(
        self, eval_entry: EvalEntry, gen_model: str, eval_model: str
    ) -> bool:
        """Check whether a specific question entry already has a judgment for the given models."""
        return eval_entry.has_judgment(gen_model, eval_model)

    def check_fully_evaluated(
        self, item: VISItem, gen_model: str, eval_model: str
    ) -> bool:
        """Check whether all questions have been evaluated for the given models."""
        return item.check_evaluation_complete(gen_model, eval_model)

    def judge_entry(
        self,
        eval_entry: EvalEntry,
        gen_model: str,
        eval_model: str,
        image_path: str,
    ) -> Judgment:
        """Judge an evaluation entry by calling LLM with the image.
        
        Args:
            eval_entry: Evaluation entry containing the question
            gen_model: Name of the model that generated the image
            eval_model: Name of the model performing evaluation
            image_path: Path to the generated image
            
        Returns:
            Judgment object with analysis and answer
        """
        question = eval_entry.question
        if not question:
            raise ValueError("Question is required")

        question_judgment_prompt = build_factual_qa_judgment_prompt(question)
        response = self.llm_client.call_image_understanding(
            model=eval_model, image_path=image_path, prompt=question_judgment_prompt
        )

        judgment = Judgment(
            eval_model=eval_model,
            gen_model=gen_model,
            analysis=response.get("analysis", ""),
            answer=response.get("answer", ""),
        )

        return judgment

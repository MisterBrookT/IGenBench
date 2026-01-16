from igenbench.engine.base_engine import BaseEngine
from igenbench.utils.llm.client import LLMClient
from igenbench.vis_item import VISItem


class GenEngine(BaseEngine):
    """Generation engine for text-to-image tasks."""

    def __init__(self, llm_client: LLMClient, model: str):
        super().__init__(llm_client, model)

    def text2image(self, item: VISItem):
        """Generate image from text prompt.
        
        Args:
            item: VISItem containing t2i_prompt
            
        Returns:
            PIL Image object
        """
        if not item.t2i_prompt:
            raise ValueError("Generation requires t2i_prompt to be set")
            
        prompt = item.t2i_prompt
        response = self.llm_client.call_image_generation(
            model=self.model, prompt=prompt
        )
        return response

from .prompt_generator import PromptGenerator
from .style_extraction_agent import StyleExtractionAgent
from .prompt_generation_pipline import PromptGenerationPipeline
from flask import current_app
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)

# potential bug: image generation rate prompts
def process_generation_request(
    pipeline: PromptGenerationPipeline,
    user_description: str = "Generate a creative and visually appealing image",
    feedback: Optional[Dict] = None
) -> Dict[str, List[str]]:
    """
    Processes a user request for image generation.
    Handles feedback, calls the appropriate pipeline generation method,
    and returns prompts and extracted features.

    Args:
        pipeline: The PromptGenerationPipeline instance.
        user_description: User input for prompt generation.
        feedback: Optional feedback information from the user.

    Returns:
        Dictionary containing:
        - prompts: List of generated prompts.
        - extracted_features: Features extracted from the prompts.
    """
    if feedback:
        pipeline.provide_feedback(
            feedback.get("liked_prompts", []),
            feedback.get("liked_style_keywords", [])
        )

    is_initial = len(pipeline.preferences["liked_prompts"]) == 0

    if is_initial:
        result = pipeline.generate_initial_prompts(user_description=user_description)
    else:
        result = pipeline.generate_refined_prompts(user_description=user_description)

    logger.info(f'Generated Prompts: {result["prompts"]}')
    print("Generated prompts:", result["prompts"])

    return result
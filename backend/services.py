from .prompt_generator import PromptGenerator
from flask import current_app
from typing import List, Optional
import logging
from .utils import process_prompts

logger = logging.getLogger(__name__)

# potential bug: image generation rate prompts
def create_prompts(user_description: str = "Generate a creative and visually appealing image", selected_prompts:Optional[str] = None) -> list:
    """
    Generate 6 unique image prompts using the PromptGenerator.
    
    Args:
        user_description: Optional user input for prompt generation
        
    Returns:
        List of 6 generated prompts
    """
    generator = PromptGenerator(current_app.openai_client)
    prompts = generator.generate_prompts(
        user_description=user_description,
        additional_context = selected_prompts
    )
    input_prompts = process_prompts(prompts)
    logger.info(f'Prompts: {input_prompts}')
    print("generating prompts", input_prompts)
    return input_prompts
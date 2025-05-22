from .prompt_generator import PromptGenerator
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def create_10_prompts(user_description: str = "Generate a creative and visually appealing image") -> list:
    """
    Generate 10 unique image prompts using the PromptGenerator.
    
    Args:
        user_description: Optional user input for prompt generation
        
    Returns:
        List of 10 generated prompts
    """
    generator = PromptGenerator(current_app.openai_client)
    prompts = generator.generate_prompts(
        user_description=user_description,
        num_prompts=2
    )
    logging.info(f'Prompts: {prompts}')
    return prompts
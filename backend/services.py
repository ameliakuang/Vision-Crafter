from .prompt_generator import PromptGenerator
from flask import current_app
import logging
from .utils import process_prompts

logger = logging.getLogger(__name__)

# potential bug: image generation rate prompts
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
        user_description=user_description
    )
    input_prompts = process_prompts(prompts)
    logger.info(f'Prompts: {input_prompts}')
    print("generating prompts", input_prompts)
    return input_prompts
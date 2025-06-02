from .prompt_generator import PromptGenerator
from flask import current_app
from typing import List, Optional, Dict
import logging
from .utils import process_prompts

logger = logging.getLogger(__name__)

# potential bug: image generation rate prompts
def create_prompts(
    user_description: str = "Generate a creative and visually appealing image", 
    selected_prompts: Optional[str] = None,
    is_initial: bool = True
) -> Dict[str, List[str]]:
    """
    Generate image prompts using the PromptGenerator.
    
    Args:
        user_description: User input for prompt generation
        selected_prompts: Previously selected prompts for context
        is_initial: Whether this is the initial generation
        
    Returns:
        Dictionary containing:
        - prompts: List of generated prompts
        - extracted_features: Features extracted from the prompts
    """
    generator = PromptGenerator(current_app.openai_client)
    
    if is_initial:
        # First-time generation, use initial generation logic
        prompts = generator.generate_prompts(
            user_description=user_description,
            initial_prompt=True  # Mark this as initial generation
        )
    else:
        # Non-initial generation, use optimized generation logic
        prompts = generator.generate_prompts(
            user_description=user_description,
            additional_context=selected_prompts
        )
    
    # Process generated prompts
    input_prompts = process_prompts(prompts)
    logger.info(f'Prompts: {input_prompts}')
    print("generating prompts", input_prompts)
    
    # Extract features
    style_agent = current_app.style_agent
    extracted_features = style_agent.extract_features(input_prompts)
    
    return {
        "prompts": input_prompts,
        "extracted_features": extracted_features
    }
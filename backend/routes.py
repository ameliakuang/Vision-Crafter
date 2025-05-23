from flask import Blueprint, current_app, request, jsonify
from .services import create_10_prompts
import logging
import asyncio
from together import Together
import time
from typing import List, Dict

api_bp = Blueprint("api", __name__)
logger = logging.getLogger(__name__)

async def generate_single_image(together: Together, prompt: str, max_retries: int = 3) -> Dict:
    """
    Generate a single image with retry mechanism
    
    Args:
        together: Together API client
        prompt: Image generation prompt
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dict containing prompt and image URL if successful
    """
    retry_count = 0
    while retry_count < max_retries:
        try:
            logger.info(f"Generating image for prompt: {prompt}")
            resp = together.images.generate(
                model="black-forest-labs/FLUX.1-schnell-Free",
                prompt=prompt,
                steps=4,
                n=1
            )
            
            if resp.data and resp.data[0].url:
                logger.info(f"Successfully received image URL for prompt")
                return {
                    "prompt": prompt,
                    "url": resp.data[0].url
                }
            else:
                logger.error(f"No image URL received for prompt")
                retry_count += 1
                continue
                
        except Exception as e:
            if "RateLimitError" in str(e):
                logger.warning(f"Rate limit hit, waiting before retry...")
                # Wait for 10 seconds before retrying
                await asyncio.sleep(10)
            else:
                logger.error(f"Error generating image for prompt '{prompt}': {str(e)}")
                logger.exception(e)
            
            retry_count += 1
            if retry_count < max_retries:
                continue
            else:
                logger.error(f"Max retries reached for prompt: {prompt}")
                return None

async def generate_images_parallel(together: Together, prompts: List[str]) -> List[Dict]:
    """
    Generate multiple images in parallel
    
    Args:
        together: Together API client
        prompts: List of prompts to generate images for
        
    Returns:
        List of dictionaries containing prompts and image URLs
    """
    # Create tasks for all prompts
    tasks = [generate_single_image(together, prompt) for prompt in prompts]
    
    # Execute all tasks concurrently
    results = await asyncio.gather(*tasks)
    
    # Filter out None results (failed generations)
    return [result for result in results if result is not None]

@api_bp.route("/generate-images", methods=["POST"])
async def gen_images():
    """
    POST  /api/generate-images
    Body: { "description": "user's description" }
    Returns: { "images": [{"prompt": "...", "url": "..."}, ...] }
    """
    # Get the user's description
    data = request.get_json(force=True)
    description = data.get("description", "Generate a creative and visually appealing image")
    
    # Generate prompts first
    prompts = create_10_prompts(description)
    
    # Generate images in parallel
    together = current_app.together_client
    result = await generate_images_parallel(together, prompts)
    print("generating image:", result)

    return jsonify({
        "results": result
    })


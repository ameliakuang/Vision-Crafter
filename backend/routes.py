from flask import Blueprint, current_app, request, jsonify
from .services import process_generation_request
import logging
import asyncio
from together import Together
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from .prompt_generation_pipline import PromptGenerationPipeline
from .prompt_generator import PromptGenerator
from .style_extraction_agent import StyleExtractionAgent

api_bp = Blueprint("api", __name__)
logger = logging.getLogger(__name__)

# Global thread pool executor for running sync methods in threads
executor = ThreadPoolExecutor()
# Semaphore to limit maximum concurrent API calls
semaphore = asyncio.Semaphore(6) 

async def generate_single_image(together: Together, prompt: str, max_retries: int = 3) -> Dict:
    """
    Generate a single image with retry mechanism using thread pool for non-blocking behavior
    """
    retry_count = 0
    while retry_count < max_retries:
        try:
            logger.info(f"Generating image for prompt: {prompt}")

            # Use run_in_executor to offload the blocking call
            def blocking_call():
                return together.images.generate(
                    model="black-forest-labs/FLUX.1-schnell",
                    prompt=prompt,
                    steps=4,
                    n=1
                )

            async with semaphore:  # Limit concurrency to avoid API overload
                resp = await asyncio.get_event_loop().run_in_executor(executor, blocking_call)

            if resp.data and resp.data[0].url:
                logger.info(f"Image generated successfully for prompt")
                return {
                    "prompt": prompt,
                    "url": resp.data[0].url
                }
            else:
                logger.warning(f"No image URL received, retrying...")
                retry_count += 1
                continue

        except Exception as e:
            if "RateLimitError" in str(e):
                logger.warning(f"Rate limit hit, waiting before retry...")
                await asyncio.sleep(5)
            else:
                logger.error(f"Error generating image for prompt '{prompt}': {str(e)}")
                logger.exception(e)

            retry_count += 1
            if retry_count >= max_retries:
                logger.error(f"Max retries reached for prompt: {prompt}")
                return None

async def generate_images_parallel(together: Together, prompts: List[str]) -> List[Dict]:
    """
    Generate multiple images in parallel using asyncio with thread pool
    """
    tasks = [generate_single_image(together, prompt) for prompt in prompts]
    results = await asyncio.gather(*tasks)
    return [result for result in results if result is not None]

@api_bp.route("/generate-images", methods=["POST"])
async def gen_images():
    """
    POST /api/generate-images
    Body: {
        "description": "user's description",
        "feedback": {  # Optional feedback information
            "liked_prompt_indices": [0, 2], # Indices relative to the LAST batch shown to the user
            "liked_style_keywords": ["minimalist", "impressionist"]
        }
    }
    Returns: {
        "prompts": ["prompt1", "prompt2", ...],  # Generated prompts
        "extracted_features": { ... },  # Extracted features
        "results": [{"prompt": "...", "url": "..."}, ...]  # Generated images
    }
    """
    data = request.get_json(force=True)
    description = data.get("description", "Generate a creative and visually appealing image")
    feedback = data.get("feedback", None)

    # Get the pipeline instance (assuming it's attached to current_app)
    pipeline = current_app.pipeline

    # Process the request using the service function
    # The service function now handles feedback and calls the correct pipeline method
    generation_result = process_generation_request(
        pipeline=pipeline,
        user_description=description,
        feedback=feedback
    )

    # Generate images in parallel
    together = current_app.together_client
    image_results = await generate_images_parallel(together, generation_result["prompts"])

    return jsonify({
        "prompts": generation_result["prompts"],
        "extracted_features": generation_result["extracted_features"],
        "results": image_results
    })

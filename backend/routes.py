from flask import Blueprint, current_app, request, jsonify
from .services import create_10_prompts
import logging

api_bp = Blueprint("api", __name__)
logger = logging.getLogger(__name__)

@api_bp.route("/generate-images", methods=["POST"])
def gen_images():
    """
    POST  /api/generate-images
    Body: { "description": "user's description" }
    Returns: { "images": [{"prompt": "...", "url": "..."}, ...] }
    """
    data = request.get_json(force=True)
    description = data.get("description", "Generate a creative and visually appealing image")
    
    # Generate prompts first
    prompts = create_10_prompts(description)
    
    # Generate images for each prompt
    together = current_app.together_client
    result = []
    
    for prompt in prompts:
        try:
            logger.info(f"Generating image for prompt: {prompt}")
            resp = together.images.generate(
                model="black-forest-labs/FLUX.1-schnell-Free",
                prompt=prompt,
                steps=4,
                n=1  # Generate one image per prompt
            )
            logger.info(f"Together API response for image: {resp}")
            if resp.data and resp.data[0].url:
                result.append({
                    "prompt": prompt,
                    "url": resp.data[0].url
                })
                logger.info(f"Successfully receive image url for prompt")
            else:
                logger.error(f"No image URL received for prompt")
                continue
        except Exception as e:
            logger.error(f"Error generating image for prompt '{prompt}': {str(e)}")
            logger.exception(e)
            continue

    return jsonify({
        "results": result
    })


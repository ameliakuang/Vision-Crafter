from openai import OpenAI
from typing import List, Optional
import numpy as np
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()
logger = logging.getLogger(__name__)

class PromptGenerator:
    def __init__(self, openai_client: OpenAI):
        self.openai_client = openai_client

        self.base_system_message_template = """You are a professional image prompt generation expert. Your tasks are:
        1. Generate {num_prompts} different detailed and vivid image prompts based on user's brief description
        2. Each prompt should contain rich visual elements and artistic styles
        3. Ensure the generated prompts are suitable for AI image generation models like Stable Diffusion or DALL·E
        4. Each prompt should be unique, creative and diverse
        5. Each prompt should have a distinct artistic style. You can use any style you can think of, such as (but not limited to):
        - Photorealistic/Realistic style
        - Cartoon/Anime style
        - Watercolor/Painting style
        - Sketch/Drawing style
        - Cyberpunk/Sci-fi style
        - Fantasy/Magical style
        - Minimalist/Simple style
        - Abstract/Modern art style
        - Chinese ink painting style
        - Impressionist style
        - And any other creative styles you can imagine
        6. Make sure to explicitly mention the style in each prompt
        7. Feel free to combine different styles or create unique style variations"""
    
    def generate_prompts(
        self,
        user_description: str,
        additional_context: Optional[str] = None,
        num_prompts: int = 10,
        style_preferences: Optional[List[str]] = None
    ) -> List[str]:
        """
        Generate image prompts.

        Args:
            user_description: User's input image description
            additional_context: Optional additional context information (such as previous prompts for in-context learning)
            num_prompts: Number of prompts to generate, default is 10
            style_preferences: Optional list of style preferences
        """
        # Build complete system message
        system_message = self.base_system_message_template.format(num_prompts=num_prompts)
        if style_preferences:
            system_message += f"\nPlease focus on these styles: {', '.join(style_preferences)}"
        if additional_context:
            system_message += f"\nAdditional requirements or context: {additional_context}"
            
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": f"Please generate {num_prompts} different image prompts based on this description, each prompt should be unique and creative: {user_description}"}
                ],
                temperature=0.8,
                max_tokens=2000,
                top_p=0.95,
                frequency_penalty=0.7,
                presence_penalty=0.7,
            )
            # Parse response and return prompt list
            generated_text = response.choices[0].message.content
            prompts = [prompt.strip() for prompt in generated_text.split('\n') if prompt.strip()]
            return prompts[:num_prompts]

        
            
        except Exception as e:
            print(f"Error occurred while generating prompts: {str(e)}")
            return []

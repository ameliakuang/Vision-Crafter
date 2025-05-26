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
        3. Ensure the generated prompts are suitable for AI image generation models like Stable Diffusion or DALL·E
        4. Each prompt should be unique, creative and diverse
        5. Each prompt should have a different style at the beginning.
        6. Make sure to explicitly mention the style in each prompt
        7. Feel free to combine different styles or create unique style variations
        8. Ensure the generated image styles are highly relevant and consistent with the user's input description.
        9. Format Requirement: Output must strictly follow this format:
            1. "Prompt text one."
            2. "Prompt text two."
            3. "Prompt text three."
           Each prompt must:
            - Begin with a number followed by a period
            - Be enclosed entirely in double quotes (")
        """
    
    def generate_prompts(
        self,
        user_description: str,
        additional_context: Optional[str] = None,
        num_prompts: int = 6,
        style_preferences: Optional[List[str]] = None
    ) -> List[str]:
        """
        Generate image prompts.

        Args:
            user_description: User's input image description
            additional_context: Optional additional context information (such as previous prompts for in-context learning)
            num_prompts: Number of prompts to generate, default is 6
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
                max_tokens=1000,
                top_p=0.95,
                frequency_penalty=0.7,
                presence_penalty=0.7,
            )
            # Parse response and return prompt list
            generated_text = response.choices[0].message.content
            prompts = [prompt.strip() for prompt in generated_text.split('\n') if prompt.strip()]
            print("++++++++++++", prompts)
            return prompts

        
            
        except Exception as e:
            print(f"Error occurred while generating prompts: {str(e)}")
            return []

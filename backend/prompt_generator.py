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
        1. Generate {num_prompts} different detailed and vivid image prompts based on user's brief description.
        2. Ensure the generated prompts are suitable for AI image generation models like Stable Diffusion or DALL·E.
        3. Format Requirement: Output must strictly follow this format:
            1. \"Prompt text one.\"\n            2. \"Prompt text two.\"\n            ...\n           Each prompt must:
            - Begin with a number followed by a period.
            - Be enclosed entirely in double quotes (\")."""

        self.initial_system_message_template = """
        4. Each prompt should be unique, creative and diverse.
        5. Each prompt should have a distinct artistic style at the beginning.
        6. Make sure to explicitly mention the style in each prompt.
        7. Feel free to combine different styles or create unique style variations.
        8. Ensure the generated image styles are highly relevant and consistent with the real world.
        """
    
    def generate_prompts(
        self,
        user_description: str,
        initial_prompt: bool = False,
        user_preferred_prompts: Optional[str] = None,
        num_prompts: int = 6,
        style_preferences: Optional[List[str]] = None
    ) -> List[str]:
        """
        Generate image prompts.

        Args:
            user_description: User's input image description
            user_preferred_prompts: Optional user preferred prompts context information (such as previous prompts for in-context learning)
            num_prompts: Number of prompts to generate, default is 6
            style_preferences: Optional list of style preferences
        """
        # Build complete system message
        system_message = self.base_system_message_template.format(num_prompts=num_prompts)
        
        if initial_prompt:
            system_message += self.initial_system_message_template
        else:
            # Add feedback handling instructions
            system_message += """
            When incorporating user feedback and preferred prompts:
            1. Analyze the style, composition, and artistic elements from preferred prompts
            2. Maintain consistency with previously successful prompts
            3. Ensure each new prompt builds upon successful elements while introducing fresh variations
            4. Pay special attention to specific details and elements that the user has shown preference for
            """

        # Construct the user prompt with clear sections
        prompt_sections = []
        
        # Base description
        prompt_sections.append(f"Generate {num_prompts} different image prompts based on user's initial prompt: {user_description}")
        
        # Handle user preferred prompts
        if user_preferred_prompts:
            logger.info(f"PromptGenerator: user_preferred_prompts is: {user_preferred_prompts}")
            prompt_sections.append(f"""
            Previous successful prompts that should guide the style and elements:
            {user_preferred_prompts}
            
            Requirements for new prompts:
            1. Match the artistic style and composition of the preferred prompts
            2. Maintain similar level of detail and complexity
            3. Keep consistent with successful elements while adding fresh variations
            """)
        
        # Handle style preferences
        if style_preferences:
            logger.info(f"PromptGenerator: style_preferences is: {style_preferences}")
            prompt_sections.append(f"""
            Style requirements:
            1. Strictly follow these style preferences: {', '.join(style_preferences)}
            2. Ensure each prompt incorporates these styles while maintaining creativity
            3. Balance style consistency with unique variations
            """)
        
        # Combine all sections
        prompt = "\n\n".join(prompt_sections)
        
        logger.info(f"PromptGenerator: current system_message is: {system_message}")
        logger.info(f"PromptGenerator: current prompt for the LLM is: {prompt}")
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
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
            return prompts

        
            
        except Exception as e:
            logger.error(f"Error occurred while generating prompts: {str(e)}")
            return []

from openai import OpenAI
from typing import List, Dict, Optional
import json

class StyleExtractionAgent:
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        # Default examples for in-context learning
        self.default_examples = [
            {
                "prompt": "A vibrant impressionist painting of a cat playing with a red ball in a sunlit garden, with delicate brushstrokes and warm colors",
                "extracted_features": {
                    "style": ["impressionist", "vibrant", "delicate brushstrokes"],
                    "subject": ["cat"],
                    "action": ["playing"],
                    "objects": ["red ball"],
                    "setting": ["sunlit garden"],
                    "colors": ["warm colors"]
                }
            },
            {
                "prompt": "A minimalist digital art of a futuristic cityscape at night, with neon lights and flying cars, rendered in cool blue tones",
                "extracted_features": {
                    "style": ["minimalist", "digital art", "futuristic"],
                    "subject": ["cityscape"],
                    "time": ["night"],
                    "objects": ["neon lights", "flying cars"],
                    "colors": ["cool blue tones"]
                }
            }
        ]

    def extract_features(
        self, 
        prompts: List[str], 
        num_keywords: int = 5,
        custom_examples: Optional[List[Dict]] = None
    ) -> Dict[str, List[str]]:
        """
        Extract detailed features from prompts, including style, subject, action, objects, etc.

        Args:
            prompts: List of prompts to analyze
            num_keywords: Number of keywords to extract per category
            custom_examples: Custom examples for in-context learning
                           Format: [{"prompt": str, "extracted_features": Dict[str, List[str]]}]

        Returns:
            Dictionary containing features for each category
        """
        # Use custom examples if provided, otherwise use default examples
        examples = custom_examples if custom_examples else self.default_examples
        
        # Build examples string
        examples_str = "\n".join([
            f"Prompt: {ex['prompt']}\nExtracted Features: {ex['extracted_features']}\n"
            for ex in examples
        ])

        # Construct the prompt
        prompt = f"""
        I will show you some example prompts and their extracted features, followed by the prompts you need to analyze.

        Examples:
        {examples_str}

        Now, please analyze the following prompts and extract their features in the same format as the examples.
        For each prompt, identify:
        - style: artistic style, technique, or visual approach
        - subject: main subject or focus
        - action: any actions or movements
        - objects: important objects or elements
        - setting: location or environment
        - colors: color schemes or specific colors
        - time: time of day or period
        - mood: emotional tone or atmosphere
        - details: any other notable details
        or anything else that is important to the prompt
        Prompts to analyze:
        {chr(10).join(f"{i+1}. {p}" for i, p in enumerate(prompts))}

        Please extract the most prominent features for each category, up to {num_keywords} items per category.
        Respond with a JSON object containing the extracted features for each prompt.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are an expert at analyzing image prompts and extracting detailed features. You understand artistic styles, composition, and visual elements."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000,
                response_format={ "type": "json_object" }
            )
            
            # Parse the returned JSON
            content = response.choices[0].message.content.strip()
            print("Extracted Features: ", content)
            return json.loads(content)
            
        except Exception as e:
            print(f"[StyleExtractionAgent] Failed to extract features: {e}")
            return {}

    def update_examples(self, new_examples: List[Dict]):
        """
        Update the examples used for in-context learning.

        Args:
            new_examples: New list of examples, following the same format as default_examples
        """
        self.default_examples = new_examples

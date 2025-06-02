import json
from datetime import datetime
from typing import List, Optional, Dict
from prompt_generator import PromptGenerator
from backend.style_extraction_agent import StyleExtractionAgent

class PromptGenerationPipeline:
    """
    A pipeline class that manages the entire prompt generation process, including:
    - Initial prompt generation
    - Refined prompt generation based on user feedback
    - Tracking prompt history and user preferences
    - Saving generation history
    """

    def __init__(self, prompt_generator: PromptGenerator, style_agent: StyleExtractionAgent):
        """
        Initialize the pipeline with a prompt generator and style extraction agent.
        
        Args:
            prompt_generator: An instance of PromptGenerator for generating prompts
            style_agent: An instance of StyleExtractionAgent for extracting style preferences
        """
        self.prompt_generator = prompt_generator
        self.style_agent = style_agent
        self.round = 1  # Track the current generation round
        self.history = []  # Store all generated prompts and feedback
        self.preferences = {
            "liked_prompts": [],  # Store user's liked complete prompts
            "style_keywords": []  # Store user's preferred style keywords
        }

    def generate_initial_prompts(self, user_description: str, num_prompts: int = 6) -> Dict[str, List[str]]:
        """
        Generate initial prompts and extract features for frontend feedback.
        
        Args:
            user_description: User's initial description for the image
            num_prompts: Number of prompts to generate (default: 6)
            
        Returns:
            Dictionary containing:
            - prompts: List of generated prompts
            - extracted_features: Features extracted from the prompts
        """
        print(f" [Round {self.round}] Generating diverse prompts...")
        prompts = self.prompt_generator.generate_prompts(
            user_description=user_description,
            num_prompts=num_prompts,
            initial_prompt=True  # Indicate this is initial generation
        )
        
        # Record generated prompts
        self._record_prompts(prompts, liked=None)
        
        # Extract features and return to frontend
        extracted_features = self._extract_style_preferences(prompts)
        
        # self.save_history_to_json()
        return {
            "prompts": prompts,
            "extracted_features": extracted_features
        }

    def generate_refined_prompts(self, user_description: str, num_prompts: int = 6) -> Dict[str, List[str]]:
        """
        Generate refined prompts using all historical preferences for in-context learning.
        
        Args:
            user_description: User's description for the image
            num_prompts: Number of prompts to generate (default: 6)
            
        Returns:
            Dictionary containing:
            - prompts: List of generated prompts
            - extracted_features: Features extracted from the prompts
        """
        print(f"[Round {self.round}] Generating refined prompts based on user preferences...")

        # Build context using all historical preferences
        additional_context = self._build_liked_prompts_context()
        
        # Use all historical style keywords
        style_preferences = self.preferences["style_keywords"]

        prompts = self.prompt_generator.generate_prompts(
            user_description=user_description,
            num_prompts=num_prompts,
            additional_context=additional_context,
            style_preferences=style_preferences
        )
        
        # Record generated prompts
        self._record_prompts(prompts, liked=None)
        
        # Extract features and return to frontend
        extracted_features = self._extract_style_preferences(prompts)
        
        # self.save_history_to_json()
        return {
            "prompts": prompts,
            "extracted_features": extracted_features
        }

    def provide_feedback(self, liked_prompt_indices: List[int], liked_style_keywords: List[str]):
        """
        Record user's feedback including both liked prompts and style keywords.
        
        Args:
            liked_prompt_indices: Indices of prompts that user liked
            liked_style_keywords: Style keywords that user liked
        """
        latest_batch_start = len(self.history) - len([h for h in self.history if h["liked"] is None])
        
        # Update prompt feedback in history
        for idx, item in enumerate(self.history[latest_batch_start:]):
            absolute_idx = latest_batch_start + idx
            if idx in liked_prompt_indices:
                self.history[absolute_idx]["liked"] = True
                # Add to liked prompts list
                self.preferences["liked_prompts"].append(item["prompt"])
            else:
                self.history[absolute_idx]["liked"] = None

        # Update style keyword preferences
        self.preferences["style_keywords"].extend(liked_style_keywords)
        # Remove duplicates while preserving order
        self.preferences["style_keywords"] = list(dict.fromkeys(self.preferences["style_keywords"]))
        
        self.round += 1
        # self.save_history_to_json()

    def _extract_style_preferences(self, prompts: List[str]) -> Dict[str, Dict[str, List[str]]]:
        """
        Extract features from prompts for frontend feedback.
        Called immediately after generating prompts.
        
        Args:
            prompts: List of prompts to analyze
            
        Returns:
            Dictionary containing extracted features for each prompt
        """
        if not prompts:
            return {}
            
        # Extract features
        features = self.style_agent.extract_features(prompts)
        return features

    def _build_liked_prompts_context(self) -> str:
        """
        Build context string from all liked prompts for in-context learning.
        
        Returns:
            Formatted string containing all liked prompts
        """
        if not self.preferences["liked_prompts"]:
            return ""
            
        return '\n'.join(
            [f'{i + 1}. "{p}"' for i, p in enumerate(self.preferences["liked_prompts"])]
        )

    def _record_prompts(self, prompts: List[str], liked: Optional[bool]):
        """
        Record generated prompts in history.
        
        Args:
            prompts: List of prompts to record
            liked: Feedback status (True/None)
        """
        for prompt in prompts:
            self.history.append({"prompt": prompt, "liked": liked})

    # def save_history_to_json(self, path: str = "prompt_history.json"):
    #     """
    #     Save the prompt generation history and preferences to a JSON file.
        
    #     Args:
    #         path: Path to save the history file
    #     """
    #     try:
    #         with open(path, "w") as f:
    #             json.dump({
    #                 "timestamp": datetime.now().isoformat(),
    #                 "rounds": self.round,
    #                 "history": self.history,
    #                 "preferences": self.preferences
    #             }, f, indent=2)
    #         print(f" Saved history to {path}")
    #     except Exception as e:
    #         print(f"Failed to save history: {str(e)}")

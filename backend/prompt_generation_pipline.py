import json
from datetime import datetime
from typing import List, Optional, Dict
from .prompt_generator import PromptGenerator
from .style_extraction_agent import StyleExtractionAgent

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

    def provide_feedback(self, liked_prompts: List[str], liked_style_keywords: List[str]):
        """
        Record user's feedback including liked prompts (by string) and style keywords.

        Args:
            liked_prompts: List of complete prompt strings that user liked from the latest batch.
            liked_style_keywords: Style keywords that user liked.
        """
        # Find the start of the latest batch in history
        # This logic remains to correctly identify which entries in history belong to the latest round
        latest_batch_start = len(self.history) - len([h for h in self.history if h["liked"] is None])
        
        # Iterate through the latest batch in history
        # and update the 'liked' status based on the provided liked_prompts strings
        latest_batch_prompts_in_history = self.history[latest_batch_start:]

        # First, mark all prompts in the latest batch as not liked (or None) by default
        for item in latest_batch_prompts_in_history:
             item["liked"] = None # Or False, depending on desired default for unliked in latest batch

        # Then, iterate through the provided liked_prompts strings
        # and find matching entries in the latest batch in history to mark them as liked
        updated_liked_prompts_list = self.preferences["liked_prompts"] # Start with existing liked prompts

        for liked_prompt_str in liked_prompts:
            found_in_latest_batch = False
            # Iterate through the *entries* in the latest batch in history
            for item in latest_batch_prompts_in_history:
                 # Check if the prompt string matches
                 if item["prompt"].strip() == liked_prompt_str.strip():
                      item["liked"] = True # Mark as liked in history
                      # Add the prompt string to the preferences liked_prompts list
                      # Avoid adding duplicates to the preferences list if the same prompt is liked again in a later round (less likely but possible)
                      if item["prompt"] not in updated_liked_prompts_list:
                          updated_liked_prompts_list.append(item["prompt"])
                      found_in_latest_batch = True
                      break # Assuming unique prompts in the latest batch for simplicity

            if not found_in_latest_batch:
                 print(f"Warning: Liked prompt string '{liked_prompt_str}' not found in the latest generation batch in history.")


        # Update the preferences liked_prompts list after processing the latest feedback
        self.preferences["liked_prompts"] = updated_liked_prompts_list

        # Update style keyword preferences - this logic remains the same
        self.preferences["style_keywords"].extend(liked_style_keywords)
        # Remove duplicates while preserving order
        self.preferences["style_keywords"] = list(dict.fromkeys(self.preferences["style_keywords"]))

        self.round += 1
        # self.save_history_to_json() # Uncomment if you want to save history here

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
